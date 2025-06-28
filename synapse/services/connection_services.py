"""
Application connection management services.
"""

from asyncio import StreamWriter
from typing import Optional, Callable, Set, List, Any

from ..utils.jwt_utils import decode_token
from ..schemas.application_connection_schema import ApplicationConnection


connections: Set[ApplicationConnection] = set()


def find_connection_by_writer(
    writer: StreamWriter
) -> Optional[ApplicationConnection]:
    """
    Find connection by its writer.

    Args:
        writer (StreamWriter): The stream writer to search for

    Returns:
        Optional[ApplicationConnection]: The connection if found else None
    """

    for connection in connections:
        if connection.writer == writer:
            return connection

    return None


def find_connection_by_id(id: int) -> Optional[ApplicationConnection]:
    """
    Find connection by its ID.

    Args:
        id (int): The connection ID to search for

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
    id: int,
    writer: StreamWriter,
    authentication_token: str
) -> ApplicationConnection:
    """
    Add a new connection.

    Args:
        id (int): Unique identifier for the connection
        writer (StreamWriter): Stream writer for the connection
        authentication_token (str): JWT token representing the user session.

    Returns:
        ApplicationConnection: The created connection object
    """

    connection = ApplicationConnection(
        id=id,
        writer=writer,
        session=decode_token(authentication_token)
    )

    connections.add(connection)
    return connection


def remove_connection_by_id(id: int) -> bool:
    """
    Remove a connection by id.

    Args:
        id (int): The connection ID of connection to remove

    Returns:
        bool: True if connection was removed, False otherwise
    """

    connection = find_connection_by_id(id)

    if connection:
        connections.discard(connection)
        return True

    return False


def remove_connection_by_writer(writer: StreamWriter) -> bool:
    """
    Remove a connection by stream writer.

    Args:
        writer (StreamWriter): The stream writer of connection to remove

    Returns:
        bool: True if connection was removed, False otherwise
    """

    connection = find_connection_by_writer(writer)

    if connection:
        connections.discard(connection)
        return True

    return False
