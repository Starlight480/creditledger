"""Re-export config from app.config for backward compatibility."""
from app.config import settings, get_settings, Settings

__all__ = ["settings", "get_settings", "Settings"]
