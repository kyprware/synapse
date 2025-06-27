"""
Application connection management services.
"""

import asyncio
import logging
from typing import Optional, Callable, Set, List, Any

from ..schemas.application_connection_schema import ApplicationConnection


logger = logging.getLogger(__name__)
connections: Set[ApplicationConnection] = set()


def find_connection_by_writer(
    writer: asyncio.StreamWriter
) -> Optional[ApplicationConnection]:
    """
    Find connection by its writer.

    Args:
        writer (asyncio.StreamWriter): The stream writer to search for

    Returns:
        Optional[ApplicationConnection]: The connection if found, None otherwise
    """

    for connection in connections:
        if connection.writer == writer:
            return connection

    return None


def find_connection_by_id(id: str) -> Optional[ApplicationConnection]:
    """
    Find connection by its ID.

    Args:
        id (str): The connection ID to search for

    Returns:
        Optional[ApplicationConnection]: The connection if found, None otherwise
    """

    for connection in connections:
        if connection.id == id:
            return connection

    return None


def find_connections(
    filter_fn: Optional[Callable[[ApplicationConnection], bool]] = None,
    sort_fn: Optional[Callable[[ApplicationConnection], Any]] = None,
    skip: int = 0,
    limit: int = 0,
) -> List[ApplicationConnection]:
    """
    Find connections with optional filtering, sorting, and pagination.

    Args:
        filter_fn (Optional[Callable]): Filter function
        sort_fn (Optional[Callable]): Sort key function
        skip (int): Number of results to skip
        limit (int): Maximum number of results to return (0 = no limit)

    Returns:
        List[ApplicationConnection]: List of matching connections
    """

    result = list(connections)

    if filter_fn:
        result = [connection for connection in result if filter_fn(connection)]

    if sort_fn:
        result.sort(key=sort_fn)

    if skip > 0:
        result = result[skip:]

    if limit > 0:
        result = result[:limit]

    return result


def add_connection(
    id: str,
    writer: asyncio.StreamWriter
) -> ApplicationConnection:
    """
    Add a new connection.

    Args:
        id (str): Unique identifier for the connection
        writer (asyncio.StreamWriter): Stream writer for the connection

    Returns:
        ApplicationConnection: The created connection object
    """

    connection = ApplicationConnection(id=id, writer=writer)
    connections.add(connection)
    logger.info(f"[CONNECTIONS] Added connection: {id}")
    return connection


def remove_connection(connection: ApplicationConnection) -> bool:
    """
    Remove a connection.

    Args:
        connection (ApplicationConnection): The connection to remove

    Returns:
        bool: True if connection was removed, False otherwise
    """

    if connection in connections:
        connections.discard(connection)
        logger.info(f"[CONNECTIONS] Removed connection: {connection.id}")
        return True

    return False
