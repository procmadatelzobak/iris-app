/**
 * Interactive Force-Directed Graph for Lore-Web
 * Custom lightweight implementation - FIXED VERSION
 */

class RelationGraph {
    constructor(containerId, data, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error('Graph container not found:', containerId);
            return;
        }

        this.nodes = [];
        this.links = [];

        // Get actual dimensions
        this.width = this.container.clientWidth || 800;
        this.height = 550; // Fixed height for stability

        // Config - TUNED for stability
        this.options = {
            nodeRadius: 20,
            repulsionStrength: 150, // Reduced
            attractionStrength: 0.02, // Reduced
            centeringStrength: 0.05, // Increased to keep in columns
            damping: 0.85, // Higher damping = less jitter
            ...options
        };

        // State
        this.hoveredNode = null;
        this.hoveredLink = null;
        this.draggedNode = null;
        this.filterPlayerId = null;
        this.isDragging = false;
        this.dragStartPos = null;
        this.simulationCooled = false;
        this.tickCount = 0;

        // Setup Canvas
        this.canvas = document.createElement('canvas');
        this.canvas.width = this.width;
        this.canvas.height = this.height;
        this.canvas.style.display = 'block';
        this.ctx = this.canvas.getContext('2d');
        this.container.innerHTML = ''; // Clear container
        this.container.appendChild(this.canvas);

        // Tooltip container (fixed position, appended to body)
        this.tooltipContainer = document.createElement('div');
        this.tooltipContainer.className = 'graph-tooltip-container';
        this.tooltipContainer.style.position = 'fixed';
        this.tooltipContainer.style.zIndex = '9999';
        this.tooltipContainer.style.pointerEvents = 'none';
        this.tooltipContainer.style.display = 'none';
        document.body.appendChild(this.tooltipContainer);

        // Process data
        this.initData(data);

        // Interactive events
        this.setupEvents();

        // Start loop
        this.startSimulation();

        // Resize handler
        window.addEventListener('resize', () => this.handleResize());
    }

    handleResize() {
        const newWidth = this.container.clientWidth;
        if (newWidth !== this.width && newWidth > 0) {
            this.width = newWidth;
            this.canvas.width = this.width;
            // Re-position nodes to new width proportionally
            this.nodes.forEach(node => {
                const ratio = node.x / (this.canvas.width || this.width);
                node.x = ratio * this.width;
            });
        }
    }

    initData({ roles, relations }) {
        if (!roles || !relations) {
            console.error('Invalid data for graph');
            return;
        }

        // Zones:
        // Admins: Top Center
        // Agents: Bottom Left
        // Users: Bottom Right

        const agents = roles.filter(r => r.type === 'agent');
        const admins = roles.filter(r => r.type === 'admin');
        const users = roles.filter(r => r.type === 'user');

        const colWidth = this.width / 4;

        // Helper to position nodes in a specific area
        const positionCluster = (rolesList, centerX, centerY, widthSpread, heightSpread) => {
            const count = rolesList.length;
            // Use golden angle for organic distribution if it's a blob, but here user wants specific zones.
            // Let's use a loose grid/cloud around the center.

            return rolesList.map((r, i) => {
                // Distribute items to avoid initial overlap
                const angle = i * (Math.PI * 2 / Math.max(count, 1)) + (Math.random() * 0.5);
                const radius = 30 + Math.random() * 40; // Base spread

                // For better spacing, we can just use random within box but check overlap? 
                // Simple random with grid logic is faster.
                // Let's vary Y more for "better spacing"

                const offsetX = (Math.random() - 0.5) * widthSpread;
                const offsetY = (Math.random() - 0.5) * heightSpread;

                return {
                    id: r.id,
                    name: r.name,
                    type: r.type,
                    avatar: r.avatar || 'avatar_user_male.png',
                    archetype: r.archetype || '',
                    ability: r.ability || '',
                    x: centerX + offsetX,
                    y: centerY + offsetY,
                    vx: 0,
                    vy: 0,
                    radius: 10 // Smaller nodes
                };
            });
        };

        // Define zones (Top=20%, Bottom=75%)
        const topY = this.height * 0.25;
        const bottomY = this.height * 0.75;

        // Horizontal centers (keep same)
        const leftX = colWidth * 0.8;
        const centerX = colWidth * 2;
        const rightX = colWidth * 3.2;

        this.nodes = [
            ...positionCluster(agents, leftX, bottomY, 150, 150),
            ...positionCluster(admins, centerX, topY, 200, 100), // Admins spread wider horizontally
            ...positionCluster(users, rightX, bottomY, 150, 150)
        ];

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
        // Mouse Move (Hover + Drag)
        this.canvas.addEventListener('mousemove', e => {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            if (this.draggedNode) {
                // Track if actually dragging (moved more than 5px)
                if (this.dragStartPos) {
                    const dx = Math.abs(x - this.dragStartPos.x);
                    const dy = Math.abs(y - this.dragStartPos.y);
                    if (dx > 5 || dy > 5) {
                        this.isDragging = true;
                    }
                }

                // Constrain dragged node to bounds
                const margin = this.draggedNode.radius + 5;
                this.draggedNode.x = Math.max(margin, Math.min(this.width - margin, x));
                this.draggedNode.y = Math.max(margin, Math.min(this.height - margin, y));
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

            // Detect Link Hover
            const prevHoverLink = this.hoveredLink;
            if (!this.hoveredNode) {
                this.hoveredLink = this.links.find(l => {
                    return this.distToSegment({ x, y }, l.source, l.target) < 8;
                });
            } else {
                this.hoveredLink = null;
            }

            // Update cursor and tooltip
            if (this.hoveredNode !== prevHoverNode || this.hoveredLink !== prevHoverLink) {
                this.canvas.style.cursor = (this.hoveredNode || this.hoveredLink) ? 'pointer' : 'default';
                this.renderTooltip(e);
            }
        });

        // Mouse Down (Drag Start)
        this.canvas.addEventListener('mousedown', e => {
            const rect = this.canvas.getBoundingClientRect();
            this.dragStartPos = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
            this.isDragging = false;

            if (this.hoveredNode) {
                this.draggedNode = this.hoveredNode;
                e.preventDefault();
            }
        });

        // Mouse Up (Drag End + Click detection)
        this.canvas.addEventListener('mouseup', e => {
            this.draggedNode = null;
            this.dragStartPos = null;
        });

        // Click handler for briefing
        this.canvas.addEventListener('click', e => {
            // Only trigger on click, not on drag
            if (this.isDragging) {
                this.isDragging = false;
                return;
            }

            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            // Check node click
            const clickedNode = this.nodes.find(n => {
                const dx = n.x - x;
                const dy = n.y - y;
                return Math.sqrt(dx * dx + dy * dy) < n.radius + 5;
            });

            if (clickedNode) {
                // Call global showBriefing function
                if (typeof showBriefing === 'function') {
                    showBriefing(clickedNode.id);
                }
                return;
            }

            // Check link click
            const clickedLink = this.links.find(l => {
                return this.distToSegment({ x, y }, l.source, l.target) < 8;
            });

            if (clickedLink) {
                // Show relation info
                this.showRelationInfo(clickedLink);
            }
        });

        // Mouse leave - hide tooltip
        this.canvas.addEventListener('mouseleave', () => {
            this.hoveredNode = null;
            this.hoveredLink = null;
            this.tooltipContainer.style.display = 'none';
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

    getLinkColor(type) {
        const colors = {
            'past': '#9c27b0',
            'trade': '#4caf50',
            'blackmail': '#ef5350',
            'romance': '#e91e63',
            'plot': '#ff9800',
            'empathy': '#4a9eff',
            'rival': '#f44336',
            'investigation': '#00bcd4'
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

    startSimulation() {
        const animate = () => {
            this.tickCount++;

            // Only update physics if not fully cooled
            if (!this.simulationCooled) {
                this.updatePhysics();
            }

            this.draw();
            requestAnimationFrame(animate);
        };
        animate();
    }

    updatePhysics() {
        let totalVelocity = 0;

        // 1. Repulsion (Node-Node)
        for (let i = 0; i < this.nodes.length; i++) {
            for (let j = i + 1; j < this.nodes.length; j++) {
                const a = this.nodes[i];
                const b = this.nodes[j];
                const dx = a.x - b.x;
                const dy = a.y - b.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;

                // Increased interaction radius for better spread
                if (dist < 280) { // Even wider range
                    const force = (this.options.repulsionStrength * 4.0) / (dist * dist); // Very strong repulsion
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

            const optimalDist = 120;
            const force = (dist - optimalDist) * this.options.attractionStrength;
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;

            link.source.vx += fx;
            link.source.vy += fy;
            link.target.vx -= fx;
            link.target.vy -= fy;
        }

        // 3. Zonal Gravity (Admins=Top, Others=Bottom)
        const colWidth = this.width / 4;
        const topY = this.height * 0.25;
        const bottomY = this.height * 0.75;

        const targets = {
            'agent': { x: colWidth * 0.8, y: bottomY },
            'admin': { x: colWidth * 2, y: topY },
            'user': { x: colWidth * 3.2, y: bottomY }
        };

        for (const node of this.nodes) {
            if (node === this.draggedNode) continue;

            const target = targets[node.type];

            // Horizontal and vertical pull
            node.vx += (target.x - node.x) * this.options.centeringStrength;
            node.vy += (target.y - node.y) * this.options.centeringStrength;

            // Apply velocity with damping
            node.x += node.vx;
            node.y += node.vy;
            node.vx *= this.options.damping;
            node.vy *= this.options.damping;

            // Boundary constraints
            const margin = node.radius + 8;
            node.x = Math.max(margin, Math.min(this.width - margin, node.x));
            node.y = Math.max(margin, Math.min(this.height - margin, node.y));

            totalVelocity += Math.abs(node.vx) + Math.abs(node.vy);
        }

        // Cool down after settling
        if (this.tickCount > 150 && totalVelocity < 0.5) {
            this.simulationCooled = true;
        }
    }

    draw() {
        this.ctx.clearRect(0, 0, this.width, this.height);

        // Background
        this.ctx.fillStyle = 'rgba(26, 26, 46, 0.3)';
        this.ctx.fillRect(0, 0, this.width, this.height);

        // Column labels
        this.ctx.font = 'bold 12px Inter, sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
        const colWidth = this.width / 5;
        this.ctx.fillText('AGENTI', colWidth * 1, 25);
        this.ctx.fillText('SPRÁVCI', colWidth * 2.5, 25);
        this.ctx.fillText('UŽIVATELÉ', colWidth * 4, 25);

        // Draw Links
        for (const link of this.links) {
            let opacity = 0.4;
            let lineWidth = 1.5;

            if (this.filterPlayerId) {
                const isRelevant = link.source.id === this.filterPlayerId || link.target.id === this.filterPlayerId;
                opacity = isRelevant ? 0.9 : 0.08;
                lineWidth = isRelevant ? 3 : 1;
            } else if (this.hoveredNode) {
                const isConnected = link.source === this.hoveredNode || link.target === this.hoveredNode;
                opacity = isConnected ? 0.9 : 0.1;
                lineWidth = isConnected ? 3 : 1;
            } else if (this.hoveredLink === link) {
                opacity = 1.0;
                lineWidth = 4;
            }

            this.ctx.beginPath();
            this.ctx.moveTo(link.source.x, link.source.y);
            this.ctx.lineTo(link.target.x, link.target.y);
            this.ctx.strokeStyle = this.getLinkColor(link.type);
            this.ctx.globalAlpha = opacity;
            this.ctx.lineWidth = lineWidth;
            this.ctx.stroke();
        }

        this.ctx.globalAlpha = 1.0;

        // Draw Nodes
        for (const node of this.nodes) {
            let opacity = 1.0;

            if (this.filterPlayerId) {
                const isSelf = node.id === this.filterPlayerId;
                const isNeighbor = this.links.some(l =>
                    (l.source.id === this.filterPlayerId && l.target === node) ||
                    (l.target.id === this.filterPlayerId && l.source === node)
                );
                opacity = (isSelf || isNeighbor) ? 1.0 : 0.15;
            } else if (this.hoveredNode && this.hoveredNode !== node) {
                const isNeighbor = this.links.some(l =>
                    (l.source === this.hoveredNode && l.target === node) ||
                    (l.target === this.hoveredNode && l.source === node)
                );
                opacity = isNeighbor ? 1.0 : 0.25;
            }

            this.ctx.globalAlpha = opacity;

            // Highlight ring
            if (node === this.hoveredNode || node.id === this.filterPlayerId) {
                this.ctx.beginPath();
                this.ctx.arc(node.x, node.y, node.radius + 5, 0, Math.PI * 2);
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
                this.ctx.fill();
            }

            // Node circle
            this.ctx.beginPath();
            this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
            this.ctx.fillStyle = '#1a1a2e';
            this.ctx.fill();
            this.ctx.lineWidth = 2;
            this.ctx.strokeStyle = this.getNodeColor(node.type);
            this.ctx.stroke();

            // Node label (name) - only if visible
            if (opacity > 0.3) {
                this.ctx.fillStyle = '#ffffff';
                this.ctx.font = '9px Inter, sans-serif';
                this.ctx.textAlign = 'center';
                this.ctx.fillText(node.name, node.x, node.y + node.radius + 12);
            }
        }

        this.ctx.globalAlpha = 1.0;
    }

    renderTooltip(event) {
        if (!this.hoveredNode && !this.hoveredLink) {
            this.tooltipContainer.style.display = 'none';
            return;
        }

        // Build tooltip content - NO NAME (already shown on node)
        let html = '';

        if (this.hoveredNode) {
            const node = this.hoveredNode;
            html = `
                <div class="node-tooltip-card ${node.type}">
                    <div class="node-tooltip-body">
                        <div class="node-tooltip-meta">${node.id} | ${node.archetype}</div>
                        ${node.ability ? `<div class="node-tooltip-ability">⚡ ${node.ability.substring(0, 80)}${node.ability.length > 80 ? '...' : ''}</div>` : ''}
                        <div style="margin-top:6px;font-size:0.75rem;color:#888;">Klikni pro briefing</div>
                    </div>
                </div>
            `;
        } else if (this.hoveredLink) {
            const link = this.hoveredLink;
            const typeLabel = {
                'past': 'Minulost', 'trade': 'Obchod', 'blackmail': 'Vydírání',
                'romance': 'Láska', 'plot': 'Spiknutí', 'rival': 'Rivalita',
                'investigation': 'Vyšetřování', 'empathy': 'Empatie'
            }[link.type] || link.type;

            html = `
                <div class="relation-tooltip-card">
                    <div class="relation-tooltip-header">
                        <span class="relation-type-badge ${link.type}">${typeLabel}</span>
                    </div>
                    <div class="relation-tooltip-pair">
                        <strong>${link.source.name}</strong> ↔ <strong>${link.target.name}</strong>
                    </div>
                    <div class="relation-tooltip-desc">
                        ${link.data.desc_source ? `<p><strong>${link.source.name}:</strong> ${link.data.desc_source}</p>` : ''}
                        ${link.data.desc_target ? `<p><strong>${link.target.name}:</strong> ${link.data.desc_target}</p>` : ''}
                    </div>
                </div>
            `;
        }

        this.tooltipContainer.innerHTML = html;
        this.tooltipContainer.style.display = 'block';

        // Position near mouse
        let x = event.clientX + 15;
        let y = event.clientY + 15;

        // Clamp to viewport
        const rect = this.tooltipContainer.getBoundingClientRect();
        if (x + rect.width > window.innerWidth - 10) {
            x = event.clientX - rect.width - 15;
        }
        if (y + rect.height > window.innerHeight - 10) {
            y = event.clientY - rect.height - 15;
        }

        this.tooltipContainer.style.left = Math.max(5, x) + 'px';
        this.tooltipContainer.style.top = Math.max(5, y) + 'px';
    }

    showRelationInfo(link) {
        // Show relation details in the briefing modal
        const modal = document.getElementById('briefingModal');
        const title = document.getElementById('briefingTitle');
        const content = document.getElementById('briefingContent');

        if (!modal || !title || !content) {
            console.error('Briefing modal not found');
            return;
        }

        const typeLabels = {
            'past': 'Minulost', 'trade': 'Obchod', 'blackmail': 'Vydírání',
            'romance': 'Láska', 'plot': 'Spiknutí', 'rival': 'Rivalita',
            'investigation': 'Vyšetřování', 'empathy': 'Empatie'
        };
        const typeLabel = typeLabels[link.type] || link.type;

        title.textContent = `Vztah: ${link.source.name} ↔ ${link.target.name}`;

        content.innerHTML = `
            <div class="briefing-section">
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <span class="relation-type-badge ${link.type}" style="font-size: 1rem; padding: 8px 16px;">
                        ${typeLabel}
                    </span>
                </div>
            </div>
            
            <div class="briefing-section">
                <h3>📝 ${link.source.name}</h3>
                <p>${link.data.desc_source || 'Bez popisu'}</p>
            </div>
            
            <div class="briefing-section">
                <h3>📝 ${link.target.name}</h3>
                <p>${link.data.desc_target || 'Bez popisu'}</p>
            </div>
            
            <div class="briefing-section" style="margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                <p style="text-align: center; color: var(--text-muted); font-size: 0.9rem;">
                    Klikněte na jména pro zobrazení jejich briefingu
                </p>
                <div style="display: flex; gap: 1rem; justify-content: center; margin-top: 1rem;">
                    <button class="btn-primary" onclick="showBriefing('${link.source.id}')">
                        Zobrazit ${link.source.name}
                    </button>
                    <button class="btn-primary" onclick="showBriefing('${link.target.id}')">
                        Zobrazit ${link.target.name}
                    </button>
                </div>
            </div>
        `;

        modal.classList.add('active');
    }

    setFilter(playerId) {
        this.filterPlayerId = (playerId === 'all' || !playerId) ? null : playerId;
        // Wake up simulation briefly when filter changes
        this.simulationCooled = false;
        this.tickCount = 0;
    }

    destroy() {
        // Cleanup
        if (this.tooltipContainer && this.tooltipContainer.parentNode) {
            this.tooltipContainer.parentNode.removeChild(this.tooltipContainer);
        }
    }
}

// Expose globally
window.RelationGraph = RelationGraph;
