/**
 * Interactive Force-Directed Graph for Lore-Web
 * Custom lightweight implementation
 */

class RelationGraph {
    constructor(containerId, data, options = {}) {
        this.container = document.getElementById(containerId);
        this.nodes = [];
        this.links = [];
        this.width = this.container.clientWidth;
        this.height = Math.max(600, window.innerHeight * 0.7);

        // Config
        this.options = {
            nodeRadius: 20,
            repulsionString: 300,
            attractionStrength: 0.05,
            centeringStrength: 0.02,
            damping: 0.8,
            ...options
        };

        // State
        this.hoveredNode = null;
        this.hoveredLink = null;
        this.draggedNode = null;
        this.filterPlayerId = null;

        // Setup Canvas
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.container.appendChild(this.canvas);

        // Tooltip container
        this.tooltipContainer = document.createElement('div');
        this.tooltipContainer.className = 'graph-tooltip-container';
        this.container.appendChild(this.tooltipContainer);

        // Resize observer
        this.resize();
        window.addEventListener('resize', () => this.resize());

        // Process data
        this.initData(data);

        // Start loop
        this.startSimulation();

        // Interactive events
        this.setupEvents();
    }

    resize() {
        this.width = this.container.clientWidth;
        // this.height = this.container.clientHeight || 600;
        this.canvas.width = this.width;
        this.canvas.height = this.height;
    }

    initData({ roles, relations }) {
        // Create Nodes
        const roleTypeX = {
            'agent': this.width * 0.2, // Left
            'admin': this.width * 0.5, // Center
            'user': this.width * 0.8   // Right
        };

        this.nodes = roles.map(r => ({
            id: r.id,
            name: r.name,
            type: r.type,
            avatar: r.avatar || 'avatar_user_male.png',
            archetype: r.archetype,
            ability: r.ability,
            x: roleTypeX[r.type] + (Math.random() - 0.5) * 100,
            y: this.height / 2 + (Math.random() - 0.5) * 200,
            vx: 0,
            vy: 0,
            radius: r.type === 'admin' ? 25 : 18
        }));

        // Node ID lookup
        const nodeMap = {};
        this.nodes.forEach(n => nodeMap[n.id] = n);

        // Create Links
        this.links = relations.map(r => ({
            source: nodeMap[r.source],
            target: nodeMap[r.target],
            type: r.type,
            data: r
        })).filter(l => l.source && l.target);
    }

    setupEvents() {
        // Mouse Move (Hover)
        this.canvas.addEventListener('mousemove', e => {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            if (this.draggedNode) {
                this.draggedNode.x = x;
                this.draggedNode.y = y;
                this.draggedNode.vx = 0;
                this.draggedNode.vy = 0;
                return;
            }

            // Detect Node Hover
            const prevHoverNode = this.hoveredNode;
            this.hoveredNode = this.nodes.find(n => {
                const dx = n.x - x;
                const dy = n.y - y;
                return Math.sqrt(dx * dx + dy * dy) < n.radius + 5;
            });

            // Detect Link Hover (distance to line segment)
            const prevHoverLink = this.hoveredLink;
            if (!this.hoveredNode) {
                this.hoveredLink = this.links.find(l => {
                    return this.distToSegment({ x, y }, l.source, l.target) < 5;
                });
            } else {
                this.hoveredLink = null;
            }

            if (this.hoveredNode !== prevHoverNode) {
                this.canvas.style.cursor = this.hoveredNode ? 'pointer' : 'default';
                this.renderTooltip();
            } else if (this.hoveredLink !== prevHoverLink) {
                this.renderTooltip();
            }
        });

        // Mouse Down (Drag Start)
        this.canvas.addEventListener('mousedown', e => {
            if (this.hoveredNode) {
                this.draggedNode = this.hoveredNode;
            }
        });

        // Mouse Up (Drag End)
        window.addEventListener('mouseup', () => {
            this.draggedNode = null;
        });
    }

    distToSegment(p, v, w) {
        const l2 = (v.x - w.x) ** 2 + (v.y - w.y) ** 2;
        if (l2 === 0) return Math.sqrt((p.x - v.x) ** 2 + (p.y - v.y) ** 2);
        let t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2;
        t = Math.max(0, Math.min(1, t));
        const px = v.x + t * (w.x - v.x);
        const py = v.y + t * (w.y - v.y);
        return Math.sqrt((p.x - px) ** 2 + (p.y - py) ** 2);
    }

    startSimulation() {
        const animate = () => {
            if (this.ctx) { // Safety check
                this.updatePhysics();
                this.draw();
            }
            requestAnimationFrame(animate);
        };
        animate();
    }

    updatePhysics() {
        // 1. Repulsion (Node-Node)
        for (let i = 0; i < this.nodes.length; i++) {
            for (let j = i + 1; j < this.nodes.length; j++) {
                const a = this.nodes[i];
                const b = this.nodes[j];
                const dx = a.x - b.x;
                const dy = a.y - b.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;

                if (dist < 200) {
                    const force = this.options.repulsionString / (dist * dist);
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    a.vx += fx;
                    a.vy += fy;
                    b.vx -= fx;
                    b.vy -= fy;
                }
            }
        }

        // 2. Attraction (Links)
        for (const link of this.links) {
            const dx = link.target.x - link.source.x;
            const dy = link.target.y - link.source.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;

            const force = (dist - 100) * this.options.attractionStrength; // 100 is optimal length
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;

            link.source.vx += fx;
            link.source.vy += fy;
            link.target.vx -= fx;
            link.target.vy -= fy;
        }

        // 3. Cluster / Centering Forces
        // Keep them roughly in their columns
        const roleTypeTargetX = {
            'agent': this.width * 0.2, // Left
            'admin': this.width * 0.5, // Center
            'user': this.width * 0.75   // Right (Adjusted from 0.8)
        };

        for (const node of this.nodes) {
            // Apply forces only if not dragged
            if (node === this.draggedNode) continue;

            // Pull towards cluster center X
            const targetX = roleTypeTargetX[node.type];
            node.vx += (targetX - node.x) * this.options.centeringStrength;

            // Allow vertical movement but keep within bounds loosely (soft center pull)
            if (node.y < 50) node.vy += 0.5;
            if (node.y > this.height - 50) node.vy -= 0.5;

            // Apply velocity with damping
            node.x += node.vx;
            node.y += node.vy;
            node.vx *= this.options.damping;
            node.vy *= this.options.damping;

            // Boundary constraints (Hard Walls)
            const margin = node.radius + 5;
            if (node.x < margin) { node.x = margin; node.vx *= -0.5; }
            if (node.x > this.width - margin) { node.x = this.width - margin; node.vx *= -0.5; }
            if (node.y < margin) { node.y = margin; node.vy *= -0.5; }
            if (node.y > this.height - margin) { node.y = this.height - margin; node.vy *= -0.5; }
        }
    }

    getLinkColor(type) {
        const colors = {
            'past': '#9c27b0', // Purple
            'trade': '#4caf50', // Green
            'blackmail': '#ef5350', // Red
            'romance': '#e91e63', // Pink
            'plot': '#ff9800', // Orange
            'empathy': '#4a9eff', // Blue
            'rival': '#f44336', // Bright Red
            'investigation': '#00bcd4' // Cyan
        };
        return colors[type] || '#d4af37';
    }

    getNodeColor(type) {
        const colors = {
            'user': '#4a9eff',
            'agent': '#e91e63',
            'admin': '#d4af37'
        };
        return colors[type] || '#666';
    }

    draw() {
        this.ctx.clearRect(0, 0, this.width, this.height);

        // --- Draw Links ---
        this.ctx.lineWidth = 2;
        for (const link of this.links) {
            // Determine visibility/opacity
            let opacity = 0.3;
            let width = 1.5;

            if (this.filterPlayerId) {
                // Filter mode: Highlighting specific connections
                const isRelevant = link.source.id === this.filterPlayerId || link.target.id === this.filterPlayerId;
                if (!isRelevant) {
                    opacity = 0.05; // Fade out irrelevant
                } else {
                    opacity = 0.8;
                    width = 3;
                }
            } else if (this.hoveredNode) {
                // Hover node mode
                const isConnected = link.source === this.hoveredNode || link.target === this.hoveredNode;
                if (isConnected) {
                    opacity = 0.8;
                    width = 3;
                } else {
                    opacity = 0.1;
                }
            } else if (this.hoveredLink === link) {
                // Hover link mode
                opacity = 1.0;
                width = 4;
            }

            this.ctx.beginPath();
            this.ctx.moveTo(link.source.x, link.source.y);
            this.ctx.lineTo(link.target.x, link.target.y);
            this.ctx.strokeStyle = this.getLinkColor(link.type);
            this.ctx.globalAlpha = opacity;
            this.ctx.lineWidth = width;
            this.ctx.stroke();
        }

        // --- Draw Nodes ---
        this.ctx.globalAlpha = 1.0;

        // Draw column labels (under nodes)
        this.ctx.font = 'bold 14px Inter';
        this.ctx.fillStyle = '#ffffff';
        this.ctx.textAlign = 'center';
        this.ctx.globalAlpha = 0.1;
        this.ctx.fillText('AGENTI', this.width * 0.2, 30);
        this.ctx.fillText('SPRÁVCI', this.width * 0.5, 30);
        this.ctx.fillText('UŽIVATELÉ', this.width * 0.75, 30);
        this.ctx.globalAlpha = 1.0;

        for (const node of this.nodes) {
            let opacity = 1.0;
            // Filter dimming
            if (this.filterPlayerId) {
                const isSelf = node.id === this.filterPlayerId;
                const isNeighbor = this.links.some(l =>
                    (l.source.id === this.filterPlayerId && l.target === node) ||
                    (l.target.id === this.filterPlayerId && l.source === node)
                );

                if (!isSelf && !isNeighbor) {
                    opacity = 0.2;
                }
            } else if (this.hoveredNode && this.hoveredNode !== node) {
                // Dim non-neighbors on hover
                const isNeighbor = this.links.some(l =>
                    (l.source === this.hoveredNode && l.target === node) ||
                    (l.target === this.hoveredNode && l.source === node)
                );
                if (!isNeighbor) opacity = 0.2;
            }

            this.ctx.globalAlpha = opacity;

            // Halo selection
            if (node === this.hoveredNode || node.id === this.filterPlayerId) {
                this.ctx.beginPath();
                this.ctx.arc(node.x, node.y, node.radius + 6, 0, Math.PI * 2);
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
                this.ctx.fill();
            }

            // Node Circle
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = '#1a1a2e'; // inner bg
            this.ctx.fill();
            this.ctx.lineWidth = 2;
            this.ctx.strokeStyle = this.getNodeColor(node.type);
            this.ctx.stroke();

            // Label (Name) - show if visible enough
            if (opacity > 0.5) {
                this.ctx.fillStyle = '#fff';
                this.ctx.font = '10px Inter';
                this.ctx.textAlign = 'center';
                this.ctx.fillText(node.name, node.x, node.y + node.radius + 15);
            }
        }

        this.ctx.globalAlpha = 1.0;
    }

    async renderTooltip() {
        if (!this.hoveredNode && !this.hoveredLink) {
            this.tooltipContainer.innerHTML = '';
            this.tooltipContainer.style.display = 'none';
            return;
        }

        this.tooltipContainer.style.display = 'block';

        let x, y, data;

        if (this.hoveredNode) {
            // Position near node
            x = this.hoveredNode.x + 20;
            y = this.hoveredNode.y - 20;

            data = {
                type: this.hoveredNode.type,
                avatar: this.hoveredNode.avatar,
                name: this.hoveredNode.name,
                id: this.hoveredNode.id,
                archetype: this.hoveredNode.archetype,
                ability_short: this.hoveredNode.ability ? this.hoveredNode.ability.substring(0, 60) + '...' : ''
            };

            if (window.fillTemplate && window.templates && window.templates.node_tooltip) {
                this.tooltipContainer.innerHTML = window.fillTemplate(window.templates.node_tooltip, data);
            } else {
                this.tooltipContainer.innerHTML = `<div>${data.name}</div>`;
            }

        } else if (this.hoveredLink) {
            x = (this.hoveredLink.source.x + this.hoveredLink.target.x) / 2 + 10;
            y = (this.hoveredLink.source.y + this.hoveredLink.target.y) / 2 - 10;

            const typeLabel = window.getRelTypeLabel ? window.getRelTypeLabel(this.hoveredLink.type) : this.hoveredLink.type.toUpperCase();

            data = {
                type: this.hoveredLink.type,
                type_label: typeLabel,
                source_name: this.hoveredLink.source.name,
                target_name: this.hoveredLink.target.name,
                desc_source: this.hoveredLink.data.desc_source || '',
                desc_target: this.hoveredLink.data.desc_target || ''
            };

            if (window.fillTemplate && window.templates && window.templates.relation_tooltip) {
                this.tooltipContainer.innerHTML = window.fillTemplate(window.templates.relation_tooltip, data);
            }
        }

        // Smart Clamping to Viewport to prevent "ustřelí" (shooting off) or invisible tooltips
        const tooltipRect = this.tooltipContainer.getBoundingClientRect();

        // If x + width > container width, shift left
        if (x + tooltipRect.width > this.width) {
            x = (this.hoveredNode ? this.hoveredNode.x : x) - tooltipRect.width - 20;
        }

        // If y + height > container height, shift up
        if (y + tooltipRect.height > this.height) {
            y = (this.hoveredNode ? this.hoveredNode.y : y) - tooltipRect.height - 20;
        }

        // Hard clamps to ensure it never leaves the box
        x = Math.max(10, Math.min(this.width - tooltipRect.width - 10, x));
        y = Math.max(10, Math.min(this.height - tooltipRect.height - 10, y));

        this.tooltipContainer.style.left = `${x}px`;
        this.tooltipContainer.style.top = `${y}px`;
    }

    setFilter(playerId) {
        this.filterPlayerId = playerId === 'all' ? null : playerId;
    }
}
