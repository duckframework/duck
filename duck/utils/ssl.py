"""
SSL related tools and utilities.
"""
import os
import struct
import subprocess

from duck.exceptions.all import SettingsError
from duck.logging import logger
from duck.settings import SETTINGS


def is_ssl_data(data: bytes) -> bool:
    """
    Checks if the given data is an SSL/TLS record.

    Args:
        data (bytes): Raw bytes received from a socket.
    
    Returns:
        bool: True if data appears to be SSL/TLS, False otherwise.
    """
    if len(data) < 3:
        return False  # Not enough data to determine SSL

    first_byte, version_major, version_minor = struct.unpack("!BBB", data[:3])

    # SSL/TLS content types (Handshake, ChangeCipherSpec, Alert, Application Data)
    if first_byte in {0x14, 0x15, 0x16, 0x17}:
        # Check for valid SSL/TLS versions
        if (version_major == 0x03 and version_minor in {0x00, 0x01, 0x02, 0x03, 0x04}):
            return True

    return False


def generate_server_cert():
    """
    Generates a key pair (Key), csr (Certificate Signing Request ) and a self-signed certificate (CRT) for server-side use.

    This will generate 3 files using openssl:
        server.csr
        server.key
        server.crt

    This uses variables set in settings.py
    """
    base_dir = SETTINGS.get("BASE_DIR")
    ssl_dir = os.path.join(str(base_dir), "etc", "ssl") if base_dir else os.getcwd()

    csr_path = SETTINGS.get("SSL_CSR_LOCATION") or os.path.join(ssl_dir, "server.csr")
    certfile_path = SETTINGS.get("SSL_CERTFILE_LOCATION") or os.path.join(ssl_dir, "server.crt")
    private_key_path = SETTINGS.get("SSL_PRIVATE_KEY_LOCATION") or os.path.join(ssl_dir, "server.key")

    os.makedirs(os.path.dirname(str(certfile_path)), exist_ok=True)
    
    logger.log(
        "Generating SSL certificate to use for HTTPS",
        level=logger.DEBUG,
    )
    
    logger.log(
        "This will generate a self-signed certificate for development.",
        level=logger.DEBUG,
    )
    
    logger.log(
        "For production, please submit the CSR (Certificate Signing Request) to trusted CA (Certificate Authority) for "
        "signing to ensure browser compatibility and trust.\n",
        level=logger.WARNING,
    )

    # check if certfile and private key both exist, if not then continue
    if os.path.isfile(certfile_path) and os.path.isfile(private_key_path):
        # both are present flag a warning
        overwrite_existing = input(
            "SSL certfile and key pair already exist. Overwrite existing (y/N): "
        )
        print()
        if not overwrite_existing.lower().startswith("y"):
            logger.log("Cancelled SSL Certificate generation",
                       level=logger.DEBUG)
            return

    domain = SETTINGS.get("SERVER_DOMAIN") or "localhost"
    country = SETTINGS.get("SERVER_COUNTRY") or "US"
    state = SETTINGS.get("SERVER_STATE") or "State"
    locality = SETTINGS.get("SERVER_LOCALITY") or "Locality"
    organization = SETTINGS.get("SERVER_ORGANIZATION") or "Duck"
    organization_unit = SETTINGS.get("SERVER_ORGANIZATION_UNIT") or "Development"

    if len(country) != 2:
        country = "US"

    # checking for openssl availability
    try:
        # Run the openssl command to check if it's available
        result = subprocess.run(
            ["openssl", "version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # If openssl is available, result.returncode should be 0
        if result.returncode == 0:
            logger.log(
                f"OpenSSL version: {result.stdout.decode('utf-8').strip()}",
                level=logger.INFO,
            )
        else:
            logger.log(
                "Error: OpenSSL command failed unexpectedly",
                level=logger.ERROR,
            )
            logger.log("Cancelled SSL Certificate generation",
                       level=logger.ERROR)
            return

    except FileNotFoundError:
        # If OpenSSL is not found on the system
        logger.log(
            "Error: OpenSSL is not installed on your system",
            level=logger.ERROR,
        )
        logger.log("Cancelled SSL Certificate generation", level=logger.ERROR)
        return
    except subprocess.CalledProcessError as e:
        # Catch any errors during the command execution
        logger.log(
            f"Error: OpenSSL command failed with message: {e.stderr.decode('utf-8')}",
            level=logger.ERROR,
        )
        logger.log("Cancelled SSL Certificate generation", level=logger.ERROR)
        return

    # create commands
    private_key_cmd = ["openssl", "genrsa", "-out", str(private_key_path), "2048"]

    csr_cmd = [
        "openssl",
        "req",
        "-new",
        "-key",
        str(private_key_path),
        "-out",
        str(csr_path),
        "-subj",
        f"/C={country}/ST={state}/L={locality}/O={organization}/OU={organization_unit}/CN={domain}",
    ]

    certfile_signing_cmd = [
        "openssl",
        "x509",
        "-req",
        "-in",
        str(csr_path),
        "-signkey",
        str(private_key_path),
        "-out",
        str(certfile_path),
        "-days",
        "365",
    ]

    # generate private key
    process = subprocess.run(private_key_cmd, check=True)

    if process.returncode == 0:
        logger.log(
            f"Created private key in {private_key_path}",
            custom_color=logger.Fore.GREEN,
        )
    else:
        logger.log("Failed to create a private key", level=logger.ERROR)
        logger.log_raw(
            f"{process.stderr.decode('utf-8')}",
            level=logger.ERROR,
            custom_color=logger.Style.RESET_ALL,
        )
        logger.log("Cancelled SSL Certificate generation", level=logger.ERROR)
        return

    # generate csr (certificate signing request)
    process = subprocess.run(csr_cmd, check=True)
    if process.returncode == 0:
        logger.log(
            f"Created CSR (certificate signing request) in {csr_path}",
            custom_color=logger.Fore.GREEN,
        )
    else:
        logger.log("Failed to create CSR", level=logger.ERROR)
        logger.log_raw(
            f"{process.stderr.decode('utf-8')}",
            level=logger.ERROR,
            custom_color=logger.Style.RESET_ALL,
        )
        logger.log("Cancelled SSL Certificate generation", level=logger.ERROR)
        return

    # self-sign and create certificate
    process = subprocess.run(certfile_signing_cmd, check=True)
    if process.returncode == 0:
        logger.log(
            f"Created self-signed certificate in {certfile_path}",
            custom_color=logger.Fore.GREEN,
        )
        logger.log(
            "SSL certificate generated successfully.",
            custom_color=logger.Fore.GREEN,
        )
    else:
        logger.log("Failed to create ssl certificate", level=logger.ERROR)
        logger.log_raw(
            f"{process.stderr.decode('utf-8')}",
            level=logger.ERROR,
            custom_color=logger.Style.RESET_ALL,
        )
        logger.log("Cancelled SSL Certificate generation", level=logger.ERROR)
        return
