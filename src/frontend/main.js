/**
 * Synesthesia Simulator - Main JavaScript Module
 * Converts content (text, colors, numbers) into multi-sensory experiences
 */

// ============================================================================
// Content Type Detection Module
// ============================================================================

/**
 * Detects the type of content provided by the user
 * @param {string} content - The input content to analyze
 * @returns {object} Object containing type and parsed value
 */
function detectContentType(content) {
    if (!content || typeof content !== 'string') {
        return { type: 'unknown', value: null };
    }

    const trimmed = content.trim();

    // Check for hex color (#RGB or #RRGGBB)
    const hexColorRegex = /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/;
    if (hexColorRegex.test(trimmed)) {
        return { type: 'color', value: trimmed };
    }

    // Check for number (integer or float)
    const numberRegex = /^-?\d+\.?\d*$/;
    if (numberRegex.test(trimmed)) {
        return { type: 'number', value: parseFloat(trimmed) };
    }

    // Default to text
    if (trimmed.length > 0) {
        return { type: 'text', value: trimmed };
    }

    return { type: 'unknown', value: null };
}

// ============================================================================
// Audio Mapping Module
// ============================================================================

/**
 * AudioMapper class - Handles Web Audio API for sound generation
 */
class AudioMapper {
    constructor() {
        this.audioContext = null;
        this.masterGain = null;
        this.volume = 0.5;
        this.isInitialized = false;
    }

    /**
     * Initialize the audio context (must be called after user interaction)
     */
    initialize() {
        if (this.isInitialized) return;
        
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.masterGain = this.audioContext.createGain();
            this.masterGain.connect(this.audioContext.destination);
            this.masterGain.gain.value = this.volume;
            this.isInitialized = true;
        } catch (error) {
            console.error('Failed to initialize audio context:', error);
        }
    }

    /**
     * Set the master volume
     * @param {number} volume - Volume level (0-1)
     */
    setVolume(volume) {
        this.volume = Math.max(0, Math.min(1, volume));
        if (this.masterGain) {
            this.masterGain.gain.value = this.volume;
        }
    }

    /**
     * Map a character to a frequency
     * @param {string} char - Single character
     * @returns {number} Frequency in Hz
     */
    charToFrequency(char) {
        const baseFrequency = 220; // A3
        const charCode = char.toUpperCase().charCodeAt(0);
        
        // Map A-Z to frequencies in a musical scale
        if (charCode >= 65 && charCode <= 90) {
            const noteIndex = charCode - 65;
            // Use pentatonic scale for more pleasant sounds
            const pentatonic = [0, 2, 4, 7, 9, 12, 14, 16, 19, 21, 24, 26, 28];
            const scaleIndex = noteIndex % pentatonic.length;
            const octaveOffset = Math.floor(noteIndex / pentatonic.length) * 12;
            return baseFrequency * Math.pow(2, (pentatonic[scaleIndex] + octaveOffset) / 12);
        }
        
        // Numbers 0-9
        if (charCode >= 48 && charCode <= 57) {
            const numValue = charCode - 48;
            return baseFrequency * Math.pow(2, numValue / 12);
        }
        
        // Default frequency for other characters
        return baseFrequency;
    }

    /**
     * Map a hex color to a frequency
     * @param {string} hexColor - Hex color string
     * @returns {object} Object with frequency and waveform type
     */
    colorToSound(hexColor) {
        const rgb = this.hexToRgb(hexColor);
        if (!rgb) return { frequency: 440, waveform: 'sine' };

        // Map hue to frequency (200-800 Hz range)
        const hsl = this.rgbToHsl(rgb.r, rgb.g, rgb.b);
        const frequency = 200 + (hsl.h / 360) * 600;

        // Map saturation to waveform type
        let waveform = 'sine';
        if (hsl.s > 0.7) waveform = 'sawtooth';
        else if (hsl.s > 0.4) waveform = 'triangle';

        return { frequency, waveform, rgb, hsl };
    }

    /**
     * Map a number to sound parameters
     * @param {number} num - The number to map
     * @returns {object} Sound parameters
     */
    numberToSound(num) {
        const absNum = Math.abs(num);
        
        // Map to frequency (100-1000 Hz logarithmic scale)
        const frequency = 100 * Math.pow(10, (absNum % 100) / 100);
        
        // Number of oscillators based on magnitude
        const oscillatorCount = Math.min(Math.floor(absNum / 10) + 1, 5);
        
        // Determine pattern type
        let pattern = 'steady';
        if (num % 2 === 0) pattern = 'pulse';
        if (num % 3 === 0) pattern = 'arpeggio';
        if (num % 5 === 0) pattern = 'sweep';

        return { frequency, oscillatorCount, pattern };
    }

    /**
     * Play a tone with the given parameters
     * @param {number} frequency - Frequency in Hz
     * @param {string} waveform - Oscillator waveform type
     * @param {number} duration - Duration in seconds
     */
    playTone(frequency, waveform = 'sine', duration = 0.5) {
        if (!this.isInitialized) this.initialize();
        if (!this.audioContext) return;

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.type = waveform;
        oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);

        // ADSR envelope
        const now = this.audioContext.currentTime;
        gainNode.gain.setValueAtTime(0, now);
        gainNode.gain.linearRampToValueAtTime(0.3, now + 0.05); // Attack
        gainNode.gain.linearRampToValueAtTime(0.2, now + 0.1); // Decay
        gainNode.gain.setValueAtTime(0.2, now + duration - 0.1); // Sustain
        gainNode.gain.linearRampToValueAtTime(0, now + duration); // Release

        oscillator.connect(gainNode);
        gainNode.connect(this.masterGain);

        oscillator.start(now);
        oscillator.stop(now + duration);

        return frequency;
    }

    /**
     * Play a sequence of tones for text
     * @param {string} text - Text to convert to tones
     * @param {number} noteDuration - Duration of each note
     */
    playTextSequence(text, noteDuration = 0.2) {
        if (!this.isInitialized) this.initialize();
        
        const chars = text.split('');
        let delay = 0;

        chars.forEach((char, index) => {
            if (char.trim()) {
                const frequency = this.charToFrequency(char);
                setTimeout(() => {
                    this.playTone(frequency, 'sine', noteDuration);
                }, delay);
                delay += noteDuration * 1000;
            } else {
                delay += noteDuration * 500; // Shorter pause for spaces
            }
        });

        return delay;
    }

    /**
     * Convert hex color to RGB
     * @param {string} hex - Hex color string
     * @returns {object|null} RGB object or null
     */
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        if (result) {
            return {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            };
        }
        // Handle 3-digit hex
        const shortResult = /^#?([a-f\d])([a-f\d])([a-f\d])$/i.exec(hex);
        if (shortResult) {
            return {
                r: parseInt(shortResult[1] + shortResult[1], 16),
                g: parseInt(shortResult[2] + shortResult[2], 16),
                b: parseInt(shortResult[3] + shortResult[3], 16)
            };
        }
        return null;
    }

    /**
     * Convert RGB to HSL
     * @param {number} r - Red (0-255)
     * @param {number} g - Green (0-255)
     * @param {number} b - Blue (0-255)
     * @returns {object} HSL object
     */
    rgbToHsl(r, g, b) {
        r /= 255;
        g /= 255;
        b /= 255;

        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
            h = s = 0;
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
            switch (max) {
                case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
                case g: h = ((b - r) / d + 2) / 6; break;
                case b: h = ((r - g) / d + 4) / 6; break;
            }
        }

        return { h: h * 360, s, l };
    }
}

// ============================================================================
// Visual Effects Module
// ============================================================================

/**
 * VisualMapper class - Handles canvas-based visualizations
 */
class VisualMapper {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.particles = [];
        this.animationId = null;
        this.intensity = 0.7;
        this.speed = 5;
        this.isAnimating = false;
        
        if (this.canvas) {
            this.resizeCanvas();
            window.addEventListener('resize', () => this.resizeCanvas());
        }
    }

    /**
     * Resize canvas to fill container
     */
    resizeCanvas() {
        if (!this.canvas) return;
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
    }

    /**
     * Set visual intensity
     * @param {number} intensity - Intensity level (0-1)
     */
    setIntensity(intensity) {
        this.intensity = Math.max(0, Math.min(1, intensity));
    }

    /**
     * Set animation speed
     * @param {number} speed - Speed multiplier (1-10)
     */
    setSpeed(speed) {
        this.speed = Math.max(1, Math.min(10, speed));
    }

    /**
     * Create particles for text visualization
     * @param {string} text - Text to visualize
     */
    createTextParticles(text) {
        if (!this.ctx) return;
        
        this.particles = [];
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;

        text.split('').forEach((char, index) => {
            const angle = (index / text.length) * Math.PI * 2;
            const radius = 50 + Math.random() * 100;
            
            this.particles.push({
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius,
                char: char,
                vx: (Math.random() - 0.5) * 2,
                vy: (Math.random() - 0.5) * 2,
                size: 20 + Math.random() * 20,
                color: `hsl(${(index * 30) % 360}, 70%, 60%)`,
                alpha: 1
            });
        });

        this.startAnimation('text');
    }

    /**
     * Create color visualization
     * @param {string} hexColor - Hex color to visualize
     */
    createColorVisualization(hexColor) {
        if (!this.ctx) return;

        // Parse color
        const r = parseInt(hexColor.slice(1, 3), 16) || parseInt(hexColor.slice(1, 2) + hexColor.slice(1, 2), 16);
        const g = parseInt(hexColor.slice(3, 5), 16) || parseInt(hexColor.slice(2, 3) + hexColor.slice(2, 3), 16);
        const b = parseInt(hexColor.slice(5, 7), 16) || parseInt(hexColor.slice(3, 4) + hexColor.slice(3, 4), 16);

        this.particles = [];
        const particleCount = Math.floor(50 * this.intensity);

        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                radius: 5 + Math.random() * 20,
                color: `rgba(${r}, ${g}, ${b}, ${0.3 + Math.random() * 0.7})`,
                vx: (Math.random() - 0.5) * 3,
                vy: (Math.random() - 0.5) * 3,
                pulse: Math.random() * Math.PI * 2
            });
        }

        this.startAnimation('color');
    }

    /**
     * Create number visualization
     * @param {number} num - Number to visualize
     */
    createNumberVisualization(num) {
        if (!this.ctx) return;

        this.particles = [];
        const absNum = Math.abs(num);
        const patternSize = Math.min(absNum, 50);
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;

        // Create geometric pattern based on number
        for (let i = 0; i < patternSize; i++) {
            const angle = (i / patternSize) * Math.PI * 2 * (num % 7 + 1);
            const radius = 30 + (i * 3);
            
            this.particles.push({
                x: centerX,
                y: centerY,
                targetX: centerX + Math.cos(angle) * radius,
                targetY: centerY + Math.sin(angle) * radius,
                size: 3 + (absNum % 10),
                color: `hsl(${(num * 30) % 360}, 80%, 50%)`,
                progress: 0
            });
        }

        this.startAnimation('number');
    }

    /**
     * Start the animation loop
     * @param {string} type - Animation type
     */
    startAnimation(type) {
        this.stopAnimation();
        this.isAnimating = true;
        this.animationType = type;
        this.animate();
    }

    /**
     * Stop the animation
     */
    stopAnimation() {
        this.isAnimating = false;
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    /**
     * Animation loop
     */
    animate() {
        if (!this.isAnimating || !this.ctx) return;

        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        switch (this.animationType) {
            case 'text':
                this.animateTextParticles();
                break;
            case 'color':
                this.animateColorParticles();
                break;
            case 'number':
                this.animateNumberPattern();
                break;
        }

        this.animationId = requestAnimationFrame(() => this.animate());
    }

    /**
     * Animate text particles
     */
    animateTextParticles() {
        this.particles.forEach(p => {
            p.x += p.vx * (this.speed / 5);
            p.y += p.vy * (this.speed / 5);

            // Bounce off walls
            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;

            this.ctx.fillStyle = p.color;
            this.ctx.font = `${p.size}px Arial`;
            this.ctx.fillText(p.char, p.x, p.y);
        });
    }

    /**
     * Animate color particles
     */
    animateColorParticles() {
        this.particles.forEach(p => {
            p.x += p.vx * (this.speed / 5);
            p.y += p.vy * (this.speed / 5);
            p.pulse += 0.05 * this.speed;

            // Bounce off walls
            if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;

            const radius = p.radius + Math.sin(p.pulse) * 10 * this.intensity;

            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, Math.abs(radius), 0, Math.PI * 2);
            this.ctx.fillStyle = p.color;
            this.ctx.fill();
        });
    }

    /**
     * Animate number pattern
     */
    animateNumberPattern() {
        this.particles.forEach(p => {
            p.progress = Math.min(1, p.progress + 0.02 * this.speed);
            
            const currentX = p.x + (p.targetX - p.x) * p.progress;
            const currentY = p.y + (p.targetY - p.y) * p.progress;

            this.ctx.beginPath();
            this.ctx.arc(currentX, currentY, p.size * this.intensity, 0, Math.PI * 2);
            this.ctx.fillStyle = p.color;
            this.ctx.fill();

            // Connect particles
            if (p.progress >= 1) {
                this.ctx.beginPath();
                this.ctx.moveTo(p.x, p.y);
                this.ctx.lineTo(currentX, currentY);
                this.ctx.strokeStyle = p.color;
                this.ctx.lineWidth = 1;
                this.ctx.stroke();
            }
        });
    }

    /**
     * Clear the canvas
     */
    clear() {
        if (this.ctx) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
        this.particles = [];
        this.stopAnimation();
    }
}

// ============================================================================
// Main Application Controller
// ============================================================================

/**
 * SynesthesiaApp - Main application controller
 */
class SynesthesiaApp {
    constructor() {
        this.audioMapper = new AudioMapper();
        this.visualMapper = new VisualMapper('visualization-canvas');
        this.currentContent = null;
        this.currentType = null;
        
        this.initializeEventListeners();
        this.initializeSliders();
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // Experience button
        const experienceBtn = document.getElementById('experience-btn');
        if (experienceBtn) {
            experienceBtn.addEventListener('click', () => this.processInput());
        }

        // Input field - Enter key
        const contentInput = document.getElementById('content-input');
        if (contentInput) {
            contentInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.processInput();
                }
            });
        }

        // Grid items
        const gridItems = document.querySelectorAll('.grid-item');
        gridItems.forEach(item => {
            item.addEventListener('click', () => {
                const type = item.dataset.type;
                const value = item.dataset.value;
                this.experience({ type, value: type === 'number' ? parseFloat(value) : value });
            });

            item.addEventListener('mouseenter', () => {
                const type = item.dataset.type;
                const value = item.dataset.value;
                this.previewExperience({ type, value: type === 'number' ? parseFloat(value) : value });
            });
        });
    }

    /**
     * Initialize slider controls
     */
    initializeSliders() {
        // Volume slider
        const volumeSlider = document.getElementById('volume-slider');
        const volumeValue = document.getElementById('volume-value');
        if (volumeSlider && volumeValue) {
            volumeSlider.addEventListener('input', (e) => {
                const value = e.target.value;
                volumeValue.textContent = `${value}%`;
                this.audioMapper.setVolume(value / 100);
            });
        }

        // Speed slider
        const speedSlider = document.getElementById('speed-slider');
        const speedValue = document.getElementById('speed-value');
        if (speedSlider && speedValue) {
            speedSlider.addEventListener('input', (e) => {
                const value = e.target.value;
                speedValue.textContent = `${value}x`;
                this.visualMapper.setSpeed(parseInt(value));
            });
        }

        // Intensity slider
        const intensitySlider = document.getElementById('intensity-slider');
        const intensityValue = document.getElementById('intensity-value');
        if (intensitySlider && intensityValue) {
            intensitySlider.addEventListener('input', (e) => {
                const value = e.target.value;
                intensityValue.textContent = `${value}%`;
                this.visualMapper.setIntensity(value / 100);
            });
        }
    }

    /**
     * Process user input
     */
    processInput() {
        const inputElement = document.getElementById('content-input');
        if (!inputElement) return;

        const content = inputElement.value;
        const detected = detectContentType(content);
        
        if (detected.type !== 'unknown') {
            this.experience(detected);
        }
    }

    /**
     * Trigger the full experience for content
     * @param {object} contentData - Object with type and value
     */
    experience(contentData) {
        this.currentContent = contentData.value;
        this.currentType = contentData.type;

        // Initialize audio on first interaction
        this.audioMapper.initialize();

        // Update status display
        this.updateStatus(contentData);

        // Update content preview
        this.updateContentPreview(contentData);

        // Trigger audio and visual based on type
        let frequency = 0;
        switch (contentData.type) {
            case 'text':
                frequency = this.audioMapper.playTextSequence(contentData.value);
                this.visualMapper.createTextParticles(contentData.value);
                break;
            case 'color':
                const colorSound = this.audioMapper.colorToSound(contentData.value);
                frequency = this.audioMapper.playTone(colorSound.frequency, colorSound.waveform, 1);
                this.visualMapper.createColorVisualization(contentData.value);
                break;
            case 'number':
                const numSound = this.audioMapper.numberToSound(contentData.value);
                frequency = this.audioMapper.playTone(numSound.frequency, 'triangle', 0.8);
                this.visualMapper.createNumberVisualization(contentData.value);
                break;
        }

        // Update frequency display
        const freqDisplay = document.getElementById('current-frequency');
        if (freqDisplay && frequency) {
            freqDisplay.textContent = `${Math.round(frequency)} Hz`;
        }
    }

    /**
     * Preview experience on hover (lighter version)
     * @param {object} contentData - Object with type and value
     */
    previewExperience(contentData) {
        this.audioMapper.initialize();
        
        switch (contentData.type) {
            case 'text':
                const freq = this.audioMapper.charToFrequency(contentData.value);
                this.audioMapper.playTone(freq, 'sine', 0.1);
                break;
            case 'color':
                const colorSound = this.audioMapper.colorToSound(contentData.value);
                this.audioMapper.playTone(colorSound.frequency, colorSound.waveform, 0.1);
                break;
            case 'number':
                const numSound = this.audioMapper.numberToSound(contentData.value);
                this.audioMapper.playTone(numSound.frequency, 'triangle', 0.1);
                break;
        }
    }

    /**
     * Update the status display
     * @param {object} contentData - Content data object
     */
    updateStatus(contentData) {
        const typeDisplay = document.getElementById('detected-type');
        const effectDisplay = document.getElementById('active-effect');

        if (typeDisplay) {
            typeDisplay.textContent = contentData.type.charAt(0).toUpperCase() + contentData.type.slice(1);
        }

        if (effectDisplay) {
            const effects = {
                text: 'Musical Sequence',
                color: 'Ambient Waveform',
                number: 'Geometric Pattern'
            };
            effectDisplay.textContent = effects[contentData.type] || '-';
        }
    }

    /**
     * Update the content preview area
     * @param {object} contentData - Content data object
     */
    updateContentPreview(contentData) {
        const preview = document.getElementById('content-preview');
        if (!preview) return;

        let displayContent = '';
        let style = '';

        switch (contentData.type) {
            case 'text':
                displayContent = contentData.value;
                style = 'color: #a29bfe;';
                break;
            case 'color':
                displayContent = contentData.value;
                style = `color: ${contentData.value}; text-shadow: 0 0 30px ${contentData.value};`;
                break;
            case 'number':
                displayContent = contentData.value.toString();
                style = 'color: #00d9ff;';
                break;
        }

        preview.innerHTML = `<span class="content-display" style="${style}">${displayContent}</span>`;
    }
}

// ============================================================================
// Module Exports (for testing)
// ============================================================================

// Export functions and classes for Node.js testing environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        detectContentType,
        AudioMapper,
        VisualMapper,
        SynesthesiaApp
    };
}

// ============================================================================
// Initialize Application
// ============================================================================

// Initialize when DOM is ready (browser environment only)
if (typeof document !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        window.synesthesiaApp = new SynesthesiaApp();
    });
}
