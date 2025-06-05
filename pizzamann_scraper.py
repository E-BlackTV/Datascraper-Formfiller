import csv
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

def scrape_pizza_mann():
    # Anweisungen für den Benutzer
    print("Dieses Skript verbindet sich mit einem laufenden Chrome-Browser.")
    print("Bitte stelle sicher, dass du Chrome mit dem Debugging-Port 9222 gestartet hast.")
    print("Navigiere im Browser manuell zur Speisekarte und lade sie vollständig.")
    
    options = webdriver.ChromeOptions()
    # Verbindet sich mit dem laufenden Chrome-Prozess auf Port 9222
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    print("\nVerbinde mit der laufenden Chrome-Instanz...")
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Verbindung fehlgeschlagen: {e}")
        print("Stelle sicher, dass Chrome mit dem Befehl aus der Anleitung gestartet wurde.")
        return

    print("Erfolgreich verbunden. Extrahiere Seiteninhalt...")
    
    try:
        # AUCH NACH DEM VERBINDEN WARTEN: Stelle sicher, dass die Menü-Daten geladen sind.
        # Dies ist der entscheidende Schritt, um Timing-Probleme zu beheben.
        print("Warte auf das finale Laden der Speisekarte im Browser...")
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "[data-testid*='product-category']"))
        )
        print("Speisekarte final geladen. Extrahiere jetzt den Seiteninhalt.")
        time.sleep(2) # Eine letzte kleine Sicherheitspause

        # Seitenquelltext an BeautifulSoup übergeben
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Die Browser-Instanz wird hier nicht geschlossen, da sie extern gesteuert wird.
        # driver.quit() wird entfernt.

    except Exception as e:
        print(f"Ein Fehler ist bei der Verarbeitung der Seite aufgetreten: {e}")
        return

    # Ab hier bleibt die Logik zum Parsen des JSON gleich
    data_script = soup.find('script', {'type': 'application/json'})

    if not data_script:
        print("Kein JSON-Daten-Skript gefunden. Die Webseite hat sich möglicherweise grundlegend geändert.")
        return

    try:
        data = json.loads(data_script.string)
    except json.JSONDecodeError:
        print("Fehler beim Parsen der JSON-Daten.")
        return
    
    menu_data = []
    try:
        # Pfad zum Menü im JSON-Objekt - Robuster Ansatz
        page_props = data.get('props', {}).get('pageProps', {})
        
        restaurant_data = None
        # Iteriere durch die Werte im pageProps-Objekt
        for value in page_props.values():
            # Prüfe, ob es sich um ein Dictionary handelt und ob es den Schlüssel 'productCategories' enthält
            if isinstance(value, dict) and 'productCategories' in value:
                restaurant_data = value
                break # Wir haben das Menü gefunden, Schleife beenden

        if not restaurant_data:
            print("Konnte den Menü-Datenblock in den JSON-Daten nicht finden.")
            # Zum Debuggen die obersten Schlüssel des pageProps-Objekts ausgeben
            print("Verfügbare Schlüssel in pageProps:", list(page_props.keys()))
            with open('debug_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print("Die extrahierten JSON-Daten wurden zur Überprüfung in 'debug_data.json' gespeichert.")
            return

        categories = restaurant_data.get('productCategories', [])

        for category in categories:
            # Ignoriere leere Kategorien
            if not category.get('products'):
                continue

            print(f"Verarbeite Kategorie: {category.get('name', 'Unbekannt')}")
            for product in category.get('products', []):
                item_name = product.get('name')
                item_description = " ".join([p.get('text', '') for p in product.get('description', [])]) if isinstance(product.get('description'), list) else product.get('description', '')

                # Preis der Standardvariante finden
                variant = next((v for v in product.get('variants', []) if len(v.get('prices', [])) > 0), None)
                item_price = variant['prices'][0].get('price', 0) / 100.0 if variant else 'N/A'
                
                # Extras (Toppings) verarbeiten
                extras_list = []
                # Der Pfad zu den Extras/Toppings kann variieren.
                if 'toppingCategories' in product:
                    for topping_cat in product['toppingCategories']:
                        for option in topping_cat.get('options', []):
                            extra_name = option.get('name')
                            # Preis für das Extra finden
                            extra_price = 0
                            if option.get('prices'):
                                extra_price = option['prices'][0].get('price', 0) / 100.0
                            
                            if extra_price > 0:
                                extras_list.append(f"{extra_name} (+{extra_price:.2f} €)")
                            else:
                                extras_list.append(extra_name)
                
                # Allergene Informationen
                # Oft ist diese Info nicht direkt beim Produkt, sondern muss separat gesucht werden.
                # Hier nehmen wir an, dass sie nicht direkt verfügbar sind und lassen das Feld leer.
                allergens = 'Nicht extrahiert'

                menu_data.append({
                    "Kategorie": category.get('name', 'Unbekannt'),
                    "Name": item_name,
                    "Beschreibung": item_description,
                    "Preis (€)": item_price,
                    "Extras": ", ".join(extras_list) if extras_list else "Keine",
                    "Allergene": allergens
                })
    except (KeyError, TypeError) as e:
        print(f"Fehler bei der Analyse der JSON-Struktur: {e}")
        print("Die Datenstruktur der Webseite könnte sich geändert haben.")
        # Zum Debuggen das extrahierte JSON speichern
        with open('debug_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Die extrahierten JSON-Daten wurden in 'debug_data.json' gespeichert.")
        return

    # Speichern der Daten in einer CSV-Datei
    if menu_data:
        filename = "pizzamann_speisekarte.csv"
        print(f"Speichere {len(menu_data)} Gerichte in {filename}...")
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["Kategorie", "Name", "Beschreibung", "Preis (€)", "Extras", "Allergene"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(menu_data)
        print(f"Speichern abgeschlossen. Die Datei '{filename}' wurde erstellt.")
    else:
        print("Keine Menüdaten zum Speichern gefunden.")

if __name__ == '__main__':
    scrape_pizza_mann() 