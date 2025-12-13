class SoundEngine {
    constructor() {
        this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        this.enabled = true;
        this.masterVolume = 0.3;
    }

    enable() {
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
        this.enabled = true;
    }

    disable() {
        this.enabled = false;
    }

    // Basic oscillator beep
    playTone(freq, type, duration, vol) {
        if (!this.enabled) return;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

        gain.gain.setValueAtTime(vol * this.masterVolume, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + duration);

        osc.connect(gain);
        gain.connect(this.ctx.destination);

        osc.start();
        osc.stop(this.ctx.currentTime + duration);
    }

    playType() {
        // High pitched click
        this.playTone(800, 'square', 0.05, 0.1);
    }

    playReceive() {
        // Double beep
        this.playTone(1200, 'sine', 0.1, 0.2);
        setTimeout(() => this.playTone(1600, 'sine', 0.2, 0.2), 100);
    }

    playSend() {
        // Low confirmation
        this.playTone(400, 'triangle', 0.1, 0.2);
    }

    playError() {
        // Buzz
        this.playTone(150, 'sawtooth', 0.3, 0.4);
    }

    playGlitch() {
        // Random noise-like
        const freq = Math.random() * 1000 + 100;
        this.playTone(freq, 'sawtooth', 0.1, 0.1);
    }
}

const sfx = new SoundEngine();

// Enable audio on first interaction
document.addEventListener('click', () => sfx.enable(), { once: true });
document.addEventListener('keydown', () => sfx.enable(), { once: true });
