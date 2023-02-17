"""A Redis storage backend for the no_brute_force module."""

from datetime import datetime
from typing import Dict

from bag.reify import reify
from redis import StrictRedis

from . import BlockedIP, IPStorageDummy


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


class IPStorageRedis(IPStorageDummy):
    """Backend that uses Redis for storage."""

    @reify
    def redis_url(self):
        return self.kerno.pluserable_settings["redis_url"]

    @reify
    def redis(self):
        return get_default_connection(kerno=self.kerno, url=self.redis_url)

    def read(self) -> BlockedIP:
        """Return the current record for the IP address."""
        adict: Dict[bytes, bytes] = self.redis.hgetall(self.key)
        if adict:
            return BlockedIP(
                attempts=int(adict[b"attempts"]),
                blocked_until=datetime.fromisoformat(
                    adict[b"blocked_until"].decode("utf8")
                ),
            )
        else:
            return super().read()

    def write(self, entity: BlockedIP, timeout: int) -> None:
        """Store ``entity`` with ``timeout``."""
        assert entity.blocked_until
        self.redis.hmset(
            self.key,
            {
                "attempts": entity.attempts,
                "blocked_until": entity.blocked_until.isoformat(),
            },
        )
        self.redis.pexpire(self.key, timeout * 1000)  # milliseconds
