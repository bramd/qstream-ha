# QStream Integration - Dutch Translation

**Date:** 2025-10-26
**Purpose:** Add Dutch (nl) translation support to the QStream Home Assistant integration using HA's official translation system.

## Overview

This document outlines the implementation of Dutch translations for the QStream integration, maximizing reuse of existing Home Assistant core translations for common terms while providing custom translations for QStream-specific content.

## Requirements

### Translation Scope

**What gets translated:**
1. Config flow UI text (setup wizard, input labels, error messages)
2. Entity names and descriptions (fan, sensors, switches)
3. Preset mode names (Low, Medium, High, Turbo, Boost)
4. Sensor states and binary sensor states
5. Error and abort messages

**What stays in English:**
- Entity IDs (e.g., `air_quality_index`, `demand_control`)
- Code-level constants
- Log messages
- Code comments

### Translation Strategy

**Reuse HA Core Translations:**
- Low → `[%key:common::state::low%]` (automatically translated to "Laag")
- Medium → `[%key:common::state::medium%]` (automatically translated to "Middel")
- High → `[%key:common::state::high%]` (automatically translated to "Hoog")
- Common error messages → Reference core translations where available

**Custom QStream Translations:**
- Turbo → "Turbo" (universal term, keep as-is)
- Boost → "Boost" (brand-specific term, keep as-is)
- Entity names → Translate to Dutch
- QStream-specific messages → Translate to Dutch

## Architecture

### File Structure

```
custom_components/qstream/
├── strings.json              # English translations (source of truth)
└── translations/
    └── nl.json              # Dutch translations
```

### How It Works

1. **Home Assistant Language Detection**
   - HA reads user's language preference from Settings → System → General
   - When language is set to Dutch (nl), HA loads `translations/nl.json`
   - Falls back to `strings.json` (English) for missing translations

2. **Translation References**
   - Format: `[%key:common::state::low%]`
   - Points to existing HA core translations
   - Avoids duplication and ensures consistency

3. **No Code Changes Required**
   - Translation system is declarative (JSON only)
   - Existing Python code already compatible
   - Preset mode constants are translation keys

## Implementation

### strings.json (English with Core References)

```json
{
  "config": {
    "step": {
      "user": {
        "title": "Set up QStream",
        "description": "Enter the IP address or hostname of your QStream device",
        "data": {
          "host": "Host"
        }
      }
    },
    "error": {
      "cannot_connect": "[%key:common::config_flow::error::cannot_connect%]",
      "timeout": "Connection timed out",
      "unknown": "[%key:common::config_flow::error::unknown%]"
    },
    "abort": {
      "already_configured": "[%key:common::config_flow::abort::already_configured_device%]"
    }
  },
  "entity": {
    "fan": {
      "qstream": {
        "state_attributes": {
          "preset_mode": {
            "state": {
              "low": "[%key:common::state::low%]",
              "medium": "[%key:common::state::medium%]",
              "high": "[%key:common::state::high%]",
              "turbo": "Turbo",
              "boost": "Boost"
            }
          }
        }
      }
    },
    "sensor": {
      "air_quality_index": {
        "name": "Air Quality Index"
      },
      "analog_flow": {
        "name": "Analog Flow"
      },
      "set_flow": {
        "name": "Set Flow"
      },
      "actual_flow": {
        "name": "Actual Flow"
      },
      "timer_remaining": {
        "name": "Timer Remaining"
      },
      "schedule_remaining": {
        "name": "Schedule Remaining"
      }
    },
    "switch": {
      "demand_control": {
        "name": "Demand Control"
      }
    },
    "binary_sensor": {
      "valve": {
        "name": "Valve"
      },
      "timer_active": {
        "name": "Timer Active"
      },
      "schedule_enabled": {
        "name": "Schedule Enabled"
      }
    }
  }
}
```

### translations/nl.json (Dutch Translations)

```json
{
  "config": {
    "step": {
      "user": {
        "title": "QStream instellen",
        "description": "Voer het IP-adres of de hostnaam van je QStream apparaat in",
        "data": {
          "host": "Host"
        }
      }
    },
    "error": {
      "timeout": "Verbindingstime-out"
    }
  },
  "entity": {
    "sensor": {
      "air_quality_index": {
        "name": "Luchtkwaliteitsindex"
      },
      "analog_flow": {
        "name": "Analoge flow"
      },
      "set_flow": {
        "name": "Ingestelde flow"
      },
      "actual_flow": {
        "name": "Werkelijke flow"
      },
      "timer_remaining": {
        "name": "Timer resterend"
      },
      "schedule_remaining": {
        "name": "Schema resterend"
      }
    },
    "switch": {
      "demand_control": {
        "name": "Vraaggestuurde regeling"
      }
    },
    "binary_sensor": {
      "valve": {
        "name": "Klep"
      },
      "timer_active": {
        "name": "Timer actief"
      },
      "schedule_enabled": {
        "name": "Schema ingeschakeld"
      }
    }
  }
}
```

**Note:** Core translation references (like `[%key:common::state::low%]`) don't need to be repeated in nl.json - HA automatically resolves them to Dutch.

## Translation Reference Guide

### Config Flow Translations

| English | Dutch | Notes |
|---------|-------|-------|
| Set up QStream | QStream instellen | |
| Enter the IP address or hostname... | Voer het IP-adres of de hostnaam van je QStream apparaat in | Added "de" before hostnaam for grammatical correctness |
| Host | Host | Technical term, keep as-is |
| Connection timed out | Verbindingstime-out | Compound word more natural than "Time-out van de verbinding" |
| Cannot connect | Uses core reference | Automatically translated by HA |
| Unknown error | Uses core reference | Automatically translated by HA |
| Already configured | Uses core reference | Automatically translated by HA |

### Preset Mode Translations

| English | Dutch | Implementation |
|---------|-------|----------------|
| Low | Laag | `[%key:common::state::low%]` |
| Medium | Middel | `[%key:common::state::medium%]` |
| High | Hoog | `[%key:common::state::high%]` |
| Turbo | Turbo | Keep as-is (universal term) |
| Boost | Boost | Keep as-is (brand term) |

### Entity Name Translations

| Entity Type | English | Dutch |
|-------------|---------|-------|
| Sensor | Air Quality Index | Luchtkwaliteitsindex |
| Sensor | Analog Flow | Analoge flow |
| Sensor | Set Flow | Ingestelde flow |
| Sensor | Actual Flow | Werkelijke flow |
| Sensor | Timer Remaining | Timer resterend |
| Sensor | Schedule Remaining | Schema resterend |
| Switch | Demand Control | Vraaggestuurde regeling |
| Binary Sensor | Valve | Klep |
| Binary Sensor | Timer Active | Timer actief |
| Binary Sensor | Schedule Enabled | Schema ingeschakeld |

## Code Impact

### No Python Code Changes Required

The existing Python code is already compatible with the translation system:

**const.py** - Preset mode constants are translation keys:
```python
PRESET_MODE_LOW = "Low"      # → Looks up "low" in translations
PRESET_MODE_MEDIUM = "Medium" # → Looks up "medium" in translations
PRESET_MODE_HIGH = "High"     # → Looks up "high" in translations
PRESET_MODE_TURBO = "Turbo"   # → Looks up "turbo" in translations
PRESET_MODE_BOOST = "Boost"   # → Looks up "boost" in translations
```

**Entity Platform Files** - Entity names automatically translated:
- Fan platform: `QStreamFan` entity
- Sensor platform: All sensor entities
- Switch platform: Demand control switch
- Binary sensor platform: All binary sensor entities

No modifications needed - HA translation system handles everything!

## Testing

### Manual Testing Steps

1. **Set Home Assistant to Dutch:**
   - Settings → System → General
   - Language: Nederlands
   - Click Save

2. **Reload Integration:**
   - Settings → Devices & Services → QStream
   - Click three dots → Reload

3. **Verify Translations:**
   - Config flow: Try adding integration again, check Dutch text
   - Entity names: Check all entities show Dutch names
   - Preset modes: Set fan preset, verify "Laag", "Middel", "Hoog" appear
   - Error messages: Trigger connection error, verify Dutch message

4. **Switch Back to English:**
   - Change language back to English
   - Reload integration
   - Verify everything appears in English

### Automated Testing

**Note:** Translation testing is typically manual in HA custom integrations. The translation files themselves are validated by:
- Home Assistant's built-in JSON validation
- Hassfest workflow (validates strings.json structure)
- HACS action (validates translation file structure)

## File Checklist

Files to create/modify:

- [x] `custom_components/qstream/strings.json` - English translations with core references
- [x] `custom_components/qstream/translations/nl.json` - Dutch translations

No other files need modification!

## Deployment

### Timeline

**Do NOT deploy immediately:**
- Wait for brands PR to be merged
- Wait for HACS submission to be approved
- Bundle with next release (after v0.1.0)

### Release Process

1. Create translation files (this implementation)
2. Test locally with Dutch language setting
3. Commit to repository
4. Include in release notes: "Added Dutch (Nederlands) translation support"

## Benefits

### For Users
- Native Dutch interface
- Consistent with Home Assistant's language
- Professional, localized experience
- No configuration needed (automatic based on HA language)

### For Maintainability
- Reuses HA core translations (less maintenance)
- Standard HA translation system (well documented)
- Easy to add more languages later (copy nl.json structure)
- No code changes required (JSON only)

## Future Enhancements

### Additional Languages

To add another language (e.g., German):
1. Copy `translations/nl.json` to `translations/de.json`
2. Translate Dutch strings to German
3. Core references automatically work
4. No code changes needed

### Translation Updates

When adding new features:
1. Add English keys to `strings.json`
2. Add Dutch translations to `translations/nl.json`
3. Core references continue to work automatically

## References

- [Home Assistant Internationalization Docs](https://developers.home-assistant.io/docs/internationalization/)
- [Translation Reference Syntax](https://developers.home-assistant.io/docs/internationalization/core)
- [Common Strings (HA Core)](https://github.com/home-assistant/core/blob/dev/homeassistant/strings.json)
