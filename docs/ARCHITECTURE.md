# Synesthesia Simulator Architecture

## Overview

The Synesthesia Simulator is a web application that converts website content (text, colors, and numbers) into multi-sensory experiences. The architecture follows a modular design with clear separation between frontend visualization, audio generation, and backend services.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Frontend (JavaScript)                   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │  │
│  │  │ Content     │  │   Audio     │  │    Visual       │   │  │
│  │  │ Detection   │  │   Mapper    │  │    Mapper       │   │  │
│  │  └──────┬──────┘  └──────┬──────┘  └───────┬─────────┘   │  │
│  │         │                │                  │             │  │
│  │         └────────────────┼──────────────────┘             │  │
│  │                          │                                 │  │
│  │              ┌───────────▼────────────┐                   │  │
│  │              │   SynesthesiaApp       │                   │  │
│  │              │   (Main Controller)    │                   │  │
│  │              └───────────┬────────────┘                   │  │
│  └──────────────────────────┼────────────────────────────────┘  │
│                             │ HTTP/REST                          │
└─────────────────────────────┼────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (Python/Flask)                        │
│  ┌─────────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │  ContentMapper  │  │UserPreferences│  │  Flask Routes   │    │
│  │  - Text→Freq    │  │  - Storage    │  │  - API Endpoints│    │
│  │  - Color→Sound  │  │  - Presets    │  │  - Static Files │    │
│  │  - Number→Pat   │  │               │  │                 │    │
│  └─────────────────┘  └──────────────┘  └─────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
sense-switchboard/
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment configuration template
├── .gitignore                # Git ignore patterns
│
├── .github/
│   └── workflows/
│       └── ci.yml            # CI/CD pipeline configuration
│
├── src/
│   ├── __init__.py
│   ├── frontend/
│   │   ├── index.html        # Main HTML page
│   │   ├── style.css         # Styling and animations
│   │   └── main.js           # Frontend JavaScript modules
│   │
│   └── backend/
│       ├── __init__.py
│       └── server.py         # Flask server and API
│
├── tests/
│   ├── __init__.py
│   ├── test_content_mapper.py
│   ├── test_user_preferences.py
│   └── test_api.py
│
└── docs/
    ├── ARCHITECTURE.md       # This file
    ├── USAGE.md              # User guide
    └── SUGGESTIONS.md        # Future improvements
```

## Component Details

### Frontend Components

#### 1. Content Detection (`detectContentType`)
- **Purpose**: Identifies the type of user input
- **Input Types**:
  - **Text**: Any alphanumeric string
  - **Color**: Hex color codes (#RGB or #RRGGBB)
  - **Number**: Integers or floating-point numbers
- **Output**: Object with `type` and `value` properties

#### 2. AudioMapper Class
- **Purpose**: Converts content to audio using Web Audio API
- **Key Features**:
  - Real-time audio synthesis
  - Multiple waveform types (sine, triangle, sawtooth)
  - ADSR envelope for natural sound
  - Configurable volume and duration

**Mapping Algorithms**:
| Content Type | Mapping Strategy |
|-------------|-----------------|
| Text | Each character → frequency using pentatonic scale |
| Color | Hue → frequency (200-800 Hz), Saturation → waveform type |
| Number | Logarithmic frequency scale, divisibility → pattern type |

#### 3. VisualMapper Class
- **Purpose**: Creates canvas-based visualizations
- **Key Features**:
  - Particle system for text animation
  - Color-based ambient effects
  - Geometric patterns for numbers
  - Configurable intensity and speed

### Backend Components

#### 1. ContentMapper Class
- **Purpose**: Server-side content analysis and mapping
- **Features**:
  - Multiple musical scale support (pentatonic, major, minor)
  - Color conversion (hex → RGB → HSL)
  - Frequency calculation with note naming
  - Pattern generation for numbers

#### 2. UserPreferences Class
- **Purpose**: Persistent storage of user settings
- **Storage**: JSON file-based (easily replaceable with database)
- **Features**:
  - User identification via hashed IDs
  - Preset management (up to 10 per user)
  - Automatic preference merging

#### 3. Flask Application
- **Purpose**: REST API and static file serving
- **Endpoints**:
  
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve main HTML page |
| `/api/health` | GET | Health check |
| `/api/detect` | POST | Detect content type |
| `/api/map/text` | POST | Map text to frequencies |
| `/api/map/color` | POST | Map color to sound params |
| `/api/map/number` | POST | Map number to patterns |
| `/api/map/auto` | POST | Auto-detect and map |
| `/api/preferences` | GET/POST | User preferences |
| `/api/preferences/preset` | POST | Add preset |

## Data Flow

### User Interaction Flow

```
1. User Input
      │
      ▼
2. Content Type Detection
      │
      ├─── Text ────────► Play character sequence
      │                   └─► Animate floating letters
      │
      ├─── Color ───────► Calculate hue frequency
      │                   └─► Generate particle cloud
      │
      └─── Number ──────► Calculate pattern frequency
                          └─► Draw geometric pattern
```

### API Request Flow

```
Client Request
      │
      ▼
Flask Router
      │
      ├─► Static Files ──► Serve from frontend/
      │
      └─► API Endpoints ──► ContentMapper/UserPreferences
                                    │
                                    ▼
                            JSON Response
```

## Audio Generation

### Frequency Calculation

**Text-to-Frequency**:
```
frequency = BASE_FREQ × 2^(semitones/12)
```
Where semitones are determined by the character's position in the selected musical scale.

**Color-to-Frequency**:
```
frequency = 200 + (hue / 360) × 600
```
Range: 200-800 Hz based on color hue.

**Number-to-Frequency**:
```
frequency = 100 × 10^((|number| mod 100) / 100)
```
Logarithmic scaling from 100 to 1000 Hz.

### Waveform Selection

| Saturation Level | Waveform |
|-----------------|----------|
| > 70% | Sawtooth (bright, rich) |
| 40-70% | Triangle (mellow) |
| < 40% | Sine (pure, soft) |

## Visual Effects

### Particle System
- Each particle has position, velocity, color, and size
- Physics simulation with boundary collision
- Fade-out animation for finite duration

### Animation Types
- **Text**: Bouncing letter particles
- **Color**: Pulsing colored circles
- **Number**: Expanding geometric patterns

## Security Considerations

1. **Input Sanitization**: All user input is validated before processing
2. **User ID Hashing**: User identifiers are SHA-256 hashed before storage
3. **CORS**: Enabled for cross-origin requests (configurable)
4. **No Secrets in Code**: Environment variables for sensitive configuration

## Performance Considerations

1. **Audio Context**: Created on-demand after user interaction (browser requirement)
2. **Canvas Optimization**: RequestAnimationFrame for smooth 60fps rendering
3. **Modular Loading**: Components loaded only when needed
4. **Efficient Particle Management**: Object pooling for particle reuse

## Extensibility Points

1. **New Content Types**: Add detection logic and mapping functions
2. **Additional Scales**: Extend the scale definitions in ContentMapper
3. **Custom Visualizations**: Add new animation types in VisualMapper
4. **Plugin Architecture**: Load external mapping modules dynamically
5. **Database Backend**: Replace JSON storage with SQL/NoSQL database
