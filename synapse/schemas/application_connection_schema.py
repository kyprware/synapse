"""
Schemas for application data types.
"""

from asyncio import StreamWriter

from pydantic import BaseModel


class ApplicationConnection(BaseModel):
    """
    Represents a connected application.

    Attributes:
        id (str): The unique identifier of the connected application.
        writer (StreamWriter): The stream writer used to communicate with the application.
    """

    id: str
    writer: StreamWriter


    class Config:
        arbitrary_types_allowed = True


    def __eq__(self, other: object) -> bool:
        """
        Compares two ConnectedApplication instances based on their ID.

        Args:
            other (object): Another object to compare against.

        Returns:
            bool: True if the other object is the same ID, False otherwise.
        """

        if not isinstance(other, ApplicationConnection):
            return False

        return self.id == other.id


    def __hash__(self) -> int:
        """
        Computes a hash value based on its ID.

        Returns:
            int: Hash of the application ID.
        """

        return hash(self.id)
