"""Time service - Business logic for time operations."""

import logging
from datetime import datetime
from datetime import timezone as dt_timezone

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

        # For simplicity, we'll just return UTC time
        # In production, use pytz or zoneinfo for proper timezone handling
        now = datetime.now(dt_timezone.utc)

        return {
            "timezone": timezone_name or "UTC",
            "timestamp": now.isoformat(),
            "unix_timestamp": int(now.timestamp()),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        }


# Singleton instance for convenience
time_client = TimeClient()
