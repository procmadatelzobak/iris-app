# IRIS Systém - Příručka pro ROOT (Gamemaster)

**Verze:** 2.0  
**Jazyk:** Český  
**Pro:** Hlavní organizátor hry (Gamemaster)

---

## Obsah

1. [Přístup do ROOT konzole](#1-přístup-do-root-konzole)
2. [Panopticon - Hlavní přehled](#2-panopticon---hlavní-přehled)
3. [Config - Nastavení AI](#3-config---nastavení-ai)
4. [Chronos - Časování](#4-chronos---časování)
5. [Ekonomika](#5-ekonomika)
6. [Výkonné protokoly](#6-výkonné-protokoly)
7. [Pokročilé funkce](#7-pokročilé-funkce)

---

## 1. Přístup do ROOT konzole

### Přihlašovací údaje
- **Uživatel:** `root`
- **Heslo:** sdělí vám organizátoři

### Po přihlášení
- Uvidíte zlatý dashboard s názvem **IRIS_ROOT_CONTROL**
- Máte přístup ke všem funkcím systému

---

## 2. Panopticon - Hlavní přehled

Kliknutím na záložku **PANOPTICON** získáte přehled o celém systému.

### 2.1 SYSTEM STATUS

| Ukazatel | Význam |
|----------|--------|
| **SHIFT OFFSET** | Aktuální hodnota posunu (0-7) |
| **ONLINE USERS** | Počet připojených uživatelů |
| **CHERNOBYL** | Úroveň nestability systému |

### 2.2 PHYSICS CONSTANTS

**TAX RATE (0.0 - 1.0)**
- Procento z odměny za úkol, které jde do Treasury
- Výchozí: 0.20 (20%)

**POWER CAP (MW)**
- Maximální kapacita systému v megawattech
- Výchozí: 100

Tlačítko **[ APPLY PHYSICS ]** uloží změny.

### 2.3 EXECUTIVE PROTOCOLS

| Tlačítko | Funkce |
|----------|--------|
| **>> FORCE SHIFT >>** | Zvýší shift o 1 |
| **GLOBAL BROADCAST** | Pošle zprávu všem uživatelům |
| **[ SYSTEM RESET ]** | Resetuje kredity, úkoly, logy (zachová DB) |
| **RELOAD UI** | Obnoví stránku |
| **[ RESTART SERVER ]** | Restartuje Python server (~5s výpadek) |
| **[ FACTORY RESET ]** | Smaže databázi a restartuje s defaulty |

> [!CAUTION]
> **FACTORY RESET** smaže VEŠKERÁ data! Vyžaduje potvrzení textem "FACTORY RESET".

### 2.4 SYSTEM LOG STREAM

- Živý přehled všech systémových událostí
- Akce uživatelů, správců, chyby

---

## 3. Config - Nastavení AI

Kliknutím na záložku **CONFIG** nastavíte AI funkce.

### 3.1 TEST MODE

**Tlačítko [ TEST MODE: DISABLED/ENABLED ]**
- Zapne rychlá přihlašovací tlačítka na login obrazovce
- Pro testování bez hesel

### 3.2 AI KEYS

**API Key**
- Zadejte OpenRouter/OpenAI API klíč
- Tlačítko **[ SAVE KEY ]** uloží

### 3.3 Hyper Config

**Model Name**
- Název modelu pro autopilota (např. `google/gemini-2.0-flash-lite-preview-02-05:free`)

**Optimizer Prompt**
- Text, podle kterého AI přepisuje zprávy agentů

Tlačítko **[ APPLY ]** uloží nastavení.

---

## 4. Chronos - Časování

Kliknutím na záložku **CHRONOS** ovládáte čas hry.

### 4.1 TARGET SHIFT

- Velké číslo ukazuje aktuální shift
- Tlačítko **[ EXECUTE ]** posune čas o 1

### 4.2 Manual Override

- Posuvník pro ruční nastavení shift hodnoty

---

## 5. Ekonomika

Kliknutím na záložku **ECONOMY** spravujete herní ekonomiku.

### 5.1 Přehled

| Pole | Význam |
|------|--------|
| **TREASURY** | Celková suma ve společné pokladně |

### 5.2 Tabulka uživatelů

Pro každého uživatele můžete:

| Akce | Popis |
|------|-------|
| **[+100]** | Přidat 100 kreditů |
| **[-100]** | Odebrat 100 kreditů |

---

## 6. Výkonné protokoly

### 6.1 SYSTEM RESET (Soft Reset)

Tlačítko pro herní reset, které simuluje **failover na záložní server**.

**Co se resetuje:**
- Teplota systému (vrací se na výchozí hodnotu)
- Vlastní názvy tlačítek a textů na dashboardech správců
- Vizuální efekty (glitch, hyper mód)

**Co zůstává zachováno:**
- Kredity uživatelů
- Power nastavení (kapacita, zatížení)
- Hodnota shiftu
- Databáze uživatelů a úkolů

**Systémová zpráva:**
Všem uživatelům (Users, Agents, Admins) se zobrazí overlay s textem:
> ⚠️ SYSTÉM REINICIALIZOVÁN ⚠️
> Došlo k přepnutí na záložní server v rámci failover protokolu.
> Všechny relace byly obnoveny. Pokračujte v práci.

- Vyžaduje potvrzení textem "NUKE"

### 6.2 RESTART SERVER
- Ukončí aktuální Python proces
- Spustí nový proces
- Všichni uživatelé budou odpojeni (~5s)
- Po restartu se musí znovu přihlásit

### 6.3 FACTORY RESET (Hard Reset)
- Smaže soubor `data/iris.db`
- Restartuje server
- Databáze se znovu vytvoří z `data/default_scenario.json`
- **VEŠKERÁ DATA BUDOU ZTRACENA**
- Vyžaduje potvrzení textem "FACTORY RESET"

---

## 7. Pokročilé funkce

### 7.1 Úprava default scenaria

Soubor `data/default_scenario.json` obsahuje:
- Počty a hesla uživatelů
- Výchozí hodnoty ekonomiky
- Nastavení power systému
- Konfiguraci LLM

Po úpravě tohoto souboru proveďte **FACTORY RESET** pro aplikaci změn.

### 7.2 Systemd služba

Pro produkční provoz použijte:
```bash
sudo cp iris.service /etc/systemd/system/
sudo systemctl enable iris
sudo systemctl start iris
```

### 7.3 Logy serveru

```bash
tail -f server.log
# nebo
journalctl -u iris -f
```

---

## Známé problémy

> [!WARNING]
> Následující funkce vyžadují pozornost:

1. **GLOBAL BROADCAST** - Tlačítko existuje, ale funkce nemusí být plně implementována v backendu.

2. **Reconnect po restartu** - Uživatelé by měli obnovit stránku po restartu serveru.

3. **Multiple ROOT sessions** - Není ošetřeno, co se stane při více současných ROOT přihlášeních.

---

**Poslední aktualizace:** 2025-12-14
