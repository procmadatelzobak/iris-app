# IRIS Systém - Uživatelská Příručka

**Verze:** 2.0  
**Jazyk:** Český  
**Pro:** Všichni hráči LARP hry

---

## Obsah

1. [Úvod](#1-úvod)
2. [Přihlášení do systému](#2-přihlášení-do-systému)
3. [Příručka pro Subjekty (Uživatele)](#3-příručka-pro-subjekty-uživatele)
4. [Příručka pro Agenty/Operátory](#4-příručka-pro-agentyoperátory)
5. [Příručka pro Správce](#5-příručka-pro-správce)
6. [Slovník pojmů](#6-slovník-pojmů)

---

## 1. Úvod

IRIS je komunikační systém pro LARP hru, kde uživatelé (subjekty) komunikují s agenty prostřednictvím terminálů. Systém simuluje dystopickou korporátní AI infrastrukturu.

### Role v systému

| Role | Popis | Počet |
|------|-------|-------|
| **Subjekt (User)** | Běžný hráč, který komunikuje s agentem | 8 |
| **Agent (Operátor)** | Odpovídá na zprávy subjektů, plní úkoly | 8 |
| **Správce (Admin)** | Ovládá herní mechaniky, schvaluje úkoly | 4 |
| **ROOT** | Hlavní správce, gamemaster | 1 |

---

## 2. Přihlášení do systému

### Adresa systému
Otevřete webový prohlížeč a přejděte na adresu, kterou vám sdělí organizátoři (např. `http://iris.local:8000`).

### Přihlašovací obrazovka
1. Do pole **IDENTIFIKÁTOR** zadejte své uživatelské jméno.
2. Do pole **HESLO** zadejte své heslo.
3. Klikněte na tlačítko **[ INICIOVAT RELACI ]**.

### Testovací režim
Pokud je aktivní testovací režim, uvidíte na přihlašovací obrazovce rychlá tlačítka pro přihlášení bez hesla. Toto je pouze pro testování.

---

## 3. Příručka pro Subjekty (Uživatele)

Po přihlášení jako subjekt uvidíte terminál s těmito částmi:

### 3.1 Levý panel - Stav subjektu

#### POSUN SVĚTA
- Zobrazuje aktuální časový posun (0-7)
- Ovlivňuje, s jakým agentem komunikujete
- Hodnotu mění správci hry

#### KREDITY
- Vaše virtuální měna
- Získáváte za splněné úkoly
- Můžete ztratit za pokuty

### 3.2 Sekce ÚKOLY

#### Tlačítko [ + VYŽÁDAT ]
- Kliknutím požádáte o nový úkol
- Úkol musí schválit správce
- Po schválení se zobrazí v seznamu

#### Stavy úkolu
| Stav | Význam |
|------|--------|
| ČEKÁ NA SCHVÁLENÍ | Požádali jste o úkol, správce jej musí schválit |
| AKTIVNÍ | Úkol je přidělen, můžete na něm pracovat |
| DOKONČENO | Úkol jste odevzdali |

#### Odevzdání úkolu
1. V seznamu úkolů najděte aktivní úkol
2. Do textového pole napište svou odpověď
3. Klikněte na tlačítko **[ ODEVZDAT ]**

### 3.3 Pravý panel - Chat

#### Posílání zpráv
1. Do pole ve spodní části napište zprávu
2. Klikněte na **[ ODESLAT ]** nebo stiskněte Enter

#### Přijaté zprávy
- Zprávy od agenta se zobrazují v chatu
- U každé zprávy vidíte odesílatele

#### Tlačítko [ ! ] (Report)
- U zpráv od agenta můžete nahlásit problém
- Kliknutím na **[ ! ]** nahlásíte zprávu jako anomálii
- **Poznámka:** Některé zprávy jsou "ověřené" (mají badge **✓ VERIFIED**) a nelze je nahlásit

### 3.4 Speciální stavy

#### Zablokovaný terminál (Purgatory)
- Pokud máte záporné kredity, chat je zablokován
- Zobrazí se červený overlay s nápisem **COMMUNICATION OFFLINE**
- Stále můžete žádat o úkoly a odevzdávat je
- Po vyrovnání kreditů se terminál odemkne

#### Glitch režim
- Při přetížení systému se obrazovka může třást a měnit barvy
- Toto je zamýšlený herní efekt

### 3.5 Odhlášení
- Klikněte na tlačítko **ODHLÁSIT** v pravém horním rohu

---

## 4. Příručka pro Agenty/Operátory

Po přihlášení jako agent uvidíte růžový terminál s těmito částmi:

### 4.1 Levý panel - Status

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

### 4.2 Tlačítko [ TOGGLE AUTOPILOT ]
- Aktivuje automatický režim odpovídání
- Když je zapnutý, AI odpovídá místo vás
- Tlačítko zčervená když je aktivní

### 4.3 Chat panel

#### Přijímání zpráv
- Zprávy od subjektů se zobrazují automaticky
- Nová zpráva spustí časovač odpovědi

#### Odpovídání
1. Napište odpověď do pole **Inject response...**
2. Klikněte **TRANSMIT** nebo stiskněte Enter

#### AI Optimalizace
- Pokud je aktivní AI Optimizer, vaše zprávy budou přepsány
- Uvidíte loader **⚙️ NEURAL REWRITING IN PROGRESS...**
- Po přepsání se zobrazí náhled:
  - Původní text přeškrtnutý
  - Nový text zeleně
- Můžete potvrdit nebo odmítnout přepis

### 4.4 Speciální stavy

#### Zámek vstupu (Timeout)
- Pokud neodpovíte včas, vstup se zablokuje
- Zobrazí se overlay **INPUT LOCKED - Connection timeout**
- Subjekt musí poslat novou zprávu

#### Overload signál
- V pravém rohu se může objevit **⚠ SYSTEM OVERLOAD ⚠**
- Signalizuje přetížení systému

### 4.5 Odhlášení
- Klikněte na **[ DISCONNECT ]** v pravém horním rohu

---

## 5. Příručka pro Správce

Po přihlášení jako správce uvidíte dashboard s těmito stanicemi:

### 5.1 HUB (Výchozí obrazovka)

Po přihlášení vidíte 4 stanice:

| Stanice | Barva | Funkce |
|---------|-------|--------|
| **UMYVADLO** | Zelená | Monitoring - sledování všech relací |
| **ROZKOŠ** | Žlutá | Kontrola - herní nastavení |
| **BAHNO** | Modrá | Ekonomika - správa kreditů |
| **MRKEV** | Fialová | Úkoly - schvalování a vyplácení |

Kliknutím na stanici se otevře její detail.

### 5.2 Stanice MONITORING (UMYVADLO)

#### Záložka VŠEVIDOUCÍ
- Mřížka všech 8 relací
- Vidíte živé chaty mezi subjekty a agenty
- Vpravo je mini-log systémových událostí

#### Záložka ŠUM
- Pouze chat karty bez logu

#### Záložka HISTORIE OMYLŮ
- Kompletní systémový log
- Tlačítko **VYMAZAT HISTORII** smaže log

#### Záložka PAVUČINA
- Grafické zobrazení sítě (experimentální)

#### SHIFT display
- V pravém horním rohu vidíte aktuální SHIFT hodnotu

### 5.3 Stanice KONTROLA (ROZKOŠ)

#### POSUN REALITY
- Velké číslo ukazuje aktuální shift
- Tlačítko **[ ROZTOČIT KOLA OSUDU ]** zvýší shift o 1

#### TLAK PÁRY (Power)
- Modrý pruh ukazuje zatížení vs. kapacitu
- Tlačítko **[ PŘIHODIT UHLÍ ]** přidá 50MW na 30 minut za 1000 CR
- Pokud je boost aktivní, zobrazí se odpočet

#### HLADINA STRESU (Teplota)
- Barevný pruh od zelené po červenou
- Manuální posuvník pro ruční nastavení
- Režimy: NORMÁL / ÚSPORA / PŘETÍŽENÍ

#### FILTR PRAVDY (Visibility)
- ŽÁDNÝ - Agenti vidí vše normálně
- ČERNÁ SKŘÍŇKA - Agenti nevidí historii
- FOREZKA - Speciální forenzní režim

### 5.4 Stanice EKONOMIKA (BAHNO)

#### NÁRODNÍ BANKA BAHNA
- Zobrazuje celkový stav pokladny (Treasury)

#### Tabulka uživatelů
- Seznam všech subjektů
- Sloupce: Jméno, Kredity, Status, Locked

#### Akce pro každého uživatele
| Tlačítko | Funkce |
|----------|--------|
| **[+]** | Přidat kredity (bonus) |
| **[-]** | Odebrat kredity (pokuta) |
| **[LOCK]** | Zablokovat terminál |
| **[UNLOCK]** | Odblokovat terminál |

### 5.5 Stanice ÚKOLY (MRKEV)

#### Seznam úkolů
- Vidíte všechny úkoly od subjektů
- Stavy: Pending (čeká), Active (aktivní), Submitted (odevzdáno)

#### Akce pro úkoly
| Tlačítko | Funkce |
|----------|--------|
| **[APPROVE]** | Schválit žádost o úkol |
| **[REJECT]** | Zamítnout žádost |
| **[PAY]** | Vyplatit odměnu za dokončený úkol |

### 5.6 Horní lišta

#### PŘEPSAT REALITU
- Zapne editační režim pro přejmenování prvků
- Klikněte na libovolný text a přepište ho
- Klikněte znovu pro uložení

#### MODZEK (AI Config)
- Otevře modální okno pro nastavení AI
- API klíče, modely, prompt

#### AUTO-DESTRUKCE
- Resetuje herní stav (kredity, úkoly, logy)
- Vyžaduje potvrzení

#### ODHLÁSIT
- Odhlásí vás ze systému

---

## 6. Slovník pojmů

| Pojem | Význam |
|-------|--------|
| **Shift** | Časový posun, určuje párování subjekt-agent |
| **Kredity** | Virtuální měna v systému |
| **Treasury** | Společná pokladna správců |
| **Glitch** | Vizuální efekt při přetížení systému |
| **Purgatory** | Stav, kdy má subjekt záporné kredity |
| **Optimizer** | AI přepisující zprávy agentů |
| **Autopilot** | Automatické odpovídání AI místo agenta |
| **Overload** | Přetížení systému (load > capacity) |

---

## Problémy a chybějící funkce

> [!WARNING]
> **Následující funkce nejsou zcela implementovány nebo dokumentovány:**

1. **Synchronizace mezi zařízeními** - Agent může mít otevřeno více oken/zařízení, text se synchronizuje, ale chování není plně zdokumentováno.

2. **Téma uživatele** - Uživatelé mají různé vizuální témata podle `status_level` (low/mid/high), ale není jasné, jak se toto nastavuje.

3. **Zvukové efekty** - Systém má zvuky pro psaní, příjem zpráv a chyby, ale jejich hlasitost a vypnutí není dokumentováno.

4. **WebSocket reconnect** - Při výpadku spojení by se měl klient automaticky znovu připojit, ale není to garantováno.

---

**Poslední aktualizace:** 2025-12-14
