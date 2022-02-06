"""Prevent brute force by storing IP addresses in redis."""

from datetime import datetime, timedelta
from typing import Dict, Tuple

from bag.reify import reify
from redis import StrictRedis

from pluserable.strings import get_strings


# https://github.com/ericrasmussen/pyramid_redis_sessions/blob/master/pyramid_redis_sessions/connection.py
def get_default_connection(kerno, url="", redis_client=StrictRedis, **redis_options):
    """Return a Redis connection ready for use.

    Once a connection is established it is saved in `kerno.brute_redis`.

    ``url`` is a connection string that will be passed straight to
    `StrictRedis.from_url`. Example::

        redis://username:password@localhost:6379/0
    """
    # attempt to get an existing connection from the registry
    redis = getattr(kerno, "brute_redis", None)

    # if we found an active connection, return it
    if redis is not None:
        return redis

    # otherwise create a new connection
    if url:
        # remove defaults to avoid duplicating settings in the `url`
        redis_options.pop("password", None)
        redis_options.pop("host", None)
        redis_options.pop("port", None)
        redis_options.pop("db", None)
        # the StrictRedis.from_url option no longer takes a socket
        # argument. instead, sockets should be encoded in the URL if
        # used. example:
        #     unix://[:password]@/path/to/socket.sock?db=0
        redis_options.pop("unix_socket_path", None)
        # connection pools are also no longer a valid option for
        # loading via URL
        redis_options.pop("connection_pool", None)
        redis = redis_client.from_url(url, **redis_options)
    else:
        redis = redis_client(**redis_options)

    # save the new connection
    setattr(kerno, "brute_redis", redis)

    return redis


class BruteForceAidDummy:
    """A test double for BruteForceAidRedis.  Shows its public API."""

    def __init__(self, kerno, ip: str) -> None:  # noqa
        pass

    def store_login_failure(self) -> int:
        """Store an authentication failure.

        Return the number of seconds the user must wait before retrying,
        or zero if this feature is not enabled.
        """
        return 0

    def is_login_blocked(self) -> Tuple[int, str]:
        """Find out whether the IP address is currently blocked.

        Return a tuple (remaining_seconds: int, error_msg: str).
        """
        return (0, "")


class BruteForceAidRedis:
    """App component that prevents brute forcing login, storing IPs in redis."""

    one_day_in_milliseconds = 60 * 60 * 24 * 1000

    def __init__(self, kerno, ip: str) -> None:  # noqa
        self.kerno = kerno
        self.ip = ip

    @reify
    def name(self):
        """Return the key used in redis to store data about this remote IP."""
        return f"login-{self.ip}"

    @reify
    def redis(self):
        return get_default_connection(kerno=self.kerno, url=self.redis_url)

    @reify
    def redis_url(self):
        return self.kerno.pluserable_settings["redis_url"]

    @reify
    def seconds_after_login_fail(self) -> int:
        """Return the configured initial duration of a login block."""
        return int(self.kerno.pluserable_settings["seconds_after_login_fail"])

    def pure_get_new_time(
        self, now: datetime, attempts: int = 1
    ) -> Tuple[datetime, int]:
        """Compute the next moment until which this IP is getting blocked.

        Pure method (no IO) that returns a tuple (datetime, int_seconds).
        The first login failure requires the user to wait 15 seconds and this
        number increases exponentially each time the credentials are found wrong.
        """
        seconds = self.seconds_after_login_fail * (2 ** (attempts - 1))
        delta = timedelta(seconds=seconds)
        new_time = now + delta
        # print(seconds, new_time)
        return (new_time, seconds)

    def store_login_failure(self) -> int:
        """Store an authentication failure in redis.

        Each value stored in redis is a dict with {blocked_until, attempts}.
        The redis key expires one day after the most recent failed attempt;
        during this time the waiting time increases exponentially.

        Return the number of seconds the user must wait before retrying,
        or zero if this feature is not enabled.
        """
        if not self.redis_url:
            return 0

        adict: Dict[bytes, bytes] = self.redis.hgetall(self.name)
        # print("got:", self.ip, adict)
        attempts = int(adict[b"attempts"]) + 1 if adict else 1
        new_time, seconds = self.pure_get_new_time(
            now=datetime.utcnow(), attempts=attempts
        )
        if adict:
            self.redis.hset(
                name=self.name, key="blocked_until", value=new_time.isoformat()
            )
            self.redis.hincrby(name=self.name, key="attempts", amount=1)
        else:
            self.redis.hmset(
                self.name,
                {
                    "attempts": attempts,
                    "blocked_until": new_time.isoformat(),
                },
            )
        self.redis.pexpire(self.name, self.one_day_in_milliseconds)
        return seconds

    def is_login_blocked(self) -> Tuple[int, str]:
        """Find out whether the IP address is currently blocked.

        Return a tuple (remaining_seconds: int, error: str).
        """
        if not self.redis_url:
            return (0, "")  # allow login attempt
        template: str = get_strings(self.kerno).login_is_blocked
        byts_blocked = self.redis.hget(self.name, "blocked_until")
        if not byts_blocked:
            return (0, "")
        blocked_until = datetime.fromisoformat(byts_blocked.decode("utf8"))
        now = datetime.utcnow()
        if blocked_until < now:
            return (0, "")  # allow login attempt
        seconds = (blocked_until - now).seconds
        return (
            seconds,
            template.format(seconds=seconds, until=str(blocked_until).split(".")[0]),
        )
