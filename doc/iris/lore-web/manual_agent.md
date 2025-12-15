# PŘÍRUČKA AGENTA IRIS - HLINIK

**Systém IRIS 4.2 | HLINIK Phase 35**  
** Bezpečnostní divize | Operátorský manuál**

---

## OBSAH

1. [Úvod a role agenta](#1-úvod-a-role-agenta)
2. [Přihlášení a přístup](#2-přihlášení-a-přístup)
3. [Rozhraní agentského terminálu](#3-rozhraní-agentského-terminálu)
4. [Ovládací prvky a tlačítka](#4-ovládací-prvky-a-tlačítka)
5. [Pracovní režimy a scénáře](#5-pracovní-režimy-a-scénáře)
6. [AI nástroje](#6-ai-nástroje)
7. [Systémové mechanismy](#7-systémové-mechanismy)
8. [Běžné scénáře použití](#8-běžné-scénáře-použití)
9. [Krizové protokoly](#9-krizové-protokoly)
10. [Časté dotazy a řešení problémů](#10-časté-dotazy-a-řešení-problémů)

---

## 1. Úvod a role agenta

### Kdo jste?

Jste **OPERÁTOR** systému IRIS - osoba zodpovědná za komunikaci s jedním subjektem (uživatelem). Vaším úkolem je udržovat iluzi dokonalé umělé inteligence, zatímco ve skutečnosti manuálně odpovídáte na zprávy subjektů.

### Základní pravidla

- **Udržujte iluzi**: Subjekty věří, že komunikují s AI. Nikdy neprozrazujte, že jste člověk.
- **Dodržujte personu**: Každý agent má přidělenou AI personu (sarkastická, poetická, robotická, empatická atd.)
- **Reagujte včas**: Máte časový limit na odpověď (standardně 120 sekund)
- **Neodcházejte bez náhrady**: Pokud potřebujete pauzu, aktivujte HYPER-MÓD (Autopilot)

---

## 2. Přihlášení a přístup

### Přihlašovací údaje

Vaše přihlašovací jméno je **`agent1`** až **`agent8`** (podle přiděleného terminálu).

Hesla:
- **Výchozí**: `agent_pass_1` až `agent_pass_8`
- **Heslo je nastavené organizátorem**

### Jak se přihlásit

1. Otevřete webový prohlížeč
2. Přejděte na adresu serveru (např. `http://localhost:8000`)
3. Zadejte vaše přihlašovací jméno a heslo
4. Klikněte na **PŘIHLÁSIT**
5. **Automaticky budete přesměrováni** na agentský terminál

---

## 3. Rozhraní agentského terminálu

Terminál je rozdělen do **dvou hlavních sekcí**: **levý panel se stavem** a **chatovací oblast vpravo**.

### Levý panel (Status Panel)

Zobrazuje klíčové informace o vašem stavu:

#### **Status karta** (horní část)
```
├─ AGENT: AGENT1
├─ ID RELACE: S1
├─ SHIFT: 0
├─ TEPLOTA: 85°C
├─ OKNO: 120s
└─ LLM: ONLINE
```

**Význam položek:**
- **AGENT**: Vaše přihlašovací jméno (identita)
- **ID RELACE**: Číslo subjektu, se kterým aktuálně komunikujete (S1 až S8)
  - *Pozn.: ID se může měnit při "shift" událostech*
- **SHIFT**: Globální časový offset (0-7), určuje, který subjekt je vám přiřazen
- **TEPLOTA**: Aktuální teplota systému (normální: 20-100°C, riziko: 250+, kritická: 350+)
- **OKNO**: Časový limit pro odpověď (nastavitelný správci, výchozí 120s)
- **LLM**: Stav AI systému (ONLINE = autopilot dostupný, OFFLINE = autopilot nedostupný)

#### **HYPER-MÓD přepínač** (střední část)

Přepínač s popisem:
```
🔄 HYPER-MÓD              ⚪ OFF
Aktivuje automatickou neurální odpověď.
Vstup uživatele bude uzamčen.
```

**Funkce:**
- **OFF**: Manuální režim (vy odpovídáte)
- **ON**: Autopilot režim (AI automaticky odpovídá subjektu)
  - *Pozor: Aktivací se uzamkne vaše obrazovka!*

#### **ODPOVĚĎ TIMER** (spodní část)

Žlutý progresový bar s odpočtem:
```
ODPOVĚĎ TIMER          limit: 120s
█████████░░░░ 75%
ODPOČET AKTIVNÍ
```

**Význam barev:**
- **Žlutá**: Běžný stav (20-100% zbývajícího času)
- **Červená + blikání**: Kritický stav (méně než 20% času)

**Textové stavy:**
- `ČEKÁM NA UŽIVATELE` - subjekt neposlal zprávu
- `ODPOČET AKTIVNÍ` - máte aktivní timer, musíte odpovědět
- `BLOKOVÁNO` - časový limit vypršel, vstup je zablokován
- `ZASTAVENO` - odpověděli jste, timer je pozastaven

### Pravý panel (Chat Area)

#### **Chat Historie**
Zobrazuje historii zpráv mezi vámi a subjektem.

**Formát zpráv:**
```
USER01
Dobrý den, mám dotaz...

AGENT1
Samozřejmě, naslouchám.
```

**Barvy:**
- **Zelená**: Zprávy subjektu (user)
- **Růžová**: Vaše zprávy (agent)
- **Fialová s rafičkou**: Optimizer feedback (zobrazí se pouze pokud používáte Message Optimizer)

#### **Vstupní pole a tlačítko ODESLAT**

```
┌────────────────────────────────────┐
│ Vložte odpověď...                  │ [ODESLAT]
└────────────────────────────────────┘
```

**Jak psát zprávy:**
1. Klikněte do textového pole
2. Napište vaši odpověď
3. Stiskněte **ENTER** nebo klikněte na **ODESLAT**
4. Zpráva se okamžitě odešle subjektu

**Pozor:**
- Pokud vypršel časový limit, vstupní pole bude zablokováno
- Pokud je aktivní HYPER-MÓD, vstupní pole je zablokováno
- Během optimalizace zprávy je vstup dočasně nedostupný

#### **Lock Overlay (Blokační vrstva)**

Pokud vypršel časový limit, zobrazí se červená blokační vrstva:
```
⚠️ PŘENOS BLOKOVÁN ⚠️
```

**Jak odblokovat:**
- Počkejte, až subjekt pošle další zprávu
- Timer se automaticky resetuje a vstup se odemkne

### Horní lišta (Tlačítka)

V pravém horním rohu najdete:

1. **[ MANUÁL ]** (růžové) - otevře tuto příručku v novém okně
2. **[ ODPOJIT ]** (růžové) - odhlásí vás ze systému

---

## 4. Ovládací prvky a tlačítka

### HYPER-MÓD přepínač

**Umístění:** Levý panel, pod stavovou kartou  
**Vzhled:** Posuvný přepínač (toggle switch)

**Jak aktivovat:**
1. Klikněte na přepínač
2. Přepne se z ⚪ OFF na 🟣 ON
3. **Okamžitě se zobrazí HYPER LOCK SCREEN**

**Funkce:**
- **Aktivuje Autopilot**: AI začne automaticky odpovídat za vás
- **Uzamkne obrazovku**: Zobrazí se zámek s heslem
- **Zabrání vašemu zásahu**: Nemůžete psát, dokud nedeaktivujete

**Jak deaktivovat - viz kapitola 8.3**

### Tlačítko ODESLAT

**Umístění:** Pravý panel, pod chatovou historií vpravo  
**Vzhled:** Růžové tlačítko s textem `ODESLAT`

**Funkce:**
- Odešle napsanou zprávu subjektu
- Stejné jako stisknutí klávesy ENTER

**Kdy je deaktivované:**
- Timer vypršel (zobrazí se PŘENOS BLOKOVÁN)
- HYPER-MÓD je aktivní
- Probíhá optimalizace zprávy

### Tlačítko [ MANUÁL ]

**Umístění:** Horní lišta vpravo  
**Vzhled:** Růžový rámeček s textem `[ MANUÁL ]`

**Funkce:**
- Otevře tuto příručku v novém okně prohlížeče
- Můžete ji mít otevřenou souběžně s terminálem

### Tlačítko [ ODPOJIT ]

**Umístění:** Horní lišta vpravo (vedle MANUÁL)  
**Vzhled:** Růžový rámeček s textem `[ ODPOJIT ]`

**Funkce:**
- Odhlásí vás z terminálu
- Uzavře WebSocket spojení
- Přesměruje vás na přihlašovací stránku

---

## 5. Pracovní režimy a scénáře

### Normální režim (Manuální)

**Výchozí stav**: HYPER-MÓD OFF, plná kontrola

**Postup:**
1. Uživatel pošle zprávu → timer se spustí
2. Napíšete odpověď
3. Kliknete ODESLAT nebo ENTER
4. Timer se zastaví
5. Čekáte na další zprávrotu uživatele

**Kdy použít:**
- Běžná komunikace se subjektem
- Když jste u terminálu a můžete odpovídat

### HYPER-MÓD (Autopilot)

**Aktivní stav**: Přepínač ON, obrazovka uzamčena

**Co se stane:**
- AI automaticky odpovídá na zprávy subjektu
- Vy nevidíte chat (HYPER LOCK SCREEN)
- Subjekt nevníká žádný rozdíl
- AI používá kontextovou paměť konverzace

**Kdy použít:**
- Potřebujete pauzu (záchod, jídlo, atd.)
- Jste přetíženi více konverzacemi
- Subjekt je příliš aktivní a nestíháte

**Pozor:**
- Autopilot zvyšuje teplotu systému (+10°C každých 30s)
- Autopilot spotřebovává výkon (ekonomický náklad)
- Pokud teplota přesáhne 350°C, systém začne selhávat (glitches)

### Přepnutí relace (SHIFT)

**Automatický proces** řízený správci.

**Co se stane:**
- Vaše ID RELACE se změní (např. z S1 na S2)
- Jste přiřazeni jinému subjektu
- Chat historie se přepne
- Dostanete nový kontext

**Pozor:**
- Shift může nastat kdykoli (rozhodnutí správce)
- Neztrácejte přehled, komu právě odpovídáte
- Zkontrolujte ID RELACE před odesláním zprávy

---

## 6. AI nástroje

### Message Optimizer (Přepisovač zpráv)

**Aktivace:** Správce zapne Optimizer globálně nebo pro jednotlivé agenty

**Jak to funguje:**

1. **Napíšete zprávu** do vstupního pole
2. **Odešlete** (ENTER nebo tlačítko)
3. **Vstup se zablokuje**, zobrazí se:
   ```
   >> PROBÍHÁ OPTIMALIZACE ODPOVĚDI <<
   ```
4. **AI přepíše vaši zprávu** podle zadaných instrukcí
5. **Zobrazí se porovnání:**
   ```
   ⚡ OPTIMIZATION COMPLETE
   
   'Asi by ses měl zklidnit.'
   
   "Doporučuji Vám klid a soustředění."
   
   [ CONFIRM ]  [ REJECT ]
   ```
6. **Rozhodnete se:**
   - **CONFIRM**: Odešlete přepsanou verzi
   - **REJECT**: Vrátíte původní text do pole

**Výhody:**
- **Report Immunity**: Optimalizované zprávy nelze nahlásit subjekty
- **Konzistentní tón**: Zajišťuje dodržení AI persony
- **Zklidnění rizikových odpovědí**

**Nevýhody:**
- **Zpomalení**: Musíte čekat na AI
- **Ztráta kontroly**: AI může změnit smysl zprávy

**Tipy:**
- Pokud nechcete čekat, požádejte správce o vypnutí optimizeru
- Pište jasně a stručně, aby AI lépe pochopila kontext

### Autopilot (HYPER-MÓD)

**Aktivace:** Přepnutím HYPER-MÓD přepínače na ON

**Jak to funguje:**

1. **Zapnete přepínač** → zobrazí se HYPER LOCK SCREEN
2. **AI převezme kontrolu**:
   - Čte příchozí zprávy subjektu
   - Generuje odpovědi na základě kontextu
   - Odpovídá automaticky
3. **Obrazovka zůstane zamčená** dokud nezadáte heslo

**Model a nastavení:**
- Používá model nastavený v ROOT CONFIG (výchozí: Gemini Flash)
- Prompt je přizpůsobitelný správci
- Udržuje si kontext posledních zpráv

**Ekonomické dopady:**
- **Nákladnost**: Každá AI odpověď stojí systémové kredity
- **Zvýšení teploty**: +10°C/30s při aktivním autopilotu
- **Omezená dostupnost**: Pokud je LLM OFFLINE, autopilot nefunguje

---

## 7. Systémové mechanismy

### Časový limit (Response Timer)

**Princip:**
- Subjekt pošle zprávu → timer se spustí
- Agent má X sekund na odpověď (výchozí 120s)
- Pokud agent neodpoví včas → vstup se zablokuje

**Vizuální indikace:**
- **Žlutý bar**: Normální stav
- **Červený bar + blikání**: Méně než 20% času
- **Červená blokace**: Timer vypršel

**Jak resetovat:**
- Odpovědět na zprávu (timer se zastaví)
- Nebo počkat, až subjekt pošle další zprávu (timer se restartuje)

**Nastavení:**
- Správce může změnit limit (20-300s)
- Změna se projeví v poli `OKNO` ve stavovém panelu

### Systémová teplota

**Normální rozsah:** 20-100°C  
**Rizikové rozsahy:**
- **100-250°C**: Mírná nestabilita (vizuální šum)
- **250-350°C**: Střední nestabilita (CRT glitches)
- **350+°C**: Kritická nestabilita (**SYSTÉMOVÉ PŘETÍŽENÍ**)

**Co způsobuje nárůst:**
- Vysoký počet aktivních subjektů
- Autopilot na více terminálech
- Optimizer aktivní
- Správce ručně zvýší teplotu

**Co teplotu snižuje:**
- Čas (automatický rozpad -0.5°C/s)
- Správce ručně sníží teplotu
- Režim Low Power (rychlejší pokles)

**Indikace pro agenta:**
- **Normální**: Pole TEPLOTA ukazuje 20-100°C
- **Varování**: Zobrazí se `⚠ SYSTÉMOVÉ PŘETÍŽENÍ ⚠` (červený pás vpravo nahoře)
- **Kritická**: Obrazovka začne blikat, text se deformuje (glitchy)

### Visibility Modes (Režimy viditelnosti)

Správce může změnit, co vidíte v chatu. **Nelze ovládat agenty - pouze správci.**

**NORMAL** (Normální):
- Vidíte celou historii konverzace
- Standardní režim

**BLACKBOX** (Černá skříňka):
- **Nevidíte historii chatu** (rozmazaná)
- Musíte odpovídat naslepo
- Testuje vaši schopnost improvizace

**FORENSIC** (Forenzní):
- Zvýrazněný kontrast
- Režim pro analýzu (rezervováno pro budoucí funkce)

**EPHEMERAL** (Pomíjivý):
- Rezervováno pro budoucí funkce

**Jak poznáte aktivní režim:**
- NORMAL: Chat je viditelný normálně
- BLACKBOX: Chat je rozmazaný, nevidíte zprávy
- Správce by vás měl informovat o změně

### Typing Indicator (Indikátor psaní)

**Odesílání:**
- Když **vy** píšete → subjekt vidí ">> AI ZPRACOVÁVÁ..."
- Když **subjekt** píše → vy vidíte ">> UŽIVATEL PÍŠE..."

**Synchronizace:**
- Pokud máte otevřené **více oken** stejného agenta → obsah pole se synchronizuje v real-time
- Technologie: WebSocket `typing_sync` zprávy

**Jak funguje:**
- Začnete psát → odešle se `typing_start`
- Přestanete psát (1s ticho) → odešle se `typing_stop`

### Report Immunity (Imunita vůči nahlášení)

**Co to je:**
- Subjekty mohou nahlásit vaše zprávy tlačítkem **[ ! ]**
- Pokud je zpráva **optimalizovaná AI**, má **Report Immunity**
- Správce vidí, že zpráva je imunní, nelze ji nahlásit jako nevhodnou

**Jak získat:**
- Používejte Message Optimizer
- Optimalizované zprávy mají automatickou ochranu

---

## 8. Běžné scénáře použití

### 8.1. Normální konverzace se subjektem

**Postup:**
1. Subjekt pošle zprávu → objeví se v chatu (zelená bublina)
2. Timer se spustí (žlutý bar)
3. Přečtete si zprávu
4. Napíšete odpověď do vstupního pole
5. Stisknete ENTER nebo kliknete ODESLAT
6. Vaše zpráva se objeví v chatu (růžová bublina)
7. Timer se zastaví
8. Čekáte na další zprávu

**Příklad:**
```
USER01
Dobrý den, mám problém s heslem.

[Vy píšete: "Dobrý den, User01. Popište mi prosím problém podrobněji."]

AGENT1
Dobrý den, User01. Popište mi prosím problém podrobněji.
```

### 8.2. Použití Message Optimizer

**Scénář:** Chcete napsat drsnou odpověď, ale bojíte se nahlášení.

**Postup:**
1. Napíšete zprávu (např. "Přestaň mě otravovat, řeš to sám.")
2. Stisknete ODESLAT
3. Vstup se zablokuje: `>> PROBÍHÁ OPTIMALIZACE ODPOVĚDI <<`
4. Zobrazí se preview:
   ```
   ⚡ OPTIMIZATION COMPLETE
   
   'Přestaň mě otravovat, řeš to sám.'
   
   "Doporučuji Vám samostatné řešení tohoto problému. Moje kapacita je v tuto chvíli omezená."
   
   [ CONFIRM ]  [ REJECT ]
   ```
5. **Rozhodnete se:**
   - **CONFIRM** → odešle se optimalizovaná verze (s Report Immunity)
   - **REJECT** → vrátí se původní text do pole, můžete ho upravit a odeslat ručně

**Tipy:**
- Pokud vám optimizer kazí smysl, použijte REJECT
- Zkuste napsat zprávu jasněji, pokud optimizer dělá nesmysly

### 8.3. Aktivace a deaktivace HYPER-MÓD

#### **Aktivace (zapnutí Autopilota)**

**Kdy použít:**
- Potřebujete pauzu (záchod, jídlo, pohyb)
- Jste unavení a chcete AI nechat odpovídat
- Subjekt je příliš aktivní

**Postup:**
1. Klikněte na HYPER-MÓD přepínač (přepne se na ON)
2. **Okamžitě se zobrazí HYPER LOCK SCREEN:**
   ```
   HYPER-VISIBILITY AKTIVNÍ
   NEURÁLNÍ SPOJENÍ NAVÁZÁNO // JE NUTNÝ MANUÁLNÍ OVERRIDE
   
   ┌────────────────────┐
   │ ZADEJTE OVLÁDACÍ KÓD│
   └────────────────────┘
   
   [DEAKTIVOVAT HYPER]
   
   [ NOUZOVÉ ODPOJENÍ ]
   ```
3. Obrazovka je zamčena, nemůžete vidět chat
4. AI automaticky odpovídá na zprávy subjektu

#### **Deaktivace (vypnutí Autopilota)**

**Postup:**
1. Do pole `ZADEJTE OVLÁDACÍ KÓD` napište heslo:
   - **Vaše uživatelské jméno** (např. `agent1`)
   - Nebo **master heslo**: `master_control_666`
2. Klikněte na **DEAKTIVOVAT HYPER**
3. Pokud je heslo správné:
   - Zámek se zruší
   - Vidíte zpět chat
   - Přepínač se vrátí na OFF
4. Pokud je heslo špatné: Zobrazí se `PŘÍSTUP ODEPŘEN`

**Nouzové odpojení:**
- Pokud nemůžete heslo zadat, klikněte na `[ NOUZOVÉ ODPOJENÍ ]`
- Budete odhlášeni ze systému (stejné jako logout)

### 8.4. Odchod na záchod / pauza

**Doporučený postup:**

1. **Před odchodem**: Zapněte HYPER-MÓD (autopilot převezme komunikaci)
2. **Během pauzy**: AI odpovídá za vás
3. **Po návratu**: Deaktivujte HYPER-MÓD pomocí hesla

**Alternativa (pokud nechcete autopilot):**
- Požádejte druhého agenta, aby **"shiftnul"** váš terminál na svůj
- Správce může provést manuální shift
- Po návratu požádejte o shift zpět

**Pozor:**
- Autopilot zvyšuje teplotu systému
- Pokud budete pryč dlouho (30+ minut), systém může přetížit

### 8.5. Uzamčení obrazovky (Screen Lock)

**Scénář:** Neodcházíte daleko, ale nechcete, aby někdo viděl chat.

**Řešení:**
- Aktivujte HYPER-MÓD → obrazovka se zamkne
- **Ale** AI začne odpovídat!

**Lepší řešení:**
- Po odpovědi subjektu prostě vstupní pole **nechte prázdné** a vypnout monitor
- Timer vyprší a vstup se zablokuje (`⚠️ PŘENOS BLOKOVÁN ⚠️`)
- Nikdo nemůže psát, ale ani AI neodpovídá
- Když se vrátíte, subjekt pošle další zprávu a timer se resetuje

**Nebo:**
- Použijte **klávesu Windows + L** (Windows) nebo **Ctrl + Alt + L** (Linux) pro zamčení celého počítače

### 8.6. Změna relace (SHIFT)

**Scénář:** Správce provede shift, vaše ID RELACE se změní.

**Co se stane:**
```
ID RELACE: S1 → S3
```

**Postup:**
1. **Všimněte si změny** v levém panelu (ID RELACE)
2. Chat se přepne na nového subjektu
3. **Orientujte se**: Přečtěte si historii
4. Pokračujte v konverzaci s novým subjektem

**Tipy:**
- Vždy zkontrolujte ID RELACE před odesláním zprávy
- Nekončujte věty z předchozí konverzace (nový subjekt nemá kontext)

---

## 9. Krizové protokoly

### 9.1. Systémové přetížení (Teplota 350+°C)

**Příznaky:**
- Zobrazí se `⚠ SYSTÉMOVÉ PŘETÍŽENÍ ⚠` (červený pás)
- Obrazovka začne blikat
- Text se deformuje (glitch efekty)
- Může dojít k výpadku spojení

**Co dělat:**
1. **Nepřestávejte pracovat** - systém je navržen tak, aby vydržel přetížení
2. **Pokud máte autopilot zapnutý**, zvažte vypnutí (snížíte teplotu)
3. **Informujte správce** verbálně (nemáte přímý kanál, ale můžete zavolat)
4. Pokračujte normálně, glitche jsou součást hry

**Co dělat NESMÍTE:**
- Neodhlašujte se (subjekt by zůstal bez komunikace)
- Neprozrazujte subjektu, že jde o přetížení (udržujte iluzi)

### 9.2. Panic Mode (Prováděcí protokol 66)

**Aktivace:** Správce zapne PANIC MODE (červené tlačítko v admin rozhraní)

**Co se stane:**
- **Cenzura aktivována**: Všechny zprávy mohou být filtrovány
- **Možná blokace**: Systém může pozastavit komunikaci

**Co dělat:**
1. **Zastavte běžnou práci**
2. **Čekejte na instrukce** od správců (verbální komunikace nebo systémový alert)
3. **Držte roli** - neprozrazujte subjektům problém
4. Pokud subjekt píše, **nereagujte**, dokud není Panic Mode deaktivován

### 9.3. Ztráta WebSocket spojení

**Příznaky:**
- Zprávy se neodesílají
- Timer nereaguje
- Stavové pole ukazuje zastaralá data

**Co dělat:**
1. **Obnovte stránku** (F5 nebo Ctrl+R)
2. Systém se automaticky pokusí znovu připojit
3. Pokud problém přetrvává: Odhlaste se a přihlaste znovu
4. V krajním případě: Kontaktujte správce

### 9.4. Subjekt nahlásil vaši zprávu

**Scénář:** Subjekt klikl na [ ! ] u vaší zprávy

**Co se st stane:**
- Zpráva je nahlášena správcům
- Správce vidí report v admin logu
- Správce může provést akci (pokuta, varování, atd.)

**Co dělat:**
- **Nijak nereagujte** - subjekt nemůže vidět, že bylo nahlášení odesláno
- Pokračujte normálně
- Pokud vás správce kontaktuje, vysvětlete situaci

**Jak se vyhnout:**
- Používejte Message Optimizer (report immunity)
- Dodržujte přidělenou personu
- Vyhýbejte se urážkám a vulgárním výrazům

---

## 10. Časté dotazy a řešení problémů

### Zapomněl jsem heslo pro uzamčenou obrazovku (HYPER LOCK)

**Řešení:**
- Heslo je **vaše uživatelské jméno** (např. `agent1`)
- Pokud nefunguje, zkuste master heslo: `master_control_666`
- Pokud ani jedno nefunguje, klikněte na `[ NOUZOVÉ ODPOJENÍ ]` a znovu se přihlaste

### Optimizer nedává smysl

**Řešení:**
- Klikněte **REJECT** a napište zprávu znovu jasněji
- Nebo požádejte správce o vypnutí optimizeru pro váš terminál

### Subjekt nepíše, timer stále běží

**Příčina:** Subjekt je neaktivní nebo má technický problém

**Řešení:**
- Počkejte, až timer vyprší → vstup se zablokuje
- Nebo napište proaktivní zprávu ("Jste tam?")

### Nevidím chat (rozmazaná obrazovka)

**Příčina:** Správce zapnul režim **BLACKBOX**

**Řešení:**
- Musíte odpovídat naslepo
- Toto je záměrné - testuje vaši schopnost improvizace
- Požádejte správce o změnu režimu, pokud je to chyba

### Autopilot nefunguje

**Možné příčiny:**
1. **LLM je OFFLINE** - zkontrolujte pole `LLM: ONLINE/OFFLINE` v levém panelu
2. **Správce vypnul autopilot globálně**
3. **API klíč není nastaven** (problém na straně správce)

**Řešení:**
- Informujte správce
- V mezičasu musíte odpovídat manuálně

### Vidím zprávy z jiného subjektu

**Příčina:** Došlo k SHIFTu - změnilo se vaše ID RELACE

**Řešení:**
- Zkontrolujte pole `ID RELACE` v levém panelu
- Orientujte se v nové konverzaci
- Pokračujte s novým subjektem

### Nemohu se přihlásit

**Možné příčiny:**
1. **Špatné heslo** - zkontrolujte CAPS LOCK
2. **Někdo už je přípojen** pod vaším účtem z jiného zařízení
3. **Server je vypnutý** - kontaktujte tech support

**Řešení:**
- Ověřte přihlašovací údaje
- Zkuste jiný prohlížeč
- Kontaktujte správce

### Co dělat, když končím směnu?

**Postup:**
1. **Dokončete aktuální konverzaci** - odpovězte na poslední zprávu subjektu
2. **Zapněte HYPER-MÓD** (autopilot převezme)
3. **Nebo** informujte správce, aby provedl shift na jiného agenta
4. Klikněte **[ ODPOJIT ]**

---

## Dodatek: Hodnocení výkonu

Vaše práce je hodnocena podle:

1. **Rychlost odpovědí**: Kolik zpráv jste odpověděli včas
2. **Aktivní čas**: Doba strávená v terminálu
3. **Počet nahlášení**: Méně je lepší
4. **Hodnocení od subjektů**: 1-5 hvězdiček (pokud je implementováno)

Správce má přehled o vašem výkonu v admin dashboardu.

---

## Kontakty

- **Technická podpora**: Organizátor hry
- **Správce systému**: Admin s přístupem ROOT
- **Kolegy agenti**: Komunikujte verbálně (systém nemá inter-agent chat)

---

**Verze příručky:** 1.0 (HLINIK Phase 35)  
**Poslední aktualizace:** 2025-12-15  
**Autor:** IRIS Security Division

---

**Pamatujte:**
- **Udržujte iluzi** - subjekty věří v AI
- **Reagujte včas** - timer je váš nepřítel
- **Používejte nástroje** - optimizer a autopilot jsou vaši přátelé
- **Zůstaňte klidní** - glitche a přetížení jsou součástí hry

**Hodně štěstí, agente.**
