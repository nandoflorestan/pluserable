from ipaddress import ip_address
from typing import List, Optional

from kerno.typing import DictStr


def validate_public_ip(ip: str) -> str:
    """Return a validated public IP address.

    Return an empty string if the IP is invalid, private or loopback.
    """
    try:
        ipo = ip_address(ip.strip())
    except ValueError:
        return ""
    return "" if ipo.is_private or ipo.is_loopback else str(ipo)


def public_client_ip(guess: Optional[str], headers: DictStr) -> str:
    """Best effort to return the IP address of the other extremity.

    This will never return IP addresses that are:

    - loopback (e. g. "127.0.0.1") or
    - private (e. g. local network IPs) or
    - invalid

    May return an empty string if a public IP cannot be found.

    This function is agnostic of web frameworks.

    This will examine *guess* and return it if it seems to make sense.
    Otherwise it will examine HTTP headers. From one of these it will return the
    rightmost IP address that makes any sense.
    This is because all IP addresses are easy to fake, except the rightmost one.
    See https://adam-p.ca/blog/2022/03/x-forwarded-for/
    """
    vguess = validate_public_ip(guess or "")
    if vguess:
        return vguess

    series: List[str] = (
        headers.get("X-Forwarded-For", "")
        or headers.get("Hostx-Forwarded-For", "")
        or headers.get("X-Real-Ip", "")
    ).split(",")
    series.reverse()
    for ip_string in series:
        result = validate_public_ip(ip_string)
        if result:
            return result
    return ""
