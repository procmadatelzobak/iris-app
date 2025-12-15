/**
 * IRIS Organizer Wiki - Main Application
 * IRIS 4.0 aktuální k HLINIK Phase 34
 */

// ============================================
// DATA STORES
// ============================================

let rolesData = [];
let relationsData = [];
let configData = {};
const state = { manuals: {} };

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    initNavigation();
    initFilters();
    // Load Manuals
    try {
        const manualsRes = await fetch('data/manuals.json');
        if (manualsRes.ok) {
            state.manuals = await manualsRes.json();
        }
    } catch (e) {
        console.error("Failed to load manuals", e);
    }

    renderDashboard();
    renderRolesTable();
    renderUsersGrid();
    renderRelations();
    updateLastUpdate();

    // HLINIK features
    renderFeaturesTable();
    initFeatureFilters();

    initTests();

});

async function loadData() {
    try {
        // Load roles
        const rolesResponse = await fetch('data/roles.json');
        rolesData = await rolesResponse.json();

        // Load relations
        const relationsResponse = await fetch('data/relations.json');
        relationsData = await relationsResponse.json();

        // Load config
        const configResponse = await fetch('data/config.json');
        configData = await configResponse.json();

        console.log('Data loaded:', { roles: rolesData.length, relations: relationsData.length });
    } catch (error) {
        console.error('Failed to load data:', error);
        // Use fallback data if files not found
        rolesData = getFallbackRoles();
        relationsData = getFallbackRelations();
    }
}

// ============================================
// NAVIGATION
// ============================================

function initNavigation() {
    // Handle nav clicks
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            navigateTo(section);
        });
    });

    // Handle quick links
    document.querySelectorAll('[data-nav]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.nav;
            navigateTo(section);
        });
    });

    // Handle hash navigation
    if (window.location.hash) {
        const section = window.location.hash.substring(1);
        navigateTo(section);
    }

    // Listen for hash changes
    window.addEventListener('hashchange', () => {
        const section = window.location.hash.substring(1);
        if (section) navigateTo(section);
    });
}

function navigateTo(section) {
    // Update nav active state
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.section === section) {
            link.classList.add('active');
        }
    });

    // Update section visibility
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.remove('active');
    });

    const targetSection = document.getElementById(`section-${section}`);
    if (targetSection) {
        targetSection.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Update URL hash
    history.replaceState(null, null, `#${section}`);
}

// ============================================
// FILTERS
// ============================================

function initFilters() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const filter = btn.dataset.filter;

            // Update active state
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Filter table
            filterRolesTable(filter);
        });
    });
}

function filterRolesTable(filter) {
    const rows = document.querySelectorAll('#rolesTableBody tr');
    rows.forEach(row => {
        if (filter === 'all') {
            row.style.display = '';
        } else {
            row.style.display = row.dataset.type === filter ? '' : 'none';
        }
    });
}

// ============================================
// DASHBOARD
// ============================================

function renderDashboard() {
    const users = rolesData.filter(r => r.type === 'user');
    const agents = rolesData.filter(r => r.type === 'agent');
    const admins = rolesData.filter(r => r.type === 'admin');

    document.getElementById('statUsers').textContent = users.length;
    document.getElementById('statAgents').textContent = agents.length;
    document.getElementById('statAdmins').textContent = admins.length;
    document.getElementById('statRelations').textContent = relationsData.length;
}

function updateLastUpdate() {
    const now = new Date();
    document.getElementById('lastUpdate').textContent = now.toLocaleDateString('cs-CZ', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// ============================================
// ROLES TABLE
// ============================================

function renderRolesTable() {
    const tbody = document.getElementById('rolesTableBody');
    tbody.innerHTML = '';

    rolesData.forEach(role => {
        const tr = document.createElement('tr');
        tr.dataset.type = role.type;
        tr.innerHTML = `
            <td><code>${role.id}</code></td>
            <td><strong>${role.name}</strong></td>
            <td><span class="role-badge ${role.type}">${getRoleTypeLabel(role.type)}</span></td>
            <td>${role.archetype}</td>
            <td><span class="ability-text">${role.ability}</span></td>
            <td>
                <button class="btn-briefing" onclick="showBriefing('${role.id}')">
                    📄 Briefing
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function getRoleTypeLabel(type) {
    const labels = {
        'user': 'Uživatel',
        'agent': 'Agent',
        'admin': 'Správce'
    };
    return labels[type] || type;
}

// ============================================
// USERS GRID
// ============================================

function renderUsersGrid() {
    const grid = document.getElementById('usersGrid');
    grid.innerHTML = '';

    // Show all roles, not just users
    rolesData.forEach(role => {
        const card = document.createElement('div');
        card.className = 'user-card';
        const roleTypeClass = role.type === 'admin' ? 'role-admin' : (role.type === 'agent' ? 'role-agent' : 'role-user');
        card.innerHTML = `
            <div class="user-card-header ${roleTypeClass}" style="display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <img src="assets/images/${role.avatar || 'avatar_user_male.png'}" style="width: 32px; height: 32px; border-radius: 4px; object-fit: cover;">
                    <span class="user-id">${role.id}</span>
                </div>
                <span style="font-size: 0.8rem; opacity: 0.7;">${role.type.toUpperCase()}</span>
            </div>
            <div class="user-card-archetype">${role.archetype}</div>
            <p class="user-card-description">${role.description}</p>
            <div class="user-card-footer">
                <span class="ability-text">⚡ ${role.ability.split(':')[0]}</span>
                <button class="btn-briefing" onclick="showBriefing('${role.id}')">
                    📄 Briefing
                </button>
            </div>
        `;
        grid.appendChild(card);
    });
}

// ============================================
// RELATIONS
// ============================================

function renderRelations() {
    renderRelationsList();
    renderRelationsGraph();
}

function renderRelationsList() {
    const list = document.getElementById('relationsList');
    list.innerHTML = '';

    relationsData.forEach(rel => {
        const sourceName = getRoleName(rel.source);
        const targetName = getRoleName(rel.target);

        const card = document.createElement('div');
        card.className = 'relation-card';
        card.style.borderLeftColor = getRelationColor(rel.type);
        card.innerHTML = `
            <div class="relation-header">
                <span class="relation-title">${rel.source} ↔ ${rel.target}</span>
                <span class="relation-type ${rel.type}">${getRelationTypeLabel(rel.type)}</span>
            </div>
            <div class="relation-desc">
                <p><strong>${sourceName}:</strong> ${rel.desc_source}</p>
                <p><strong>${targetName}:</strong> ${rel.desc_target}</p>
            </div>
        `;
        list.appendChild(card);
    });
}

function getRoleName(id) {
    const role = rolesData.find(r => r.id === id);
    return role ? role.name : id;
}

function getRelationTypeLabel(type) {
    const labels = {
        'past': 'Minulost',
        'trade': 'Obchod',
        'blackmail': 'Vydírání',
        'romance': 'Láska',
        'plot': 'Spiknutí',
        'empathy': 'Empatie',
        'rival': 'Rivalita',
        'investigation': 'Vyšetřování'
    };
    return labels[type] || type;
}

function getRelationColor(type) {
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

function renderRelationsGraph() {
    const svg = document.getElementById('relationsGraph');
    const width = svg.parentElement.clientWidth;
    const height = 400;

    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.innerHTML = '';

    // Create nodes from roles
    const nodes = rolesData.map((role, i) => {
        const angle = (i / rolesData.length) * 2 * Math.PI;
        const radius = Math.min(width, height) * 0.35;
        return {
            id: role.id,
            name: role.name,
            type: role.type,
            x: width / 2 + Math.cos(angle) * radius,
            y: height / 2 + Math.sin(angle) * radius
        };
    });

    // Draw edges (relations)
    relationsData.forEach(rel => {
        const source = nodes.find(n => n.id === rel.source);
        const target = nodes.find(n => n.id === rel.target);
        if (source && target) {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', source.x);
            line.setAttribute('y1', source.y);
            line.setAttribute('x2', target.x);
            line.setAttribute('y2', target.y);
            line.setAttribute('stroke', getRelationColor(rel.type));
            line.setAttribute('stroke-width', '2');
            line.setAttribute('opacity', '0.6');
            svg.appendChild(line);
        }
    });

    // Draw nodes
    nodes.forEach(node => {
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', 'graph-node');
        g.style.cursor = 'pointer';
        g.onclick = () => showBriefing(node.id);

        // Circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', node.x);
        circle.setAttribute('cy', node.y);
        circle.setAttribute('r', '20');
        circle.setAttribute('fill', getNodeColor(node.type));
        circle.setAttribute('stroke', '#1a1a25');
        circle.setAttribute('stroke-width', '2');
        g.appendChild(circle);

        // Label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', node.x);
        text.setAttribute('y', node.y + 4);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('fill', '#fff');
        text.setAttribute('font-size', '10');
        text.setAttribute('font-weight', 'bold');
        text.textContent = node.id;
        g.appendChild(text);

        svg.appendChild(g);
    });
}

function getNodeColor(type) {
    const colors = {
        'user': '#4a9eff',
        'agent': '#e91e63',
        'admin': '#d4af37'
    };
    return colors[type] || '#666';
}

// ============================================
// BRIEFING MODAL
// ============================================

function showBriefing(roleId) {
    const role = rolesData.find(r => r.id === roleId);
    if (!role) return;

    const modal = document.getElementById('briefingModal');
    const title = document.getElementById('briefingTitle');
    const content = document.getElementById('briefingContent');

    // Get relations for this role
    const roleRelations = getRelationsForRole(roleId);
    const roleTypeClass = role.type === 'admin' ? 'role-admin' : (role.type === 'agent' ? 'role-agent' : 'role-user');

    title.textContent = `${role.name} (${role.id})`;

    content.innerHTML = `
        <div class="briefing-section">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <span class="role-badge ${role.type}" style="font-size: 0.9rem; padding: 4px 12px;">
                    ${getRoleTypeLabel(role.type)}
                </span>
                <span style="color: var(--text-muted); font-size: 0.85rem;">
                    IRIS 4.0 | HLINIK Phase 34
                </span>
            </div>
        </div>
        
        <div class="role-detail-header ${roleTypeClass}">
            <div style="display:flex; gap: 20px; align-items:center;">
                <img src="assets/images/${role.avatar || 'avatar_user_male.png'}" style="width: 100px; height: 100px; border-radius: 8px; border: 2px solid var(--border-color); object-fit: cover;">
                <div>
                    <h2 style="margin:0">${role.name}</h2>
                    <div style="font-family: var(--font-mono); color: rgba(255,255,255,0.7); margin-top: 5px;">${role.id} | ${role.archetype}</div>
                </div>
            </div>
        </div>
        
        <div class="briefing-section">
            <h3>👤 Archetyp</h3>
            <p><strong>${role.archetype}</strong></p>
            <p>${role.description}</p>
        </div>
        
        <div class="briefing-section">
            <h3>🎯 Cíle mise</h3>
            <ul class="briefing-goals">
                ${role.goals.map(g => `<li>${g}</li>`).join('')}
            </ul>
        </div>
        
        <div class="briefing-section">
            <h3>⚡ Speciální schopnost</h3>
            <div class="briefing-ability">
                ${role.ability}
            </div>
        </div>
        
        <div class="briefing-section">
            <h3>🔗 Vazby a tajemství</h3>
            ${roleRelations.length > 0
            ? roleRelations.map(rel => `
                    <div class="briefing-relation">
                        <strong>Vztah k ${rel.target}:</strong> ${rel.desc}
                    </div>
                `).join('')
            : '<p style="color: var(--text-muted); font-style: italic;">Žádné specifické vazby na začátku hry.</p>'
        }
        </div>
    `;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function getRelationsForRole(roleId) {
    const relations = [];

    relationsData.forEach(rel => {
        if (rel.source === roleId) {
            relations.push({
                target: rel.target,
                desc: rel.desc_source,
                type: rel.type
            });
        } else if (rel.target === roleId) {
            relations.push({
                target: rel.source,
                desc: rel.desc_target,
                type: rel.type
            });
        }
    });

    return relations;
}

function closeBriefing() {
    document.getElementById('briefingModal').classList.remove('active');
    document.body.style.overflow = '';
}

function printBriefing() {
    window.print();
}

// Close modal on overlay click
document.getElementById('briefingModal').addEventListener('click', (e) => {
    if (e.target.id === 'briefingModal') {
        closeBriefing();
    }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeBriefing();
        closeManual();
    }
});

// ============================================
// MANUALS
// ============================================

function showManual(type) {
    const manual = state.manuals[type];

    if (!manual) {
        // Fallback to a simple alert or a briefing modal if the manual is not found
        // For now, let's use a simple alert or console log.
        // If you want to show it in the briefing modal, you'd need to adjust showBriefing to accept generic content.
        console.warn(`Manual of type '${type}' not found in state.manuals.`);
        alert(`Manuál typu '${type}' nebyl nalezen.`);
        return;
    }

    const viewer = document.getElementById('manualViewer');
    const title = document.getElementById('manualTitle');
    const content = document.getElementById('manualContent');

    title.textContent = manual.title;
    content.innerHTML = manual.content;

    viewer.classList.add('active');
    viewer.scrollIntoView({ behavior: 'smooth' });
}

function closeManual() {
    document.getElementById('manualViewer').classList.remove('active');
}

// ============================================
// TESTS VIEWER
// ============================================

async function initTests() {
    try {
        const response = await fetch('data/test_runs/index.json');
        const runs = await response.json();
        renderTestRunsList(runs);
    } catch (e) {
        console.error("Failed to load test runs", e);
        document.getElementById('testRunsList').innerHTML = '<p class="text-muted">Zatím žádné záznamy testů.</p>';
    }
}

function renderTestRunsList(runs) {
    const list = document.getElementById('testRunsList');
    list.innerHTML = '';

    if (!runs || runs.length === 0) {
        list.innerHTML = '<p class="text-muted">Žádné záznamy.</p>';
        return;
    }

    // Sort by timestamp desc
    runs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    runs.forEach(run => {
        const item = document.createElement('div');
        item.className = 'test-run-item';
        item.onclick = () => {
            document.querySelectorAll('.test-run-item').forEach(el => el.classList.remove('active'));
            item.classList.add('active');
            loadTestRunDetail(run);
        };

        const date = new Date(run.timestamp).toLocaleString('cs-CZ');
        const statusClass = run.status === 'success' ? 'passed' : 'failed';

        item.innerHTML = `
            <div class="test-run-header">
                <span class="test-status ${statusClass}">${run.status}</span>
                <span>${run.duration}s</span>
            </div>
            <div class="test-meta">
                <div>${date}</div>
                <div>${run.scenario_name}</div>
            </div>
        `;
        list.appendChild(item);
    });
}

async function loadTestRunDetail(runMeta) {
    const detailContainer = document.getElementById('testRunDetail');
    detailContainer.innerHTML = '<p class="text-muted">Načítám detail logu...</p>';

    try {
        const response = await fetch(`data/test_runs/runs/${runMeta.filename}`);
        if (!response.ok) throw new Error('File not found');
        const data = await response.json();
        renderTestDetail(data);
    } catch (e) {
        detailContainer.innerHTML = '<p class="text-muted" style="color:var(--accent-red)">Chyba při načítání detailu logu. Soubor asi neexistuje.</p>';
        console.error(e);
    }
}

function renderTestDetail(data) {
    const detailContainer = document.getElementById('testRunDetail');

    let html = `
        <div class="section-header" style="margin-bottom: 20px;">
            <h2>${data.scenario_name}</h2>
            <p class="section-subtitle">${new Date(data.timestamp).toLocaleString('cs-CZ')} | ${data.stats.users_active} Users Active</p>
        </div>
        
        <div class="version-info" style="margin-bottom: 20px; padding: 15px; background: var(--bg-primary); border-radius: 8px;">
            <div class="version-item">
                <span class="label">Status</span>
                <span class="value" style="color: ${data.status === 'success' ? 'var(--accent-green)' : 'var(--accent-red)'}">${data.status.toUpperCase()}</span>
            </div>
            <div class="version-item">
                <span class="label">Prům. Latence</span>
                <span class="value">${data.stats.avg_latency} ms</span>
            </div>
            <div class="version-item">
                <span class="label">Chyby</span>
                <span class="value" style="color: ${data.stats.errors > 0 ? 'var(--accent-red)' : 'var(--text-primary)'}">${data.stats.errors}</span>
            </div>
        </div>
        
        <h3>📜 Průběh testu (Log Stream)</h3>
        <div class="log-container">
    `;

    data.logs.forEach(log => {
        let imageHtml = '';
        if (log.screenshot) {
            imageHtml = `
                <div class="log-img-wrapper">
                    <img src="data/test_runs/runs/${log.screenshot}" loading="lazy" alt="Screenshot" onclick="window.open(this.src, '_blank')" style="cursor:zoom-in">
                    <div class="log-img-caption">📸 Screenshot: ${log.screenshot}</div>
                </div>
            `;
        }

        html += `
            <div class="log-entry">
                <div class="log-time">${log.time.split('T')[1].split('.')[0]}</div>
                <div class="log-level ${log.level}">${log.level}</div>
                <div class="log-message">
                    ${log.message}
                    ${imageHtml}
                </div>
            </div>
        `;
    });

    html += `</div>`;
    detailContainer.innerHTML = html;
}

// ============================================
// FALLBACK DATA
// ============================================

function getFallbackRoles() {
    return [
        { id: "U01", type: "user", name: "Jana Nováková", archetype: "Zadlužená učitelka", description: "Potřebujete peníze na opravu střechy.", ability: "Grammar Nazi: Bonus za opravu gramatiky", goals: ["Vydělat 3000 NC"] },
        { id: "U02", type: "user", name: "Karel 'Bet' Dlouhý", archetype: "Gambler", description: "Dlužíte peníze lichvářům.", ability: "All-in: Vsadit polovinu výdělku", goals: ["Vydělat 10000 NC"] },
        { id: "A01", type: "agent", name: "Petr Svoboda", archetype: "Cynický Student", description: "Nenávidíte tuhle práci.", ability: "Sarkasmus: Povolený drzý tón", goals: ["Nechat se vyhodit po výplatě"] },
        { id: "A02", type: "agent", name: "Ema 'Echo'", archetype: "Herečka", description: "Hrajete AI jako roli.", ability: "Drama: Verše přesvědčí víc", goals: ["Dostat 5 hvězdiček"] },
        { id: "S01", type: "admin", name: "Ing. Miloš Vrána", archetype: "Manažer staré školy", description: "Ředitel směny.", ability: "Ban Hammer: Vyhazovat uživatele", goals: ["Udržet firmu v chodu"] }
    ];
}

function getFallbackRelations() {
    return [
        { source: "U01", target: "A01", type: "past", desc_source: "Poznala jste svého žáka.", desc_target: "Jana je vaše učitelka." }
    ];
}

// Make functions globally available
window.showBriefing = showBriefing;
window.closeBriefing = closeBriefing;
window.printBriefing = printBriefing;
window.showManual = showManual;
window.closeManual = closeManual;
window.exportBriefingPDF = exportBriefingPDF;
window.exportManualPDF = exportManualPDF;

// ============================================
// PDF EXPORT FUNCTIONS
// ============================================

let currentBriefingRoleId = null;
let currentManualType = null;

// Store current role when showing briefing
const originalShowBriefing = showBriefing;
window.showBriefing = function (roleId) {
    currentBriefingRoleId = roleId;
    originalShowBriefing(roleId);
};

// Store current manual when showing
const originalShowManual = showManual;
window.showManual = function (type) {
    currentManualType = type;
    originalShowManual(type);
};

function exportBriefingPDF() {
    if (!currentBriefingRoleId) {
        alert('Nejdříve otevřete briefing');
        return;
    }

    const role = rolesData.find(r => r.id === currentBriefingRoleId);
    if (!role) return;

    // Create printable content
    const printContent = generateBriefingHTML(role);
    openPrintWindow(printContent, `Briefing_${role.id}_${role.name.replace(/\s+/g, '_')}`);
}

function exportManualPDF(type) {
    const manualType = type || currentManualType;
    if (!manualType) {
        alert('Nejdříve otevřete manuál');
        return;
    }
    const manual = state.manuals[manualType];
    if (!manual) return;

    const printContent = generateManualHTML(manual);
    openPrintWindow(printContent, `Prirucka_${manualType}`);
}

function generateBriefingHTML(role) {
    const roleRelations = getRelationsForRole(role.id);

    return `
        <!DOCTYPE html>
        <html lang="cs">
        <head>
            <meta charset="UTF-8">
            <title>Briefing: ${role.name} (${role.id})</title>
            <style>
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    padding: 40px; 
                    max-width: 800px; 
                    margin: 0 auto;
                    line-height: 1.6;
                    color: #222;
                }
                .header { 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center; 
                    border-bottom: 3px solid #d4af37; 
                    padding-bottom: 15px; 
                    margin-bottom: 25px; 
                }
                .header h1 { font-size: 1.8rem; color: #333; }
                .badge { 
                    background: #d4af37; 
                    color: #000; 
                    padding: 5px 12px; 
                    border-radius: 4px; 
                    font-weight: bold;
                    font-size: 0.85rem;
                }
                .version { color: #666; font-size: 0.85rem; }
                h2 { 
                    color: #d4af37; 
                    margin: 25px 0 10px 0; 
                    font-size: 1.2rem;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 5px;
                }
                p { margin: 10px 0; }
                ul { margin: 10px 0 10px 25px; }
                li { margin: 5px 0; }
                .ability-box { 
                    background: #e8f5e9; 
                    border-left: 4px solid #4caf50; 
                    padding: 15px; 
                    margin: 15px 0; 
                }
                .relation-box { 
                    background: #fff8e1; 
                    border-left: 4px solid #ff9800; 
                    padding: 12px; 
                    margin: 10px 0; 
                }
                .footer { 
                    margin-top: 30px; 
                    padding-top: 15px; 
                    border-top: 1px solid #ddd; 
                    font-size: 0.8rem; 
                    color: #666; 
                }
                @media print {
                    body { padding: 20px; }
                    .header { page-break-after: avoid; }
                }
            </style>
        </head>
        <body>
            <div class="header">
                <div>
                    <h1>BRIEFING: ${role.name} (${role.id})</h1>
                    <span class="version">IRIS 4.0 | HLINIK Phase 34</span>
                </div>
                <span class="badge">${getRoleTypeLabel(role.type).toUpperCase()}</span>
            </div>
            
            <h2>👤 Archetyp</h2>
            <p><strong>${role.archetype}</strong></p>
            <p>${role.description}</p>
            
            <h2>🎯 Cíle mise</h2>
            <ul>
                ${role.goals.map(g => `<li>${g}</li>`).join('')}
            </ul>
            
            <h2>⚡ Speciální schopnost</h2>
            <div class="ability-box">
                ${role.ability}
            </div>
            
            <h2>🔗 Vazby a tajemství</h2>
            ${roleRelations.length > 0
            ? roleRelations.map(rel => `
                    <div class="relation-box">
                        <strong>Vztah k ${rel.target}:</strong> ${rel.desc}
                    </div>
                `).join('')
            : '<p><em>Žádné specifické vazby na začátku hry.</em></p>'
        }
            
            <div class="footer">
                <p>Dokument podléhá NDA. | IRIS 4.0 | HLINIK Phase 34</p>
            </div>
        </body>
        </html>
    `;
}

function generateManualHTML(manual) {
    return `
        <!DOCTYPE html>
        <html lang="cs">
        <head>
            <meta charset="UTF-8">
            <title>${manual.title}</title>
            <style>
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { 
                    font-family: 'Segoe UI', Arial, sans-serif; 
                    padding: 40px; 
                    max-width: 800px; 
                    margin: 0 auto;
                    line-height: 1.6;
                    color: #222;
                }
                h1 { 
                    border-bottom: 3px solid #d4af37; 
                    padding-bottom: 15px; 
                    margin-bottom: 25px; 
                    font-size: 1.8rem;
                }
                h2 { 
                    color: #d4af37; 
                    margin: 25px 0 10px 0; 
                    font-size: 1.3rem;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 5px;
                }
                h3 { 
                    margin: 20px 0 10px 0; 
                    font-size: 1.1rem;
                    color: #444;
                }
                p { margin: 10px 0; }
                ul { margin: 10px 0 10px 25px; }
                li { margin: 5px 0; }
                table { 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin: 15px 0; 
                }
                th, td { 
                    border: 1px solid #ddd; 
                    padding: 10px; 
                    text-align: left; 
                }
                th { 
                    background: #f5f5f5; 
                    color: #333;
                    font-weight: 600;
                }
                .footer { 
                    margin-top: 30px; 
                    padding-top: 15px; 
                    border-top: 1px solid #ddd; 
                    font-size: 0.8rem; 
                    color: #666; 
                }
                @media print {
                    body { padding: 20px; }
                }
            </style>
        </head>
        <body>
            ${manual.content}
            <div class="footer">
                <p>IRIS 4.0 | HLINIK Phase 34 | Organizátorská Wiki</p>
            </div>
        </body>
        </html>
    `;
}

function openPrintWindow(htmlContent, filename) {
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
        alert('Povolení blokátoru vyskakovacích oken. Povolte pop-up okna pro tuto stránku.');
        return;
    }

    printWindow.document.write(htmlContent);
    printWindow.document.close();

    // Wait for content to load then print
    printWindow.onload = function () {
        printWindow.focus();
        printWindow.print();
    };
}

// ============================================
// HLINIK FEATURES DATA
// ============================================

const featuresData = [
    // Core Features
    { status: "✅", category: "core", name: "JWT Autentizace", desc: "Bezpečné přihlašování s HTTP-only cookies" },
    { status: "✅", category: "core", name: "Role-based Access", desc: "Přístup podle rolí (User/Agent/Admin/Root)" },
    { status: "✅", category: "core", name: "WebSocket Real-time", desc: "Okamžitá komunikace přes WebSocket" },
    { status: "✅", category: "core", name: "Session Routing", desc: "8 izolovaných kanálů s dynamickým přiřazením" },
    { status: "✅", category: "core", name: "Ekonomický systém", desc: "Kredity, daně, Treasury, Purgatory mód" },
    { status: "✅", category: "core", name: "Task systém", desc: "Schvalování, hodnocení, výplata úkolů" },
    
    // User Features
    { status: "✅", category: "user", name: "Retro terminál", desc: "CRT efekty, 4 témata (Low/Mid/High/Party)" },
    { status: "✅", category: "user", name: "Chat s agentem", desc: "Posílání a přijímání zpráv v reálném čase" },
    { status: "✅", category: "user", name: "Report systém", desc: "Nahlášení nevhodných zpráv" },
    { status: "✅", category: "user", name: "Purgatory mód", desc: "Blokace chatu při záporném zůstatku, úkoly povoleny" },
    { status: "✅", category: "user", name: "Party mód", desc: "Speciální téma s animovanými bublinami" },
    { status: "✅", category: "user", name: "Správa úkolů", desc: "Žádost o úkol, odevzdání, sledování stavu" },
    
    // Agent Features
    { status: "✅", category: "agent", name: "Agent terminál", desc: "Monochromatický retro design" },
    { status: "✅", category: "agent", name: "Message Optimizer", desc: "AI přepis zpráv s potvrzením před odesláním" },
    { status: "✅", category: "agent", name: "Autopilot", desc: "Automatické AI odpovědi" },
    { status: "✅", category: "agent", name: "Response Timer", desc: "Žlutý progress bar s časovým limitem" },
    { status: "✅", category: "agent", name: "Visibility módy", desc: "Normal, Blackbox, Forensic, Ephemeral" },
    { status: "✅", category: "agent", name: "Typing sync", desc: "Real-time synchronizace psaní" },
    
    // Admin Features
    { status: "✅", category: "admin", name: "Dashboard Hub", desc: "4 stanice: Monitor, Control, Economy, Tasks" },
    { status: "✅", category: "admin", name: "Panopticon", desc: "Přehled všech 8 relací, systémové logy" },
    { status: "✅", category: "admin", name: "Ekonomika", desc: "Pokuty, bonusy, zámky, status levely" },
    { status: "✅", category: "admin", name: "Úkoly", desc: "Schvalování, editace, hodnocení s LLM" },
    { status: "✅", category: "admin", name: "Kontrola", desc: "Shift, teplota, AI optimizer, visibility" },
    { status: "✅", category: "admin", name: "Network graf", desc: "Canvas vizualizace User-Agent spojení" },
    
    // ROOT Features
    { status: "✅", category: "admin", name: "ROOT Dashboard", desc: "Elite admin interface s 5 taby" },
    { status: "✅", category: "admin", name: "Test Mode", desc: "Quick login tlačítka pro testování" },
    { status: "✅", category: "admin", name: "AI Config", desc: "Nastavení Optimizer a Autopilot modelů" },
    { status: "✅", category: "admin", name: "Chronos", desc: "Časová manipulace, override teploty" },
    
    // AI Features
    { status: "✅", category: "ai", name: "Multi-provider", desc: "OpenAI, OpenRouter, Gemini" },
    { status: "✅", category: "ai", name: "Task Generation", desc: "LLM generování popisů úkolů" },
    { status: "✅", category: "ai", name: "Report Immunity", desc: "AI zprávy nelze nahlásit" },
    { status: "⚠️", category: "ai", name: "Task LLM Config", desc: "Backend existuje, UI není implementováno" },
    { status: "⚠️", category: "ai", name: "Provider Selection", desc: "Částečná implementace v UI" }
];

function renderFeaturesTable() {
    const tbody = document.getElementById('featuresTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    featuresData.forEach(feature => {
        const tr = document.createElement('tr');
        tr.dataset.featureCategory = feature.category;
        
        const statusColor = feature.status === '✅' ? 'var(--accent-green)' : 
                           feature.status === '⚠️' ? 'var(--accent-orange)' : 'var(--text-muted)';
        
        const categoryLabels = {
            'core': '🏗️ Jádro',
            'user': '👥 Uživatel',
            'agent': '🤖 Agent',
            'admin': '👔 Admin',
            'ai': '🧠 AI'
        };

        tr.innerHTML = `
            <td style="color: ${statusColor}; text-align: center;">${feature.status}</td>
            <td><span class="role-badge" style="background: var(--bg-secondary);">${categoryLabels[feature.category] || feature.category}</span></td>
            <td><strong>${feature.name}</strong></td>
            <td class="ability-text">${feature.desc}</td>
        `;
        tbody.appendChild(tr);
    });
}

function initFeatureFilters() {
    document.querySelectorAll('[data-feature-filter]').forEach(btn => {
        btn.addEventListener('click', () => {
            const filter = btn.dataset.featureFilter;

            // Update active state
            document.querySelectorAll('[data-feature-filter]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Filter table
            filterFeaturesTable(filter);
        });
    });
}

function filterFeaturesTable(filter) {
    const rows = document.querySelectorAll('#featuresTableBody tr');
    rows.forEach(row => {
        if (filter === 'all') {
            row.style.display = '';
        } else {
            row.style.display = row.dataset.featureCategory === filter ? '' : 'none';
        }
    });
}

// ============================================
// AUDIT SWITCHING
// ============================================

function switchAudit(auditId) {
    // Hide all audit contents
    document.querySelectorAll('.audit-content').forEach(content => {
        content.classList.remove('active');
    });

    // Show selected audit
    const selectedAudit = document.getElementById(auditId);
    if (selectedAudit) {
        selectedAudit.classList.add('active');
    }
}

// Make function globally available
window.switchAudit = switchAudit;
