"""Prevent abuse of certain features by temporarily storing IP addresses.

This can be used to prevent brute forced login and registration.

Each time an operation is attempted, the user must wait longer before trying again,
according to configuration or the default ``DURATIONS``.

The redis key expires when the highest block duration is reached.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from kerno.state import MalbonaRezulto

from pluserable.strings import get_strings


def min2sec(x: int) -> int:
    return x * 60


def hour2sec(x: int) -> int:
    return x * 60 * 60


DURATIONS = [  # Default operation block durations
    15,  # seconds
    min2sec(2),
    min2sec(9),
    min2sec(30),
    hour2sec(2),
    hour2sec(4),
    hour2sec(8),
    hour2sec(16),
    hour2sec(24),
]


@dataclass
class BlockedIP:
    """The record that gets stored for each IP address.

    If someone is not yet blocked, attempts == 0 and blocked_until == None.
    """

    attempts: int  # This gets incremented at each failed attempt.
    blocked_until: Optional[datetime]

    def get_remaining_time_blocked(self, now: Optional[datetime] = None) -> timedelta:
        if self.blocked_until is None:
            return timedelta(0)
        now = now or datetime.utcnow()
        return max(timedelta(0), self.blocked_until - now)

    def __bool__(self):
        """Evaluate instance as truish if currently blocked."""
        if self.blocked_until is None:
            return False
        return self.blocked_until > datetime.utcnow()


class IPStorageDummy:
    """A test double for IPStorageRedis. Shows its public API."""

    def __init__(self, kerno, operation: str, ip: str) -> None:  # noqa
        self.kerno = kerno
        self.operation = operation
        self.ip = ip

    @property
    def key(self):
        """Return the key used to store data about this remote IP."""
        return f"{self.operation}-{self.ip}"

    def read(self) -> BlockedIP:
        """Return the current record for the IP address."""
        return BlockedIP(attempts=0, blocked_until=None)

    def write(self, entity: BlockedIP, timeout: int) -> None:
        """Store ``entity`` with ``timeout``."""
        pass


class NoBruteForce:
    """App component that prevents brute forced operations."""

    def __init__(
        self, kerno, store: IPStorageDummy, block_durations: list[int] = DURATIONS
    ) -> None:  # noqa
        self.kerno = kerno
        self.store = store
        self.block_durations = block_durations  # in seconds

    def read(self) -> BlockedIP:
        """Return the current record for the IP address."""
        return self.store.read()

    @property
    def _highest_block_duration(self) -> int:
        """Return the longest block duration in seconds."""
        return self.block_durations[len(self.block_durations) - 1]

    def _get_new_time(self, now: datetime, attempts: int) -> Tuple[datetime, int]:
        """Compute the next moment until which this operation is blocked for the IP.

        Pure method (no IO) that returns a tuple (datetime, int_seconds).
        The first operation blocks subsequent operations for a number of seconds
        and this number increases each time, until the last item in *block_durations*.
        """
        seconds = self.block_durations[min(attempts - 1, len(self.block_durations) - 1)]
        new_time = now + timedelta(seconds=seconds)
        print(new_time, seconds)  # TODO remove
        return (new_time, seconds)

    def block_longer(self, old: Optional[BlockedIP] = None) -> Tuple[BlockedIP, int]:
        """Block the IP for longer than before."""
        old = old or self.read()
        attempts = old.attempts + 1
        new_time, seconds = self._get_new_time(now=datetime.utcnow(), attempts=attempts)
        new = BlockedIP(attempts=attempts, blocked_until=new_time)
        self.store.write(new, timeout=self._highest_block_duration)
        return (new, seconds)

    def check_and_raise_or_block_longer(self) -> Tuple[BlockedIP, int]:
        block = self.read()
        if block:
            seconds = str(block.get_remaining_time_blocked().total_seconds()).split(
                "."
            )[0]
            # print(block, seconds, datetime.utcnow())
            strings = get_strings(self.kerno)
            raise MalbonaRezulto(
                status_int=503,  # Service Unavailable
                title=strings.registration_blocked_title,
                plain=strings.registration_is_blocked.format(
                    seconds=seconds, until=str(block.blocked_until).split(".")[0]
                ),
                headers={"Retry-After": seconds},
            )
        else:
            new, sec = self.block_longer(old=block)
            # print(new, sec, datetime.utcnow())
            return (new, sec)
