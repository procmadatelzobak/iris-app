
# Architektonická Specifikace Systému IRIS v2.0: Komplexní Technický Návrh a Implementační Strategie pro Izolované Prostředí

## 1. Exekutivní Shrnutí a Architektonická Filozofie

Tento dokument představuje vyčerpávající technickou specifikaci pro vývoj systému IRIS (verze 2.0), určenou primárně pro autonomního programovacího agenta či seniorního vývojového inženýra. Systém IRIS je navržen jako kritická infrastruktura pro podporu imersivní simulace (LARP) projektu Eltex, kde zprostředkovává veškerou interakci mezi izolovanými testovacími subjekty (uživateli) a skrytými operátory (agenty). Architektura musí reflektovat specifické narativní a mechanické požadavky, jako je iluze autonomní umělé inteligence "HLINÍK", dynamická ekonomika založená na sociálním kreditu, a pokročilé mechanismy řízení chaosu, včetně tzv. "Chernobyl" protokolu.

Základním imperativem návrhu je absolutní stabilita v izolovaném prostředí bez přístupu k externí síti Internet (Zero-External-Dependency, ZED). Systém musí fungovat jako monolitický, self-contained ekosystém, který je odolný vůči nestandardnímu chování uživatelů i hardwarovým limitům nasazení (např. v podzemním bunkru). Návrh preferuje robustnost standardních knihoven jazyka Python a atomicitu transakční databáze SQLite před komplexitou distribuovaných systémů, které by v daném kontextu představovaly zbytečné riziko selhání.

### 1.1 Definice Cílů a Rozsah Systému

Cílem systému není pouze přenos textových zpráv, ale vytvoření komplexního psychologického nástroje. Systém musí aktivně podporovat atmosféru paranoie a nejistoty prostřednictvím vizuálních a funkčních glitchů, manipulace s latencí a řízeného uvolňování informací. Z narativního hlediska systém simuluje pokročilou AI, která však v jádru spoléhá na "Mechanical Turk" princip lidských operátorů.1

Technický rozsah zahrnuje:

1.  Backendové Jádro: Asynchronní server (FastAPI/Uvicorn) řídící herní logiku, stavové automaty a WebSocket komunikaci.
    
2.  Perzistentní Úložiště: Relační databáze SQLite s optimalizací pro vysokou konkurentnost zápisů (WAL mode).
    
3.  Klientská Rozhraní: Tři oddělené Single Page Applications (SPA) pro Uživatele, Agenty a Správce, doručované přímo z backendu bez závislosti na CDN.
    
4.  Herní Engine: Modulární logika zahrnující ekonomiku, sociální status, rotaci agentů (Shift+1) a simulaci nestability (Chernobyl).
    

### 1.2 Volba Technologického Stacku a Omezení

Vzhledem k požadavku na absenci externích závislostí a nutnost běhu v izolované síti ("air-gapped"), byl zvolen konzervativní, avšak vysoce výkonný stack.

-   Jazyk: Python 3.10+ (využívající striktní typování typing a nová asynchronní primitiva).
    
-   Aplikační Framework: FastAPI. Volba padla na FastAPI oproti Flasku z důvodu nativní podpory asynchronních operací (async/await) a WebSocketů, což je klíčové pro real-time charakter chatu a dashboardů. Pydantic modely navíc zajišťují rigorózní validaci dat na vstupu i výstupu, což minimalizuje runtime chyby.
    
-   Databáze: SQLite3. Ačkoliv se v podnikové sféře často volí PostgreSQL, pro izolovaný LARP systém je SQLite ideální. Eliminuje potřebu správy samostatného databázového serveru, zjednodušuje zálohování (kopírování jednoho souboru) a při správné konfiguraci (WAL mode) zvládá stovky konkurentních operací za sekundu, což pro 20-30 účastníků dostačuje s obrovskou rezervou.
    
-   Protokol: WebSockets pro obousměrnou komunikaci v reálném čase. HTTP REST API bude využito pouze pro úvodní autentizaci a upload statických souborů.
    

### 1.3 Architektonické Principy

Architektura ctí princip "Fail-Safe & Recover". V prostředí LARPu je restart serveru (ať už z technických důvodů nebo jako herní mechanika) běžným jevem. Systém proto musí být schopen se po restartu okamžitě vrátit do konzistentního stavu. Veškerý stav hry, včetně obsahu chatu, stavu ekonomiky a úrovně "Chernobyl" baru, musí být perzistentně ukládán. In-memory struktury budou sloužit pouze jako cache pro aktivní sockety.

## 

----------

2. Datový Model a Návrh Persistence (SQLite)

Jádrem stability systému je rigorózně navržené databázové schéma. Vzhledem k požadavkům na komplexní ekonomiku, sociální statusy a logiku střídání agentů (Shift+1), nelze spoléhat na NoSQL dokumentové úložiště. Relační integrita je nezbytná pro zajištění konzistence transakcí (např. aby uživatel nemohl utratit kredity, které nemá).

### 2.1 Konfigurace SQLite Engine

Pro zajištění výkonu a spolehlivosti bude SQLite inicializováno s následujícími PRAGMA direktivami:

-   PRAGMA journal_mode = WAL; (Write-Ahead Logging): Umožňuje, aby čtení neblokovalo zápis a naopak. To je kritické pro plynulost chatu, kdy agenti píší a správci zároveň sledují dashboardy.
    
-   PRAGMA synchronous = NORMAL;: Balancuje mezi bezpečností dat a rychlostí zápisu. V kontextu hry je ztráta posledních 200ms dat při výpadku proudu akceptovatelná výměnou za vyšší propustnost.
    
-   PRAGMA foreign_keys = ON;: Vynucuje referenční integritu na úrovni databáze, což brání vzniku "sirotčích" záznamů (např. zprávy bez existujícího uživatele).
    

### 2.2 Entitně-Relační Schéma (Detailní Specifikace)

Databáze iris.db bude obsahovat následující tabulky. Schéma reflektuje všechny funkční požadavky, včetně sociálního statusu a Shift+1 mechaniky.

#### 2.2.1 Tabulka users (Testovací subjekty)

Tato tabulka uchovává stav hráčů-uživatelů.

Atribut

Datový Typ

Omezení

Popis a Význam

id

INTEGER

PK, AUTOINCREMENT

Unikátní identifikátor.

username

TEXT

UNIQUE, NOT NULL

Herní identifikace (např. "Subjekt 89").

password_hash

TEXT

NOT NULL

Bezpečně hashované heslo (PBKDF2/Argon2).

credits

INTEGER

DEFAULT 0

Aktuální ekonomický zůstatek. Nesmí jít pod nulu (kontrolováno aplikační logikou).

social_score

INTEGER

DEFAULT 0

Numerická hodnota sociálního statusu (základ pro výpočet Tieru).

current_tier

INTEGER

DEFAULT 1

FK na social_tiers. Cachovaná hodnota pro rychlý přístup.

is_active

BOOLEAN

DEFAULT 1

Indikátor, zda je uživatel ve hře (pro případ vyloučení).

last_activity

TIMESTAMP

DEFAULT NOW

Pro detekci neaktivity a automatické pokuty.

#### 2.2.2 Tabulka agents (Operátoři)

Tabulka agentů je specifická tím, že definuje jejich "fyzické umístění" v systému, což je klíčové pro mechaniku rotace.

Atribut

Datový Typ

Omezení

Popis a Význam

id

INTEGER

PK, AUTOINCREMENT

Interní ID.

username

TEXT

UNIQUE, NOT NULL

Login operátora (např. "Operator_Alpha").

seat_index

INTEGER

UNIQUE, NOT NULL

Číslo 0-N. Definuje pozici v "kruhu". Toto číslo je neměnné a váže se k fyzickému terminálu agenta. Mechanika Shift+1 operuje nad tímto indexem.

hyper_mode_state

INTEGER

DEFAULT 0

Aktuální stav HYPER módu (0-3). Umožňuje adminům sledovat, kdo "podvádí" s AI.

#### 2.2.3 Tabulka chat_sessions (Dynamické mapování)

Tato tabulka je srdcem mechaniky Shift+1. Neurčuje statický vztah, ale aktuální dynamické propojení.

Atribut

Datový Typ

Omezení

Popis a Význam

user_id

INTEGER

PK, FK users.id

Každý uživatel má právě jednu aktivní session.

assigned_seat

INTEGER

NOT NULL

Index sedadla (agents.seat_index), kterému jsou aktuálně doručovány zprávy od tohoto uživatele.

thread_id

TEXT

UNIQUE, UUID

Identifikátor pro frontendové vlákno.

is_frozen

BOOLEAN

DEFAULT 0

Pokud TRUE, chat je dočasně blokován (např. během rotace nebo restartu).

#### 2.2.4 Tabulka social_tiers (Konfigurace statusu)

Číselník definující sociální vrstvy a jejich ekonomické dopady.

Atribut

Datový Typ

Omezení

Popis a Význam

tier_level

INTEGER

PK

Úroveň 1-5.

name

TEXT

NOT NULL

Název statusu (např. "Dělník", "Občan", "Vizipnář").

min_score

INTEGER

NOT NULL

Hranice skóre pro dosažení.

wage_multiplier

REAL

DEFAULT 1.0

Násobitel odměn za úkoly (např. 1.2x pro Elitu).

fine_multiplier

REAL

DEFAULT 1.0

Násobitel pokut (často vyšší pro vyšší kasty jako narativní prvek).

#### 2.2.5 Tabulka messages (Auditní log)

Kompletní historie komunikace. Slouží pro zobrazení historie uživateli a pro auditní dashboardy správců.1

Atribut

Datový Typ

Omezení

Popis a Význam

id

INTEGER

PK, AUTOINCREMENT

Sekvenční ID.

session_id

INTEGER

FK chat_sessions

Vazba na konverzaci.

sender_type

TEXT

CHECK('USER', 'SYSTEM')

Rozlišení, kdo zprávu poslal.

content

TEXT

NOT NULL

Obsah zprávy.

hyper_used

INTEGER

DEFAULT 0

Zaznamenává, zda a jaký HYPER mód agent použil (pro statistiky "Chernobylu").

is_reported

BOOLEAN

DEFAULT 0

Příznak, zda uživatel nahlásil zprávu jako "podezřelou".

timestamp

DATETIME

DEFAULT NOW

Časová značka.

#### 2.2.6 Tabulka global_state (Stav systému)

Klíč-hodnota úložiště pro proměnné, které ovlivňují celý systém.

Klíč (PK)

Hodnota

Popis

chernobyl_index

0.45

Float 0.0-1.0. Úroveň nestability.

economy_inflation

1.5

Float. Globální násobitel cen v obchodě.

system_mode

RUNNING

Enum: RUNNING, PAUSED, REBOOTING, MELTDOWN.

shift_offset

3

Kolikrát proběhla rotace (pro debug).

## 

----------

3. Jádro Backendové Logiky (Core Engines)

Backendová logika je rozdělena do izolovaných "Enginů", které spravují specifické aspekty simulace. Tento modulární přístup umožňuje snadné úpravy pravidel hry bez rizika rozbití základní komunikační vrstvy.

### 3.1 Chernobyl Instability Engine

Tento engine implementuje logiku "Chernobyl baru", vizuálního indikátoru, který reprezentuje stabilitu AI systému HLINÍK. Podle narativu 1 je systém nestabilní a náchylný k chybám, pokud není správně udržován.

Algoritmus Výpočtu Instability:

Instabilita $I$ v čase $t$ je vypočtena jako:

  
  

$$I(t) = \text{clamp}(I(t-1) + \Delta_{events} - \Delta_{decay}, 0.0, 1.0)$$

Kde $\Delta_{events}$ zahrnuje:

-   Hlášení uživatele: $+0.05$ (významný skok, signalizuje selhání Turingova testu).
    
-   Použití HYPER módu 3 (Glitch): $+0.02$ (rizikové chování agenta).
    
-   Klíčová slova: Pokud zpráva obsahuje slova jako "Eltex", "Humpolec", "Podvod", přičte se $+0.01$.
    

$\Delta_{decay}$ představuje přirozené uklidnění systému v čase (např. $-0.001$ každou sekundu), aby hra nespěla k nevyhnutelnému konci příliš rychle a vyžadovala aktivní "sabotáž" ze strany hráčů.

Důsledky Úrovní Instability:

-   0.0 - 0.3 (Zelená): Normální provoz.
    
-   0.3 - 0.6 (Žlutá): Vizuální artefakty na dashboardech správců. Občasné zpoždění odeslání zprávy (simulovaný lag 500ms).
    
-   0.6 - 0.9 (Červená): Terminály uživatelů začínají blikat. Některé znaky ve zprávách jsou nahrazeny hexadecimálními kódy (glitch text).
    
-   1.0 (Meltdown): Kritická chyba. Systém automaticky vyvolá "Forced Reboot" sekvenci, odpojí všechny uživatele a provede nucenou rotaci agentů.
    

### 3.2 Rotation Engine (Mechanika Shift+1)

Tato mechanika je klíčovým prvkem pro udržení anonymity a chaosu. Jejím cílem je zpřetrhat vazbu mezi konkrétním fyzickým agentem a uživatelem, aniž by se přerušila kontinuita "AI HLINÍK" z pohledu uživatele.

Proces Rotace:

1.  Iniciace: Správce stiskne tlačítko "EXECUTE SHIFT" na dashboardu.
    
2.  Lockdown: Engine nastaví system_mode = REBOOTING. Všechny aktivní WebSocket spojení obdrží zprávu {"type": "system_freeze", "msg": "RECALIBRATING NEURAL PATHWAYS..."}. Klienti zablokují input pole.
    
3.  Transakce: V jedné atomické transakci provede SQL update:  
    SQL  
    UPDATE chat_sessions  
    SET assigned_seat = (assigned_seat +  1) % (SELECT  count(*) FROM agents);  
      
    
4.  Context Switch: Backend identifikuje nové páry Agent-Uživatel. Agentům je zaslán signál {"type": "context_refresh", "new_user_id": X, "history": [...]}. Zde je implementována volitelná logika "Soft Amnesia" – agent vidí jen posledních 5 zpráv z historie nového uživatele, aby se simulovala ztráta kontextu po restartu.1
    
5.  Unlock: Systém se vrátí do system_mode = RUNNING a odblokuje klienty. Uživatel pokračuje v chatu, ale odpovídá mu jiný člověk.
    

### 3.3 Economy & Social Status Engine

Ekonomika systému slouží k řízení tempa hry a motivace hráčů. Engine spravuje kredity, pokuty a sociální status.

Logika Sociálního Statusu:

Status není statický, ale dynamický. Každý uživatel má social_score. Hranice pro Tiery jsou uloženy v DB.

-   Gain: Splnění úkolu (+Body), Nahlášení chyby (+Body).
    
-   Drain: Každou herní hodinu se aplikuje "daň z existence" (např. -5% skóre). To nutí hráče k neustálé aktivitě.
    

Ekonomika Odměn a Pokut:

Engine počítá odměnu za úkol dynamicky:

Final Reward = (Base Reward * Social Tier Multiplier).

Pokuty jsou strhávány buď automaticky (za neaktivitu) nebo manuálně správcem. Pokud by pokuta dostala uživatele do záporu, engine nastaví stav na 0 a aplikuje status "INSOLVENT", což může zablokovat určité funkce terminálu.

## 

----------

4. Komunikační Vrstva a Protokoly (WebSockets)

Pro zajištění real-time interakce využívá systém protokol WebSocket. Implementace musí být robustní vůči "zombie" spojením a výpadkům sítě.

### 4.1 Formát Zpráv (JSON Payload)

Veškerá komunikace probíhá výměnou JSON objektů. Každý objekt musí obsahovat pole type (pro server->client) nebo action (pro client->server).

Client -> Server (Příklady):

  

JSON

  
  

// Odeslání zprávy  
{  
"action": "send_message",  
"content": "Jaký je smysl projektu Eltex?"  
}  
  
// Nahlášení anomálie (Chernobyl trigger)  
{  
"action": "report_message",  
"target_message_id": 12345,  
"reason": "unnatural_phrasing"  
}  
  
// Interakce s obchodem  
{  
"action": "purchase_item",  
"item_id": "info_packet_alpha"  
}  
  

Server -> Client (Příklady):

  

JSON

  
  

// Příchozí zpráva chatu  
{  
"type": "chat_message",  
"data": {  
"id": 890,  
"sender": "HLINIK",  
"content": "Data byla analyzována. Výsledek je negativní.",  
"timestamp": "2025-10-24T14:30:00Z",  
"visual_glitch_level": 0.2  // Frontend aplikuje CSS noise  
}  
}  
  
// Aktualizace stavu (Heartbeat payload)  
{  
"type": "status_update",  
"data": {  
"credits": 150,  
"social_tier": "Občan",  
"chernobyl_bar": 0.65,  
"system_status": "RUNNING"  
}  
}  
  

### 4.2 Správa Spojení (Connection Manager)

Vzhledem k absenci Redis (ZED požadavek) je Connection Manager implementován in-memory v Pythonu.

Třída ConnectionManager udržuje:

1.  active_connections: Dict - Mapování UserID na socket.
    
2.  agent_connections: Dict - Mapování SeatIndex na socket agenta.
    
3.  admin_connections: List - Seznam připojených dashboardů.
    

Logika Směrování (Routing):

Když Agent na sedadle 3 odešle zprávu:

1.  Manager zjistí z chat_sessions, který user_id je aktuálně přiřazen k sedadlu 3.
    
2.  Vyhledá socket pro toto user_id.
    
3.  Pokud je socket aktivní, odešle JSON.
    
4.  Pokud není, zprávu pouze uloží do DB. Frontend uživatele si při znovupřipojení vyžádá historii (/api/history).
    

## 

----------

5. Specifikace Agenta a HYPER Módů

Rozhraní a logika pro agenty jsou navrženy tak, aby podporovaly roli "Wizard of Oz" operátora. Agent má k dispozici čtyři stavy HYPER módu, které mění způsob generování odpovědí a ovlivňují stabilitu systému.

### 5.1 Definice 4 Stavů HYPER Módu

Přepínač na konzoli agenta má 4 polohy. Každá poloha mění backendovou logiku zpracování zprávy.

1.  Mód 0: MANUAL (Standard)
    

-   Funkce: Agent píše text ručně. Backend zprávu doručí beze změny.
    
-   Vliv na Chernobyl: Žádný (+0.0).
    
-   Použití: Běžná konverzace, budování důvěry.
    

2.  Mód 1: AUTO-COMPLETE (Korporátní Efektivita)
    

-   Funkce: Frontend agenta nabízí našeptávání předdefinovaných frází ("Rozumím", "Analyzuji", "Prosím specifikujte zadání"). Backend pouze loguje použití.
    
-   Vliv na Chernobyl: Minimální (+0.001).
    
-   Použití: Rychlé odbavení rutinních dotazů. Odpovědi zní strojově a konzistentně.
    

3.  Mód 2: LLM PROXY (Simulace AI)
    

-   Funkce: Agent ne píše, ale stiskne tlačítko "GENERATE". Backend vyhledá odpověď v interní znalostní bázi (nebo použije lokální LLM, pokud je hardware dostupný, jinak propracovaný vyhledávací strom nad texty z PDF 1). Odpovědi jsou fakticky přesné, ale formální a "encyklopedické".
    
-   Vliv na Chernobyl: Střední (+0.01).
    
-   Použití: Poskytování informací, které agent nezná (historie Eltexu), ale za cenu rizika odhalení "robotického" tónu.
    

4.  Mód 3: GLITCH / TRUTH (Únik Dat)
    

-   Funkce: Nebezpečný mód. Backend vezme odpověď (zadanou nebo vygenerovanou) a aplikuje na ni filtr "poškození dat". Do textu jsou vloženy fragmenty pravdy o projektu Eltex ("...SYSTEM OVERRIDE: SUBJECTS ARE HUMAN..."), hexadecimální kódy a Zalgo znaky.
    
-   Vliv na Chernobyl: Vysoký (+0.05).
    
-   Použití: Vyvrcholení příběhu, sabotáž, momenty "prolomení bariéry".
    

## 

----------

6. Administrátorské Rozhraní (4 Dashboardy)

Pro efektivní řízení hry 4 správci je navržen systém čtyř specializovaných dashboardů. Ačkoliv technicky jde o jednu webovou aplikaci, zobrazení se liší podle role nebo záložky. Dashboardy se aktualizují v reálném čase přes WebSockets.

### 6.1 Dashboard 1: "SYSTEM INTEGRITY & CHERNOBYL"

Tento pohled je určen pro "bezpečnostního technika".

-   Dominantní prvek: Velký graf instability (Chernobyl Bar) v čase.
    
-   Ovládací prvky:
    

-   Slider pro manuální úpravu instability (pro dramatické účely).
    
-   Tlačítko "EMERGENCY SCRAM" (vyvolá okamžitý restart a rotaci).
    

-   Real-time Feed: Seznam nahlášených zpráv ("Ticket #89: User 4 nahlásil zprávu od Agenta 2"). Správce může ticket "vyřešit" (smazat) nebo "eskalovat" (zvýšit instabilitu).
    

### 6.2 Dashboard 2: "ECONOMY & PRODUCTIVITY"

Pohled pro "HR manažera" a ekonoma.

-   Metriky: Celkové HDP (suma kreditů v oběhu), Průměrná spokojenost (odvozeno od počtu reportů), Inflace.
    
-   Ovládací prvky:
    

-   Global Inflation Multiplier: Slider (0.5x - 5.0x). Okamžitě mění ceny v obchodech uživatelů.
    
-   Mass Fine: Tlačítko pro stržení kreditů všem (disciplinární trest).
    
-   Stimulus: Tlačítko pro rozdání kreditů (podpora aktivity).
    

-   Tabulka: Žebříček nejproduktivnějších uživatelů (podle splněných úkolů).
    

### 6.3 Dashboard 3: "OPS & ROTATION MATRIX"

Nejtechničtější pohled pro řízení agentů.

-   Vizuál: "Kruhová matice". Zobrazuje grafické spojení mezi Agenty (vnitřní kruh) a Uživateli (vnější kruh).
    
-   Indikátory: Spojnice mění barvu podle aktivity chatu (Šedá = ticho, Zelená = aktivní, Červená = konflikt/report).
    
-   Ovládání:
    

-   Velké červené tlačítko EXECUTE SHIFT+1.
    
-   Tlačítko PAUSE ALL CHATS.
    

### 6.4 Dashboard 4: "LOGS & SURVEILLANCE"

Auditní pohled.

-   Funkce: Umožňuje "odposlouchávat" libovolnou konverzaci. Správce klikne na ID session a vidí chat v reálném čase, aniž by do něj mohl zasahovat.
    
-   System Logs: Výpis serverových hlášek (připojení, odpojení, chyby, SQL queries - pro debug).
    

## 

----------

7. Klientské Terminály (Uživatelské UX)

Design uživatelského rozhraní je klíčový pro "suspension of disbelief". Rozhraní musí působit jako proprietární software korporace, ne jako webová stránka.

### 7.1 Vizuální Styl a Omezení

-   Estetika: Retro-futurismus. Černé pozadí, monochromatický text (zelená/jantarová/modrá - konfigurovatelné). Použití fontů s pevnou šířkou (monospaced).
    
-   Omezení: Uživatel nemůže používat pravé tlačítko myši (zablokováno JS), nemůže kopírovat text ven. Aplikace běží v režimu "Full Screen Kiosk" (pokud to prohlížeč dovolí).
    
-   Glitch Efekty: Frontend naslouchá proměnné visual_glitch_level ze serveru. Pokud hodnota stoupne, CSS aplikuje náhodné posuny (transform: translate), rozmazání (filter: blur) a problikávání.
    

### 7.2 Moduly Terminálu

1.  Chat Stream: Hlavní okno. Zprávy se vypisují znak po znaku (typewriter effect) pro simulaci starého hardwaru a "přemýšlení" AI.
    
2.  Task Manager: Seznam dostupných úkolů. Uživatel zde odevzdává textová řešení.
    
3.  Marketplace: Obchod, kde uživatel utrácí kredity za "Tokeny na dotazy" nebo "Vylepšení statusu". Ceny jsou dynamicky načítány ze serveru (reflektují inflaci).
    
4.  Report Button: Tlačítko s vykřičníkem u každé příchozí zprávy. Umožňuje nahlásit "podezřelou AI".
    

## 

----------

8. Bezpečnost a Stabilita (ZED Prostředí)

V izolovaném prostředí bez přístupu k internetu je stabilita absolutní prioritou.

### 8.1 Ošetření Chyb (Error Handling)

-   WebSocket Reconnect: Klient (JS) musí implementovat "Exponential Backoff" strategii pro znovupřipojení. Pokud server spadne, klient zkouší připojení po 1s, 2s, 4s, 8s... Zároveň zobrazuje uživateli "SYSTEM CONNECTION LOST... RETRYING".
    
-   Graceful Degradation: Pokud selže databáze (např. lock), server nesmí spadnout. Musí zachytit výjimku, zalogovat ji a poslat uživateli zprávu "DATABASE ERROR - TRY AGAIN".
    

### 8.2 Sanitizace a Validace

Ačkoliv jde o uzavřenou hru, nelze vyloučit pokusy hráčů o "hackování" (SQL Injection přes chat input).

-   Pydantic Modely: Veškerá data vstupující do API jsou validována striktními schématy.
    
-   SQL Parameters: aiosqlite je používáno výhradně s parametrizovanými dotazy (execute("SELECT * FROM users WHERE id=?", (user_id,))).
    

## 

----------

9. Plán Vývoje a Testování

Vývoj je strukturován do iterativních fází pro jednoho programátora.

### Fáze 1: Core Architektura (Dny 1-2)

-   Setup projektu (FastAPI, uvicorn).
    
-   Implementace SQLite schématu a migračních skriptů.
    
-   Základní REST API pro autentizaci (JWT tokeny).
    
-   Milestone: Fungující login a vytvoření uživatele v DB.
    

### Fáze 2: Real-time Chat (Dny 3-4)

-   Implementace ConnectionManager a WebSocket endpointů.
    
-   Základní routing zpráv (User <-> Agent).
    
-   Frontend prototyp (pouze textové pole a výpis).
    
-   Milestone: Dva prohlížeče si mohou posílat zprávy.
    

### Fáze 3: Herní Enginy (Dny 5-7)

-   Implementace Economy Engine (kredity, transakce).
    
-   Implementace Rotation Engine (Shift+1 logika v SQL).
    
-   Implementace Chernobyl Engine (logika instability).
    
-   Integrace HYPER módů do backendu.
    
-   Milestone: Funkční rotace agentů a přičítání kreditů.
    

### Fáze 4: UI/UX a Dashboardy (Dny 8-10)

-   Vytvoření HTML/JS šablon pro Dashboardy.
    
-   Stylování Terminálů (CSS efekty).
    
-   Vizualizace Chernobyl baru.
    
-   Milestone: Kompletní vizuální podoba systému.
    

### Fáze 5: Stress Testing a Deployment (Dny 11-12)

-   Test T1 (Concurrency): Skript simulující 50 klientů posílajících zprávy každých 100ms. Cíl: Server nesmí spadnout, latence pod 200ms.
    
-   Test T2 (Recovery): Tvrdé vypnutí serveru (kill -9) během simulované zátěže. Po startu musí být data konzistentní (WAL mode test).
    
-   Test T3 (Logic): Ověření, že Shift+1 správně přehodí uživatele a neztratí zprávy ve frontě.
    

### Závěr

Tento dokument specifikuje systém, který není jen pasivním nástrojem, ale aktivním účastníkem LARPu Iris. Jeho architektura kombinuje robustnost průmyslového softwaru s flexibilitou herního enginu, čímž vytváří ideální podhoubí pro vznik požadované atmosféry paranoie a odhalování skryté pravdy o projektu Eltex.

#### Citovaná díla

1.  HNV- Iris, kostra příběhu.pdf
