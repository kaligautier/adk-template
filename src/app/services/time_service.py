"""Time service - Business logic for time operations."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

logger = logging.getLogger(__name__)


class TimeClient:
    """Time client for time-related operations."""

    def get_current_time_info(self, timezone_name: str = None) -> dict:
        """
        Get current time information.

        Args:
            timezone_name: Optional timezone name (e.g., "UTC", "America/New_York")

        Returns:
            dict: Current time information
        """
        logger.debug(f"Getting current time for timezone: {timezone_name or 'UTC'}")

        timezone_name = "UTC" if timezone_name is None else timezone_name
        try:
            timezone = ZoneInfo(timezone_name)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(f"Unknown timezone: {timezone_name}") from exc

        now = datetime.now(timezone)

        return {
            "timezone": timezone_name,
            "timestamp": now.isoformat(),
            "unix_timestamp": int(now.timestamp()),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        }


# Singleton instance for convenience
time_client = TimeClient()
