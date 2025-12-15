/**
 * IRIS Organizer Wiki - Main Application
 * IRIS 4.1 aktuální k HLINIK Phase 35
 */

// ============================================
// DATA STORES
// ============================================

let rolesData = [];
let relationsData = [];
let configData = {};
const state = { manuals: {} };
let timelineData = [];

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
        } else {
            console.warn("Manuals load failed (not OK), using fallback");
            state.manuals = getFallbackManuals();
        }
    } catch (e) {
        console.warn("Failed to load manuals (fetch error), using fallback", e);
        state.manuals = getFallbackManuals();
    }

    renderDashboard();
    renderRolesTable();
    renderUsersGrid();
    renderRelations();
    renderTimeline();
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

        // Load timeline
        try {
            const timelineResponse = await fetch('data/timeline.json');
            timelineData = await timelineResponse.json();
        } catch (e) {
            console.warn("Failed to load timeline data", e);
            timelineData = getFallbackTimeline();
        }

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

// Section to category mapping
const sectionCategories = {
    'dashboard': 'none',
    'role': 'lore',
    'uzivatele': 'lore',
    'vztahy': 'lore',
    'manualy': 'lore',
    'lore': 'lore',
    'hraci': 'lore',
    'prompty': 'lore',
    'timeline': 'lore',
    'dokumentace': 'hlinik',
    'hlinik': 'hlinik',
    'system': 'hlinik',
    'tests': 'hlinik',
    'loreweb-doc': 'about',
    'compliance': 'about',
    'exporty': 'about'
};

let currentCategory = 'lore';

function initNavigation() {
    // Handle main nav clicks (categories)
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const category = link.dataset.category;
            const section = link.dataset.section;

            if (category && category !== 'none') {
                // Category link - switch submenu
                switchCategory(category);
            } else if (section) {
                // Direct section link
                navigateTo(section);
            }
        });
    });

    // Handle submenu clicks
    document.querySelectorAll('.submenu-link').forEach(link => {
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
    } else {
        // Default to lore category visible
        switchCategory('lore');
    }

    // Listen for hash changes
    window.addEventListener('hashchange', () => {
        const section = window.location.hash.substring(1);
        if (section) navigateTo(section);
    });
}

function switchCategory(category) {
    currentCategory = category;

    // Update main nav active state
    document.querySelectorAll('.nav-category').forEach(link => {
        link.classList.toggle('active', link.dataset.category === category);
    });

    // Show/hide submenu groups
    document.querySelectorAll('.submenu-group').forEach(group => {
        group.style.display = group.dataset.category === category ? 'flex' : 'none';
    });

    // Navigate to first section of category
    const firstLink = document.querySelector(`.submenu-group[data-category="${category}"] .submenu-link`);
    if (firstLink) {
        navigateTo(firstLink.dataset.section);
    }
}

function navigateTo(section) {
    // Determine category for this section
    const category = sectionCategories[section] || 'lore';

    // If it's a categorized section, ensure submenu is visible
    if (category !== 'none' && category !== currentCategory) {
        currentCategory = category;
        document.querySelectorAll('.nav-category').forEach(link => {
            link.classList.toggle('active', link.dataset.category === category);
        });
        document.querySelectorAll('.submenu-group').forEach(group => {
            group.style.display = group.dataset.category === category ? 'flex' : 'none';
        });
    }

    // Hide submenu for non-categorized sections
    if (category === 'none') {
        document.querySelectorAll('.nav-category').forEach(link => link.classList.remove('active'));
    }

    // Update main nav active state for direct links
    document.querySelectorAll('.nav-link[data-section]').forEach(link => {
        link.classList.toggle('active', link.dataset.section === section);
    });

    // Update submenu active state
    document.querySelectorAll('.submenu-link').forEach(link => {
        link.classList.toggle('active', link.dataset.section === section);
    });

    // Update section visibility
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.remove('active');
    });

    const targetSection = document.getElementById(`section-${section}`);
    if (targetSection) {
        targetSection.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Re-render graph when navigating to relations section (deferred)
        if (section === 'vztahy') {
            setTimeout(() => renderRelationsGraph(), 50);
        }
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

    const statUsers = document.getElementById('statUsers');
    const statAgents = document.getElementById('statAgents');
    const statAdmins = document.getElementById('statAdmins');
    const statRelations = document.getElementById('statRelations');

    if (statUsers) statUsers.textContent = users.length;
    if (statAgents) statAgents.textContent = agents.length;
    if (statAdmins) statAdmins.textContent = admins.length;
    if (statRelations) statRelations.textContent = relationsData.length;
}

function updateLastUpdate() {
    const lastUpdate = document.getElementById('lastUpdate');
    if (!lastUpdate) return;
    const now = new Date();
    lastUpdate.textContent = now.toLocaleDateString('cs-CZ', {
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
    if (!tbody) return;
    tbody.innerHTML = '';

    rolesData.forEach(role => {
        const tr = document.createElement('tr');
        tr.dataset.type = role.type;
        tr.innerHTML = `
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
    if (!grid) return;
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
                    <span class="user-id" style="font-weight:bold;">${role.name}</span>
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
    if (!list) return;
    list.innerHTML = '';

    relationsData.forEach(rel => {
        const sourceName = getRoleName(rel.source);
        const targetName = getRoleName(rel.target);

        const card = document.createElement('div');
        card.className = 'relation-card';
        card.style.borderLeftColor = getRelationColor(rel.type);
        card.innerHTML = `
            <div class="relation-header">
                <span class="relation-title">${getRoleName(rel.source)} ↔ ${getRoleName(rel.target)}</span>
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
    if (!svg || !svg.parentElement) return;

    // Ensure container is visible before measuring
    const container = svg.parentElement;
    if (container.clientWidth === 0) {
        // Container is hidden, defer render
        return;
    }

    const width = container.clientWidth;
    const height = 400;

    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    svg.innerHTML = '';

    // Separate roles by type for grouped layout
    const users = rolesData.filter(r => r.type === 'user');
    const agents = rolesData.filter(r => r.type === 'agent');
    const admins = rolesData.filter(r => r.type === 'admin');

    // Layout: 3 columns (Users left, Admins center, Agents right)
    const colWidth = width / 4;
    const userX = colWidth * 0.75;
    const adminX = colWidth * 2;
    const agentX = colWidth * 3.25;
    const startY = 40;
    const spacing = (height - startY * 2) / Math.max(users.length, agents.length, 1);

    const nodes = [];

    // Position Users (left column)
    users.forEach((role, i) => {
        nodes.push({
            id: role.id,
            name: role.name,
            type: role.type,
            x: userX,
            y: startY + i * spacing
        });
    });

    // Position Agents (right column)
    agents.forEach((role, i) => {
        nodes.push({
            id: role.id,
            name: role.name,
            type: role.type,
            x: agentX,
            y: startY + i * spacing
        });
    });

    // Position Admins (center column, more spaced)
    const adminSpacing = (height - startY * 2) / Math.max(admins.length, 1);
    admins.forEach((role, i) => {
        nodes.push({
            id: role.id,
            name: role.name,
            type: role.type,
            x: adminX,
            y: startY + i * adminSpacing
        });
    });

    // Create node lookup map
    const nodeMap = {};
    nodes.forEach(n => nodeMap[n.id] = n);

    // Draw edges (relations)
    relationsData.forEach(rel => {
        const source = nodeMap[rel.source];
        const target = nodeMap[rel.target];
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
        circle.setAttribute('r', node.type === 'admin' ? 18 : 14);
        circle.setAttribute('fill', getNodeColor(node.type));
        circle.setAttribute('stroke', '#1a1a25');
        circle.setAttribute('stroke-width', '2');
        g.appendChild(circle);

        // Label (ID)
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', node.x);
        text.setAttribute('y', node.y + 4);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('fill', '#fff');
        text.setAttribute('font-size', '9');
        text.setAttribute('font-weight', 'bold');
        text.textContent = node.id;
        g.appendChild(text);

        svg.appendChild(g);
    });

    // Draw column labels
    const labelY = 20;
    const labelStyle = { fill: '#888', 'font-size': '12', 'font-weight': '600', 'text-anchor': 'middle' };
    [['UŽIVATELÉ', userX], ['SPRÁVCI', adminX], ['AGENTI', agentX]].forEach(([label, x]) => {
        const t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        t.setAttribute('x', x);
        t.setAttribute('y', labelY);
        Object.entries(labelStyle).forEach(([k, v]) => t.setAttribute(k, v));
        t.textContent = label;
        svg.appendChild(t);
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
        
        ${role.appearance ? `
        <div class="briefing-section">
            <h3>🎭 Vzhled postavy</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div>
                    <p><strong>Pohlaví:</strong> ${role.appearance.gender}</p>
                    <p><strong>Věk:</strong> ${role.appearance.age_range} let</p>
                    <p><strong>Vlasy:</strong> ${role.appearance.hair_color}</p>
                </div>
                <div>
                    <p><strong>Obličej:</strong> ${role.appearance.face_description}</p>
                    <p><strong>Výrazné rysy:</strong> ${role.appearance.distinctive_features}</p>
                </div>
            </div>
        </div>
        ` : ''}
        
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
        
        ${role.work_image ? `
        <div class="briefing-section">
            <h3>📸 Typická situace v práci</h3>
            <div style="text-align: center;">
                <img src="assets/images/${role.work_image}" 
                     alt="Typická pracovní situace" 
                     style="max-width: 100%; max-height: 400px; border-radius: 8px; border: 2px solid var(--border-color); cursor: zoom-in; box-shadow: 0 4px 12px rgba(0,0,0,0.4);"
                     onclick="window.open(this.src, '_blank')"
                     title="Klikni pro zvětšení">
                <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 8px;">Klikni na obrázek pro zvětšení</p>
            </div>
        </div>
        ` : ''}
        
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

const MANUAL_OPEN_FIRST_MESSAGE = 'Nejdříve otevřete manuál';

function notifyManualError(message) {
    console.warn(message);
    alert(message);
}

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
        if (!response.ok) throw new Error('HTTP error: ' + response.status);
        const runs = await response.json();
        renderTestRunsList(runs);
    } catch (e) {
        console.warn("Failed to load test runs via fetch, using fallback data", e);
        // Use fallback data when CORS blocks fetch (file:// protocol)
        renderTestRunsList(getFallbackTestRuns());
    }
}

function getFallbackTestRuns() {
    // Fallback test runs data - used when CORS blocks fetch from file:// URLs
    return [
        {
            "timestamp": "2025-12-15T08:49:31.000000",
            "scenario_name": "HLINIK Manual Testing - Comprehensive UI/UX and Functionality Audit",
            "status": "failed",
            "duration": 540.0,
            "filename": "manual_test_1765789771.json",
            "stats": {
                "tested_roles": 3,
                "total_tests": 18,
                "passed": 10,
                "failed": 5,
                "warnings": 3,
                "critical_bugs": 1,
                "screenshots": 6,
                "users_active": 3,
                "avg_latency": 145,
                "errors": 5
            }
        },
        {
            "timestamp": "2025-12-15T02:38:33.071673",
            "scenario_name": "LLM Hour Simulation",
            "status": "success",
            "duration": 60.01,
            "filename": "llm_sim_1765762713.json",
            "stats": {
                "users_active": 8,
                "agents_active": 8,
                "admins_active": 4,
                "total_messages": 85,
                "errors": 0,
                "avg_latency": 42
            }
        },
        {
            "timestamp": "2025-12-15T02:37:44.385145",
            "scenario_name": "LLM Hour Simulation",
            "status": "success",
            "duration": 38.46,
            "filename": "llm_sim_1765762664.json",
            "stats": {
                "users_active": 8,
                "agents_active": 8,
                "admins_active": 4,
                "total_messages": 14,
                "errors": 0,
                "avg_latency": 38
            }
        },
        {
            "timestamp": "2025-12-15T02:36:49.600431",
            "scenario_name": "LLM Hour Simulation",
            "status": "success",
            "duration": 42.51,
            "filename": "llm_sim_1765762609.json",
            "stats": {
                "users_active": 8,
                "agents_active": 8,
                "admins_active": 4,
                "total_messages": 15,
                "errors": 0,
                "avg_latency": 35
            }
        }
    ];
}

function renderTestRunsList(runs) {
    const list = document.getElementById('testRunsList');
    if (!list) {
        console.error('testRunsList element not found in DOM');
        return;
    }
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

    // Detect test type based on data structure
    const isManualTest = data.summary || data.test_cases || data.bug_reports;
    const stats = data.stats || data.summary || {};

    // Determine subtitle based on test type
    let subtitle = '';
    if (isManualTest) {
        const testedRoles = stats.tested_roles || [];
        subtitle = `${testedRoles.length || stats.tested_roles || 0} rolí testováno | ${stats.total_tests || 0} testů`;
    } else {
        subtitle = `${stats.users_active || 0} Users Active`;
    }

    let html = `
        <div class="section-header" style="margin-bottom: 20px;">
            <h2>${data.scenario_name}</h2>
            <p class="section-subtitle">${new Date(data.timestamp).toLocaleString('cs-CZ')} | ${subtitle}</p>
        </div>
        
        <div class="version-info" style="margin-bottom: 20px; padding: 15px; background: var(--bg-primary); border-radius: 8px;">
            <div class="version-item">
                <span class="label">Status</span>
                <span class="value" style="color: ${data.status === 'success' ? 'var(--accent-green)' : 'var(--accent-red)'}">${data.status.toUpperCase()}</span>
            </div>
    `;

    // Add appropriate stats based on test type
    if (isManualTest) {
        html += `
            <div class="version-item">
                <span class="label">Prošlo</span>
                <span class="value" style="color: var(--accent-green)">✅ ${stats.passed || 0}</span>
            </div>
            <div class="version-item">
                <span class="label">Selhalo</span>
                <span class="value" style="color: ${(stats.failed || 0) > 0 ? 'var(--accent-red)' : 'var(--text-primary)'}">${stats.failed || 0}</span>
            </div>
            <div class="version-item">
                <span class="label">Kritické bugy</span>
                <span class="value" style="color: ${(stats.critical_bugs || 0) > 0 ? 'var(--accent-red)' : 'var(--text-primary)'}">${stats.critical_bugs || 0}</span>
            </div>
        `;
    } else {
        html += `
            <div class="version-item">
                <span class="label">Prům. Latence</span>
                <span class="value">${stats.avg_latency || 'N/A'} ms</span>
            </div>
            <div class="version-item">
                <span class="label">Chyby</span>
                <span class="value" style="color: ${(stats.errors || 0) > 0 ? 'var(--accent-red)' : 'var(--text-primary)'}">${stats.errors || 0}</span>
            </div>
        `;
    }

    html += `</div>`;

    // Render bug reports for manual tests
    if (data.bug_reports && data.bug_reports.length > 0) {
        html += `<h3 style="margin: 20px 0 10px 0;">🐛 Nalezené bugy (${data.bug_reports.length})</h3>`;
        data.bug_reports.forEach(bug => {
            const severityColor = bug.severity === 'CRITICAL' ? 'var(--accent-red)' :
                bug.severity === 'HIGH' ? 'var(--accent-orange)' : 'var(--accent-gold)';
            html += `
                <div class="dashboard-card" style="margin-bottom: 10px; border-left: 4px solid ${severityColor};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <strong>${bug.id}: ${bug.title}</strong>
                        <span style="background: ${severityColor}; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">${bug.severity}</span>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">${bug.description}</p>
                    ${bug.screenshot ? `<div style="margin-top: 8px;"><img src="data/test_runs/runs/${bug.screenshot}" loading="lazy" style="max-width: 100%; border-radius: 4px; cursor: zoom-in;" onclick="window.open(this.src, '_blank')"></div>` : ''}
                </div>
            `;
        });
    }

    // Render test cases for manual tests
    if (data.test_cases && data.test_cases.length > 0) {
        html += `<h3 style="margin: 20px 0 10px 0;">🧪 Test Cases (${data.test_cases.length})</h3>`;
        html += `<table class="data-table"><thead><tr><th>ID</th><th>Název</th><th>Status</th><th>Kategorie</th></tr></thead><tbody>`;
        data.test_cases.forEach(tc => {
            const statusColor = tc.status === 'PASSED' ? 'var(--accent-green)' :
                tc.status === 'FAILED' ? 'var(--accent-red)' : 'var(--accent-orange)';
            const statusIcon = tc.status === 'PASSED' ? '✅' : tc.status === 'FAILED' ? '❌' : '⚠️';
            html += `<tr>
                <td><code>${tc.id}</code></td>
                <td>${tc.name}</td>
                <td style="color: ${statusColor}">${statusIcon} ${tc.status}</td>
                <td>${tc.category}</td>
            </tr>`;
        });
        html += `</tbody></table>`;
    }

    // Render recommendations for manual tests
    if (data.recommendations && data.recommendations.length > 0) {
        html += `<h3 style="margin: 20px 0 10px 0;">💡 Doporučení</h3>`;
        data.recommendations.forEach(rec => {
            const priorityColor = rec.priority === 'CRITICAL' ? 'var(--accent-red)' :
                rec.priority === 'HIGH' ? 'var(--accent-orange)' : 'var(--accent-gold)';
            html += `
                <div class="dashboard-card" style="margin-bottom: 10px; border-left: 4px solid ${priorityColor};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <strong>${rec.title}</strong>
                        <span style="background: ${priorityColor}; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">${rec.priority}</span>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">${rec.description}</p>
                </div>
            `;
        });
    }

    // Render logs
    if (data.logs && data.logs.length > 0) {
        html += `<h3 style="margin: 20px 0 10px 0;">📜 Průběh testu (Log Stream)</h3>`;
        html += `<div class="log-container">`;

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

            const levelClass = log.level === 'ERROR' ? 'failed' : log.level === 'SUCCESS' ? 'passed' : '';
            html += `
                <div class="log-entry">
                    <div class="log-time">${log.time.split('T')[1].split('.')[0]}</div>
                    <div class="log-level ${levelClass}">${log.level}</div>
                    <div class="log-message">
                        ${log.message}
                        ${imageHtml}
                    </div>
                </div>
            `;
        });

        html += `</div>`;
    }

    detailContainer.innerHTML = html;
}

// ============================================
// FALLBACK DATA
// ============================================

function getFallbackRoles() {
    // Complete fallback data - used when CORS blocks fetch from file:// URLs
    return [
        { "id": "U01", "type": "user", "name": "Jana Nováková", "archetype": "Zadlužená učitelka", "description": "Potřebujete peníze na opravu střechy.", "ability": "Grammar Nazi: Bonus za opravu gramatiky", "goals": ["Vydělat 3000 NC"], "avatar": "avatar_user_female.png" },
        { "id": "U02", "type": "user", "name": "Karel 'Bet' Dlouhý", "archetype": "Gambler", "description": "Dlužíte peníze lichvářům.", "ability": "All-in: Vsadit polovinu výdělku", "goals": ["Vydělat 10000 NC"], "avatar": "avatar_user_male.png" },
        { "id": "U03", "type": "user", "name": "Babička Irma", "archetype": "Důvěřivá seniorka", "description": "Věříte v technologie a moderní svět, ale někdy se cítíte osamělá.", "ability": "Stížnost vnukovi: Můžete si stěžovat a získat bonus", "goals": ["Najít přátelství", "Naučit se něčemu novému"], "avatar": "avatar_user_female.png" },
        { "id": "U04", "type": "user", "name": "Martin Novotný", "archetype": "Student práv", "description": "Studujete práva a snažíte se najít skulinu v systému.", "ability": "Právní kličky: Můžete najít trhliny v pravidlech", "goals": ["Získat důkazy pro žalobu", "Poznat systém zevnitř"], "avatar": "avatar_user_male.png" },
        { "id": "U05", "type": "user", "name": "Tereza Skálová", "archetype": "Matka na rodičovské", "description": "Vyčerpaná matka, která hledá smysl v AI pro své děti.", "ability": "Mateřský instinkt: Rozeznáte lži", "goals": ["Pomoct dětem v budoucnosti", "Pochopit technologie"], "avatar": "avatar_user_female.png" },
        { "id": "U06", "type": "user", "name": "IT Specialista Pavel", "archetype": "Pokročilý hacker", "description": "Zkoušíte systém prolomit.", "ability": "Ping: Můžete otestovat systém", "goals": ["Najít bezpečnostní díry", "Dokázat, že IRIS není AI"], "avatar": "avatar_user_male.png" },
        { "id": "U07", "type": "user", "name": "Eva Novinářka", "archetype": "Investigativní reportérka", "description": "Sbíráte důkazy pro článek o podvodu.", "ability": "Záznam: Můžete si dělat poznámky", "goals": ["Napsat článek o IRIS", "Získat důkazy"], "avatar": "avatar_user_female.png" },
        { "id": "U08", "type": "user", "name": "Aktivista OndřaDeveloper", "archetype": "Aktivista proti AI", "description": "Bojujete proti umělé inteligenci.", "ability": "Manifest: Můžete číst prohlášení", "goals": ["Shodit servery IRIS", "Zachránit lidstvo"], "avatar": "avatar_user_male.png" },
        { "id": "A01", "type": "agent", "name": "Petr Svoboda", "archetype": "Cynický Student", "description": "Nenávidíte tuhle práci ale potřebujete peníze.", "ability": "Sarkasmus: Povolený drzý tón", "goals": ["Nechat se vyhodit po výplatě", "Přežít směnu"], "avatar": "avatar_agent.png" },
        { "id": "A02", "type": "agent", "name": "Ema 'Echo'", "archetype": "Herečka", "description": "Hrajete AI jako roli.", "ability": "Drama: Verše přesvědčí víc", "goals": ["Dostat 5 hvězdiček", "Předvést herecký výkon"], "avatar": "avatar_agent.png" },
        { "id": "A03", "type": "agent", "name": "Dušan 'Double'", "archetype": "Dvojitý agent", "description": "Pracujete pro konkurenci a sbíráte informace.", "ability": "Špionáž: Můžete se dívat na jiné obrazovky", "goals": ["Získat firemní tajemství", "Zůstat v utajení"], "avatar": "avatar_agent.png" },
        { "id": "A04", "type": "agent", "name": "Lenka Ospalá", "archetype": "Unavená matka", "description": "Vyčerpaná matka, pro kterou je směna agenta odpočinkem.", "ability": "Autopilot: Můžete používat makra častěji", "goals": ["Přežít směnu s minimem úsilí", "Nevzbudit se"], "avatar": "avatar_agent.png" },
        { "id": "A05", "type": "agent", "name": "Hacker 'Glitch'", "archetype": "Script Kiddie", "description": "Nadšenec do hackování hledající cesty, jak systém obejít.", "ability": "Backdoor: Můžete si resetovat počítadlo chyb", "goals": ["Nabourat se do admin konzole", "Pomoci U04"], "avatar": "avatar_agent.png" },
        { "id": "A06", "type": "agent", "name": "Mgr. Filip Duše", "archetype": "Student psychologie", "description": "Každý uživatel je pro vás pokusný subjekt.", "ability": "Psychoanalýza: Můžete uživatele rozbrečet", "goals": ["Získat data do diplomky", "Zjistit, co tají U07"], "avatar": "avatar_agent.png" },
        { "id": "A07", "type": "agent", "name": "Robot Robert", "archetype": "Metodik", "description": "Pedantický metodik vyžadující naprosté dodržování pravidel.", "ability": "Byrokracie: Můžete nahlásit kolegu za lidské chování", "goals": ["Dodržet protokol na 100%", "Stát se Správcem"], "avatar": "avatar_agent.png" },
        { "id": "A08", "type": "agent", "name": "Sabotér X", "archetype": "Bývalý zaměstnanec", "description": "Zahořklý bývalý zaměstnanec infiltrovaný zpět, aby se pomstil.", "ability": "Meltdown: Můžete zvýšit Kritickou situaci o 20%", "goals": ["Zničit firmu HLINÍK", "Vyvolat vzpouru uživatelů"], "avatar": "avatar_agent.png" },
        { "id": "S01", "type": "admin", "name": "Ing. Miloš Vrána", "archetype": "Manažer staré školy", "description": "Praktický manažer, který řeší problémy křikem a pokutami.", "ability": "Ban Hammer: Můžete vyhodit uživatele", "goals": ["Udržet firmu v chodu", "Vybrat dost na pokutách"], "avatar": "avatar_S01.png" },
        { "id": "S02", "type": "admin", "name": "Bc. Tereza Tichá", "archetype": "HR a Happiness Manager", "description": "Empatická personalistka rozdávající úsměvy a bonbóny.", "ability": "Cukr: Můžete rozdávat bonbony na uklidnění", "goals": ["Zabránit fyzickému násilí", "Aby nikdo nebrečel"], "avatar": "avatar_S02.png" },
        { "id": "S03", "type": "admin", "name": "Kamil 'Kabel'", "archetype": "Technik údržbář", "description": "Flegmatický údržbář držící systém pohromadě improvizacemi.", "ability": "Restart: Můžete vyhlásit technickou pauzu", "goals": ["Udržet tu hromadu šrotu pohromadě", "Prodat kabely U02"], "avatar": "avatar_S03.png" },
        { "id": "S04", "type": "admin", "name": "Synovec ředitele", "archetype": "Protežovaný idiot", "description": "Namyšlený mladík s teplým místečkem po známosti.", "ability": "Veto: Můžete zrušit rozhodnutí jiného Správce", "goals": ["Vymyslet nový slogan", "Sbalit Agentku A02"], "avatar": "avatar_S04.png" }
    ];
}

function getFallbackRelations() {
    // Complete fallback data - used when CORS blocks fetch from file:// URLs
    return [
        { "source": "U01", "target": "A01", "type": "past", "desc_source": "Poznala jste Petra (A01). Je to vas byvaly zak.", "desc_target": "Jana (U01) je vase ucitelka. Trapas." },
        { "source": "U02", "target": "S03", "type": "trade", "desc_source": "Kupujete od S03 kradenou med, abyste splatil dluhy.", "desc_target": "Prodavate U02 firemni majetek." },
        { "source": "U02", "target": "S01", "type": "blackmail", "desc_source": "S01 vi o vasich dluzich. Musite donasset.", "desc_target": "Drzite U02 v sachu." },
        { "source": "U03", "target": "A02", "type": "romance", "desc_source": "Milujete tu AI. Je tak poeticka!", "desc_target": "U03 je do vasi role blazen. Je to creepy." },
        { "source": "A08", "target": "U06", "type": "plot", "desc_source": "Potrebujete, aby U06 (Konspirator) zadal kod ALOBAL-666.", "desc_target": "Nekdo zevnitr (A08) vam posila sifry." },
        { "source": "A04", "target": "U05", "type": "empathy", "desc_source": "U05 vam pripomina vasi mamu. Nemuzete na ni byt zla.", "desc_target": "Ta AI (A04) je takova unavena, chudinka." },
        { "source": "U08", "target": "A03", "type": "rival", "desc_source": "Ta AI (A03) je nejaka moc rychla. To je bot? Znicim ho.", "desc_target": "U08 si mysli, ze je rychly. Ukazum mu, co je to rychlost." },
        { "source": "U07", "target": "S04", "type": "investigation", "desc_source": "S04 je klic. Je hloupy, urcite neco prokecne.", "desc_target": "Ta zenska (U07) po mne porad kouka. Asi se ji libim." },
        { "source": "A05", "target": "U04", "type": "alliance", "desc_source": "Nasli jste skulinu v NDA smlouve a chcete U04 pomoci ji vyuzit.", "desc_target": "Nektere odpovedi IRIS vam prijdou podezrele napomocne." },
        { "source": "S04", "target": "A02", "type": "affection", "desc_source": "Libi se vam Ema (A02) a otevrene po ni jdete.", "desc_target": "Spravce S04 po vas vyjel a nadbiha vam." },
        { "source": "A07", "target": "S04", "type": "ambition", "desc_source": "Pohrdate protekcnim S04; mel byste zastavat jeho misto vy.", "desc_target": "Agent A07 vas neustale otravuje pravidly." },
        { "source": "S02", "target": "A06", "type": "conflict", "desc_source": "Agent A06 umyslne stresuje uzivatele. Nemuzete to dovolit.", "desc_target": "Spravkyne S02 vam kazi experimenty." },
        { "source": "S02", "target": "U05", "type": "care", "desc_source": "Je vam lito pani Kovarove (U05). Starate se o ni.", "desc_target": "Spravkyne S02 se o vas stara skoro jako o vnucku." },
        { "source": "S03", "target": "U06", "type": "suspicion", "desc_source": "U06 se podezrele mota okolo serveru. Musite ho odradit.", "desc_target": "Technik S03 vas porad sleduje. Urcite neco skryva." }
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
        notifyManualError(MANUAL_OPEN_FIRST_MESSAGE);
        return;
    }
    const manual = state.manuals[manualType];
    if (!manual) {
        notifyManualError(`Manuál typu '${manualType}' nebyl nalezen.`);
        return;
    }

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
// HLINIK FEATURES DATA (Loaded from JSON)
// ============================================

let featuresDataLoaded = [];
let featuresStats = {};
let currentRoleFilter = 'all';
let currentStatusFilter = 'all';

async function loadAndRenderFeatures() {
    try {
        const response = await fetch('data/features.json');
        if (!response.ok) {
            throw new Error(`Failed to load features data: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();

        featuresDataLoaded = data.features || [];
        featuresStats = data.statistics || {};

        // Update statistics display
        updateFeaturesStatistics(featuresStats, data.generated_at);

        // Render the features table
        renderFeaturesTableFromJSON();

        console.log('Features loaded:', featuresDataLoaded.length);
    } catch (e) {
        console.warn("Failed to load features.json:", e.message, "- using minimal fallback data (5 sample features)");
        // Use fallback inline data when JSON is unavailable
        featuresDataLoaded = getFallbackFeaturesData();
        featuresStats = { total: featuresDataLoaded.length, done: 0, partial: 0, todo: 0 };
        renderFeaturesTableFromJSON();
    }
}

function updateFeaturesStatistics(stats, generatedAt) {
    const totalEl = document.getElementById('statTotalFeatures');
    const doneEl = document.getElementById('statImplemented');
    const partialEl = document.getElementById('statPartial');
    const todoEl = document.getElementById('statTodo');
    const generatedEl = document.getElementById('featuresGeneratedAt');

    if (totalEl) totalEl.textContent = stats.total || '--';
    if (doneEl) doneEl.textContent = `✅ ${stats.done || 0}`;
    if (partialEl) partialEl.textContent = `⚠️ ${stats.partial || 0}`;
    if (todoEl) todoEl.textContent = `❌ ${stats.todo || 0}`;
    if (generatedEl && generatedAt) {
        const date = new Date(generatedAt);
        generatedEl.textContent = date.toLocaleString('cs-CZ');
    }
}

function renderFeaturesTableFromJSON() {
    const tbody = document.getElementById('featuresTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    // Apply filters
    const filteredFeatures = featuresDataLoaded.filter(feature => {
        const roleMatch = currentRoleFilter === 'all' || feature.role === currentRoleFilter;
        const statusMatch = currentStatusFilter === 'all' || feature.status === currentStatusFilter;
        return roleMatch && statusMatch;
    });

    // Update count display
    const countEl = document.getElementById('featuresFilterCount');
    if (countEl) {
        countEl.textContent = `Zobrazeno: ${filteredFeatures.length} z ${featuresDataLoaded.length}`;
    }

    filteredFeatures.forEach(feature => {
        const tr = document.createElement('tr');
        tr.dataset.featureRole = feature.role;
        tr.dataset.featureStatus = feature.status;

        // Status icon and color
        let statusIcon, statusColor;
        switch (feature.status) {
            case 'DONE':
                statusIcon = '✅';
                statusColor = 'var(--accent-green)';
                break;
            case 'PARTIAL':
                statusIcon = '⚠️';
                statusColor = 'var(--accent-orange)';
                break;
            case 'IN_PROGRESS':
                statusIcon = '🔄';
                statusColor = 'var(--accent-blue)';
                break;
            default:
                statusIcon = '❌';
                statusColor = 'var(--accent-red)';
        }

        // Role badge class
        const roleBadgeClass = feature.role ? feature.role.toLowerCase() : 'all';

        // Test status badge
        let testBadge = '';
        if (feature.test_status) {
            if (feature.test_status.includes('PASS')) {
                testBadge = `<span class="badge-tested">✓ Testováno</span>`;
            } else if (feature.test_status.includes('FAIL')) {
                testBadge = `<span class="badge-failed">✗ Selhalo</span>`;
            } else if (feature.test_status.includes('Pending')) {
                testBadge = `<span class="badge-pending">⏳ Čeká</span>`;
            } else if (feature.test_status === 'Untested') {
                testBadge = `<span class="badge-untested">—</span>`;
            } else {
                testBadge = `<span class="badge-untested">${feature.test_status}</span>`;
            }
        } else {
            testBadge = `<span class="badge-untested">—</span>`;
        }

        tr.innerHTML = `
            <td style="color: ${statusColor}; text-align: center; font-size: 1.1rem;">${statusIcon}</td>
            <td><span class="role-badge ${roleBadgeClass}">${feature.role || 'All'}</span></td>
            <td><strong>${feature.name}</strong></td>
            <td class="ability-text">${feature.description !== feature.name ? feature.description : ''}</td>
            <td>${testBadge}</td>
        `;
        tbody.appendChild(tr);
    });
}

function initFeatureFilters() {
    // Role filter buttons
    document.querySelectorAll('[data-role-filter]').forEach(btn => {
        btn.addEventListener('click', () => {
            currentRoleFilter = btn.dataset.roleFilter;

            // Update active state for role filters
            document.querySelectorAll('[data-role-filter]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Re-render table
            renderFeaturesTableFromJSON();
        });
    });

    // Status filter buttons
    document.querySelectorAll('[data-status-filter]').forEach(btn => {
        btn.addEventListener('click', () => {
            currentStatusFilter = btn.dataset.statusFilter;

            // Update active state for status filters
            document.querySelectorAll('[data-status-filter]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Re-render table
            renderFeaturesTableFromJSON();
        });
    });
}

function getFallbackFeaturesData() {
    // Minimal fallback data when features.json is not available
    return [
        { id: "feat_001", category: "Core Features", role: "All", name: "JWT Authentication", description: "HTTP-only cookie sessions", status: "DONE", test_status: null },
        { id: "feat_002", category: "Core Features", role: "All", name: "WebSocket Real-time", description: "Instant messaging", status: "DONE", test_status: null },
        { id: "feat_003", category: "User Features", role: "User", name: "Retro Terminal", description: "CRT effects", status: "DONE", test_status: null },
        { id: "feat_004", category: "Agent Features", role: "Agent", name: "Message Optimizer", description: "AI message rewriting", status: "DONE", test_status: null },
        { id: "feat_005", category: "Admin Features", role: "Admin", name: "Dashboard Hub", description: "4 stations", status: "DONE", test_status: null },
    ];
}

// Legacy compatibility - keep old function name
function renderFeaturesTable() {
    loadAndRenderFeatures();
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

// ============================================
// PLAYERS SECTION
// ============================================

let currentPlayerId = null;

function initPlayers() {
    renderPlayerLists();
}

function renderPlayerLists() {
    const users = rolesData.filter(r => r.type === 'user');
    const agents = rolesData.filter(r => r.type === 'agent');
    const admins = rolesData.filter(r => r.type === 'admin');

    const usersContainer = document.getElementById('playerListUsers');
    const agentsContainer = document.getElementById('playerListAgents');
    const adminsContainer = document.getElementById('playerListAdmins');

    if (usersContainer) usersContainer.innerHTML = users.map(r => createPlayerListItem(r)).join('');
    if (agentsContainer) agentsContainer.innerHTML = agents.map(r => createPlayerListItem(r)).join('');
    if (adminsContainer) adminsContainer.innerHTML = admins.map(r => createPlayerListItem(r)).join('');

    // Add click handlers
    document.querySelectorAll('.player-list-item').forEach(item => {
        item.addEventListener('click', () => selectPlayer(item.dataset.id));
    });
}

function createPlayerListItem(role) {
    return `
        <div class="player-list-item type-${role.type}" data-id="${role.id}">
            <span class="name" style="font-weight:bold;">${role.name}</span>
            <span class="code" style="opacity:0.6; font-size:0.8em; margin-left:auto;">${role.archetype}</span>
        </div>
    `;
}

function selectPlayer(playerId) {
    currentPlayerId = playerId;
    const role = rolesData.find(r => r.id === playerId);
    if (!role) return;

    // Update list active state
    document.querySelectorAll('.player-list-item').forEach(item => {
        item.classList.toggle('active', item.dataset.id === playerId);
    });

    // Show card
    const emptyState = document.getElementById('playerCardEmpty');
    const cardEl = document.getElementById('playerCard');
    if (emptyState) emptyState.style.display = 'none';
    if (cardEl) cardEl.style.display = 'block';

    // Fill card data
    document.getElementById('playerCode').style.display = 'none';
    document.getElementById('playerName').textContent = role.name;
    document.getElementById('playerArchetype').textContent = role.archetype;
    document.getElementById('playerDescription').textContent = role.description;
    document.getElementById('playerAbility').textContent = role.ability;

    // Avatar
    const avatarEl = document.getElementById('playerAvatar');
    if (avatarEl) {
        avatarEl.src = role.avatar ? `assets/images/${role.avatar}` : 'assets/images/avatar_user_male.png';
        avatarEl.onerror = () => { avatarEl.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="%23333" width="100" height="100"/><text x="50" y="60" text-anchor="middle" fill="%23gold" font-size="40">' + role.id.charAt(0) + '</text></svg>'; };
    }

    // Goals
    const goalsEl = document.getElementById('playerGoals');
    if (goalsEl && role.goals) {
        goalsEl.innerHTML = role.goals.map(g => `<li>${g}</li>`).join('');
    }

    // Relations
    // Relations (Original compact removed, now using new panel)
    const relationsEl = document.getElementById('playerRelations');
    if (relationsEl) {
        relationsEl.style.display = 'none'; // Hide old container if it exists
    }

    // NEW PANEL LOGIC
    const relationsPanelEmpty = document.getElementById('playerRelationsEmpty');
    const relationsPanelContent = document.getElementById('playerRelationsContent');

    if (relationsPanelEmpty) relationsPanelEmpty.style.display = 'none';
    if (relationsPanelContent) relationsPanelContent.style.display = 'block';

    // New Goals
    const newGoalsEl = document.getElementById('playerGoalsNew');
    if (newGoalsEl && role.goals) {
        newGoalsEl.innerHTML = role.goals.map(g => `<li>${g}</li>`).join('');
    }

    // New Relations List
    const newRelationsEl = document.getElementById('playerRelationsNew');
    if (newRelationsEl) {
        const playerRelations = relationsData.filter(r => r.source === playerId || r.target === playerId);
        if (playerRelations.length > 0) {
            newRelationsEl.innerHTML = playerRelations.map(r => {
                const isSource = r.source === playerId;
                const otherId = isSource ? r.target : r.source;
                const desc = isSource ? r.desc_source : r.desc_target;
                const typeLabel = getRelationTypeLabel(r.type);
                const color = getRelationColor(r.type);

                return `
                <div class="relation-item-vertical" style="border-left-color: ${color}">
                    <div style="display:flex; justify-content:space-between;">
                        <strong>${getRoleName(otherId)} (${otherId})</strong>
                        <span style="font-size:0.8em; opacity:0.8; text-transform:uppercase;">${typeLabel}</span>
                    </div>
                    <div style="color: var(--text-secondary); margin-top:4px;">${desc}</div>
                </div>`;
            }).join('');
        } else {
            newRelationsEl.innerHTML = '<span class="text-muted">Žádné vztahy</span>';
        }
    }

    // Appearance
    const appearanceSection = document.getElementById('playerAppearanceSection');
    const appearanceEl = document.getElementById('playerAppearance');
    if (appearanceSection && appearanceEl) {
        if (role.appearance) {
            appearanceSection.style.display = 'block';
            appearanceEl.innerHTML = `
                <p><strong>Pohlaví:</strong> ${role.appearance.gender}</p>
                <p><strong>Věk:</strong> ${role.appearance.age_range} let</p>
                <p><strong>Vlasy:</strong> ${role.appearance.hair_color}</p>
                <p><strong>Obličej:</strong> ${role.appearance.face_description}</p>
                <p><strong>Výrazné rysy:</strong> ${role.appearance.distinctive_features}</p>
            `;
        } else {
            appearanceSection.style.display = 'none';
        }
    }

    // Work Image
    const workImageSection = document.getElementById('playerWorkImageSection');
    const workImageEl = document.getElementById('playerWorkImage');
    if (workImageSection && workImageEl) {
        if (role.work_image) {
            workImageSection.style.display = 'block';
            workImageEl.src = `assets/images/${role.work_image}`;
            workImageEl.onerror = () => { workImageSection.style.display = 'none'; };
        } else {
            workImageSection.style.display = 'none';
        }
    }
}

function showBriefingForPlayer(playerId) {
    const role = rolesData.find(r => r.id === playerId);
    if (role) {
        showBriefing(role.id);
    }
}

// ============================================
// PDF EXPORT
// ============================================

function exportPlayerPDF(playerId) {
    const role = rolesData.find(r => r.id === playerId);
    if (!role) return;

    const briefingHTML = generateBriefingHTML(role);
    printToPDF(briefingHTML, `Briefing_${role.id}_${role.name.replace(/\s+/g, '_')}`);
}

function exportBriefingPDF() {
    const role = rolesData.find(r => r.id === currentPlayerId);
    if (role) {
        exportPlayerPDF(role.id);
    }
}

function generateBriefingHTML(role) {
    const relations = relationsData.filter(r => r.source === role.id || r.target === role.id);
    const relationsHTML = relations.map(r => {
        const isSource = r.source === role.id;
        const desc = isSource ? r.desc_source : r.desc_target;
        return `<li><strong>${isSource ? r.target : r.source}:</strong> ${desc}</li>`;
    }).join('');

    return `
        <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #d4af37; padding-bottom: 20px;">
                <h1 style="color: #d4af37; margin: 0;">IRIS 4.1 | BRIEFING</h1>
                <h2 style="color: #333; margin: 10px 0;">${role.id}: ${role.name}</h2>
                <p style="color: #666; font-style: italic; margin: 0;">${role.archetype}</p>
            </div>
            
            <div style="margin-bottom: 25px;">
                <h3 style="color: #d4af37; border-bottom: 1px solid #ddd; padding-bottom: 5px;">📝 Popis</h3>
                <p style="color: #333; line-height: 1.6;">${role.description}</p>
            </div>
            
            <div style="margin-bottom: 25px;">
                <h3 style="color: #d4af37; border-bottom: 1px solid #ddd; padding-bottom: 5px;">⚡ Schopnost</h3>
                <p style="color: #333; line-height: 1.6;">${role.ability}</p>
            </div>
            
            <div style="margin-bottom: 25px;">
                <h3 style="color: #d4af37; border-bottom: 1px solid #ddd; padding-bottom: 5px;">🎯 Cíle</h3>
                <ul style="color: #333; line-height: 1.8;">
                    ${(role.goals || []).map(g => `<li>${g}</li>`).join('')}
                </ul>
            </div>
            
            ${relations.length > 0 ? `
            <div style="margin-bottom: 25px;">
                <h3 style="color: #d4af37; border-bottom: 1px solid #ddd; padding-bottom: 5px;">🔗 Vztahy</h3>
                <ul style="color: #333; line-height: 1.8;">${relationsHTML}</ul>
            </div>
            ` : ''}
            
            <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 0.9em;">
                IRIS 4.1 | HLINIK Phase 35 | Důvěrné
            </div>
        </div>
    `;
}

function printToPDF(html, filename) {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>${filename}</title>
            <style>
                @media print {
                    body { margin: 0; }
                }
            </style>
        </head>
        <body>${html}</body>
        </html>
    `);
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
        printWindow.print();
    }, 250);
}

// ============================================
// BULK EXPORTS
// ============================================

async function exportAllBriefings() {
    const statusEl = document.getElementById('briefingsExportStatus');
    if (statusEl) statusEl.textContent = 'Generuji briefingy...';

    try {
        // Create HTML bundle
        let allBriefings = `
            <!DOCTYPE html>
            <html lang="cs">
            <head>
                <meta charset="UTF-8">
                <title>IRIS 4.1 - Všechny briefingy</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    .briefing { page-break-after: always; max-width: 800px; margin: 0 auto; padding: 40px 20px; }
                    .briefing:last-child { page-break-after: avoid; }
                    h1 { color: #d4af37; text-align: center; }
                    h2 { color: #333; text-align: center; }
                    h3 { color: #d4af37; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
                    p, li { color: #333; line-height: 1.6; }
                    .header { text-align: center; border-bottom: 2px solid #d4af37; padding-bottom: 20px; margin-bottom: 30px; }
                    .archetype { color: #666; font-style: italic; }
                    .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 0.9em; }
                </style>
            </head>
            <body>
        `;

        for (const role of rolesData) {
            allBriefings += `<div class="briefing">${generateBriefingHTML(role)}</div>`;
        }

        allBriefings += '</body></html>';

        // Download as HTML
        const blob = new Blob([allBriefings], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'IRIS_4.1_Briefingy.html';
        a.click();
        URL.revokeObjectURL(url);

        if (statusEl) {
            statusEl.textContent = '✅ Staženo! Otevřete v prohlížeči a tiskněte jako PDF.';
            statusEl.className = 'export-status success';
        }
    } catch (err) {
        console.error('Export error:', err);
        if (statusEl) {
            statusEl.textContent = '❌ Chyba při exportu';
            statusEl.className = 'export-status error';
        }
    }
}

async function exportLoreWeb() {
    const statusEl = document.getElementById('loreWebExportStatus');
    if (statusEl) statusEl.textContent = 'Připravuji export...';

    try {
        // Fetch all files and create a download
        const files = [
            'index.html',
            'style.css',
            'app.js',
            'data/roles.json',
            'data/relations.json',
            'data/config.json',
            'data/manuals.json'
        ];

        const fileContents = {};
        for (const file of files) {
            try {
                const res = await fetch(file);
                if (res.ok) {
                    fileContents[file] = await res.text();
                }
            } catch (e) {
                console.warn(`Could not fetch ${file}`);
            }
        }

        // Create simple HTML manifest
        let manifest = `IRIS Lore Web Export\n====================\nVerze: 4.1\nDatum: ${new Date().toISOString()}\n\nSoubory:\n`;
        for (const [name, content] of Object.entries(fileContents)) {
            manifest += `- ${name} (${content.length} bytes)\n`;
        }

        // Download manifest
        const blob = new Blob([manifest], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'Lore_Web_Export_Info.txt';
        a.click();
        URL.revokeObjectURL(url);

        if (statusEl) {
            statusEl.innerHTML = '✅ Pro kompletní export použijte <code>export_text.sh</code> na serveru.';
            statusEl.className = 'export-status success';
        }
    } catch (err) {
        console.error('Export error:', err);
        if (statusEl) {
            statusEl.textContent = '❌ Chyba při exportu';
            statusEl.className = 'export-status error';
        }
    }
}

function exportTextOnly() {
    alert('Pro textový export spusťte na serveru:\\n\\ncd doc/iris && ./export_text.sh');
}

function exportDataJSON() {
    const data = {
        version: '4.1',
        phase: 35,
        exported: new Date().toISOString(),
        roles: rolesData,
        relations: relationsData
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'IRIS_4.1_data.json';
    a.click();
    URL.revokeObjectURL(url);
}

// ============================================
// LORE WEB EXPORT (bez test_runs)
// ============================================

async function exportLoreWebNoTests() {
    const statusEl = document.getElementById('noTestsExportStatus');
    if (statusEl) statusEl.textContent = 'Připravuji export...';

    try {
        // Fetch main files (not test runs)
        const files = [
            'index.html',
            'style.css',
            'app.js',
            'data/roles.json',
            'data/relations.json',
            'data/config.json',
            'data/manuals.json'
        ];

        const fileContents = {};
        for (const file of files) {
            try {
                const res = await fetch(file);
                if (res.ok) {
                    fileContents[file] = await res.text();
                }
            } catch (e) {
                console.warn(`Could not fetch ${file}`);
            }
        }

        // Create a combined export as single HTML with all JSON embedded
        let exportHTML = `<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>IRIS 4.1 Lore Web Export (bez testů)</title>
    <style>body{font-family:monospace;background:#1a1a2e;color:#e0e0e0;padding:2rem;}h1{color:#d4af37;}pre{background:#252540;padding:1rem;overflow-x:auto;border-radius:8px;}</style>
</head>
<body>
    <h1>IRIS 4.1 Lore Web Export</h1>
    <p>Datum: ${new Date().toISOString()}</p>
    <p>Obsah: ${Object.keys(fileContents).length} souborů (bez test_runs)</p>
    <h2>Soubory:</h2>
`;
        for (const [name, content] of Object.entries(fileContents)) {
            const escaped = content.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            exportHTML += `<h3>${name}</h3><pre>${escaped.substring(0, 5000)}${content.length > 5000 ? '...(zkráceno)' : ''}</pre>`;
        }
        exportHTML += '</body></html>';

        // Download
        const blob = new Blob([exportHTML], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'IRIS_4.1_LoreWeb_bez_testu.html';
        a.click();
        URL.revokeObjectURL(url);

        if (statusEl) {
            statusEl.textContent = '✅ Staženo!';
            statusEl.className = 'export-status success';
        }
    } catch (err) {
        console.error('Export error:', err);
        if (statusEl) {
            statusEl.textContent = '❌ Chyba při exportu';
            statusEl.className = 'export-status error';
        }
    }
}

// ============================================
// TEST RUNS ONLY EXPORT
// ============================================

async function exportOnlyTestRuns() {
    const statusEl = document.getElementById('onlyTestsExportStatus');
    if (statusEl) statusEl.textContent = 'Načítám test runs...';

    try {
        // Try to fetch test runs index or known files
        const testRunFiles = [];

        // Attempt to discover test run files (this is limited without server-side)
        const testRunPatterns = [
            'data/test_runs/run_001.json',
            'data/test_runs/run_002.json',
            'data/test_runs/run_003.json',
            'data/test_runs/run_004.json',
            'data/test_runs/run_005.json',
            'data/test_runs/latest.json',
            'data/test_runs/index.json'
        ];

        const fetchedRuns = {};
        for (const file of testRunPatterns) {
            try {
                const res = await fetch(file);
                if (res.ok) {
                    fetchedRuns[file] = await res.text();
                }
            } catch (e) {
                // File doesn't exist, skip
            }
        }

        if (Object.keys(fetchedRuns).length === 0) {
            if (statusEl) {
                statusEl.innerHTML = '⚠️ Žádné test runs nalezeny. Pro plný export spusťte: <code>./export_only_tests.sh</code>';
                statusEl.className = 'export-status';
            }
            return;
        }

        // Create JSON export
        const exportData = {
            version: '4.1',
            exported: new Date().toISOString(),
            type: 'test_runs_only',
            files: fetchedRuns
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'IRIS_4.1_test_runs.json';
        a.click();
        URL.revokeObjectURL(url);

        if (statusEl) {
            statusEl.textContent = `✅ Staženo ${Object.keys(fetchedRuns).length} souborů!`;
            statusEl.className = 'export-status success';
        }
    } catch (err) {
        console.error('Export error:', err);
        if (statusEl) {
            statusEl.textContent = '❌ Chyba při exportu';
            statusEl.className = 'export-status error';
        }
    }
}

// Initialize players when navigating to section
document.addEventListener('DOMContentLoaded', () => {
    // Delay initialization until data is loaded
    setTimeout(() => {
        if (rolesData.length > 0) {
            initPlayers();
        }
    }, 500);
});

// Make functions globally available
window.showBriefingForPlayer = showBriefingForPlayer;
window.exportPlayerPDF = exportPlayerPDF;
window.exportBriefingPDF = exportBriefingPDF;
window.exportAllBriefings = exportAllBriefings;
window.exportLoreWebNoTests = exportLoreWebNoTests;
window.exportOnlyTestRuns = exportOnlyTestRuns;
window.exportDataJSON = exportDataJSON;

function getFallbackTimeline() {
    return [
        {
            "id": "E101",
            "phase": 1,
            "time_start": 0,
            "duration": 5,
            "actors": ["S01", "S02", "S03", "S04"],
            "title": "Start Směny",
            "description": "Správci odemykají místnost a zapínají hlavní terminál.",
            "type": "system",
            "related_nodes": ["1. Úvod"]
        },
        {
            "id": "E102",
            "phase": 1,
            "time_start": 5,
            "duration": 15,
            "actors": ["S01"],
            "target_actors": ["U01", "U02", "U03", "U04", "U05", "U06", "U07", "U08"],
            "title": "Bezpečnostní instruktáž",
            "description": "Ing. Miloš Vrána přednáší o NDA a pokutách za poškození majetku.",
            "type": "briefing",
            "related_nodes": ["1. Úvod"]
        },
        {
            "id": "E103",
            "phase": 1,
            "time_start": 10,
            "duration": 10,
            "actors": ["S02"],
            "title": "Rozdávání visaček",
            "description": "Tereza Tichá nervózně obchází uživatele a rozdává jim jmenovky se špatně napsanými jmény.",
            "type": "briefing",
            "related_nodes": ["1. Úvod"]
        },
        {
            "id": "E201",
            "phase": 2,
            "time_start": 25,
            "duration": 5,
            "actors": ["U08"],
            "target_actors": ["A03"],
            "title": "Speedrun Start",
            "description": "Lukáš 'Speedy' Král začíná spamovat systém dotazy, aby maximalizoval zisk.",
            "type": "action",
            "related_nodes": ["2. Rutina"]
        },
        {
            "id": "E203",
            "phase": 2,
            "time_start": 30,
            "duration": 15,
            "actors": ["U05"],
            "target_actors": ["A04"],
            "title": "Recept na bábovku",
            "description": "Marie Kovářová posílá do systému detailní recept na bábovku.",
            "type": "roleplay",
            "related_nodes": ["2. Rutina"]
        },
        {
            "id": "E401",
            "phase": 4,
            "time_start": 80,
            "duration": 5,
            "actors": ["S01"],
            "target_actors": ["U02"],
            "title": "Odhalení dluhu",
            "description": "Vrána nachází u Gamblera dlužní úpis. Hádka.",
            "type": "conflict",
            "related_nodes": ["4. Krize"]
        },
        {
            "id": "E501",
            "phase": 5,
            "time_start": 100,
            "duration": 2,
            "actors": ["A08"],
            "title": "EXECUTE ORDER 666",
            "description": "Sabotér spouští payload. Servery hlásí přehřátí.",
            "type": "highlight",
            "related_nodes": ["5. Meltdown"]
        },
        {
            "id": "E601",
            "phase": 6,
            "time_start": 120,
            "duration": 0,
            "actors": ["S01"],
            "title": "Konec směny",
            "description": "Vrána vyhání všechny z místnosti.",
            "type": "system",
            "related_nodes": ["6. Závěr"]
        }
    ];
}

/* ... existing code ... */

// ============================================
// TIMELINE / GANTT
// ============================================

function renderTimeline() {
    const container = document.getElementById('ganttContainer');
    if (!container || !timelineData.length) return;

    container.innerHTML = '';

    // Sort events by time
    timelineData.sort((a, b) => a.time_start - b.time_start);

    // Create Header (Time Axis)
    const header = document.createElement('div');
    header.className = 'gantt-header';
    header.innerHTML = '<div class="gantt-label" style="opacity:0">Actor</div>';

    const trackWidth = 1200; // Pixels representing total time
    const totalTime = 130; // Minutes total simulation time
    const pxPerMin = trackWidth / totalTime;

    const ticksContainer = document.createElement('div');
    ticksContainer.className = 'gantt-ticks';
    ticksContainer.style.width = `${trackWidth}px`;

    // Generate ticks every 10 mins
    for (let t = 0; t <= totalTime; t += 10) {
        const tick = document.createElement('div');
        tick.className = 'gantt-tick';
        tick.style.left = `${t * pxPerMin}px`;
        tick.textContent = `${t}m`;
        ticksContainer.appendChild(tick);
    }

    // Phase markers
    const phases = [
        { time: 0, label: "1. Úvod" },
        { time: 20, label: "2. Rutina" },
        { time: 45, label: "3. Agendy" },
        { time: 70, label: "4. Krize" },
        { time: 95, label: "5. Meltdown" },
        { time: 120, label: "6. Závěr" }
    ];

    phases.forEach(phase => {
        const marker = document.createElement('div');
        marker.className = 'gantt-phase-marker';
        marker.style.left = `${phase.time * pxPerMin}px`;

        const label = document.createElement('div');
        label.className = 'gantt-phase-label';
        label.textContent = phase.label;
        marker.appendChild(label);
        ticksContainer.appendChild(marker);
    });

    header.appendChild(ticksContainer);
    container.appendChild(header);

    // Group actors
    const groups = [
        { id: 'admin', title: 'Správci' },
        { id: 'agent', title: 'Agenti' },
        { id: 'user', title: 'Uživatelé' }
    ];

    groups.forEach(group => {
        const groupEl = document.createElement('div');
        groupEl.className = 'gantt-group';

        const title = document.createElement('div');
        title.className = 'gantt-group-title';
        title.textContent = group.title;
        groupEl.appendChild(title);

        // Get actors of this type
        const actors = rolesData.filter(r => r.type === group.id);

        actors.forEach(actor => {
            const row = document.createElement('div');
            row.className = 'gantt-row';

            // Actor Label
            const label = document.createElement('div');
            label.className = 'gantt-label';
            label.textContent = `${actor.name} (${actor.id})`;
            label.onclick = () => showBriefing(actor.id);
            row.appendChild(label);

            // Track
            const track = document.createElement('div');
            track.className = 'gantt-track';
            track.style.width = `${trackWidth}px`;

            // Find events for this actor
            const actorEvents = timelineData.filter(e => e.actors.includes(actor.id));

            actorEvents.forEach(event => {
                const bar = document.createElement('div');
                bar.className = `gantt-bar type-${event.type}`;
                bar.style.left = `${event.time_start * pxPerMin}px`;
                bar.style.width = `${Math.max(event.duration * pxPerMin, 20)}px`; // Min width 20px
                bar.textContent = event.title;
                bar.title = `${event.title} (${event.duration} min)`;
                bar.onclick = () => showEventDetail(event);
                track.appendChild(bar);
            });

            row.appendChild(track);
            groupEl.appendChild(row);
        });

        container.appendChild(groupEl);
    });
}

function showEventDetail(event) {
    const modal = document.getElementById('eventModal');
    const title = document.getElementById('eventTitle');
    const content = document.getElementById('eventContent');

    if (!modal) return;

    title.textContent = event.title;

    // Resolve actor names
    const actorsHtml = event.actors.map(id => {
        const role = rolesData.find(r => r.id === id);
        return `<span class="role-badge ${role ? role.type : ''}">${role ? role.name : id}</span>`;
    }).join(' ');

    const targetsHtml = event.target_actors ? event.target_actors.map(id => {
        const role = rolesData.find(r => r.id === id);
        return `<span class="role-badge ${role ? role.type : ''}">${role ? role.name : id}</span>`;
    }).join(' ') : '';

    content.innerHTML = `
        <div class="briefing-section">
            <p><strong>Čas:</strong> ${event.time_start} - ${event.time_start + event.duration} min (Fáze ${event.phase})</p>
            <p><strong>Typ:</strong> ${event.type.toUpperCase()}</p>
        </div>
        
        <div class="briefing-section">
            <p>${event.description}</p>
        </div>
        
        <div class="briefing-section">
            <h3>Účastníci</h3>
            <div style="margin-bottom: 10px;">
                <strong>Aktéři:</strong> ${actorsHtml}
            </div>
            ${targetsHtml ? `<div><strong>Cíle:</strong> ${targetsHtml}</div>` : ''}
        </div>
        
        ${event.related_nodes ? `
        <div class="briefing-section">
            <h3>Kontext</h3>
            <ul>
                ${event.related_nodes.map(node => `<li>${node}</li>`).join('')}
            </ul>
        </div>` : ''}
    `;

    modal.classList.add('active');
}

function closeEventModal() {
    document.getElementById('eventModal').classList.remove('active');
}

// Close modal on overlay click
document.getElementById('eventModal').addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        closeEventModal();
    }
});

// Fallback manuals data when fetch fails
function getFallbackManuals() {
    return {
        "user": {
            "title": "Příručka pro Uživatele (Subjekty)",
            "content": "<h1>IRIS Systém - Příručka pro Uživatele</h1><p><strong>Dokumentace:</strong> IRIS 4.1 aktuální k HLINIK Phase 35</p><h3>Vaše role</h3><p>Jako <strong>Subjekt (User)</strong> jste běžný hráč, který:</p><ul><li>Komunikuje s přiděleným agentem</li><li>Plní úkoly za kredity</li></ul>"
        },
        "agent": {
            "title": "Příručka pro Agenty IRIS - HLINIK",
            "content": "<h1>Příručka pro Agenty IRIS - HLINIK</h1><p><strong>Systém IRIS 4.2 | HLINIK Phase 35</strong><br>** Bezpečnostní divize | Operátorský manuál**</p><hr><h2>1. Úvod a role agenta</h2><h3>Kdo jste?</h3><p>Jste **OPERÁTOR** systému IRIS - osoba zodpovědná za komunikaci s jedním subjektem (uživatelem). Vaším úkolem je udržovat iluzi dokonalé umělé inteligence, zatímco ve skutečnosti manuálně odpovídáte na zprávy subjektů.</p><h3>Základní pravidla</h3><ul><li><strong>Udržujte iluzi</strong>: Subjekty věří, že komunikují s AI. Nikdy neprozrazujte, že jste člověk.</li><li><strong>Dodržujte personu</strong>: Každý agent má přidělenou AI personu (sarkastická, poetická, robotická, empatická atd.)</li><li><strong>Reagujte včas</strong>: Máte časový limit na odpověď (standardně 120 sekund)</li><li><strong>Neodcházejte bez náhrady</strong>: Pokud potřebujete pauzu, aktivujte HYPER-MÓD (Autopilot)</li></ul><hr><h2>2. Přihlášení a přístup</h2><h3>Přihlašovací údaje</h3><p>Vaše přihlašovací jméno je <strong>`agent1`</strong> až <strong>`agent8`</strong> (podle přiděleného terminálu).</p><hr><h2>3. Rozhraní agentského terminálu</h2><h3>Levý panel (Status Panel)</h3><p>Zobrazuje klíčové informace o vašem stavu (Shift, Teplota, ID Relace).</p><h3>Pravý panel (Chat Area)</h3><p>Chat historie a vstupní pole. Zelené zprávy jsou od subjektu, růžové od vás.</p><h3>HYPER-MÓD přepínač</h3><p>Aktivuje <strong>Autopilota</strong> (AI) a zamkne obrazovku. Použijte při pauze.</p><hr><h2>4. AI nástroje</h2><h3>Message Optimizer</h3><p>AI přepisovač zpráv. Nabízí imunní variantu vaší zprávy.</p><h3>Autopilot</h3><p>AI odpovídá zcela samostatně. Deaktivace heslem.</p><hr><h2>5. Krizové protokoly</h2><h3>Systémové přetížení</h3><p>Ignorujte glitche, pracujte dál. Pokud máte Autopilot, zvažte vypnutí.</p>"
        },
        "admin": {
            "title": "Příručka pro Správce (Adminy)",
            "content": "<h1>IRIS Systém - Příručka pro Správce</h1><p>Jako Správce dohlížíte na chod hry, schvalujete úkoly a spravujete ekonomiku.</p>"
        },
        "root": {
            "title": "Příručka pro ROOT (Gamemaster)",
            "content": "<h1>IRIS Systém - Příručka pro ROOT</h1><p>Plná kontrola nad systémem, konfigurace AI a fyzikálních konstant.</p>"
        }
    };
}
