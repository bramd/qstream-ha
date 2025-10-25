# QStream Home Assistant Integration

Home Assistant custom integration for BUVA QStream 2.0 WiFi-enabled ventilation fans.

## Features

- Fan entity with percentage and preset mode control
- Demand control switch for automatic AQI-based speed adjustment
- Air quality sensor
- Diagnostic sensors for flow rates, timer, schedule, and valve state

## Installation

### Via HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "QStream Ventilation Fan"
3. Click Install
4. Restart Home Assistant
5. Add integration via Configuration ’ Integrations ’ Add Integration

### Manual Installation

1. Copy `custom_components/qstream/` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Add integration via Configuration ’ Integrations ’ Add Integration

## Configuration

1. Go to Configuration ’ Integrations
2. Click "+ Add Integration"
3. Search for "QStream"
4. Enter your device's IP address or hostname
5. Optionally provide a friendly name

## Entities Created

- `fan.qstream_fan` - Main fan control
- `switch.qstream_fan_demand_control` - Toggle demand control
- `sensor.qstream_fan_air_quality` - Air quality index (AQI)
- Multiple diagnostic sensors for monitoring

## License

MIT
