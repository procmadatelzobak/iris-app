/**
 * Economy Sensor - Visualization of Wealth Distribution
 * 8 User Orbs in a "Nebula".
 * Particles flow to/from users based on transactions.
 */
class EconomySensor {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('EconomySensor: Canvas not found');
            return;
        }
        this.ctx = this.canvas.getContext('2d');

        // State
        this.users = new Map(); // id -> { credit, x, y, r, targetR }
        this.particles = [];
        this.fog = [];

        this.resize();
        window.addEventListener('resize', () => this.resize());

        this.initUsers();
        this.initFog();

        // Loop
        this.running = false;
        this.start();
    }

    resize() {
        if (!this.canvas.parentElement) return;
        this.canvas.width = this.canvas.parentElement.offsetWidth;
        this.canvas.height = this.canvas.parentElement.offsetHeight;
        this.cx = this.canvas.width / 2;
        this.cy = this.canvas.height / 2;

        // Re-position users in a circle
        this.updateUserPositions();
    }

    initUsers() {
        for (let i = 1; i <= 8; i++) {
            this.users.set(i, {
                id: i,
                credits: 1000,
                displayCredits: 1000,
                x: 0, y: 0,
                r: 10,
                color: [100, 100, 100], // RGB
                pulse: Math.random() * Math.PI
            });
        }
        this.updateUserPositions();
    }

    updateUserPositions() {
        const radius = Math.min(this.cx, this.cy) * 0.7;
        let idx = 0;
        this.users.forEach(u => {
            const angle = (idx / 8) * Math.PI * 2;
            u.x = this.cx + Math.cos(angle) * radius;
            u.y = this.cy + Math.sin(angle) * radius;
            idx++;
        });
    }

    initFog() {
        this.fog = [];
        for (let i = 0; i < 50; i++) {
            this.fog.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.2,
                vy: (Math.random() - 0.5) * 0.2,
                size: Math.random() * 50 + 20,
                life: Math.random()
            });
        }
    }

    updateData(userList) {
        // userList: [{id: 1, credits: 1200}, ...]
        // console.log("EcoSensor Update:", userList);
        userList.forEach(apiUser => {
            const uid = parseInt(apiUser.id);
            const u = this.users.get(uid);
            if (u) {
                const diff = apiUser.credits - u.credits;
                if (Math.abs(diff) > 0) {
                    console.log(`Transaction for User ${uid}: ${diff}`);
                    this.spawnTransactionParticles(u, diff);
                    this.triggerPulse(u, diff);
                }
                // Always sync target credits
                u.credits = apiUser.credits;
            }
        });
    }

    triggerPulse(user, amount) {
        // Shake / Flash effect
        user.pulseSpeed = 0.5; // Speed up pulse
        user.r_anim = 10; // Temporary radius boost
    }

    spawnTransactionParticles(user, amount) {
        const count = Math.min(50, Math.abs(amount) / 10 + 5);
        const isIncome = amount > 0;

        for (let i = 0; i < count; i++) {
            // Income: Center -> User
            // Expense: User -> Center (or void)
            const p = {
                x: isIncome ? this.cx : user.x,
                y: isIncome ? this.cy : user.y,
                targetX: isIncome ? user.x : this.cx,
                targetY: isIncome ? user.y : this.cy,
                progress: 0,
                speed: Math.random() * 0.02 + 0.01,
                color: isIncome ? [255, 255, 200] : [255, 50, 50],
                size: Math.random() * 3 + 1,
                jitter: Math.random() * 20 - 10
            };
            this.particles.push(p);
        }
    }

    getCreditColor(credits) {
        // Black (0) -> Red -> Orange -> Yellow -> Green -> Blue -> White (>5000)
        if (credits <= 0) return [20, 0, 0];    // Near Black/Red
        if (credits < 500) return [100, 0, 0];  // Dark Red
        if (credits < 1000) return [200, 50, 0]; // Red-Orange
        if (credits < 2000) return [255, 150, 0]; // Orange
        if (credits < 3000) return [255, 255, 0]; // Yellow
        if (credits < 4000) return [0, 255, 0];  // Green
        if (credits < 5000) return [0, 100, 255]; // Blue
        return [255, 255, 255]; // White (Rich)
    }

    update() {
        // Draw Background (Nebula)
        this.ctx.fillStyle = '#020502';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Update Fog (Ambient)
        this.fog.forEach(f => {
            f.x += f.vx;
            f.y += f.vy;
            if (f.x < -100) f.x = this.canvas.width + 100;
            if (f.x > this.canvas.width + 100) f.x = -100;
            if (f.y < -100) f.y = this.canvas.height + 100;
            if (f.y > this.canvas.height + 100) f.y = -100;

            // Simple radial glow
            const g = this.ctx.createRadialGradient(f.x, f.y, 0, f.x, f.y, f.size);
            g.addColorStop(0, 'rgba(0, 50, 20, 0.05)');
            g.addColorStop(1, 'rgba(0,0,0,0)');
            this.ctx.fillStyle = g;
            this.ctx.beginPath();
            this.ctx.arc(f.x, f.y, f.size, 0, Math.PI * 2);
            this.ctx.fill();
        });

        // Update Users (Orbs)
        this.users.forEach(u => {
            // Lerp Display Credits
            u.displayCredits += (u.credits - u.displayCredits) * 0.05;

            // Calc Color
            const targetColor = this.getCreditColor(u.displayCredits);
            // Lerp color
            u.color = u.color.map((c, i) => c + (targetColor[i] - c) * 0.05);

            // Pulse
            if (u.pulseSpeed) {
                u.pulse += u.pulseSpeed;
                u.pulseSpeed *= 0.95; // decay
                if (u.pulseSpeed < 0.05) u.pulseSpeed = 0.05;
            } else {
                u.pulse += 0.05;
            }

            if (u.r_anim) {
                u.r_anim *= 0.9;
                if (u.r_anim < 0.1) u.r_anim = 0;
            }

            const pulseSize = Math.sin(u.pulse) * 3 + (u.r_anim || 0);

            // Base size based on credits
            const baseR = 15 + Math.sqrt(Math.max(0, u.displayCredits)) * 0.4;
            const r = baseR + pulseSize;

            // Draw Orb
            const [cr, cg, cb] = u.color.map(Math.round);

            // Glow
            this.ctx.shadowColor = `rgb(${cr},${cg},${cb})`;
            this.ctx.shadowBlur = 20;

            const grad = this.ctx.createRadialGradient(u.x, u.y, r * 0.2, u.x, u.y, r);
            grad.addColorStop(0, `rgb(${Math.min(255, cr + 100)}, ${Math.min(255, cg + 100)}, ${Math.min(255, cb + 100)})`);
            grad.addColorStop(0.6, `rgb(${cr}, ${cg}, ${cb})`);
            grad.addColorStop(1, `rgba(${cr}, ${cg}, ${cb}, 0)`);

            this.ctx.fillStyle = grad;
            this.ctx.beginPath();
            this.ctx.arc(u.x, u.y, r, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.shadowBlur = 0;

            // Label
            this.ctx.fillStyle = '#fff';
            this.ctx.font = 'bold 12px monospace';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(`USER ${u.id}`, u.x, u.y + r + 15);
            this.ctx.font = '10px monospace';
            this.ctx.fillStyle = '#aaa';
            this.ctx.fillText(Math.round(u.displayCredits) + " CR", u.x, u.y + r + 26);
        });

        // Update Particles (Transactions)
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.progress += p.speed;

            if (p.progress >= 1) {
                this.particles.splice(i, 1);
                continue;
            }

            // Bezier-ish path with jitter
            const cx = p.targetX - p.x;
            const cy = p.targetY - p.y;

            // Current pos
            const currX = p.x + cx * p.progress + Math.sin(p.progress * Math.PI * 4) * p.jitter * (1 - p.progress);
            const currY = p.y + cy * p.progress + Math.cos(p.progress * Math.PI * 4) * p.jitter * (1 - p.progress);

            const [pr, pg, pb] = p.color;
            this.ctx.fillStyle = `rgb(${pr}, ${pg}, ${pb})`;
            this.ctx.beginPath();
            this.ctx.arc(currX, currY, p.size, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }

    start() {
        this.running = true;
        const loop = () => {
            if (!this.running) return;
            this.update();
            requestAnimationFrame(loop);
        };
        loop();
    }

    stop() {
        this.running = false;
    }
}
