# IRIS Systém - Příručka pro Systémového Inženýra

**Verze:** 2.0  
**Jazyk:** Český  
**Pro:** IT / Technika zodpovědná za instalaci a provoz

---

## Obsah

1. [Požadavky](#1-požadavky)
2. [Instalace](#2-instalace)
3. [Spuštění](#3-spuštění)
4. [Automatický start (Systemd)](#4-automatický-start-systemd)
5. [Konfigurace](#5-konfigurace)
6. [Údržba](#6-údržba)
7. [Řešení problémů](#7-řešení-problémů)
8. [Bezpečnost](#8-bezpečnost)

---

## 1. Požadavky

### Hardware
- Jakýkoliv počítač s min. 1GB RAM
- Síťové připojení (LAN/WiFi)

### Software
- Linux (doporučeno Ubuntu 22.04+) nebo Windows 10+
- Python 3.10+
- Webový prohlížeč (Chrome/Firefox)

### Síť
- Port 8000 musí být dostupný v lokální síti
- Doporučeno: Statická IP nebo hostname

---

## 2. Instalace

### Stažení projektu
```bash
git clone <repository_url>
cd iris-app/IRIS_LARP
```

### Spuštění instalace
```bash
chmod +x install.sh
./install.sh
```

Skript provede:
1. Kontrolu Pythonu
2. Vytvoření virtuálního prostředí (`venv/`)
3. Instalaci závislostí z `requirements.txt`

### Výstup úspěšné instalace
```
[IRIS] Starting Installation...
[IRIS] Creating virtual environment...
[IRIS] Installing dependencies...
[IRIS] Installation Complete.
[IRIS] Use './run.sh' to start the system.
```

---

## 3. Spuštění

### Manuální spuštění
```bash
./run.sh
```

Skript:
1. Aktivuje virtuální prostředí
2. Uvolní port 8000 (pokud obsazen)
3. Spustí server

### Výstup
```
[IRIS] Booting System...
INFO: Uvicorn running on http://0.0.0.0:8000
```

### Přístup
- Otevřete prohlížeč: `http://<IP_SERVERU>:8000`
- Pro localhost: `http://localhost:8000`

---

## 4. Automatický start (Systemd)

### Příprava služby

1. Zkopírujte šablonu:
```bash
sudo cp iris.service /etc/systemd/system/
```

2. Upravte cesty v souboru:
```bash
sudo nano /etc/systemd/system/iris.service
```

Změňte tyto hodnoty:
```ini
User=<váš_uživatel>
WorkingDirectory=/cesta/k/IRIS_LARP
ExecStart=/cesta/k/IRIS_LARP/venv/bin/python run.py
```

### Aktivace
```bash
sudo systemctl daemon-reload
sudo systemctl enable iris
sudo systemctl start iris
```

### Kontrola stavu
```bash
sudo systemctl status iris
```

### Zobrazení logů
```bash
journalctl -u iris -f
```

### Restart služby
```bash
sudo systemctl restart iris
```

---

## 5. Konfigurace

### Soubor .env (volitelný)
Vytvořte soubor `.env` v kořenovém adresáři:
```bash
OPENROUTER_API_KEY=sk-or-...
SECRET_KEY=your_jwt_secret_here
```

### Default Scenario
Soubor `data/default_scenario.json` obsahuje:

```json
{
    "users": {
        "root": { "password": "master_control_666" },
        "admins": { "count": 4, "password_pattern": "secure_admin_{i}" },
        "agents": { "count": 8, "password_pattern": "agent_pass_{i}" },
        "users": { "count": 8, "password_pattern": "subject_pass_{i}" }
    },
    "economy": { "treasury_balance": 500, "tax_rate": 0.20 },
    "power": { "capacity": 100 }
}
```

> [!WARNING]
> Změny v tomto souboru se projeví až po **FACTORY RESET** z ROOT konzole nebo po smazání `data/iris.db`.

### Úprava počtu uživatelů
Změňte hodnoty `count` v příslušných sekcích `default_scenario.json`.

---

## 6. Údržba

### Záloha dat
```bash
cp data/iris.db data/iris_backup_$(date +%Y%m%d).db
```

### Kontrola logů
```bash
tail -100 server.log
```

### Čištění logů
```bash
> server.log
```

### Obnova ze zálohy
```bash
systemctl stop iris
cp data/iris_backup_YYYYMMDD.db data/iris.db
systemctl start iris
```

---

## 7. Řešení problémů

### Server se nespustí

**Problém:** `[ERROR] Port 8000 in use`
```bash
# Ukončit proces na portu
fuser -k 8000/tcp
# Nebo najít PID
lsof -i :8000
kill <PID>
```

**Problém:** `ModuleNotFoundError`
```bash
# Přeinstalovat závislosti
source venv/bin/activate
pip install -r requirements.txt
```

### Databáze je zamčená

**Řešení:**
```bash
# Zastavit server
systemctl stop iris
# Smazat databázi (POZOR: ztráta dat!)
rm data/iris.db
# Spustit znovu (vytvoří novou DB)
systemctl start iris
```

### Uživatelé se nemohou přihlásit

1. Zkontrolujte, zda server běží:
```bash
systemctl status iris
```

2. Zkontrolujte síťové připojení:
```bash
curl http://localhost:8000
```

3. Zkontrolujte logy:
```bash
tail -50 server.log
```

### Factory Reset nefunguje

**Manuální provedení:**
```bash
systemctl stop iris
rm data/iris.db
systemctl start iris
```

---

## 8. Bezpečnost

### Soubory, které NESMÍ být v gitu
- `data/iris.db` - databáze
- `data/admin_labels.json` - runtime konfigurace
- `.env` - API klíče
- `server.log` - logy
- `venv/` - virtuální prostředí

### Kontrola .gitignore
```bash
git status
# Žádné .db ani .env soubory by neměly být v seznamu
```

### Změna hesel pro produkci
1. Upravte `data/default_scenario.json`
2. Proveďte FACTORY RESET
3. Sdělte nová hesla hráčům bezpečným kanálem

### Firewall
Pro produkci omezte přístup pouze na port 8000:
```bash
sudo ufw allow 8000/tcp
sudo ufw enable
```

---

## Struktura projektu

```
IRIS_LARP/
├── app/                    # Python aplikace
│   ├── routers/            # API endpoints
│   ├── templates/          # HTML šablony
│   ├── logic/              # Herní logika
│   ├── main.py             # FastAPI app
│   ├── database.py         # SQLAlchemy modely
│   └── seed.py             # Inicializace DB
├── data/
│   ├── default_scenario.json  # Konfigurace (TRACKOVAT)
│   ├── iris.db                # Databáze (IGNOROVAT)
│   └── admin_labels.json      # Labels (IGNOROVAT)
├── static/                 # CSS, JS, assets
├── docs/                   # Dokumentace
├── tests/                  # Testy
├── install.sh              # Instalační skript
├── run.sh                  # Spouštěcí skript
├── run.py                  # Python entry point
├── iris.service            # Systemd šablona
└── requirements.txt        # Závislosti
```

---

## Kontakt na podporu

V případě problémů kontaktujte organizátory hry.

---

**Poslední aktualizace:** 2025-12-14
