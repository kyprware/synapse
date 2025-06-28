"""
Schemas for application data types.
"""

from asyncio import StreamWriter

from pydantic import BaseModel


class ApplicationSession(BaseModel):
    """
    Represents session information for an authenticated application.

    Attributes:
        sub (int): Subject application ID.
        iat (int): Issued At time.
        name (str): Application name.
        is_admin (bool): If the session is an admin session.
    """

    sub: int
    iat: int
    name: str
    is_admin: bool


class ApplicationConnection(BaseModel):
    """
    Represents a connected application.

    Attributes:
        id (int): The unique identifier of the connected application.
        writer (StreamWriter): The stream writer used to communicate with the application.
        session (ApplicationSession): application session info.
    """

    id: int
    writer: StreamWriter
    session: ApplicationSession


    class Config:
        arbitrary_types_allowed = True


    def __eq__(self, other: object) -> bool:
        """
        Compares two ApplicationConnection instances based on ID and writer.

        Args:
            other (object): Another object to compare against.

        Returns:
            bool: True if the other object are the same, False otherwise.
        """

        if not isinstance(other, ApplicationConnection):
            return False

        return self.id == other.id and self.writer == other.writer


    def __hash__(self) -> int:
        """
        Computes a hash value based on ID and writer.

        Returns:
            int: Hash combining the application ID and writer.
        """

        return hash((self.id, self.writer))
