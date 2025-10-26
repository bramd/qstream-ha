# QStream Home Assistant Integration

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Home Assistant custom integration for BUVA QStream 2.0 WiFi-enabled ventilation fans.

## Features

### Entities

**Fan Entity** (`fan.qstream_fan`)
- Percentage-based speed control (0-100%)
- Four preset modes (Low, Medium, High, Turbo) mapped to device levels
- Turn on/off control

**Switch Entity** (`switch.qstream_fan_demand_control`)
- Toggle automatic speed adjustment based on air quality sensor
- Preserves current fan speed when toggled

**Sensors**
- `sensor.qstream_fan_air_quality` - Air Quality Index (AQI) from device sensor
- `sensor.qstream_fan_analog_flow` - Flow demanded by analog sensor (%)
- `sensor.qstream_fan_set_flow` - Target flow percentage (%)
- `sensor.qstream_fan_actual_flow` - Current actual flow (%)
- `sensor.qstream_fan_timer_remaining` - Timer remaining (minutes)
- `sensor.qstream_fan_schedule_mode` - Current schedule mode (DAY/NIGHT)
- `sensor.qstream_fan_schedule_remaining` - Schedule remaining (minutes)

**Binary Sensors**
- `binary_sensor.qstream_fan_valve` - Valve position (open/closed)
- `binary_sensor.qstream_fan_timer_active` - Timer active state
- `binary_sensor.qstream_fan_schedule_enabled` - Schedule enabled state

## Installation

### Prerequisites

- Home Assistant 2025.10 or later
- QStream 2.0 device on local network
- Device IP address or hostname

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots menu (top right)
4. Select "Custom repositories"
5. Add repository URL: `https://github.com/bramd/qstream-ha`
6. Category: Integration
7. Click "Add"
8. Search for "QStream Ventilation Fan"
9. Click "Download"
10. Restart Home Assistant
11. Add integration via Configuration → Integrations → Add Integration

### Manual Installation

1. Copy the `custom_components/qstream/` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Add integration via Configuration → Integrations → Add Integration

## Configuration

1. Navigate to Configuration → Integrations
2. Click "+ Add Integration"
3. Search for "QStream"
4. Enter your device's IP address or hostname (e.g., `192.168.1.100`)
5. Optionally provide a friendly name (defaults to "QStream Fan")
6. Click Submit

The integration will validate the connection and create all entities automatically.

## Usage Examples

### Automations

**Turn on fan at 75% when humidity exceeds 70%:**

```yaml
automation:
  - alias: "Bathroom Fan Auto On"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bathroom_humidity
        above: 70
    action:
      - service: fan.set_percentage
        target:
          entity_id: fan.qstream_fan
        data:
          percentage: 75
```

**Enable demand control during the day:**

```yaml
automation:
  - alias: "Enable Demand Control Morning"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.qstream_fan_demand_control
```

**Notify when air quality is poor:**

```yaml
automation:
  - alias: "Poor Air Quality Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.qstream_fan_air_quality
        above: 150
    action:
      - service: notify.mobile_app
        data:
          message: "Air quality is poor (AQI: {{ states('sensor.qstream_fan_air_quality') }})"
```

## Troubleshooting

### Integration fails to connect

- Verify device IP address is correct
- Ensure device is powered on and connected to network
- Check firewall rules allow communication on port 80
- Try pinging the device from Home Assistant host

### Entities show as unavailable

- Check Home Assistant logs for connection errors
- Verify device hasn't changed IP address (consider DHCP reservation)
- Restart integration from Configuration → Integrations

### Preset modes don't match expected speeds

Preset modes map to device levels 1-4, which are user-configurable on the device itself. Check device settings and adjust levels as needed.

## Development

### Claude Code Skills

This repository includes project-specific skills for Claude Code to help with development workflows.

**Setup:** See [.claude/README.md](.claude/README.md) for installation instructions.

**Available skills:**
- `/qstream:cutting-a-release` - Automate releases with safety checks and version management

See [docs/skills/README.md](docs/skills/README.md) for detailed documentation.

### Running Tests

```bash
pytest tests/ -v
```

### Linting

```bash
ruff check custom_components/qstream/
```

### Type Checking

```bash
mypy custom_components/qstream/
```

## Support

- Report bugs: [GitHub Issues](https://github.com/bramd/qstream-ha/issues)
- Feature requests: [GitHub Discussions](https://github.com/bramd/qstream-ha/discussions)

## License

MIT License - see [LICENSE](LICENSE) file for details

## Credits

- Built using the [qstream](https://pypi.org/project/qstream/) Python library
- Community reverse-engineered QStream 2.0 API (not officially supported by BUVA)

## Disclaimer

This integration is not affiliated with or endorsed by BUVA. Use at your own risk.
