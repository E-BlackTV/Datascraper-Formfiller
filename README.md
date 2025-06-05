# Restaurant Menu Scraper and Uploader

Dieses Projekt besteht aus zwei Python-Skripten:

1.  `example_scraper.py`: Extrahiert Speisekartendaten (Kategorien, Gerichte, Preise, Beschreibungen, Allergene) von einer Beispiel-Restaurant-Webseite und speichert sie in einer CSV-Datei (`example_menu_data.csv`).
2.  `example_uploader.py`: Liest die Daten aus der `example_menu_data.csv` und lädt sie automatisiert in ein Admin-Panel zur Speisekarteneingabe hoch.

## 1. `example_scraper.py` - Datenextraktion

Dieses Skript verwendet Selenium, um Daten von einer Webseite zu extrahieren.

### Voraussetzungen

- Python 3.x
- pip (Python Package Installer)
- Google Chrome Browser
- ChromeDriver (muss mit der installierten Chrome-Version kompatibel sein)

### Installation

1.  **Selenium installieren:**

    ```bash
    pip3 install selenium
    ```

2.  **ChromeDriver installieren:**
    - **macOS (mit Homebrew):**
      ```bash
      brew install chromedriver
      ```
    - **Andere Betriebssysteme:** Lade den passenden ChromeDriver von [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads) herunter und stelle sicher, dass er sich im System-PATH befindet oder gib den Pfad im Skript an.

### Konfiguration und Anpassung

1.  **Ziel-URL ändern:**
    Öffne `example_scraper.py` und ändere die Variable `url` (Zeile 19) zur URL der Restaurant-Webseite, von der du Daten extrahieren möchtest:

    ```python
    url = "https://www.deine-restaurant-webseite.com/speisekarte"
    ```

2.  **Selektoren (XPATHs) anpassen:**
    Die Webseitenstruktur jeder Restaurantseite ist anders. Daher musst du wahrscheinlich die XPATH-Selektoren im Skript anpassen, um die richtigen Elemente zu finden. Verwende die Entwicklertools deines Browsers (Rechtsklick -> Untersuchen), um die HTML-Struktur zu analysieren und die passenden XPATHs zu finden für:

    - **Cookie-Banner-Button** (Zeile 26-29): Oft notwendig, um mit der Seite interagieren zu können.
    - **Kategorie-Container** (Zeile 41): Das Element, das jede Speisekategorie umschließt.
    - **Kategoriename** (Zeile 52): Das Element innerhalb eines Kategorie-Containers, das den Namen der Kategorie enthält (oft ein `<h2>` oder ähnliches).
    - **Produkt-Container** (Zeile 59): Das Element, das alle Gerichte einer Kategorie umschließt.
    - **Gerichte-Elemente** (Zeile 65): Die einzelnen Elemente für jedes Gericht.
    - **Gerichtsname** (Zeile 72): `producttitle`
    - **Gerichtsbeschreibung** (Zeile 77): `productdesc`
    - **Gerichtspreis** (Zeile 85): `productprice`
    - **Allergene** (Zeile 90): `allergene`

    Passe die `By.XPATH` Werte entsprechend an. Beispiel:

    ```python
    category_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'menu-category')]")
    # ... und so weiter für andere Selektoren
    ```

3.  **Wartezeiten (Optional):**
    Abhängig von der Ladegeschwindigkeit der Webseite müssen eventuell `time.sleep()` Werte angepasst werden, um sicherzustellen, dass Inhalte geladen sind, bevor das Skript versucht, darauf zuzugreifen.

### Ausführung

Führe das Skript über dein Terminal aus:

```bash
python3 example_scraper.py
```

Das Skript gibt den Fortschritt im Terminal aus und erstellt am Ende die Datei `example_menu_data.csv` im selben Verzeichnis.

### Output

- `example_menu_data.csv`: Eine CSV-Datei mit den Spalten: `Kategorie`, `Name`, `Beschreibung`, `Preis`, `Allergene`.

## 2. `example_uploader.py` - Datenhochladen ins Admin-Panel

Dieses Skript verwendet Selenium, um sich mit einer bestehenden Chrome-Browsersitzung zu verbinden und die in `example_menu_data.csv` gespeicherten Gerichte automatisiert in ein Web-Formular (z.B. ein Admin-Panel für Restaurants) einzutragen.

### Voraussetzungen

- Python 3.x
- pip (Python Package Installer)
- Google Chrome Browser
- ChromeDriver (muss mit der installierten Chrome-Version kompatibel sein und für Selenium erreichbar sein)
- Die Datei `example_menu_data.csv` (generiert durch `example_scraper.py` oder manuell erstellt mit passender Struktur).

### Setup

1.  **Chrome im Debugging-Modus starten:**
    Damit Selenium eine bestehende Browsersitzung steuern kann, muss Chrome mit einem offenen Debugging-Port gestartet werden. Schließe alle laufenden Chrome-Instanzen und starte Chrome über das Terminal:

    - **macOS:**
      ```bash
      "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
      ```
    - **Windows:**
      ```bash
      "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
      # (Passe den Pfad ggf. an deine Chrome-Installation an)
      ```
    - **Linux:**
      `bash
google-chrome --remote-debugging-port=9222
`
      Ein neues Chrome-Fenster öffnet sich. **Lasse dieses Terminalfenster und den Chrome-Browser während der Ausführung des Skripts geöffnet.**

2.  **Manuelle Vorbereitung im Browser:**
    - Logge dich in diesem Chrome-Fenster manuell in dein Admin-Panel ein.
    - Navigiere zu der Seite, auf der du neue Gerichte hinzufügen kannst.
    - **WICHTIG:** Wähle die Speise-Kategorie aus, für die du Gerichte hochladen möchtest. Das Skript wird dich nach dem Namen dieser Kategorie fragen, um die entsprechenden Gerichte aus der CSV zu filtern.

### Konfiguration und Anpassung

1.  **CSV-Dateipfad (falls nötig):**
    Die Variable `CSV_FILE_PATH` in `example_uploader.py` ist standardmäßig auf `example_menu_data.csv` gesetzt. Ändere dies, falls deine CSV-Datei anders heißt oder woanders liegt.

2.  **Selektoren für das Admin-Panel (SEHR WICHTIG):**
    Dies ist der kritischste Teil der Anpassung. Du musst die CSS-Selektoren oder XPATHs für die Formularfelder und Buttons in deinem Admin-Panel genau identifizieren und im Skript eintragen. Verwende die Entwicklertools deines Browsers (Rechtsklick -> Untersuchen).
    Ändere die folgenden Variablen am Anfang von `example_uploader.py`:

    - `ADD_NEW_DISH_BUTTON_SELECTOR`: Selektor für den Button "Neues Gericht hinzufügen" (oder ähnlich). **Achtung: Der aktuelle Beispiel-Selektor `(By.ID, "1")` ist sehr generisch und muss wahrscheinlich angepasst werden!**
    - `DISH_NAME_INPUT_SELECTOR`: Selektor für das Eingabefeld des Gerichtsnamens.
    - `DISH_PRICE_INPUT_SELECTOR`: Selektor für das Eingabefeld des Preises.
    - `DISH_DESCRIPTION_INPUT_SELECTOR`: Selektor für das Eingabefeld der Beschreibung.
    - `DISH_TAX_INPUT_SELECTOR`: Selektor für das Eingabefeld des Steuersatzes.
    - `DISH_ALLERGENS_INPUT_SELECTOR`: Selektor für das Eingabefeld der Allergene.
    - `SAVE_DISH_BUTTON_SELECTOR`: Selektor für den Speicher-Button des Formulars.

    **Beispiel für spezifischere Selektoren (oft IDs oder eindeutige Klassen/Attribute):**

    ```python
    ADD_NEW_DISH_BUTTON_SELECTOR = (By.XPATH, "//button[contains(text(), 'Neues Gericht erstellen')]")
    DISH_NAME_INPUT_SELECTOR = (By.ID, "dishNameField")
    # ... usw.
    ```

    **Tipp:** IDs sind meist die zuverlässigsten Selektoren. Wenn es keine IDs gibt, verwende spezifische Klassen-Kombinationen oder XPATHs.

3.  **Anpassung der Wartezeiten (Geschwindigkeit):**
    Am Anfang des Skripts findest du Variablen für Wartezeiten:

    - `SHORT_WAIT` (Standard: 0.5 Sekunden): Kurze Pause nach dem Ausfüllen einzelner Felder.
    - `MEDIUM_WAIT` (Standard: 3 Sekunden): Längere Pause am Anfang und nach Fehlern.
    - `LONG_WAIT` (Standard: 3 Sekunden): Pause nach dem Klick auf "Speichern", um der Seite Zeit zu geben, zu reagieren (z.B. ein Modal zu schließen oder die Liste zu aktualisieren).
    - `WebDriverWait(driver, 10)`: Der generelle Timeout für explizite Waits (z.B. Warten auf Klickbarkeit eines Elements). Erhöhe diesen Wert (z.B. auf `20`), wenn deine Admin-Seite langsam lädt.

    Reduziere die `SHORT_WAIT` und `LONG_WAIT` Zeiten, um das Skript zu beschleunigen, aber sei vorsichtig: Zu kurze Wartezeiten können zu Fehlern führen, wenn die Seite noch nicht bereit für die nächste Aktion ist. Erhöhe sie, wenn das Skript zu schnell für die Webseite ist.

### Ausführung

1.  Stelle sicher, dass Chrome im Debugging-Modus läuft und du im Admin-Panel auf der richtigen Seite/Kategorie bist.
2.  Führe das Skript über dein Terminal aus:
    ```bash
    python3 example_uploader.py
    ```
3.  Das Skript fragt dich nach dem **genauen Namen der Kategorie**, die du im Browser geöffnet hast (Groß-/Kleinschreibung wie in der CSV-Datei). Gib den Namen ein und drücke Enter.
4.  Das Skript beginnt dann, die Gerichte für diese Kategorie nacheinander einzutragen.

### Wichtige Hinweise & Fehlerbehebung

- **`ElementClickInterceptedException`**: Dieser Fehler tritt häufig auf, wenn ein anderes Element (z.B. ein Popup, ein Overlay oder ein sich langsam schließendes Modal nach dem Speichern) den Klick auf den Ziel-Button blockiert.
  - **Lösung**: Erhöhe `LONG_WAIT` nach dem Speichern. Überprüfe, ob es Modals gibt, die explizit geschlossen werden müssen (ggf. durch einen weiteren Klick oder das Senden der `ESC`-Taste – die `Keys`-Klasse ist im Skript auskommentiert, kann aber importiert und verwendet werden). Manchmal hilft auch ein JavaScript-Klick, der im Skript als Fallback implementiert ist.
- **Falsche Selektoren**: Wenn das Skript Elemente nicht findet oder mit den falschen interagiert, sind die Selektoren in `example_uploader.py` nicht korrekt. Überprüfe sie sorgfältig mit den Entwicklertools.
- **Stabilität**: Die Automatisierung von Webseiten-Interaktionen kann fehleranfällig sein, besonders wenn sich die Struktur der Webseite ändert.
- **Verantwortung**: Nutze diese Skripte verantwortungsbewusst und beachte die Nutzungsbedingungen der Webseiten.

## .gitignore

Die `.gitignore`-Datei ist so konfiguriert, dass `*.csv`-Dateien (also auch `example_menu_data.csv` und die ursprüngliche `hanil_speisekarte.csv`) sowie `.DS_Store`-Dateien (macOS) nicht in Git-Repositories aufgenommen werden.
