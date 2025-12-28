"""
Unit tests for the ContentMapper class.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.server import ContentMapper


class TestContentMapperInit:
    """Tests for ContentMapper initialization."""
    
    def test_default_initialization(self):
        """Test default initialization with pentatonic scale."""
        mapper = ContentMapper()
        assert mapper.scale_name == 'pentatonic'
        assert mapper.scale == ContentMapper.PENTATONIC_SCALE
    
    def test_major_scale_initialization(self):
        """Test initialization with major scale."""
        mapper = ContentMapper(scale='major')
        assert mapper.scale_name == 'major'
        assert mapper.scale == ContentMapper.MAJOR_SCALE
    
    def test_minor_scale_initialization(self):
        """Test initialization with minor scale."""
        mapper = ContentMapper(scale='minor')
        assert mapper.scale_name == 'minor'
        assert mapper.scale == ContentMapper.MINOR_SCALE
    
    def test_invalid_scale_defaults_to_pentatonic(self):
        """Test that invalid scale defaults to pentatonic."""
        mapper = ContentMapper(scale='invalid')
        assert mapper.scale == ContentMapper.PENTATONIC_SCALE


class TestSetScale:
    """Tests for set_scale method."""
    
    def test_set_scale_to_major(self):
        """Test setting scale to major."""
        mapper = ContentMapper()
        mapper.set_scale('major')
        assert mapper.scale_name == 'major'
        assert mapper.scale == ContentMapper.MAJOR_SCALE
    
    def test_set_scale_to_minor(self):
        """Test setting scale to minor."""
        mapper = ContentMapper()
        mapper.set_scale('minor')
        assert mapper.scale_name == 'minor'
        assert mapper.scale == ContentMapper.MINOR_SCALE
    
    def test_set_scale_to_pentatonic(self):
        """Test setting scale to pentatonic."""
        mapper = ContentMapper(scale='major')
        mapper.set_scale('pentatonic')
        assert mapper.scale_name == 'pentatonic'
        assert mapper.scale == ContentMapper.PENTATONIC_SCALE


class TestCharToFrequency:
    """Tests for char_to_frequency method."""
    
    def test_letter_a_frequency(self):
        """Test frequency for letter A."""
        mapper = ContentMapper()
        freq = mapper.char_to_frequency('A')
        assert freq == mapper.BASE_FREQUENCY  # A should be base frequency
    
    def test_letter_lowercase_same_as_uppercase(self):
        """Test that lowercase and uppercase produce same frequency."""
        mapper = ContentMapper()
        freq_upper = mapper.char_to_frequency('A')
        freq_lower = mapper.char_to_frequency('a')
        assert freq_upper == freq_lower
    
    def test_different_letters_different_frequencies(self):
        """Test that different letters produce different frequencies."""
        mapper = ContentMapper()
        freq_a = mapper.char_to_frequency('A')
        freq_b = mapper.char_to_frequency('B')
        assert freq_a != freq_b
    
    def test_number_character_frequency(self):
        """Test frequency for number characters."""
        mapper = ContentMapper()
        freq_0 = mapper.char_to_frequency('0')
        freq_5 = mapper.char_to_frequency('5')
        assert freq_0 != freq_5
        assert freq_0 == mapper.BASE_FREQUENCY
    
    def test_empty_char_returns_base_frequency(self):
        """Test empty character returns base frequency."""
        mapper = ContentMapper()
        freq = mapper.char_to_frequency('')
        assert freq == mapper.BASE_FREQUENCY
    
    def test_special_char_returns_base_frequency(self):
        """Test special characters return base frequency."""
        mapper = ContentMapper()
        freq = mapper.char_to_frequency('@')
        assert freq == mapper.BASE_FREQUENCY


class TestTextToFrequencies:
    """Tests for text_to_frequencies method."""
    
    def test_simple_text_conversion(self):
        """Test simple text conversion."""
        mapper = ContentMapper()
        result = mapper.text_to_frequencies('ABC')
        assert len(result) == 3
        assert all('frequency' in r for r in result)
        assert all('char' in r for r in result)
    
    def test_text_with_spaces(self):
        """Test text with spaces creates rests."""
        mapper = ContentMapper()
        result = mapper.text_to_frequencies('A B')
        assert len(result) == 3
        assert result[1]['note'] == 'rest'
        assert result[1]['frequency'] == 0
    
    def test_empty_text_returns_empty_list(self):
        """Test empty text returns empty list."""
        mapper = ContentMapper()
        result = mapper.text_to_frequencies('')
        assert result == []
    
    def test_index_increments(self):
        """Test that index increments correctly."""
        mapper = ContentMapper()
        result = mapper.text_to_frequencies('ABCD')
        for i, r in enumerate(result):
            assert r['index'] == i


class TestHexToRgb:
    """Tests for hex_to_rgb method."""
    
    def test_valid_6_digit_hex(self):
        """Test valid 6-digit hex color."""
        mapper = ContentMapper()
        rgb = mapper.hex_to_rgb('#FF0000')
        assert rgb == (255, 0, 0)
    
    def test_valid_6_digit_hex_without_hash(self):
        """Test valid 6-digit hex without hash."""
        mapper = ContentMapper()
        rgb = mapper.hex_to_rgb('00FF00')
        assert rgb == (0, 255, 0)
    
    def test_valid_3_digit_hex(self):
        """Test valid 3-digit hex color."""
        mapper = ContentMapper()
        rgb = mapper.hex_to_rgb('#F00')
        assert rgb == (255, 0, 0)
    
    def test_valid_3_digit_hex_without_hash(self):
        """Test valid 3-digit hex without hash."""
        mapper = ContentMapper()
        rgb = mapper.hex_to_rgb('0F0')
        assert rgb == (0, 255, 0)
    
    def test_invalid_hex_returns_none(self):
        """Test invalid hex returns None."""
        mapper = ContentMapper()
        assert mapper.hex_to_rgb('GGGGGG') is None
        assert mapper.hex_to_rgb('') is None
        assert mapper.hex_to_rgb('#12') is None
    
    def test_mixed_case_hex(self):
        """Test mixed case hex color."""
        mapper = ContentMapper()
        rgb = mapper.hex_to_rgb('#aAbBcC')
        assert rgb == (170, 187, 204)


class TestRgbToHsl:
    """Tests for rgb_to_hsl method."""
    
    def test_red_to_hsl(self):
        """Test red RGB to HSL."""
        mapper = ContentMapper()
        h, s, l = mapper.rgb_to_hsl(255, 0, 0)
        assert h == 0  # Red hue
        assert s == 1  # Full saturation
        assert l == 0.5  # Half lightness
    
    def test_white_to_hsl(self):
        """Test white RGB to HSL."""
        mapper = ContentMapper()
        h, s, l = mapper.rgb_to_hsl(255, 255, 255)
        assert s == 0  # No saturation
        assert l == 1  # Full lightness
    
    def test_black_to_hsl(self):
        """Test black RGB to HSL."""
        mapper = ContentMapper()
        h, s, l = mapper.rgb_to_hsl(0, 0, 0)
        assert s == 0  # No saturation
        assert l == 0  # No lightness
    
    def test_gray_to_hsl(self):
        """Test gray RGB to HSL."""
        mapper = ContentMapper()
        h, s, l = mapper.rgb_to_hsl(128, 128, 128)
        assert s == 0  # No saturation
        assert 0.4 < l < 0.6  # Around half lightness


class TestColorToSound:
    """Tests for color_to_sound method."""
    
    def test_valid_color_returns_frequency(self):
        """Test valid color returns frequency data."""
        mapper = ContentMapper()
        result = mapper.color_to_sound('#FF0000')
        assert 'frequency' in result
        assert 'waveform' in result
        assert 'rgb' in result
        assert 'hsl' in result
    
    def test_high_saturation_uses_sawtooth(self):
        """Test high saturation colors use sawtooth waveform."""
        mapper = ContentMapper()
        result = mapper.color_to_sound('#FF0000')  # Fully saturated red
        assert result['waveform'] == 'sawtooth'
    
    def test_low_saturation_uses_sine(self):
        """Test low saturation colors use sine waveform."""
        mapper = ContentMapper()
        result = mapper.color_to_sound('#888888')  # Gray (no saturation)
        assert result['waveform'] == 'sine'
    
    def test_invalid_color_returns_error(self):
        """Test invalid color returns error."""
        mapper = ContentMapper()
        result = mapper.color_to_sound('invalid')
        assert 'error' in result
    
    def test_complementary_color_included(self):
        """Test complementary color is included."""
        mapper = ContentMapper()
        result = mapper.color_to_sound('#FF0000')
        assert 'complementary' in result
        assert result['complementary'] == '#00ffff'


class TestNumberToPattern:
    """Tests for number_to_pattern method."""
    
    def test_positive_number_pattern(self):
        """Test positive number produces pattern."""
        mapper = ContentMapper()
        result = mapper.number_to_pattern(42)
        assert 'frequency' in result
        assert 'pattern' in result
        assert 'visual' in result
        assert result['is_negative'] is False
    
    def test_negative_number_pattern(self):
        """Test negative number produces pattern."""
        mapper = ContentMapper()
        result = mapper.number_to_pattern(-42)
        assert result['is_negative'] is True
        assert result['magnitude'] == 42
    
    def test_even_number_pulse_pattern(self):
        """Test even numbers get pulse pattern."""
        mapper = ContentMapper()
        result = mapper.number_to_pattern(4)
        assert result['pattern'] == 'pulse'
    
    def test_multiple_of_three_arpeggio(self):
        """Test multiples of 3 get arpeggio pattern."""
        mapper = ContentMapper()
        result = mapper.number_to_pattern(9)
        assert result['pattern'] == 'arpeggio'
    
    def test_multiple_of_five_sweep(self):
        """Test multiples of 5 get sweep pattern."""
        mapper = ContentMapper()
        result = mapper.number_to_pattern(25)
        assert result['pattern'] == 'sweep'
    
    def test_multiple_of_seven_wave(self):
        """Test multiples of 7 get wave pattern."""
        mapper = ContentMapper()
        result = mapper.number_to_pattern(49)
        assert result['pattern'] == 'wave'
    
    def test_oscillator_count_capped(self):
        """Test oscillator count is capped at 5."""
        mapper = ContentMapper()
        result = mapper.number_to_pattern(1000)
        assert result['oscillator_count'] <= 5
    
    def test_particle_count_capped(self):
        """Test particle count is capped at 100."""
        mapper = ContentMapper()
        result = mapper.number_to_pattern(200)
        assert result['visual']['particle_count'] <= 100


class TestDetectContentType:
    """Tests for detect_content_type method."""
    
    def test_detect_hex_color_6_digit(self):
        """Test detection of 6-digit hex color."""
        mapper = ContentMapper()
        result = mapper.detect_content_type('#FF5733')
        assert result['type'] == 'color'
        assert result['value'] == '#FF5733'
    
    def test_detect_hex_color_3_digit(self):
        """Test detection of 3-digit hex color."""
        mapper = ContentMapper()
        result = mapper.detect_content_type('#F00')
        assert result['type'] == 'color'
        assert result['value'] == '#F00'
    
    def test_detect_integer(self):
        """Test detection of integer."""
        mapper = ContentMapper()
        result = mapper.detect_content_type('42')
        assert result['type'] == 'number'
        assert result['value'] == 42.0
    
    def test_detect_negative_number(self):
        """Test detection of negative number."""
        mapper = ContentMapper()
        result = mapper.detect_content_type('-17')
        assert result['type'] == 'number'
        assert result['value'] == -17.0
    
    def test_detect_float(self):
        """Test detection of float."""
        mapper = ContentMapper()
        result = mapper.detect_content_type('3.14')
        assert result['type'] == 'number'
        assert result['value'] == 3.14
    
    def test_detect_text(self):
        """Test detection of text."""
        mapper = ContentMapper()
        result = mapper.detect_content_type('Hello World')
        assert result['type'] == 'text'
        assert result['value'] == 'Hello World'
    
    def test_detect_empty_string(self):
        """Test detection of empty string."""
        mapper = ContentMapper()
        result = mapper.detect_content_type('')
        assert result['type'] == 'unknown'
        assert result['value'] is None
    
    def test_detect_whitespace_only(self):
        """Test detection of whitespace only."""
        mapper = ContentMapper()
        result = mapper.detect_content_type('   ')
        assert result['type'] == 'unknown'
    
    def test_detect_none(self):
        """Test detection of None."""
        mapper = ContentMapper()
        result = mapper.detect_content_type(None)
        assert result['type'] == 'unknown'
    
    def test_detect_non_string(self):
        """Test detection of non-string input."""
        mapper = ContentMapper()
        result = mapper.detect_content_type(123)
        assert result['type'] == 'unknown'
    
    def test_strips_whitespace(self):
        """Test that input is stripped of whitespace."""
        mapper = ContentMapper()
        result = mapper.detect_content_type('  42  ')
        assert result['type'] == 'number'
        assert result['value'] == 42.0
