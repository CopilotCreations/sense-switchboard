"""
Synesthesia Simulator Backend Server

A Flask-based server that provides:
- Static file serving for the frontend
- Dynamic content mapping API
- User preferences storage
- Complex procedural conversion mappings
"""

import os
import json
import hashlib
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from typing import Dict, Any, Optional, List, Tuple
import math


# ============================================================================
# Content Mapping Module
# ============================================================================

class ContentMapper:
    """Handles conversion of content to sensory parameters."""
    
    # Musical scales for text-to-tone mapping
    PENTATONIC_SCALE = [0, 2, 4, 7, 9]  # C, D, E, G, A
    MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]  # C, D, E, F, G, A, B
    MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]  # C, D, Eb, F, G, Ab, Bb
    
    # Base frequency (A3)
    BASE_FREQUENCY = 220.0
    
    def __init__(self, scale: str = 'pentatonic'):
        """
        Initialize the content mapper.
        
        Args:
            scale: Musical scale to use ('pentatonic', 'major', 'minor')
        """
        self.scale = self._get_scale(scale)
        self.scale_name = scale
    
    def _get_scale(self, scale_name: str) -> List[int]:
        """Get the scale intervals for the given scale name."""
        scales = {
            'pentatonic': self.PENTATONIC_SCALE,
            'major': self.MAJOR_SCALE,
            'minor': self.MINOR_SCALE
        }
        return scales.get(scale_name, self.PENTATONIC_SCALE)
    
    def set_scale(self, scale_name: str) -> None:
        """Set the musical scale to use."""
        self.scale = self._get_scale(scale_name)
        self.scale_name = scale_name
    
    def char_to_frequency(self, char: str) -> float:
        """
        Convert a character to a frequency.
        
        Args:
            char: Single character to convert
            
        Returns:
            Frequency in Hz
        """
        if not char:
            return self.BASE_FREQUENCY
        
        char_code = ord(char.upper())
        
        # Map A-Z to frequencies
        if 65 <= char_code <= 90:
            note_index = char_code - 65
            scale_index = note_index % len(self.scale)
            octave_offset = (note_index // len(self.scale)) * 12
            semitones = self.scale[scale_index] + octave_offset
            return self.BASE_FREQUENCY * (2 ** (semitones / 12))
        
        # Map 0-9 to frequencies
        if 48 <= char_code <= 57:
            num_value = char_code - 48
            return self.BASE_FREQUENCY * (2 ** (num_value / 12))
        
        # Default for other characters
        return self.BASE_FREQUENCY
    
    def text_to_frequencies(self, text: str) -> List[Dict[str, Any]]:
        """
        Convert text to a sequence of frequency mappings.
        
        Args:
            text: Text to convert
            
        Returns:
            List of dictionaries with frequency and character info
        """
        result = []
        for i, char in enumerate(text):
            if char.strip():
                freq = self.char_to_frequency(char)
                result.append({
                    'index': i,
                    'char': char,
                    'frequency': round(freq, 2),
                    'note': self._frequency_to_note(freq),
                    'duration': 0.2
                })
            else:
                result.append({
                    'index': i,
                    'char': char,
                    'frequency': 0,
                    'note': 'rest',
                    'duration': 0.1
                })
        return result
    
    def _frequency_to_note(self, frequency: float) -> str:
        """Convert a frequency to a note name."""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        if frequency <= 0:
            return 'rest'
        
        # Calculate semitones from A4 (440 Hz)
        semitones = 12 * math.log2(frequency / 440) + 69
        note_index = int(round(semitones)) % 12
        octave = int(round(semitones)) // 12 - 1
        
        return f"{notes[note_index]}{octave}"
    
    def hex_to_rgb(self, hex_color: str) -> Optional[Tuple[int, int, int]]:
        """
        Convert hex color to RGB.
        
        Args:
            hex_color: Hex color string (with or without #)
            
        Returns:
            Tuple of (r, g, b) or None if invalid
        """
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 3:
            hex_color = ''.join([c * 2 for c in hex_color])
        
        if len(hex_color) != 6:
            return None
        
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return None
    
    def rgb_to_hsl(self, r: int, g: int, b: int) -> Tuple[float, float, float]:
        """
        Convert RGB to HSL.
        
        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)
            
        Returns:
            Tuple of (h, s, l) where h is 0-360 and s, l are 0-1
        """
        r, g, b = r / 255, g / 255, b / 255
        
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2
        
        if max_c == min_c:
            h = s = 0
        else:
            d = max_c - min_c
            s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
            
            if max_c == r:
                h = ((g - b) / d + (6 if g < b else 0)) / 6
            elif max_c == g:
                h = ((b - r) / d + 2) / 6
            else:
                h = ((r - g) / d + 4) / 6
        
        return (h * 360, s, l)
    
    def color_to_sound(self, hex_color: str) -> Dict[str, Any]:
        """
        Convert a color to sound parameters.
        
        Args:
            hex_color: Hex color string
            
        Returns:
            Dictionary with frequency, waveform, and color info
        """
        rgb = self.hex_to_rgb(hex_color)
        if not rgb:
            return {
                'frequency': 440,
                'waveform': 'sine',
                'rgb': None,
                'hsl': None,
                'error': 'Invalid color format'
            }
        
        hsl = self.rgb_to_hsl(*rgb)
        
        # Map hue to frequency (200-800 Hz range)
        frequency = 200 + (hsl[0] / 360) * 600
        
        # Map saturation to waveform type
        if hsl[1] > 0.7:
            waveform = 'sawtooth'
        elif hsl[1] > 0.4:
            waveform = 'triangle'
        else:
            waveform = 'sine'
        
        # Map lightness to volume modifier
        volume_modifier = 0.5 + hsl[2] * 0.5
        
        return {
            'frequency': round(frequency, 2),
            'waveform': waveform,
            'volume_modifier': round(volume_modifier, 2),
            'rgb': {'r': rgb[0], 'g': rgb[1], 'b': rgb[2]},
            'hsl': {'h': round(hsl[0], 2), 's': round(hsl[1], 2), 'l': round(hsl[2], 2)},
            'complementary': self._get_complementary_color(hex_color)
        }
    
    def _get_complementary_color(self, hex_color: str) -> str:
        """Get the complementary color."""
        rgb = self.hex_to_rgb(hex_color)
        if not rgb:
            return '#000000'
        
        comp = tuple(255 - c for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*comp)
    
    def number_to_pattern(self, number: float) -> Dict[str, Any]:
        """
        Convert a number to a pattern/animation parameters.
        
        Args:
            number: Number to convert
            
        Returns:
            Dictionary with pattern parameters
        """
        abs_num = abs(number)
        
        # Frequency based on logarithmic scale
        frequency = 100 * (10 ** ((abs_num % 100) / 100))
        
        # Determine pattern type based on divisibility
        pattern = 'steady'
        if number % 7 == 0:
            pattern = 'wave'
        elif number % 5 == 0:
            pattern = 'sweep'
        elif number % 3 == 0:
            pattern = 'arpeggio'
        elif number % 2 == 0:
            pattern = 'pulse'
        
        # Visual parameters
        sides = 3 + (int(abs_num) % 7)  # 3-9 sides polygon
        rotation_speed = (abs_num % 10) + 1
        color_shift = (abs_num * 30) % 360
        
        return {
            'frequency': round(frequency, 2),
            'pattern': pattern,
            'oscillator_count': min(int(abs_num // 10) + 1, 5),
            'visual': {
                'sides': sides,
                'rotation_speed': rotation_speed,
                'color_hue': color_shift,
                'particle_count': min(int(abs_num), 100)
            },
            'is_negative': number < 0,
            'magnitude': abs_num
        }
    
    def detect_content_type(self, content: str) -> Dict[str, Any]:
        """
        Detect the type of content.
        
        Args:
            content: Input content string
            
        Returns:
            Dictionary with type and parsed value
        """
        if not content or not isinstance(content, str):
            return {'type': 'unknown', 'value': None}
        
        content = content.strip()
        
        # Check for hex color
        if content.startswith('#'):
            hex_part = content[1:]
            if len(hex_part) in (3, 6) and all(c in '0123456789ABCDEFabcdef' for c in hex_part):
                return {'type': 'color', 'value': content}
        
        # Check for number
        try:
            num = float(content)
            return {'type': 'number', 'value': num}
        except ValueError:
            pass
        
        # Default to text
        if content:
            return {'type': 'text', 'value': content}
        
        return {'type': 'unknown', 'value': None}


# ============================================================================
# User Preferences Module
# ============================================================================

class UserPreferences:
    """Handles storage and retrieval of user preferences."""
    
    def __init__(self, storage_file: str = 'preferences.json'):
        """
        Initialize user preferences storage.
        
        Args:
            storage_file: Path to the JSON file for storing preferences
        """
        self.storage_file = storage_file
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load preferences from file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_preferences(self) -> None:
        """Save preferences to file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except IOError:
            pass
    
    def _get_user_id(self, identifier: str) -> str:
        """Generate a consistent user ID from an identifier."""
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]
    
    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get preferences for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            User preferences dictionary
        """
        hashed_id = self._get_user_id(user_id)
        return self.preferences.get(hashed_id, {
            'volume': 50,
            'speed': 5,
            'intensity': 70,
            'scale': 'pentatonic',
            'presets': []
        })
    
    def set_preferences(self, user_id: str, prefs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set preferences for a user.
        
        Args:
            user_id: User identifier
            prefs: Preferences to set
            
        Returns:
            Updated preferences
        """
        hashed_id = self._get_user_id(user_id)
        current = self.get_preferences(user_id)
        current.update(prefs)
        self.preferences[hashed_id] = current
        self._save_preferences()
        return current
    
    def add_preset(self, user_id: str, preset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Add a preset for a user.
        
        Args:
            user_id: User identifier
            preset: Preset configuration
            
        Returns:
            Updated list of presets
        """
        prefs = self.get_preferences(user_id)
        presets = prefs.get('presets', [])
        preset['id'] = hashlib.sha256(json.dumps(preset).encode()).hexdigest()[:8]
        presets.append(preset)
        prefs['presets'] = presets[:10]  # Limit to 10 presets
        self.set_preferences(user_id, prefs)
        return prefs['presets']


# ============================================================================
# Flask Application
# ============================================================================

def create_app(static_folder: Optional[str] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        static_folder: Path to static files folder
        
    Returns:
        Configured Flask application
    """
    if static_folder is None:
        static_folder = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    
    app = Flask(__name__, static_folder=static_folder)
    CORS(app)
    
    # Initialize services
    content_mapper = ContentMapper()
    user_prefs = UserPreferences()
    
    # ========================================================================
    # Static File Routes
    # ========================================================================
    
    @app.route('/')
    def index():
        """Serve the main index.html file."""
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:filename>')
    def static_files(filename):
        """Serve static files."""
        return send_from_directory(app.static_folder, filename)
    
    # ========================================================================
    # API Routes
    # ========================================================================
    
    @app.route('/api/detect', methods=['POST'])
    def detect_content():
        """Detect content type from input."""
        data = request.get_json() or {}
        content = data.get('content', '')
        result = content_mapper.detect_content_type(content)
        return jsonify(result)
    
    @app.route('/api/map/text', methods=['POST'])
    def map_text():
        """Convert text to frequency mappings."""
        data = request.get_json() or {}
        text = data.get('text', '')
        scale = data.get('scale', 'pentatonic')
        
        content_mapper.set_scale(scale)
        frequencies = content_mapper.text_to_frequencies(text)
        
        return jsonify({
            'input': text,
            'scale': scale,
            'mappings': frequencies,
            'total_duration': sum(f['duration'] for f in frequencies)
        })
    
    @app.route('/api/map/color', methods=['POST'])
    def map_color():
        """Convert color to sound parameters."""
        data = request.get_json() or {}
        color = data.get('color', '#000000')
        
        result = content_mapper.color_to_sound(color)
        result['input'] = color
        
        return jsonify(result)
    
    @app.route('/api/map/number', methods=['POST'])
    def map_number():
        """Convert number to pattern parameters."""
        data = request.get_json() or {}
        try:
            number = float(data.get('number', 0))
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid number'}), 400
        
        result = content_mapper.number_to_pattern(number)
        result['input'] = number
        
        return jsonify(result)
    
    @app.route('/api/map/auto', methods=['POST'])
    def map_auto():
        """Automatically detect and map content."""
        data = request.get_json() or {}
        content = data.get('content', '')
        
        detected = content_mapper.detect_content_type(content)
        
        if detected['type'] == 'text':
            mapping = {
                'mappings': content_mapper.text_to_frequencies(detected['value']),
                'total_duration': sum(f['duration'] for f in content_mapper.text_to_frequencies(detected['value']))
            }
        elif detected['type'] == 'color':
            mapping = content_mapper.color_to_sound(detected['value'])
        elif detected['type'] == 'number':
            mapping = content_mapper.number_to_pattern(detected['value'])
        else:
            mapping = {}
        
        return jsonify({
            'detected': detected,
            'mapping': mapping
        })
    
    # ========================================================================
    # Preferences Routes
    # ========================================================================
    
    @app.route('/api/preferences', methods=['GET'])
    def get_preferences():
        """Get user preferences."""
        user_id = request.headers.get('X-User-ID', 'default')
        prefs = user_prefs.get_preferences(user_id)
        return jsonify(prefs)
    
    @app.route('/api/preferences', methods=['POST'])
    def set_preferences():
        """Set user preferences."""
        user_id = request.headers.get('X-User-ID', 'default')
        data = request.get_json() or {}
        prefs = user_prefs.set_preferences(user_id, data)
        return jsonify(prefs)
    
    @app.route('/api/preferences/preset', methods=['POST'])
    def add_preset():
        """Add a user preset."""
        user_id = request.headers.get('X-User-ID', 'default')
        data = request.get_json() or {}
        presets = user_prefs.add_preset(user_id, data)
        return jsonify({'presets': presets})
    
    # ========================================================================
    # Health Check
    # ========================================================================
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'service': 'synesthesia-simulator'
        })
    
    return app


# Create default app instance
app = create_app()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Synesthesia Simulator Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"Starting Synesthesia Simulator server at http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
