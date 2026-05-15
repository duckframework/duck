"""
Utilities for tracking and validating occupied ports within Duck.
"""

from duck.exceptions.all import PortError


class PortRegistry:
    """
    Registry for ports reserved or currently in use during Duck's lifecycle.
    """

    _occupied_ports: dict[int, str] = {}
    """
    Maps occupied ports to their registered occupier/source.
    """

    @classmethod
    def register_port(cls, port: int, occupier: str) -> None:
        """
        Register a port as occupied.

        Args:
            port: Port number to register.
            occupier: Identifier for the owner/consumer of the port.

        Raises:
            PortError: If the port is already registered.
        """
        existing_occupier = cls._occupied_ports.get(port)

        if existing_occupier:
            raise PortError(
                (
                    f'Port "{port}" is already occupied by '
                    f'"{existing_occupier}".'
                )
            )

        cls._occupied_ports[port] = occupier

    # Queries

    @classmethod
    def is_port_occupied(cls, port: int) -> bool:
        """
        Check whether a port is already registered as occupied.

        Args:
            port: Port number to check.

        Returns:
            True if the port is occupied, otherwise False.
        """
        return port in cls._occupied_ports

    @classmethod
    def get_port_occupier(cls, port: int) -> str | None:
        """
        Return the occupier registered for a given port.

        Args:
            port: Port number to resolve.

        Returns:
            Registered occupier if found, otherwise None.
        """
        return cls._occupied_ports.get(port)

    # Mutations

    @classmethod
    def unregister_port(cls, port: int) -> None:
        """
        Remove a registered occupied port.

        Args:
            port: Port number to unregister.
        """
        occupier = cls._occupied_ports.pop(port, None)
