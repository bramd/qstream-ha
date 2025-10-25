"""Constants for the QStream integration."""

DOMAIN = "qstream"

# Configuration
CONF_HOST = "host"

# Update interval
UPDATE_INTERVAL_SECONDS = 30

# Preset modes for fan entity
PRESET_MODE_LOW = "Low"
PRESET_MODE_MEDIUM = "Medium"
PRESET_MODE_HIGH = "High"
PRESET_MODE_TURBO = "Turbo"

PRESET_MODES = [
    PRESET_MODE_LOW,
    PRESET_MODE_MEDIUM,
    PRESET_MODE_HIGH,
    PRESET_MODE_TURBO,
]

# Mapping preset modes to device levels (1-4)
PRESET_TO_LEVEL = {
    PRESET_MODE_LOW: 1,
    PRESET_MODE_MEDIUM: 2,
    PRESET_MODE_HIGH: 3,
    PRESET_MODE_TURBO: 4,
}

# Timer duration for manual control (minutes)
DEFAULT_TIMER_DURATION = 240
