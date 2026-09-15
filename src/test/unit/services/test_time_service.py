"""Unit tests for time service."""

from datetime import datetime
from datetime import timezone as dt_timezone

from app.services.time_service import TimeClient


class TestTimeClientGetCurrentTimeInfo:
    """Tests for TimeClient.get_current_time_info method."""

    def should_return_utc_time_when_no_timezone_specified(self):
        """Test default timezone is UTC."""
        client = TimeClient()
        result = client.get_current_time_info()

        assert result["timezone"] == "UTC"
        assert "timestamp" in result
        assert "unix_timestamp" in result
        assert "formatted" in result

    def should_return_iso_format_timestamp(self):
        """Test timestamp is in ISO format."""
        client = TimeClient()
        result = client.get_current_time_info()

        # Verify it's valid ISO format by parsing
        datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))

    def should_return_unix_timestamp_as_integer(self):
        """Test unix timestamp is an integer."""
        client = TimeClient()
        result = client.get_current_time_info()

        assert isinstance(result["unix_timestamp"], int)
        assert result["unix_timestamp"] > 0

    def should_return_formatted_time_string(self):
        """Test formatted time string is present."""
        client = TimeClient()
        result = client.get_current_time_info()

        assert isinstance(result["formatted"], str)
        assert len(result["formatted"]) > 0

    def should_use_provided_timezone_name(self):
        """Test custom timezone name is stored in result."""
        client = TimeClient()
        result = client.get_current_time_info("America/New_York")

        assert result["timezone"] == "America/New_York"

    def should_return_current_time_close_to_now(self):
        """Test returned time is close to actual current time."""
        client = TimeClient()
        before = datetime.now(dt_timezone.utc)
        result = client.get_current_time_info()
        after = datetime.now(dt_timezone.utc)

        result_time = datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))

        # Time should be between before and after (with small buffer)
        assert before <= result_time <= after

    def should_return_all_required_fields(self):
        """Test result contains all required fields."""
        client = TimeClient()
        result = client.get_current_time_info()

        required_fields = ["timezone", "timestamp", "unix_timestamp", "formatted"]
        for field in required_fields:
            assert field in result
