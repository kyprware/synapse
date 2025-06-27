"""
Schemas for application data types.
"""

from asyncio import StreamWriter

from pydantic import BaseModel


class ApplicationConnection(BaseModel):
    """
    Represents a connected application.

    Attributes:
        id (int): The unique identifier of the connected application.
        writer (StreamWriter): The stream writer used to communicate with the application.
    """

    id: int
    writer: StreamWriter
    authentication_token: str


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
