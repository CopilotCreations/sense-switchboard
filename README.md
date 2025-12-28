# Synesthesia Simulator

> Transform digital content into multi-sensory experiences

[![CI/CD Pipeline](https://github.com/your-username/synesthesia-simulator/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/synesthesia-simulator/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

The Synesthesia Simulator is an interactive web application that converts website content into multi-sensory experiences. Just like synesthesia—a neurological phenomenon where stimulation of one sense triggers automatic experiences in another—this application transforms:

- **Text → Musical tones** using pentatonic scales
- **Colors → Ambient sounds** and visual waveforms
- **Numbers → Geometric patterns** and vibrations

## Features

✨ **Real-time Content Transformation**
- Automatic content type detection
- Instant audio-visual feedback
- Smooth animations and transitions

🎵 **Audio Generation**
- Web Audio API synthesis
- Multiple waveform types
- Configurable volume and duration

🎨 **Visual Effects**
- Canvas-based particle systems
- Color-reactive animations
- Geometric pattern generation

⚙️ **Customization**
- Adjustable mapping sliders
- User preference storage
- Preset management

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Modern web browser with audio support

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/synesthesia-simulator.git
cd synesthesia-simulator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

Open http://127.0.0.1:5000 in your browser.

### Command Line Options

```bash
python run.py --host 0.0.0.0    # Allow external connections
python run.py --port 8080       # Use custom port
python run.py --debug           # Enable debug mode
```

## Usage

### Interactive Mode

1. Enter content in the input field:
   - **Text**: `Hello World`
   - **Color**: `#FF5733`
   - **Number**: `42`

2. Click "Experience" or press Enter

3. Adjust the sliders to customize:
   - Volume (0-100%)
   - Animation Speed (1-10x)
   - Visual Intensity (1-100%)

### API Mode

```python
import requests

# Detect content type
response = requests.post('http://localhost:5000/api/detect', 
    json={'content': '#FF0000'})
print(response.json())  # {'type': 'color', 'value': '#FF0000'}

# Map text to frequencies
response = requests.post('http://localhost:5000/api/map/text',
    json={'text': 'ABC', 'scale': 'pentatonic'})
print(response.json())
```

## Project Structure

```
sense-switchboard/
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── .env.example              # Environment configuration
├── .gitignore                # Git ignore patterns
├── .github/workflows/        # CI/CD configuration
│   └── ci.yml
├── src/
│   ├── frontend/             # Web interface
│   │   ├── index.html
│   │   ├── style.css
│   │   └── main.js
│   └── backend/              # Flask server
│       ├── __init__.py
│       └── server.py
├── tests/                    # Test suite
│   ├── test_content_mapper.py
│   ├── test_user_preferences.py
│   └── test_api.py
└── docs/                     # Documentation
    ├── ARCHITECTURE.md
    ├── USAGE.md
    └── SUGGESTIONS.md
```

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md) - Technical design and system overview
- [User Guide](docs/USAGE.md) - Complete usage documentation
- [Suggestions](docs/SUGGESTIONS.md) - Future improvement ideas

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_content_mapper.py -v
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/detect` | POST | Detect content type |
| `/api/map/text` | POST | Map text to frequencies |
| `/api/map/color` | POST | Map color to sound |
| `/api/map/number` | POST | Map number to pattern |
| `/api/map/auto` | POST | Auto-detect and map |
| `/api/preferences` | GET/POST | User preferences |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by synesthesia research and multi-sensory experiences
- Built with Flask, Web Audio API, and Canvas
- Thanks to all contributors and testers
