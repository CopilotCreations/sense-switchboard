"""
Unit tests for the Flask API endpoints.
"""

import pytest
import sys
import os
import json

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.server import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app(static_folder=os.path.join(os.path.dirname(__file__), '..', 'src', 'frontend'))
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_returns_200(self, client):
        """Test health endpoint returns 200."""
        response = client.get('/api/health')
        assert response.status_code == 200
    
    def test_health_returns_status(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert data['service'] == 'synesthesia-simulator'


class TestDetectEndpoint:
    """Tests for the detect content endpoint."""
    
    def test_detect_color(self, client):
        """Test detecting a color."""
        response = client.post('/api/detect',
                              data=json.dumps({'content': '#FF0000'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['type'] == 'color'
        assert data['value'] == '#FF0000'
    
    def test_detect_number(self, client):
        """Test detecting a number."""
        response = client.post('/api/detect',
                              data=json.dumps({'content': '42'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['type'] == 'number'
        assert data['value'] == 42.0
    
    def test_detect_text(self, client):
        """Test detecting text."""
        response = client.post('/api/detect',
                              data=json.dumps({'content': 'Hello'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['type'] == 'text'
        assert data['value'] == 'Hello'
    
    def test_detect_empty(self, client):
        """Test detecting empty content."""
        response = client.post('/api/detect',
                              data=json.dumps({'content': ''}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['type'] == 'unknown'
    
    def test_detect_no_body(self, client):
        """Test detect with no request body."""
        response = client.post('/api/detect',
                              data=json.dumps({}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['type'] == 'unknown'


class TestMapTextEndpoint:
    """Tests for the map text endpoint."""
    
    def test_map_text_basic(self, client):
        """Test basic text mapping."""
        response = client.post('/api/map/text',
                              data=json.dumps({'text': 'ABC'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['input'] == 'ABC'
        assert len(data['mappings']) == 3
        assert 'total_duration' in data
    
    def test_map_text_with_scale(self, client):
        """Test text mapping with custom scale."""
        response = client.post('/api/map/text',
                              data=json.dumps({'text': 'A', 'scale': 'major'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['scale'] == 'major'
    
    def test_map_text_empty(self, client):
        """Test mapping empty text."""
        response = client.post('/api/map/text',
                              data=json.dumps({'text': ''}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['mappings'] == []


class TestMapColorEndpoint:
    """Tests for the map color endpoint."""
    
    def test_map_color_basic(self, client):
        """Test basic color mapping."""
        response = client.post('/api/map/color',
                              data=json.dumps({'color': '#FF0000'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['input'] == '#FF0000'
        assert 'frequency' in data
        assert 'waveform' in data
        assert 'rgb' in data
    
    def test_map_color_includes_complementary(self, client):
        """Test color mapping includes complementary."""
        response = client.post('/api/map/color',
                              data=json.dumps({'color': '#FF0000'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert 'complementary' in data
    
    def test_map_color_invalid(self, client):
        """Test mapping invalid color."""
        response = client.post('/api/map/color',
                              data=json.dumps({'color': 'invalid'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert 'error' in data


class TestMapNumberEndpoint:
    """Tests for the map number endpoint."""
    
    def test_map_number_basic(self, client):
        """Test basic number mapping."""
        response = client.post('/api/map/number',
                              data=json.dumps({'number': 42}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['input'] == 42
        assert 'frequency' in data
        assert 'pattern' in data
        assert 'visual' in data
    
    def test_map_number_negative(self, client):
        """Test mapping negative number."""
        response = client.post('/api/map/number',
                              data=json.dumps({'number': -10}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['is_negative'] is True
    
    def test_map_number_invalid(self, client):
        """Test mapping invalid number."""
        response = client.post('/api/map/number',
                              data=json.dumps({'number': 'not a number'}),
                              content_type='application/json')
        assert response.status_code == 400


class TestMapAutoEndpoint:
    """Tests for the auto-mapping endpoint."""
    
    def test_auto_map_text(self, client):
        """Test auto-mapping text."""
        response = client.post('/api/map/auto',
                              data=json.dumps({'content': 'Hello'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['detected']['type'] == 'text'
        assert 'mappings' in data['mapping']
    
    def test_auto_map_color(self, client):
        """Test auto-mapping color."""
        response = client.post('/api/map/auto',
                              data=json.dumps({'content': '#FF0000'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['detected']['type'] == 'color'
        assert 'frequency' in data['mapping']
    
    def test_auto_map_number(self, client):
        """Test auto-mapping number."""
        response = client.post('/api/map/auto',
                              data=json.dumps({'content': '42'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['detected']['type'] == 'number'
        assert 'pattern' in data['mapping']
    
    def test_auto_map_unknown(self, client):
        """Test auto-mapping unknown content."""
        response = client.post('/api/map/auto',
                              data=json.dumps({'content': ''}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['detected']['type'] == 'unknown'
        assert data['mapping'] == {}


class TestPreferencesEndpoints:
    """Tests for the preferences endpoints."""
    
    def test_get_preferences_default(self, client):
        """Test getting default preferences."""
        response = client.get('/api/preferences')
        data = json.loads(response.data)
        assert 'volume' in data
        assert 'speed' in data
        assert 'intensity' in data
    
    def test_set_preferences(self, client):
        """Test setting preferences."""
        response = client.post('/api/preferences',
                              data=json.dumps({'volume': 80}),
                              content_type='application/json',
                              headers={'X-User-ID': 'test_user'})
        data = json.loads(response.data)
        assert data['volume'] == 80
    
    def test_get_preferences_with_user_id(self, client):
        """Test getting preferences with user ID."""
        # First set preferences
        client.post('/api/preferences',
                   data=json.dumps({'volume': 90}),
                   content_type='application/json',
                   headers={'X-User-ID': 'specific_user'})
        
        # Then get them
        response = client.get('/api/preferences',
                             headers={'X-User-ID': 'specific_user'})
        data = json.loads(response.data)
        assert data['volume'] == 90
    
    def test_add_preset(self, client):
        """Test adding a preset."""
        response = client.post('/api/preferences/preset',
                              data=json.dumps({'name': 'Test Preset'}),
                              content_type='application/json',
                              headers={'X-User-ID': 'preset_user'})
        data = json.loads(response.data)
        assert 'presets' in data
        assert len(data['presets']) >= 1


class TestStaticFiles:
    """Tests for static file serving."""
    
    def test_index_page(self, client):
        """Test that index page is served."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Synesthesia Simulator' in response.data
    
    def test_css_file(self, client):
        """Test that CSS file is served."""
        response = client.get('/style.css')
        assert response.status_code == 200
    
    def test_js_file(self, client):
        """Test that JS file is served."""
        response = client.get('/main.js')
        assert response.status_code == 200
