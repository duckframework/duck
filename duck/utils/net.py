"""
Network helper utilily tools.
"""
import re
import socket
import ipaddress

from typing import Tuple


# Pre-compile regex and constants for speed
HOSTNAME_LABEL_RE = re.compile(r"^(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
MAX_HOSTNAME_LENGTH = 253


def is_ipv6(ip_address: str) -> bool:
    """
    Check if the provided IP address is a valid IPv6 address.
    """
    try:
        socket.inet_pton(socket.AF_INET6, ip_address)
        return True
    except socket.error:
        return False


def is_ipv4(ip_address: str) -> bool:
    """
    Check if the provided IP address is a valid IPv4 address.
    """
    try:
        socket.inet_pton(socket.AF_INET, ip_address)
        return True
    except socket.error:
        return False


def is_domain(name) -> bool:
    """
    Check if the provided name is a valid domain name.
    """
    return all(
        [len(part) <= 63 and part.isalnum() for part in name.split(".")])


def is_valid_host(host) -> Tuple[bool, str]:
    """
    Super-fast validation of hostname or IP address, optionally with a port.
    Returns a tuple (is_valid, message).
    """
    if not host:
        return False, "Hostname is empty"

    # Fast split for port (IPv4/hostname:port case)
    if ':' in host and host.count(':') == 1:
        h, port = host.split(':', 1)
        if not port.isdigit() or not (0 < int(port) < 65536):
            return False, f"Invalid port number '{port}'. Port must be an integer between 1 and 65535."
        host = h  # continue validating host only

    elif ':' in host:
        # IPv6 with port, e.g., [::1]:8000
        if host.startswith('[') and ']' in host:
            i = host.find(']')
            addr = host[1:i]
            port = host[i+2:] if host[i+1:i+2] == ':' else ''
            try:
                ip = ipaddress.ip_address(addr)
            except Exception:
                return False, "Malformed IPv6 address."
            if not port.isdigit() or not (0 < int(port) < 65536):
                return False, f"Invalid port '{port}' on IPv6 address."
            return True, "Valid IPv6 address with port."
        # else: fall through to next checks

    # Try IP address (IPv4 or IPv6)
    try:
        ip = ipaddress.ip_address(host.strip("[]"))
        return True, f"Valid IP address (IPv{ip.version})."
    except Exception:
        pass

    # Hostname validation
    if len(host) > MAX_HOSTNAME_LENGTH:
        return False, f"Hostname exceeds the maximum length of {MAX_HOSTNAME_LENGTH} characters."

    labels = host.split(".")
    if any(not label for label in labels):
        return False, "Hostname contains empty labels (e.g., consecutive dots)."

    for label in labels:
        if not HOSTNAME_LABEL_RE.match(label):
            return False, f"Invalid label '{label}' in hostname."
            
    return True, "Valid hostname."
