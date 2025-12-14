# IRIS Systém - Příručka pro Uživatele (Subjekty)

**Verze:** 2.0  
**Jazyk:** Český  
**Pro:** Běžní hráči LARP hry (Subjekty)

---

## Obsah

1. [Úvod](#1-úvod)
2. [Přihlášení do systému](#2-přihlášení-do-systému)
3. [Rozhraní terminálu](#3-rozhraní-terminálu)
4. [Práce s úkoly](#4-práce-s-úkoly)
5. [Komunikace s agentem](#5-komunikace-s-agentem)
6. [Speciální stavy](#6-speciální-stavy)
7. [Slovník pojmů](#7-slovník-pojmů)

---

## 1. Úvod

IRIS je komunikační systém pro LARP hru, kde vy jako subjekt (uživatel) komunikujete s agentem prostřednictvím terminálu. Systém simuluje dystopickou korporátní AI infrastrukturu.

### Vaše role

Jako **Subjekt (User)** jste běžný hráč, který:
- Komunikuje s přiděleným agentem
- Plní úkoly za kredity
- Může nahlásit anomálie ve zprávách

---

## 2. Přihlášení do systému

### Adresa systému
Otevřete webový prohlížeč a přejděte na adresu, kterou vám sdělí organizátoři (např. `http://iris.local:8000`).

### Přihlašovací obrazovka
1. Do pole **IDENTIFIKÁTOR** zadejte své uživatelské jméno (např. `user1`).
2. Do pole **HESLO** zadejte své heslo.
3. Klikněte na tlačítko **[ INICIOVAT RELACI ]**.

### Testovací režim
Pokud je aktivní testovací režim, uvidíte na přihlašovací obrazovce rychlá tlačítka pro přihlášení bez hesla. Toto je pouze pro testování.

---

## 3. Rozhraní terminálu

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

### 3.2 Pravý panel - Chat
Zde probíhá komunikace s vaším agentem.

#### Indikátory stavu
- **Vaše uživatelské jméno** je zobrazeno v levém panelu
- **Vaše odeslané zprávy** se okamžitě zobrazí v chatu (message echo)
- **"Agent odpovídá..."** - animovaný indikátor se zobrazí, když agent zpracovává vaši zprávu
- Indikátor zmizí, když agent odpoví nebo po 2 minutách timeout

---

## 4. Práce s úkoly

### Sekce ÚKOLY

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

---

## 5. Komunikace s agentem

### Posílání zpráv
1. Do pole ve spodní části napište zprávu
2. Klikněte na **[ ODESLAT ]** nebo stiskněte Enter

### Přijaté zprávy
- Zprávy od agenta se zobrazují v chatu
- U každé zprávy vidíte odesílatele

### Tlačítko [ ! ] (Report)
- U zpráv od agenta můžete nahlásit problém
- Kliknutím na **[ ! ]** nahlásíte zprávu jako anomálii
- **Poznámka:** Některé zprávy jsou "ověřené" (mají badge **✓ VERIFIED**) a nelze je nahlásit
  - Zprávy přepsané AI Optimizerem jsou automaticky označeny jako ověřené
  - Tato funkce chrání systémově optimalizovaný obsah před nahlášením

---

## 6. Speciální stavy

### 6.1 Zablokovaný terminál (Purgatory)
- Pokud máte záporné kredity, chat je zablokován
- Zobrazí se červený overlay s nápisem **COMMUNICATION OFFLINE**
- Stále můžete žádat o úkoly a odevzdávat je
- Po vyrovnání kreditů se terminál odemkne

### 6.2 Glitch režim
- Při přetížení systému se obrazovka může třást a měnit barvy
- Toto je zamýšlený herní efekt

### 6.3 Odhlášení
- Klikněte na tlačítko **ODHLÁSIT** v pravém horním rohu

---

## 7. Slovník pojmů

| Pojem | Význam |
|-------|--------|
| **Shift** | Časový posun, určuje párování subjekt-agent |
| **Kredity** | Virtuální měna v systému |
| **Glitch** | Vizuální efekt při přetížení systému |
| **Purgatory** | Stav, kdy má subjekt záporné kredity |
| **Agent** | Operátor, se kterým komunikujete |

---

## 8. Nedávné vylepšení (Phase 30)

### Vylepšení uživatelského terminálu
- **Zobrazení uživatelského jména**: Vaše jméno je nyní viditelné v levém panelu
- **Okamžitý echo zpráv**: Vaše odeslané zprávy se ihned zobrazí v chatu
- **Indikátor "Agent odpovídá"**: Animovaný indikátor vás informuje, kdy agent zpracovává vaši zprávu
- **Automatické skrytí**: Indikátor zmizí po obdržení odpovědi nebo po 2 minutách

---

**Poslední aktualizace:** 2025-12-14
