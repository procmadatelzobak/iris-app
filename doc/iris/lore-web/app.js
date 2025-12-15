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

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    initNavigation();
    initFilters();
    renderDashboard();
    renderRolesTable();
    renderUsersGrid();
    renderRelations();
    updateLastUpdate();
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
        card.innerHTML = `
            <div class="user-card-header">
                <div>
                    <h3>${role.name}</h3>
                    <span class="user-card-id">${role.id}</span>
                </div>
                <span class="role-badge ${role.type}">${getRoleTypeLabel(role.type)}</span>
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

const manualContent = {
    user: {
        title: 'Příručka pro Uživatele (Subjekty)',
        content: `
            <h1>IRIS Systém - Příručka pro Uživatele</h1>
            <p><strong>Dokumentace:</strong> IRIS 4.0 aktuální k HLINIK Phase 34</p>
            
            <h2>1. Úvod</h2>
            <p>IRIS je komunikační systém pro LARP hru, kde vy jako subjekt (uživatel) komunikujete s agentem prostřednictvím terminálu. Systém simuluje dystopickou korporátní AI infrastrukturu.</p>
            
            <h3>Vaše role</h3>
            <p>Jako <strong>Subjekt (User)</strong> jste běžný hráč, který:</p>
            <ul>
                <li>Komunikuje s přiděleným agentem</li>
                <li>Plní úkoly za kredity</li>
                <li>Může nahlásit anomálie ve zprávách</li>
            </ul>
            
            <h2>2. Přihlášení do systému</h2>
            <table>
                <tr><th>Pole</th><th>Hodnota</th></tr>
                <tr><td>Uživatel</td><td>user1 až user8</td></tr>
                <tr><td>Heslo</td><td>sdělí organizátoři</td></tr>
            </table>
            
            <h2>3. Rozhraní terminálu</h2>
            <h3>Levý panel - Stav subjektu</h3>
            <ul>
                <li><strong>POSUN SVĚTA:</strong> Aktuální časový posun (0-7)</li>
                <li><strong>KREDITY:</strong> Vaše virtuální měna</li>
            </ul>
            
            <h2>4. Práce s úkoly</h2>
            <table>
                <tr><th>Stav</th><th>Význam</th></tr>
                <tr><td>ČEKÁ NA SCHVÁLENÍ</td><td>Požádali jste o úkol, správce jej musí schválit</td></tr>
                <tr><td>AKTIVNÍ</td><td>Úkol je přidělen, můžete na něm pracovat</td></tr>
                <tr><td>DOKONČENO</td><td>Úkol jste odevzdali</td></tr>
            </table>
            
            <h2>5. Speciální stavy</h2>
            <ul>
                <li><strong>Purgatory:</strong> Pokud máte záporné kredity, chat je zablokován</li>
                <li><strong>Glitch:</strong> Vizuální efekt při přetížení systému</li>
            </ul>
        `
    },
    agent: {
        title: 'Příručka pro Agenty (Operátory)',
        content: `
            <h1>IRIS Systém - Příručka pro Agenty</h1>
            <p><strong>Dokumentace:</strong> IRIS 4.0 aktuální k HLINIK Phase 34</p>
            
            <h2>1. Úvod</h2>
            <p>Jako <strong>Agent (Operátor)</strong> jste odpovědní za komunikaci se subjekty (běžnými hráči). Odpovídáte na jejich zprávy a pomáháte jim v rámci herního světa.</p>
            
            <h3>Vaše role</h3>
            <ul>
                <li>Odpovídáte na zprávy od přidělených subjektů</li>
                <li>Musíte reagovat včas (sledujte časovač)</li>
                <li>Můžete využít AI asistenci (Autopilot)</li>
            </ul>
            
            <h2>2. Rozhraní agenta</h2>
            <h3>Levý panel - Status</h3>
            <ul>
                <li><strong>CÍLOVÝ POSUN SVĚTA:</strong> Zobrazuje aktuální shift hodnotu</li>
                <li><strong>STAV PŘIPOJENÍ:</strong> Ukazuje vaše ID relace</li>
                <li><strong>ČASOVAČ ODPOVĚDI:</strong> Žlutý pruh ukazuje zbývající čas</li>
            </ul>
            
            <h2>3. Komunikace se subjekty</h2>
            <ul>
                <li>Zprávy od subjektů se zobrazují automaticky</li>
                <li>Nová zpráva spustí časovač odpovědi</li>
                <li>Musíte odpovědět včas, jinak se vstup zablokuje</li>
            </ul>
            
            <h2>4. Autopilot a AI</h2>
            <ul>
                <li><strong>TOGGLE AUTOPILOT:</strong> Aktivuje automatický režim odpovídání</li>
                <li><strong>AI Optimalizace:</strong> Vaše zprávy mohou být přepsány AI</li>
            </ul>
            
            <h2>5. Speciální stavy</h2>
            <ul>
                <li><strong>Timeout:</strong> Pokud neodpovíte včas, vstup se zablokuje</li>
                <li><strong>Overload:</strong> Signalizuje přetížení systému</li>
            </ul>
        `
    },
    admin: {
        title: 'Příručka pro Správce (Adminy)',
        content: `
            <h1>IRIS Systém - Příručka pro Správce</h1>
            <p><strong>Dokumentace:</strong> IRIS 4.0 aktuální k HLINIK Phase 34</p>
            
            <h2>1. Úvod</h2>
            <p>Jako <strong>Správce (Admin)</strong> ovládáte herní mechaniky, schvalujete úkoly a dohlížíte na průběh hry.</p>
            
            <h2>2. Dashboard - Přehled stanic</h2>
            <table>
                <tr><th>Stanice</th><th>Barva</th><th>Funkce</th></tr>
                <tr><td>UMYVADLO</td><td>Zelená</td><td>Monitoring - sledování všech relací</td></tr>
                <tr><td>ROZKOŠ</td><td>Žlutá</td><td>Kontrola - herní nastavení</td></tr>
                <tr><td>BAHNO</td><td>Modrá</td><td>Ekonomika - správa kreditů</td></tr>
                <tr><td>MRKEV</td><td>Fialová</td><td>Úkoly - schvalování a vyplácení</td></tr>
            </table>
            
            <h2>3. Stanice MONITORING</h2>
            <ul>
                <li><strong>VŠEVIDOUCÍ:</strong> Mřížka všech 8 relací</li>
                <li><strong>ŠUM:</strong> Pouze chat karty bez logu</li>
                <li><strong>HISTORIE OMYLŮ:</strong> Kompletní systémový log</li>
                <li><strong>PAVUČINA:</strong> Grafické zobrazení sítě</li>
            </ul>
            
            <h2>4. Stanice KONTROLA</h2>
            <ul>
                <li><strong>POSUN REALITY:</strong> Ovládání shift hodnoty</li>
                <li><strong>TLAK PÁRY:</strong> Power management</li>
                <li><strong>HLADINA STRESU:</strong> Teplota systému</li>
            </ul>
            
            <h2>5. Stanice EKONOMIKA</h2>
            <ul>
                <li><strong>[+]:</strong> Přidat kredity (bonus)</li>
                <li><strong>[-]:</strong> Odebrat kredity (pokuta)</li>
                <li><strong>[LOCK]:</strong> Zablokovat terminál</li>
            </ul>
        `
    },
    root: {
        title: 'Příručka pro ROOT (Gamemaster)',
        content: `
            <h1>IRIS Systém - Příručka pro ROOT</h1>
            <p><strong>Dokumentace:</strong> IRIS 4.0 aktuální k HLINIK Phase 34</p>
            
            <h2>1. Přístup do ROOT konzole</h2>
            <table>
                <tr><th>Pole</th><th>Hodnota</th></tr>
                <tr><td>Uživatel</td><td>root</td></tr>
                <tr><td>Heslo</td><td>sdělí organizátoři</td></tr>
            </table>
            
            <h2>2. Panopticon - Hlavní přehled</h2>
            <h3>SYSTEM STATUS</h3>
            <ul>
                <li><strong>SHIFT OFFSET:</strong> Aktuální hodnota posunu (0-7)</li>
                <li><strong>ONLINE USERS:</strong> Počet připojených uživatelů</li>
                <li><strong>CHERNOBYL:</strong> Úroveň nestability systému</li>
            </ul>
            
            <h3>PHYSICS CONSTANTS</h3>
            <ul>
                <li><strong>TAX RATE:</strong> Procento z odměny za úkol do Treasury</li>
                <li><strong>POWER CAP:</strong> Maximální kapacita systému v MW</li>
            </ul>
            
            <h2>3. Executive Protocols</h2>
            <table>
                <tr><th>Tlačítko</th><th>Funkce</th></tr>
                <tr><td>FORCE SHIFT</td><td>Zvýší shift o 1</td></tr>
                <tr><td>GLOBAL BROADCAST</td><td>Pošle zprávu všem</td></tr>
                <tr><td>SYSTEM RESET</td><td>Resetuje kredity, úkoly, logy</td></tr>
                <tr><td>RESTART SERVER</td><td>Restartuje Python server</td></tr>
                <tr><td>FACTORY RESET</td><td>Smaže DB a restartuje</td></tr>
            </table>
            
            <h2>4. AI Configuration</h2>
            <ul>
                <li><strong>OPTIMIZER PROMPT:</strong> Text pro přepisování zpráv</li>
                <li><strong>AUTOPILOT MODEL:</strong> Výběr modelu</li>
                <li><strong>API KEYS:</strong> Klíče pro OpenAI, OpenRouter, Gemini</li>
            </ul>
            
            <h2>5. Panic Mode</h2>
            <p>Emergency censorship - nahrazuje odchozí zprávy LLM odpovědí. Použijte v krizových situacích.</p>
        `
    }
};

function showManual(type) {
    const manual = manualContent[type];
    if (!manual) return;

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
    const manual = manualContent[type];
    if (!manual) return;

    const printContent = generateManualHTML(manual);
    openPrintWindow(printContent, `Prirucka_${type}`);
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
