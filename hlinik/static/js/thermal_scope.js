/**
 * ThermalScope - 60s Sci-Fi Analog Particle Simulation
 * Visualizes system temperature through particle dynamics.
 */
class ThermalScope {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`ThermalScope: Canvas #${canvasId} not found`);
            return;
        }
        this.ctx = this.canvas.getContext('2d');

        // Physics State
        this.temperature = 20; // Default
        this.particles = [];
        this.maxParticles = 150;
        this.animationFrame = null;

        // Visual Params (Dynamic)
        this.speedMult = 1.0;
        this.wobble = 0.0;
        this.coreColor = [100, 200, 255]; // R, G, B
        this.baseRadius = 2;

        this.resize();
        window.addEventListener('resize', () => this.resize());

        this.initParticles();
        this.start();
    }

    resize() {
        if (!this.canvas.parentElement) return;
        this.canvas.width = this.canvas.parentElement.offsetWidth;
        this.canvas.height = this.canvas.parentElement.offsetHeight;
        this.cx = this.canvas.width / 2;
        this.cy = this.canvas.height / 2;
    }

    setTemperature(temp) {
        this.temperature = temp;
        // Map temp (20 - 400) to visual params

        if (temp < 100) {
            // COLD / NORMAL
            this.speedMult = 0.5 + (temp / 100) * 0.5; // 0.5 -> 1.0
            this.coreColor = [0, 255, 255]; // Cyan
            this.wobble = 0.2;
        } else if (temp < 300) {
            // WARM / HOT
            this.speedMult = 1.0 + ((temp - 100) / 200) * 2.0; // 1.0 -> 3.0
            this.coreColor = [255, 200, 50]; // Gold/Orange
            this.wobble = 0.5 + ((temp - 100) / 200) * 1.0;
        } else {
            // CRITITAL
            this.speedMult = 3.0 + ((temp - 300) / 100) * 3.0; // 3.0 -> 6.0!
            this.coreColor = [255, 50, 50]; // Red
            this.wobble = 2.0 + ((temp - 300) / 100) * 5.0; // Violent shaking
        }
    }

    initParticles() {
        this.particles = [];
        for (let i = 0; i < this.maxParticles; i++) {
            this.particles.push(this.createParticle(true));
        }
    }

    createParticle(randomStart = false) {
        const angle = Math.random() * Math.PI * 2;
        // Start either randomly in the area or at center
        const r = randomStart ? Math.random() * 100 : 0;

        return {
            x: this.cx + Math.cos(angle) * r,
            y: this.cy + Math.sin(angle) * r,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            life: Math.random() * 0.5 + 0.5, // 0.5 - 1.0
            size: Math.random() * 2 + 1,
            angle: angle,
            orbitalV: (Math.random() * 0.02 + 0.01) * (Math.random() > 0.5 ? 1 : -1)
        };
    }

    update() {
        // Clear with trails (Ghosting effect)
        this.ctx.fillStyle = 'rgba(10, 20, 30, 0.2)'; // Dark blue-ish fade
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Shake Context if critical
        this.ctx.save();
        if (this.temperature > 320) {
            const shake = Math.random() * (this.temperature - 300) * 0.05;
            this.ctx.translate((Math.random() - 0.5) * shake, (Math.random() - 0.5) * shake);
        }

        // Draw Core
        const coreSize = 10 + (this.temperature / 400) * 20 + Math.sin(Date.now() / 200) * 2;
        const [r, g, b] = this.coreColor;

        // Dynamic Core Gradient
        const gradient = this.ctx.createRadialGradient(this.cx, this.cy, 0, this.cx, this.cy, coreSize * 3);
        gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, 1)`);
        gradient.addColorStop(0.2, `rgba(${r}, ${g}, ${b}, 0.5)`);
        gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);

        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        this.ctx.arc(this.cx, this.cy, coreSize * 3, 0, Math.PI * 2);
        this.ctx.fill();

        // Update Particles
        this.particles.forEach(p => {
            // Orbital mechanics + Thermal Expansion
            const dx = p.x - this.cx;
            const dy = p.y - this.cy;
            const dist = Math.sqrt(dx * dx + dy * dy);

            // Repulsion force (Heat expansion)
            const repulsion = (this.temperature / 800) * 2.0;

            // Orbital Rotation
            const ca = Math.cos(p.orbitalV * this.speedMult);
            const sa = Math.sin(p.orbitalV * this.speedMult);

            // Apply Rotation
            let nx = dx * ca - dy * sa;
            let ny = dx * sa + dy * ca;

            // Apply Repulsion/Velocity
            nx += nx * (repulsion * 0.05); // Push out
            ny += ny * (repulsion * 0.05);

            // Add jitter/Brownian motion based on temp
            nx += (Math.random() - 0.5) * this.wobble;
            ny += (Math.random() - 0.5) * this.wobble;

            p.x = this.cx + nx;
            p.y = this.cy + ny;

            p.life -= 0.005 * this.speedMult;

            // Reset if dead or out of bounds
            if (p.life <= 0 || dist > Math.min(this.canvas.width, this.canvas.height) / 2) {
                // Respawn near center
                const angle = Math.random() * Math.PI * 2;
                const r = Math.random() * 20;
                p.x = this.cx + Math.cos(angle) * r;
                p.y = this.cy + Math.sin(angle) * r;
                p.life = 1.0;
            }

            // Draw Particle
            const alpha = p.life;
            this.ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size * (1 + this.temperature / 200), 0, Math.PI * 2);
            this.ctx.fill();
        });

        // Scanlines Overlay
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        for (let y = 0; y < this.canvas.height; y += 4) {
            this.ctx.fillRect(0, y, this.canvas.width, 2);
        }

        // Circular Mask (Scope look)
        this.ctx.restore(); // Undo shake for mask

        // Bezel / Vignette
        const outerRadius = Math.min(this.canvas.width, this.canvas.height) / 2;

        // Clear corners to make it round visually (optional, or just do overlay)
        // Let's do a strong vignette instead
        const vignette = this.ctx.createRadialGradient(this.cx, this.cy, outerRadius * 0.8, this.cx, this.cy, outerRadius);
        vignette.addColorStop(0, 'rgba(0,0,0,0)');
        vignette.addColorStop(1, 'rgba(0,0,0,1)');

        this.ctx.fillStyle = vignette;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Crosshair
        this.ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, 0.3)`;
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.moveTo(this.cx - 20, this.cy);
        this.ctx.lineTo(this.cx + 20, this.cy);
        this.ctx.moveTo(this.cx, this.cy - 20);
        this.ctx.lineTo(this.cx, this.cy + 20);
        this.ctx.stroke();
    }

    start() {
        const loop = () => {
            this.update();
            this.animationFrame = requestAnimationFrame(loop);
        };
        loop();
        console.log("ThermalScope started");
    }

    stop() {
        if (this.animationFrame) cancelAnimationFrame(this.animationFrame);
    }
}
