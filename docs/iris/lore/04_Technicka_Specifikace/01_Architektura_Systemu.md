# TECHNICKÁ ARCHITEKTURA A UX

Technické řešení systému není pouhou kulisou, ale aktivním narativním prvkem. Specifikace systému je interpretována skrze prizma korporátní neschopnosti a improvizace.

## 1. Hardwarová Infrastruktura: Princip ZED
Základním technickým dogmatem je **ZED (Zero External Dependency)** – Nulová Externí Závislost.

* **Technické vysvětlení:** Systém běží lokálně na jednom serveru (laptop v krabici) bez připojení k internetu, aby se předešlo výpadkům a latenci.
* **Narativní vysvětlení (Lore):** "Ochrana integrity kvantových stavů hliníku před dekoherencí z veřejného internetu."
* **Skutečný důvod:** Firma nezaplatila poskytovateli internetu a vedení se bojí, že si Uživatelé na Googlu ověří, že "hliníková paměť" je nesmysl.

## 2. Softwarový Stack: "Spaghetti Code"
Aplikace je postavena tak, aby reflektovala chaotický vývoj.

* **Framework:** Python 3.10+ a FastAPI (protože CEO slyšel, že "Fast" znamená rychle).
* **Databáze:** SQLite (souborová databáze), protože Správce IT neuměl nainstalovat robustní SQL server. Prezentováno jako "decentralizovaná atomická struktura".
* **Komunikace:** WebSockets ("Neuronová vlákna") pro real-time chat.

## 3. UX Design a Glitche
Design musí vypadat tak, jak si lidé v roce 1990 představovali rok 2025 (Retro-Futurismus).

**Barevná paleta a Typografie:**
* **Pozadí:** Černá (#000000).
* **Akcenty:** Neonové barvy – **Cyan (#00FFFF)** a **Magenta (#FF00FF)**.
* **Písmo:** Monospaced (připomínající terminál/konzoli), např. *Courier New* nebo *Roboto Mono*.

**Visual Glitch Engine:**
Systém obsahuje zabudovaný generátor chyb. Když stoupá hodnota *Kritické situace*:
* UI se začne třást (CSS animace).
* Barvy se invertují.
* Text se rozpadá na náhodné znaky.
* *Vysvětlení pro Uživatele:* "Vidíte vizualizaci intenzivního myšlenkového procesu AI."

## 4. Mechanika "Perfect Mirroring" (Dohled)
Systém implementuje funkci **Draft Sync**.
* **Funkce:** Správci a Agenti vidí na svých dashboardech text, který Uživatel teprve píše do vstupního pole (ještě před odesláním).
* **Korporátní newspeak:** "Technologie prediktivní empatie."
* **Účel:** Totální dohled. Správci mohou zasáhnout, pokud se schyluje k nevhodné zprávě.
* 
