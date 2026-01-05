"""
Unit tests for the UserPreferences class.
"""

import pytest
import os
import json
import tempfile
import sys
import uuid

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.server import UserPreferences


@pytest.fixture
def temp_prefs_file():
    """Create a temporary file for preferences and clean up after.

    Yields:
        str: Path to a temporary JSON file for storing test preferences.
    """
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, f'test_prefs_{uuid.uuid4().hex}.json')
    yield temp_file
    # Cleanup
    try:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    except:
        pass


class TestUserPreferencesInit:
    """Tests for UserPreferences initialization."""
    
    def test_default_initialization(self, temp_prefs_file):
        """Test default initialization with no existing preferences file.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        prefs = UserPreferences(storage_file=temp_prefs_file)
        assert prefs.preferences == {}
    
    def test_loads_existing_preferences(self, temp_prefs_file):
        """Test loading existing preferences file.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        with open(temp_prefs_file, 'w') as f:
            json.dump({'user123': {'volume': 80}}, f)
        
        prefs = UserPreferences(storage_file=temp_prefs_file)
        assert 'user123' in prefs.preferences
    
    def test_handles_corrupted_file(self, temp_prefs_file):
        """Test handling of corrupted JSON file.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        with open(temp_prefs_file, 'w') as f:
            f.write('invalid json')
        
        prefs = UserPreferences(storage_file=temp_prefs_file)
        assert prefs.preferences == {}


class TestGetPreferences:
    """Tests for get_preferences method."""
    
    def test_returns_defaults_for_new_user(self, temp_prefs_file):
        """Test that defaults are returned for new user.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        prefs = UserPreferences(storage_file=temp_prefs_file)
        result = prefs.get_preferences('new_user')
        
        assert result['volume'] == 50
        assert result['speed'] == 5
        assert result['intensity'] == 70
        assert result['scale'] == 'pentatonic'
        assert result['presets'] == []
    
    def test_returns_stored_preferences(self, temp_prefs_file):
        """Test that stored preferences are returned.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        import hashlib
        hashed_id = hashlib.sha256('test_user'.encode()).hexdigest()[:16]
        
        with open(temp_prefs_file, 'w') as f:
            json.dump({hashed_id: {'volume': 80, 'speed': 8}}, f)
        
        prefs = UserPreferences(storage_file=temp_prefs_file)
        result = prefs.get_preferences('test_user')
        
        assert result['volume'] == 80
        assert result['speed'] == 8


class TestSetPreferences:
    """Tests for set_preferences method."""
    
    def test_sets_preferences(self, temp_prefs_file):
        """Test setting preferences.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        prefs = UserPreferences(storage_file=temp_prefs_file)
        result = prefs.set_preferences('user1', {'volume': 90})
        
        assert result['volume'] == 90
    
    def test_merges_with_existing(self, temp_prefs_file):
        """Test that new preferences merge with existing.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        prefs = UserPreferences(storage_file=temp_prefs_file)
        prefs.set_preferences('user1', {'volume': 90})
        result = prefs.set_preferences('user1', {'speed': 8})
        
        assert result['volume'] == 90
        assert result['speed'] == 8
    
    def test_saves_to_file(self, temp_prefs_file):
        """Test that preferences are saved to file.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        prefs = UserPreferences(storage_file=temp_prefs_file)
        prefs.set_preferences('user1', {'volume': 75})
        
        # Reload and check
        with open(temp_prefs_file, 'r') as f:
            saved = json.load(f)
        
        assert len(saved) == 1


class TestAddPreset:
    """Tests for add_preset method."""
    
    def test_adds_preset(self, temp_prefs_file):
        """Test adding a preset.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        prefs = UserPreferences(storage_file=temp_prefs_file)
        preset = {'name': 'My Preset', 'volume': 80}
        result = prefs.add_preset('user1', preset)
        
        assert len(result) == 1
        assert result[0]['name'] == 'My Preset'
        assert 'id' in result[0]
    
    def test_limits_presets_to_10(self, temp_prefs_file):
        """Test that presets are limited to 10.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        prefs = UserPreferences(storage_file=temp_prefs_file)
        
        for i in range(15):
            prefs.add_preset('user1', {'name': f'Preset {i}'})
        
        result = prefs.get_preferences('user1')
        assert len(result['presets']) == 10
    
    def test_generates_unique_ids(self, temp_prefs_file):
        """Test that each preset gets a unique ID.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        prefs = UserPreferences(storage_file=temp_prefs_file)
        
        result1 = prefs.add_preset('user1', {'name': 'Preset 1'})
        result2 = prefs.add_preset('user1', {'name': 'Preset 2'})
        
        assert result1[0]['id'] != result2[1]['id']


class TestPrivateMethods:
    """Tests for private helper methods."""
    
    def test_get_user_id_consistent(self, temp_prefs_file):
        """Test that user ID hashing is consistent.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        prefs = UserPreferences(storage_file=temp_prefs_file)
        id1 = prefs._get_user_id('test_user')
        id2 = prefs._get_user_id('test_user')
        
        assert id1 == id2
        assert len(id1) == 16
    
    def test_get_user_id_different_for_different_users(self, temp_prefs_file):
        """Test that different users get different IDs.

        Args:
            temp_prefs_file: Pytest fixture providing a temporary file path.
        """
        prefs = UserPreferences(storage_file=temp_prefs_file)
        id1 = prefs._get_user_id('user1')
        id2 = prefs._get_user_id('user2')
        
        assert id1 != id2
