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
PRESET_MODE_BOOST = "Boost"

PRESET_MODES = [
    PRESET_MODE_LOW,
    PRESET_MODE_MEDIUM,
    PRESET_MODE_HIGH,
    PRESET_MODE_TURBO,
    PRESET_MODE_BOOST,
]

# Mapping preset modes to device levels (0-4)
PRESET_TO_LEVEL = {
    PRESET_MODE_LOW: 0,
    PRESET_MODE_MEDIUM: 1,
    PRESET_MODE_HIGH: 2,
    PRESET_MODE_TURBO: 3,
    PRESET_MODE_BOOST: 4,
}

# Timer duration for manual control (minutes)
DEFAULT_TIMER_DURATION = 240
BOOST_TIMER_DURATION = 10  # Boost mode uses shorter duration
