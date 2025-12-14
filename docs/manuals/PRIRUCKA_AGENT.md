# IRIS Systém - Příručka pro Agenty (Operátory)

**Verze:** 2.0  
**Jazyk:** Český  
**Pro:** Agenti/Operátoři LARP hry

---

## Obsah

1. [Úvod](#1-úvod)
2. [Přihlášení do systému](#2-přihlášení-do-systému)
3. [Rozhraní agenta](#3-rozhraní-agenta)
4. [Komunikace se subjekty](#4-komunikace-se-subjekty)
5. [Autopilot a AI](#5-autopilot-a-ai)
6. [Speciální stavy](#6-speciální-stavy)
7. [Slovník pojmů](#7-slovník-pojmů)

---

## 1. Úvod

Jako **Agent (Operátor)** jste odpovědní za komunikaci se subjekty (běžnými hráči). Odpovídáte na jejich zprávy a pomáháte jim v rámci herního světa.

### Vaše role

- Odpovídáte na zprávy od přidělených subjektů
- Musíte reagovat včas (sledujte časovač)
- Můžete využít AI asistenci (Autopilot)

---

## 2. Přihlášení do systému

### Adresa systému
Otevřete webový prohlížeč a přejděte na adresu, kterou vám sdělí organizátoři (např. `http://iris.local:8000`).

### Přihlašovací údaje
- **Uživatel:** `agent1` až `agent8`
- **Heslo:** sdělí vám organizátoři

### Přihlašovací obrazovka
1. Do pole **IDENTIFIKÁTOR** zadejte své uživatelské jméno.
2. Do pole **HESLO** zadejte své heslo.
3. Klikněte na tlačítko **[ INICIOVAT RELACI ]**.

---

## 3. Rozhraní agenta

Po přihlášení jako agent uvidíte růžový terminál s těmito částmi:

### 3.1 Levý panel - Status

#### CÍLOVÝ POSUN SVĚTA
- Zobrazuje aktuální shift hodnotu
- Určuje, s jakým subjektem komunikujete

#### STAV PŘIPOJENÍ
- Ukazuje vaše ID relace (např. S1, S2...)
- Zelená tečka = připojeno

#### ČASOVAČ ODPOVĚDI
- Žlutý pruh ukazuje zbývající čas na odpověď
- Když čas vyprší, vstup se zablokuje
- Po odeslání zprávy se časovač resetuje

### 3.2 Chat panel
Hlavní prostor pro komunikaci se subjekty.

---

## 4. Komunikace se subjekty

### Přijímání zpráv
- Zprávy od subjektů se zobrazují automaticky
- Nová zpráva spustí časovač odpovědi

### Odpovídání
1. Napište odpověď do pole **Inject response...**
2. Klikněte **TRANSMIT** nebo stiskněte Enter

### Časový limit
- Musíte odpovědět včas, jinak se vstup zablokuje
- Sledujte žlutý pruh časovače

---

## 5. Autopilot a AI

### 5.1 Tlačítko [ TOGGLE AUTOPILOT ]
- Aktivuje automatický režim odpovídání
- Když je zapnutý, AI odpovídá místo vás
- Tlačítko zčervená když je aktivní

### 5.2 AI Optimalizace
- Pokud je aktivní AI Optimizer, vaše zprávy budou přepsány
- Uvidíte loader **⚙️ NEURAL REWRITING IN PROGRESS...**
- Po přepsání se zobrazí náhled:
  - Původní text přeškrtnutý
  - Nový text zeleně
- Můžete potvrdit nebo odmítnout přepis

---

## 6. Speciální stavy

### 6.1 Zámek vstupu (Timeout)
- Pokud neodpovíte včas, vstup se zablokuje
- Zobrazí se overlay **INPUT LOCKED - Connection timeout**
- Subjekt musí poslat novou zprávu

### 6.2 Overload signál
- V pravém rohu se může objevit **⚠ SYSTEM OVERLOAD ⚠**
- Signalizuje přetížení systému

### 6.3 Odhlášení
- Klikněte na **[ DISCONNECT ]** v pravém horním rohu

---

## 7. Slovník pojmů

| Pojem | Význam |
|-------|--------|
| **Shift** | Časový posun, určuje párování subjekt-agent |
| **Subjekt** | Uživatel (běžný hráč), se kterým komunikujete |
| **Autopilot** | Automatické odpovídání AI místo agenta |
| **Optimizer** | AI přepisující zprávy agentů |
| **Overload** | Přetížení systému (load > capacity) |
| **Timeout** | Vypršení časového limitu pro odpověď |

---

**Poslední aktualizace:** 2025-12-14
