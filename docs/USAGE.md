# Synesthesia Simulator - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Features](#features)
4. [Usage Guide](#usage-guide)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

## Introduction

The Synesthesia Simulator is an interactive web application that transforms digital content into multi-sensory experiences. Just like synesthesia—a neurological phenomenon where stimulation of one sense triggers automatic experiences in another—this application converts text, colors, and numbers into sounds and visual patterns.

### What You Can Do

- **Text → Music**: Type any text and hear it as a melody
- **Colors → Ambient Sound**: Enter hex colors and experience them as audio frequencies with visual effects
- **Numbers → Patterns**: Input numbers to generate geometric animations with corresponding sounds

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Modern web browser (Chrome, Firefox, Safari, or Edge)
- Audio-enabled device (speakers or headphones)

### Installation

1. **Clone or download the project**:
   ```bash
   cd sense-switchboard
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the server**:
   ```bash
   python run.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://127.0.0.1:5000
   ```

### Quick Start Options

```bash
# Start with custom port
python run.py --port 8080

# Enable debug mode (for development)
python run.py --debug

# Allow external connections
python run.py --host 0.0.0.0
```

## Features

### 1. Content Detection

The application automatically detects the type of content you enter:

| Input Format | Detected Type | Example |
|-------------|---------------|---------|
| `#RRGGBB` or `#RGB` | Color | `#FF5733`, `#F00` |
| Numeric values | Number | `42`, `-17`, `3.14` |
| Any other text | Text | `Hello World` |

### 2. Audio Mapping

#### Text to Music
- Each letter is mapped to a musical note
- Uses a pentatonic scale for pleasant harmonies
- Spaces create brief pauses
- Capital and lowercase letters produce the same tone

#### Color to Sound
- **Hue** determines the base frequency (200-800 Hz)
- **Saturation** determines the waveform:
  - High saturation → Bright, buzzy sound (sawtooth)
  - Medium saturation → Mellow tone (triangle)
  - Low saturation → Pure, soft tone (sine)
- **Lightness** affects volume

#### Number to Patterns
- Numbers are mapped to frequencies on a logarithmic scale
- Divisibility rules determine the pattern:
  - Divisible by 7 → Wave pattern
  - Divisible by 5 → Sweep effect
  - Divisible by 3 → Arpeggio
  - Divisible by 2 → Pulse

### 3. Visual Effects

Each content type triggers unique visualizations:

- **Text**: Floating, bouncing letters
- **Color**: Pulsing particle clouds in the input color
- **Number**: Expanding geometric patterns

### 4. Adjustable Controls

| Control | Range | Effect |
|---------|-------|--------|
| Volume | 0-100% | Master audio volume |
| Animation Speed | 1-10x | Visual animation speed |
| Visual Intensity | 1-100% | Particle count and size |

### 5. Interactive Grid

Click or hover over the sample items in the grid to:
- **Click**: Trigger the full experience
- **Hover**: Preview the sound briefly

## Usage Guide

### Basic Usage

1. **Enter content** in the input field at the top
2. **Click "Experience"** or press Enter
3. **Adjust sliders** to customize the experience
4. **Use the grid** for quick interactions

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Trigger experience for current input |
| Escape | Stop current animation |

### Tips for Best Experience

1. **Use headphones** for the best audio experience
2. **Try complementary colors** for harmonic sounds
3. **Experiment with prime numbers** for unique patterns
4. **Combine letters** to create melodies

## API Reference

The backend provides a REST API for programmatic access.

### Endpoints

#### Health Check
```http
GET /api/health
```
Returns:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "synesthesia-simulator"
}
```

#### Detect Content Type
```http
POST /api/detect
Content-Type: application/json

{
  "content": "#FF0000"
}
```
Returns:
```json
{
  "type": "color",
  "value": "#FF0000"
}
```

#### Map Text to Frequencies
```http
POST /api/map/text
Content-Type: application/json

{
  "text": "ABC",
  "scale": "pentatonic"
}
```
Returns:
```json
{
  "input": "ABC",
  "scale": "pentatonic",
  "mappings": [
    {"index": 0, "char": "A", "frequency": 220.0, "note": "A3", "duration": 0.2},
    {"index": 1, "char": "B", "frequency": 246.94, "note": "B3", "duration": 0.2},
    {"index": 2, "char": "C", "frequency": 277.18, "note": "C#4", "duration": 0.2}
  ],
  "total_duration": 0.6
}
```

#### Map Color to Sound
```http
POST /api/map/color
Content-Type: application/json

{
  "color": "#FF0000"
}
```
Returns:
```json
{
  "input": "#FF0000",
  "frequency": 200.0,
  "waveform": "sawtooth",
  "volume_modifier": 0.75,
  "rgb": {"r": 255, "g": 0, "b": 0},
  "hsl": {"h": 0.0, "s": 1.0, "l": 0.5},
  "complementary": "#00ffff"
}
```

#### Map Number to Pattern
```http
POST /api/map/number
Content-Type: application/json

{
  "number": 42
}
```
Returns:
```json
{
  "input": 42,
  "frequency": 263.03,
  "pattern": "pulse",
  "oscillator_count": 5,
  "visual": {
    "sides": 3,
    "rotation_speed": 3,
    "color_hue": 180,
    "particle_count": 42
  },
  "is_negative": false,
  "magnitude": 42
}
```

#### Auto-Map Content
```http
POST /api/map/auto
Content-Type: application/json

{
  "content": "Hello"
}
```
Automatically detects type and returns appropriate mapping.

#### Get/Set Preferences
```http
GET /api/preferences
X-User-ID: your-user-id

POST /api/preferences
Content-Type: application/json
X-User-ID: your-user-id

{
  "volume": 80,
  "speed": 7
}
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Server settings
HOST=127.0.0.1
PORT=5000
DEBUG=false

# Logging
LOG_LEVEL=INFO
```

### Musical Scales

The application supports three musical scales:

| Scale | Notes | Character |
|-------|-------|-----------|
| Pentatonic | C, D, E, G, A | Harmonious, Asian-inspired |
| Major | C, D, E, F, G, A, B | Bright, happy |
| Minor | C, D, Eb, F, G, Ab, Bb | Darker, emotional |

## Troubleshooting

### No Sound Playing

1. **Check browser permissions**: Some browsers require user interaction before playing audio
2. **Verify volume**: Check both the app slider and system volume
3. **Try clicking** "Experience" button (first interaction requirement)

### Visualization Not Showing

1. **Ensure canvas is visible**: Check if the display area is properly sized
2. **Refresh the page**: Clear any cached state
3. **Check browser console**: Look for JavaScript errors

### Server Won't Start

1. **Port in use**: Try a different port with `--port 8080`
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Python version**: Ensure Python 3.9+ is installed

### Common Error Messages

| Error | Solution |
|-------|----------|
| `AudioContext not allowed` | Click anywhere on the page first |
| `Address already in use` | Change the port number |
| `Module not found` | Install missing dependencies |

### Getting Help

If you encounter issues not covered here:

1. Check the GitHub Issues page
2. Review the ARCHITECTURE.md for technical details
3. Enable debug mode (`--debug`) for verbose logging

## Examples

### Creating a Musical Phrase

Try entering: `ABCDEFG` to hear a musical scale.

### Color Harmony Exploration

Enter these colors in sequence:
- `#FF0000` (Red)
- `#00FF00` (Green)
- `#0000FF` (Blue)

### Number Pattern Discovery

Try these numbers for different patterns:
- `7` - Wave pattern
- `15` - Sweep (divisible by 5)
- `21` - Arpeggio (divisible by 3 and 7)
- `42` - Pulse with multiple oscillators
