"""
Application registry management utilities.
"""

import asyncio
import logging
from typing import Optional, Set

from ..schemas.application_connection_shema import ConnectedApplication


logger = logging.getLogger(__name__)


class ConnectedApplicationRegistry:
    """
    Registry manager for connected applications.
    """

    def __init__(self):
        """
        Initialize the application registry.
        """

        self._applications: Set[ConnectedApplication] = set()


    def register(
        self,
        app_id: str,
        writer: asyncio.StreamWriter
    ) -> ConnectedApplication:
        """
        Register an application connection.

        Args:
            app_id: Unique application identifier
            writer: Stream writer for the connection

        Returns:
            The registered application object
        """

        app = RegisteredApplication(id=app_id, writer=writer)
        self._applications.add(app)

        logger.info(f"[REGISTRY] Registered application: {app_id}")
        return app


    def unregister(self, app_id: str) -> bool:
        """
        Unregister an application by its ID.

        Args:
            app_id: The application ID to unregister

        Returns:
            True if application was found and removed, False otherwise
        """

        app = self.find_by_id(app_id)

        if app:
            self._applications.discard(app)
            logger.info(f"[REGISTRY] Unregistered application: {app_id}")
            return True

        return False


    def find_by_id(self, app_id: str) -> Optional[ConnectedApplication]:
        """
        Find an application by its ID.

        Args:
            app_id: The application ID to search for

        Returns:
            The RegisteredApplication if found, None otherwise
        """

        for app in self._applications:
            if app.id == app_id:
                return app

        return None


    def find_by_writer(
        self,
        writer: asyncio.StreamWriter
    ) -> Optional[ConnectedApplication]:
        """
        Find an application by its writer.

        Args:
            writer: The stream writer to search for

        Returns:
            The registered application object if found, None otherwise
        """

        for app in self._applications:
            if app.writer == writer:
                return app

        return None


    def get_all_applications(self) -> Set[ConnectedApplication]:
        """
        Get all registered applications.

        Returns:
            Set of all registered applications
        """

        return self._applications.copy()
