import ipaddress
import re
import socket
from urllib.parse import urlparse

from app.errors import HttpError

# Same ranges the previous server refused: loopback, link-local, and private space.
_BLOCKED_V4 = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("255.255.255.255/32"),
]
_BLOCKED_V6 = [
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]
_LOCAL_NAMES = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
}
_MAPPED = re.compile(r"^::ffff:(\d+\.\d+\.\d+\.\d+)$", re.IGNORECASE)


def assert_public_url(value: str):
    """Accept only an http(s) URL whose host resolves to a public address."""
    try:
        parsed = urlparse(str(value).strip())
    except ValueError as error:
        raise HttpError(400, "Enter a valid http or https URL") from error

    if not parsed.hostname:
        raise HttpError(400, "Enter a valid http or https URL")
    if parsed.scheme not in ("http", "https"):
        raise HttpError(400, "Only http and https URLs can be saved")
    if parsed.username or parsed.password:
        raise HttpError(400, "URLs with a username or password are not allowed")

    host = parsed.hostname.rstrip(".").lower()
    if not host or host in _LOCAL_NAMES or host.endswith(".localhost") or host.endswith(".local"):
        raise HttpError(400, "That host is not allowed")

    if _is_ip(host):
        _assert_address_allowed(host)
        return parsed

    try:
        records = socket.getaddrinfo(host, None)
    except socket.gaierror as error:
        raise HttpError(502, "Could not resolve that host") from error

    addresses = [record[4][0] for record in records]
    if not addresses:
        raise HttpError(502, "Could not resolve that host")
    # Reject the name if any answer is private. A public name can still point inward.
    for address in addresses:
        _assert_address_allowed(address)
    return parsed


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


def _assert_address_allowed(address: str) -> None:
    mapped = _MAPPED.match(address)
    raw = mapped.group(1) if mapped else address
    try:
        ip = ipaddress.ip_address(raw)
    except ValueError as error:
        raise HttpError(400, "That host is not allowed") from error

    networks = _BLOCKED_V4 if ip.version == 4 else _BLOCKED_V6
    if any(ip in network for network in networks):
        raise HttpError(400, "That host is not allowed")
