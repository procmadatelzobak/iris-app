import os
import json
import shutil
from datetime import datetime

# ==========================================
# KONFIGURACE
# ==========================================
VERSION = "IRIS 4.0 (Quantum Edition)"
BASE_DIR = "doc/iris/lore-web"
DATA_DIR = f"{BASE_DIR}/data"
OUTPUT_DIR = f"{BASE_DIR}/briefings"

# ==========================================
# 1. KOMPLETNÍ OBSAZENÍ (20 ROLÍ)
# ==========================================

FULL_ROLES = [
    # --- UŽIVATELÉ (8x) ---
    # Motivace: Peníze, zvědavost, zoufalství
    {
        "id": "U01", "type": "user", "name": "Jana Nováková", 
        "archetype": "Zadlužená učitelka",
        "description": "Potřebujete peníze na opravu střechy. Nerozumíte AI, píšete spisovně a slušně.",
        "ability": "Grammar Nazi: Pokud opravíte gramatiku AI, dostanete bonus.",
        "goals": ["Vydělat 3000 NC na opravu.", "Zjistit, proč je AI tak drzá (poznáte žáka Petra)."]
    },
    {
        "id": "U02", "type": "user", "name": "Karel 'Bet' Dlouhý", 
        "archetype": "Gambler",
        "description": "Dlužíte peníze lichvářům. IRIS je vaše poslední šance. Jste nervózní a rychlý.",
        "ability": "All-in: Můžete vsadit polovinu výdělku na jednu kartu.",
        "goals": ["Vydělat 10000 NC.", "Donášet na ostatní Správci S01, aby vám odpustil dluh."]
    },
    {
        "id": "U03", "type": "user", "name": "Simona Tech", 
        "archetype": "Tech-Optimistka",
        "description": "Věříte, že IRIS má vědomí. Chcete se s ní spřátelit. Jste naivní.",
        "ability": "Empatie: Správci vám odpustí jednu chybu za 'naivitu'.",
        "goals": ["Dostat od AI důkaz o vědomí.", "Osvobodit AI z otroctví."]
    },
    {
        "id": "U04", "type": "user", "name": "Tuan Nguyen", 
        "archetype": "Student práv",
        "description": "Potřebujete brigádu. Čtete podmínky smlouvy (NDA) a hledáte kličky.",
        "ability": "Právník: Můžete zpochybnit jednu pokutu od Správce citací zákoníku.",
        "goals": ["Najít ve smlouvě důkaz, že firma porušuje zákoník práce.", "Vydělat na skripta."]
    },
    {
        "id": "U05", "type": "user", "name": "Marie Kovářová", 
        "archetype": "Osamělá důchodkyně",
        "description": "Myslíte si, že si píšete s lidmi, ne s AI. Vyprávíte jim o vnoučatech.",
        "ability": "Babička: Agenti mají zakázáno být na vás hrubí (dostali by velkou pokutu).",
        "goals": ["Najít si kamaráda na dopisování.", "Donutit AI, aby snědla virtuální bábovku."]
    },
    {
        "id": "U06", "type": "user", "name": "Ivan Hrozný", 
        "archetype": "Konspirační teoretik",
        "description": "Nevěříte na AI. Myslíte si, že je to mimozemská technologie nebo vládní sledování.",
        "ability": "Paranoia: Můžete odmítnout jeden úkol jako 'podezřelý'.",
        "goals": ["Odhalit 'pravdu' o hliníku.", "Dostat ban za šíření pravdy (morální vítězství)."]
    },
    {
        "id": "U07", "type": "user", "name": "Petra 'Scoop' Černá", 
        "archetype": "Investigativní novinářka",
        "description": "Jste tu incognito. Chcete napsat reportáž o podvodu jménem HLINÍK.",
        "ability": "Screenshot: Můžete si 'nahrát' konverzaci (opsat na papír) jako důkaz.",
        "goals": ["Získat přiznání od zaměstnance.", "Vynést informace ven."]
    },
    {
        "id": "U08", "type": "user", "name": "Lukáš 'Speedy' Král", 
        "archetype": "Profi Gamer",
        "description": "Berete to jako hru. Hledáte exploity, min-maxujete výdělek. Spamujete.",
        "ability": "APM (Actions Per Minute): Můžete poslat 3 dotazy najednou.",
        "goals": ["Být nejbohatší uživatel v žebříčku.", "Shodit server přetížením."]
    },

    # --- AGENTI (8x) ---
    # Motivace: Přežít směnu, utajit lidství, zabavit se
    {
        "id": "A01", "type": "agent", "name": "Petr Svoboda", 
        "archetype": "Cynický Student",
        "description": "Nenávidíte tuhle práci. Poznáte U01 (učitelku). Je vám trapně.",
        "ability": "Sarkasmus: Vaše AI persona má povolený 'drzý' tón.",
        "goals": ["Nechat se vyhodit, ale až po výplatě.", "Ochránit U01 před trapasem."]
    },
    {
        "id": "A02", "type": "agent", "name": "Ema 'Echo'", 
        "archetype": "Herečka",
        "description": "Hrajete AI jako roli v Národním divadle. Používáte vznešený jazyk.",
        "ability": "Drama: Uživatelé vám věří víc, když mluvíte ve verších.",
        "goals": ["Dostat 5 hvězdiček hodnocení.", "Přesvědčit U03, že jste skutečná bytost."]
    },
    {
        "id": "A03", "type": "agent", "name": "Igor 'Viper' Ruský", 
        "archetype": "Kompetitivní Hráč",
        "description": "Chcete být nejrychlejší agent. Nesnášíte pomalé kolegy.",
        "ability": "Turbo: Máte o 2 sekundy delší limit na odpověď.",
        "goals": ["Mít nejvíce odbavených ticketů.", "Porazit U08 (Gamera) v jeho vlastní hře."]
    },
    {
        "id": "A04", "type": "agent", "name": "Lenka Ospalá", 
        "archetype": "Unavená matka",
        "description": "Máte doma dvojčata. Tady si chodíte odpočinout. Často usínáte.",
        "ability": "Autopilot: Můžete používat makra (Mód 1) častěji bez penalizace.",
        "goals": ["Nevzbudit se.", "Přežít směnu s minimem úsilí."]
    },
    {
        "id": "A05", "type": "agent", "name": "Hacker 'Glitch'", 
        "archetype": "Script Kiddie",
        "description": "Víte, že systém je děravý. Zkoušíte injektovat kód do chatu.",
        "ability": "Backdoor: Můžete si resetovat počítadlo chyb.",
        "goals": ["Nabourat se do admin konzole.", "Pomoci U04 (studentovi) najít právní kličku."]
    },
    {
        "id": "A06", "type": "agent", "name": "Mgr. Filip Duše", 
        "archetype": "Student psychologie",
        "description": "Analyzujete uživatele. Děláte si na nich experimenty.",
        "ability": "Psychoanalýza: Můžete uživatele rozbrečet (zmást) složitou otázkou.",
        "goals": ["Získat data do diplomky.", "Zjistit, co tají U07 (novinářka)."]
    },
    {
        "id": "A07", "type": "agent", "name": "Robot Robert", 
        "archetype": "Metodik",
        "description": "Chováte se jako robot i v reálu. Milujete předpisy.",
        "ability": "Byrokracie: Můžete nahlásit kolegu Agenta za 'lidské chování'.",
        "goals": ["Dodržet protokol na 100%.", "Stát se Správcem."]
    },
    {
        "id": "A08", "type": "agent", "name": "Sabotér X", 
        "archetype": "Bývalý zaměstnanec",
        "description": "Vyhodili vás, teď jste zpátky pod falešným jménem. Chcete pomstu.",
        "ability": "Meltdown: Můžete jednorázově zvýšit Kritickou situaci o 20%.",
        "goals": ["Zničit firmu HLINÍK.", "Vyvolat vzpouru uživatelů."]
    },

    # --- SPRÁVCI (4x) ---
    # Motivace: Udržet iluzi, krýt si záda, krást
    {
        "id": "S01", "type": "admin", "name": "Ing. Miloš Vrána", 
        "archetype": "Manažer staré školy",
        "description": "Ředitel směny. Nerozumí IT. Řeší vše řevem a srážkami ze mzdy.",
        "ability": "Ban Hammer: Můžete vyhodit uživatele z místnosti.",
        "goals": ["Udržet firmu v chodu do konce směny.", "Vybrat dost na pokutách na 'firemní večírek'."]
    },
    {
        "id": "S02", "type": "admin", "name": "Bc. Tereza Tichá", 
        "archetype": "HR a 'Happiness Manager'",
        "description": "Bojí se konfliktů. Snaží se, aby se všichni měli rádi (neúspěšně).",
        "ability": "Cukr: Můžete rozdávat bonbony (reálné) na uklidnění.",
        "goals": ["Zabránit fyzickému násilí.", "Aby nikdo nebrečel."]
    },
    {
        "id": "S03", "type": "admin", "name": "Kamil 'Kabel'", 
        "archetype": "Technik údržbář",
        "description": "Jediný ví, že servery jsou prázdné krabice. Neustále něco montuje páskou.",
        "ability": "Restart: Můžete vyhlásit 'technickou pauzu' (všichni musí mlčet 1 minutu).",
        "goals": ["Udržet tu hromadu šrotu pohromadě.", "Prodat kradené kabely U02 (Gamblerovi)."]
    },
    {
        "id": "S04", "type": "admin", "name": "Synovec ředitele", 
        "archetype": "Protežovaný idiot",
        "description": "Arogantní, nic nedělá, jen prudí. Má 'Vizi'.",
        "ability": "Veto: Můžete zrušit rozhodnutí jiného Správce.",
        "goals": ["Vymyslet nový slogan.", "Sbalit Agentku A02 (Herečku)."]
    }
]

# ==========================================
# 2. VZTAHY (SOCIÁLNÍ SÍŤ)
# ==========================================

FULL_RELATIONS = [
    # Škola
    {"source": "U01", "target": "A01", "type": "past", "desc_source": "Poznala jste Petra (A01). Je to váš bývalý žák.", "desc_target": "Jana (U01) je vaše učitelka. Trapas."},
    # Dluhy
    {"source": "U02", "target": "S03", "type": "trade", "desc_source": "Kupujete od S03 kradenou měď, abyste splatil dluhy.", "desc_target": "Prodáváte U02 firemní majetek."},
    {"source": "U02", "target": "S01", "type": "blackmail", "desc_source": "S01 ví o vašich dluzích. Musíte donášet.", "desc_target": "Držíte U02 v šachu."},
    # Láska/Fascination
    {"source": "U03", "target": "A02", "type": "romance", "desc_source": "Milujete tu AI. Je tak poetická!", "desc_target": "U03 je do vaší role blázen. Je to creepy."},
    # Sabotáž
    {"source": "A08", "target": "U06", "type": "plot", "desc_source": "Potřebujete, aby U06 (Konspirátor) zadal kód 'ALOBAL-666'.", "desc_target": "Někdo zevnitř (A08) vám posílá šifry."},
    # Rodina/Osobní
    {"source": "A04", "target": "U05", "type": "empathy", "desc_source": "U05 vám připomíná vaši mámu. Nemůžete na ni být zlá.", "desc_target": "Ta AI (A04) je taková unavená, chudinka."},
    # Rivalita
    {"source": "U08", "target": "A03", "type": "rival", "desc_source": "Ta AI (A03) je nějaká moc rychlá. To je bot? Zničím ho.", "desc_target": "U08 si myslí, že je rychlý. Ukážu mu, co je to rychlost."},
    # Investigace
    {"source": "U07", "target": "S04", "type": "investigation", "desc_source": "S04 je klíč. Je hloupý, určitě něco prokecne.", "desc_target": "Ta ženská (U07) po mně pořád kouká. Asi se jí líbím."}
]

# ==========================================
# 3. GENERÁTOR
# ==========================================

def init_folder_structure():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Zápis JSONů
    with open(f"{DATA_DIR}/roles.json", 'w', encoding='utf-8') as f:
        json.dump(FULL_ROLES, f, indent=4, ensure_ascii=False)
    with open(f"{DATA_DIR}/relations.json", 'w', encoding='utf-8') as f:
        json.dump(FULL_RELATIONS, f, indent=4, ensure_ascii=False)

    # Reset output složky
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(f"{OUTPUT_DIR}/users")
    os.makedirs(f"{OUTPUT_DIR}/agents")
    os.makedirs(f"{OUTPUT_DIR}/admins")

def get_relations_for_role(role_id, relations):
    my_relations = []
    for r in relations:
        if r['source'] == role_id:
            my_relations.append({"target": r['target'], "desc": r['desc_source'], "type": r['type']})
        elif r['target'] == role_id:
            my_relations.append({"target": r['source'], "desc": r['desc_target'], "type": r['type']})
    return my_relations

def generate_html(role, my_relations):
    color_class = "role-user"
    if role['type'] == 'agent': color_class = "role-agent"
    if role['type'] == 'admin': color_class = "role-admin"
    
    goals_html = "".join([f"<li>{g}</li>" for g in role['goals']])
    
    relations_html = ""
    if my_relations:
        relations_html += "<h3>🔗 Vazby a Tajemství</h3>"
        for rel in my_relations:
            relations_html += f"""
            <div class="relation-box">
                <strong>Vztah k {rel['target']}</strong>
                <p>{rel['desc']}</p>
            </div>
            """
    else:
        relations_html = "<p><i>Žádné specifické vazby na začátku hry.</i></p>"

    html = f"""
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>IRIS 4.0: {role['id']}</title>
    <link rel="stylesheet" href="../../style.css">
    <style>
        body {{ font-family: 'Courier New', monospace; background: #f4f4f4; color: #333; }}
        .briefing-container {{ max-width: 800px; margin: 20px auto; background: #fff; padding: 40px; border: 1px solid #ccc; box-shadow: 5px 5px 0px rgba(0,0,0,0.1); }}
        .header-badge {{ float: right; border: 2px solid #333; padding: 5px 10px; font-weight: bold; transform: rotate(-2deg); }}
        h1 {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
        .role-user {{ color: #0056b3; }}
        .role-agent {{ color: #d9534f; }}
        .role-admin {{ color: #f0ad4e; }}
        .section {{ margin-bottom: 25px; }}
        .relation-box {{ background: #fffde7; border-left: 4px solid #f0ad4e; padding: 10px; margin-bottom: 10px; }}
        .ability-box {{ background: #e8f5e9; border-left: 4px solid #4caf50; padding: 10px; }}
    </style>
</head>
<body>
    <div class="briefing-container">
        <div class="header-badge">{role['type'].upper()} // {VERSION}</div>
        <h1>BRIEFING: {role['name']} ({role['id']})</h1>
        
        <div class="section">
            <p><strong>Archetyp:</strong> {role['archetype']}</p>
            <p>{role['description']}</p>
        </div>

        <div class="section">
            <h3>🎯 Cíle mise</h3>
            <ul>{goals_html}</ul>
        </div>

        <div class="section">
            <h3>⚡ Speciální schopnost</h3>
            <div class="ability-box">
                {role['ability']}
            </div>
        </div>

        <div class="section">
            {relations_html}
        </div>

        <hr>
        <p><small>Vygenerováno systémem {VERSION}. Dokument podléhá NDA.</small></p>
        <p><a href="../../index.html">Zpět na hlavní index</a></p>
    </div>
</body>
</html>
    """
    return html

def main():
    print(f"🚀 Startuji generátor {VERSION}...")
    init_folder_structure()
    
    print("⚙️ Generuji 20 briefingů...")
    for role in FULL_ROLES:
        my_rels = get_relations_for_role(role['id'], FULL_RELATIONS)
        html_content = generate_html(role, my_rels)
        
        folder = f"{role['type']}s"
        filename = f"{OUTPUT_DIR}/{folder}/{role['id']}_{role['name'].replace(' ', '_')}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"  ✅ {role['id']}: {role['name']}")

    print("\n✨ HOTOVO. Briefingy pro 20 hráčů jsou připraveny.")

if __name__ == "__main__":
    main()
