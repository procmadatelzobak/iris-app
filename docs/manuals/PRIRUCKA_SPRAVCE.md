# IRIS Systém - Příručka pro Správce (Adminy)

**Verze:** 2.0  
**Jazyk:** Český  
**Pro:** Správci hry (Game Masters)

---

## Obsah

1. [Úvod](#1-úvod)
2. [Přihlášení do systému](#2-přihlášení-do-systému)
3. [Dashboard - Přehled stanic](#3-dashboard---přehled-stanic)
4. [Stanice MONITORING (UMYVADLO)](#4-stanice-monitoring-umyvadlo)
5. [Stanice KONTROLA (ROZKOŠ)](#5-stanice-kontrola-rozkoš)
6. [Stanice EKONOMIKA (BAHNO)](#6-stanice-ekonomika-bahno)
7. [Stanice ÚKOLY (MRKEV)](#7-stanice-úkoly-mrkev)
8. [Horní lišta](#8-horní-lišta)
9. [Slovník pojmů](#9-slovník-pojmů)

---

## 1. Úvod

Jako **Správce (Admin)** ovládáte herní mechaniky, schvalujete úkoly a dohlížíte na průběh hry.

### Vaše role

- Sledujete všechny relace mezi subjekty a agenty
- Ovládáte herní nastavení (shift, power, teplota)
- Spravujete ekonomiku (kredity, pokuty)
- Schvalujete a vyplácíte úkoly

---

## 2. Přihlášení do systému

### Adresa systému
Otevřete webový prohlížeč a přejděte na adresu, kterou vám sdělí organizátoři (např. `http://iris.local:8000`).

### Přihlašovací údaje
- **Uživatel:** `admin1` až `admin4`
- **Heslo:** sdělí vám organizátoři

### Přihlašovací obrazovka

![Přihlašovací obrazovka](login_screen.png)

1. Do pole **IDENTIFIKÁTOR** zadejte své uživatelské jméno.
2. Do pole **HESLO** zadejte své heslo.
3. Klikněte na tlačítko **[ INICIOVAT RELACI ]**.

---

## 3. Dashboard - Přehled stanic

Po přihlášení vidíte **HUB** se 4 stanicemi:

| Stanice | Barva | Funkce |
|---------|-------|--------|
| **UMYVADLO** | Zelená | Monitoring - sledování všech relací |
| **ROZKOŠ** | Žlutá | Kontrola - herní nastavení |
| **BAHNO** | Modrá | Ekonomika - správa kreditů |
| **MRKEV** | Fialová | Úkoly - schvalování a vyplácení |

Kliknutím na stanici se otevře její detail.

---

## 4. Stanice MONITORING (UMYVADLO)

### Záložka VŠEVIDOUCÍ
- Mřížka všech 8 relací
- Vidíte živé chaty mezi subjekty a agenty
- Vpravo je mini-log systémových událostí

### Záložka ŠUM
- Pouze chat karty bez logu

### Záložka HISTORIE OMYLŮ
- Kompletní systémový log
- Tlačítko **VYMAZAT HISTORII** smaže log

### Záložka PAVUČINA
- Grafické zobrazení sítě (experimentální)

### SHIFT display
- V pravém horním rohu vidíte aktuální SHIFT hodnotu

---

## 5. Stanice KONTROLA (ROZKOŠ)

### POSUN REALITY
- Velké číslo ukazuje aktuální shift
- Tlačítko **[ ROZTOČIT KOLA OSUDU ]** zvýší shift o 1

### TLAK PÁRY (Power)
- Modrý pruh ukazuje zatížení vs. kapacitu
- Tlačítko **[ PŘIHODIT UHLÍ ]** přidá 50MW na 30 minut za 1000 CR
- Pokud je boost aktivní, zobrazí se odpočet

### HLADINA STRESU (Teplota)
- Barevný pruh od zelené po červenou
- Manuální posuvník pro ruční nastavení
- Režimy: NORMÁL / ÚSPORA / PŘETÍŽENÍ

### FILTR PRAVDY (Visibility)
- ŽÁDNÝ - Agenti vidí vše normálně
- ČERNÁ SKŘÍŇKA - Agenti nevidí historii
- FOREZKA - Speciální forenzní režim

---

## 6. Stanice EKONOMIKA (BAHNO)

### NÁRODNÍ BANKA BAHNA
- Zobrazuje celkový stav pokladny (Treasury)

### Tabulka uživatelů
- Seznam všech subjektů
- Sloupce: Jméno, Kredity, Status, Locked

### Akce pro každého uživatele
| Tlačítko | Funkce |
|----------|--------|
| **[+]** | Přidat kredity (bonus) |
| **[-]** | Odebrat kredity (pokuta) |
| **[LOCK]** | Zablokovat terminál |
| **[UNLOCK]** | Odblokovat terminál |

---

## 7. Stanice ÚKOLY (MRKEV)

### Seznam úkolů
- Vidíte všechny úkoly od subjektů
- Stavy: Pending (čeká), Active (aktivní), Submitted (odevzdáno)

### Akce pro úkoly
| Tlačítko | Funkce |
|----------|--------|
| **[APPROVE]** | Schválit žádost o úkol |
| **[REJECT]** | Zamítnout žádost |
| **[PAY]** | Vyplatit odměnu za dokončený úkol |

---

## 8. Horní lišta

### PŘEPSAT REALITU
- Zapne editační režim pro přejmenování prvků
- Klikněte na libovolný text a přepište ho
- Klikněte znovu pro uložení

### MODZEK (AI Config)
- Otevře modální okno pro nastavení AI
- API klíče, modely, prompt

### AUTO-DESTRUKCE
- Resetuje herní stav (kredity, úkoly, logy)
- Vyžaduje potvrzení

### ODHLÁSIT
- Odhlásí vás ze systému

---

## 9. Slovník pojmů

| Pojem | Význam |
|-------|--------|
| **Shift** | Časový posun, určuje párování subjekt-agent |
| **Kredity** | Virtuální měna v systému |
| **Treasury** | Společná pokladna správců |
| **Glitch** | Vizuální efekt při přetížení systému |
| **Purgatory** | Stav, kdy má subjekt záporné kredity |
| **Overload** | Přetížení systému (load > capacity) |

---

**Poslední aktualizace:** 2025-12-14
