from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
# from selenium.webdriver.common.keys import Keys # Für das Senden von Tasten wie ESC
import time
import csv
import os
import traceback

# Pfad zur CSV-Datei
CSV_FILE_PATH = 'example_menu_data.csv' 

# --- ANPASSBARE SELEKTOREN FÜR DEIN ADMIN PANEL ---
# BITTE DIESE SELEKTOREN SO SPEZIFISCH WIE MÖGLICH MACHEN!

# Button, um ein neues Gericht zur aktuellen Kategorie hinzuzufügen
# Wenn (By.ID, "1") nicht eindeutig ist, DRINGEND einen spezifischeren Selektor verwenden!
# ADD_NEW_DISH_BUTTON_SELECTOR = (By.ID, "1") # Dein aktueller Wert - Vorsicht!
ADD_NEW_DISH_BUTTON_SELECTOR = (By.ID, "1") # ROBUSTERER VORSCHLAG


# Eingabefeld für den Gerichtsnamen im Formular
DISH_NAME_INPUT_SELECTOR = (By.ID, "menuItemName") # Deine Anpassung

# Eingabefeld für den Preis
DISH_PRICE_INPUT_SELECTOR = (By.ID, "menuItemPrice") # Deine Anpassung

# Eingabefeld für die Beschreibung
DISH_DESCRIPTION_INPUT_SELECTOR = (By.ID, "menuItemDescription") # Deine Anpassung

# Eingabefeld für den Steuersatz
DISH_TAX_INPUT_SELECTOR = (By.ID, "menuItemTax") # Deine Anpassung

# Eingabefeld für Allergene
DISH_ALLERGENS_INPUT_SELECTOR = (By.ID, "menuItemAllergies") # Deine Anpassung

# Speicher-Button im Formular
SAVE_DISH_BUTTON_SELECTOR = (By.XPATH, "//button[contains(@class, 'btn-primary') and normalize-space(text())='Speichern']") # Spezifischer Selektor
# --- ENDE ANPASSBARE SELEKTOREN ---

# Angepasste Wartezeiten
SHORT_WAIT = 0.5  # Reduziert von 1.5s
MEDIUM_WAIT = 3   # Für initiale Wartezeit und als Fallback
LONG_WAIT = 3     # Nach dem Speichern, um Modals Zeit zu geben

def read_dishes_from_csv(file_path):
    """Liest alle Gerichte aus der CSV-Datei."""
    dishes = []
    if not os.path.exists(file_path):
        print(f"FEHLER: CSV-Datei nicht gefunden unter {file_path}")
        return dishes
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            dishes.append(row)
    print(f"{len(dishes)} Gerichte aus {file_path} geladen.")
    return dishes

def filter_dishes_by_category(all_dishes, target_category_name):
    """Filtert Gerichte nach dem angegebenen Kategorienamen."""
    filtered = [dish for dish in all_dishes if dish['Kategorie'].strip().lower() == target_category_name.strip().lower()]
    print(f"{len(filtered)} Gerichte für Kategorie '{target_category_name}' gefunden.")
    return filtered

def main():
    print("Starte den Uploader für das Admin Panel...")
    print("Stelle sicher, dass Chrome mit --remote-debugging-port=9222 gestartet wurde,")
    print("du in deinem Admin Panel eingeloggt und auf der richtigen Menü-Seite bist,")
    print("und die korrekte Kategorie für den Upload bereits ausgewählt ist.\n")

    all_dishes_from_csv = read_dishes_from_csv(CSV_FILE_PATH)
    if not all_dishes_from_csv:
        input("CSV-Datei nicht gefunden oder leer. Drücke ENTER zum Beenden.\n")
        return

    target_category = input("Gib den genauen Namen der Kategorie ein, die du gerade in deinem Admin Panel geöffnet hast (Groß-/Kleinschreibung beachten, wie in der CSV):\n> ")
    if not target_category:
        print("Keine Kategorie eingegeben. Skript wird beendet.")
        input("Drücke ENTER zum Beenden.\n")
        return

    dishes_to_upload = filter_dishes_by_category(all_dishes_from_csv, target_category)
    if not dishes_to_upload:
        print(f"Keine Gerichte für die Kategorie '{target_category}' in der CSV gefunden oder die Kategorie existiert nicht in der CSV.")
        input("Drücke ENTER zum Beenden.\n")
        return

    print(f"Bereite den Upload von {len(dishes_to_upload)} Gerichten für die Kategorie '{target_category}' vor...")
    
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        print("\nVersuche, mit dem Chrome-Browser auf Port 9222 zu verbinden...")
        driver = webdriver.Chrome(options=chrome_options)
        
        wait = WebDriverWait(driver, 10)
        print("Erfolgreich mit dem laufenden Chrome-Browser verbunden.")

    except Exception as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"FEHLER BEI DER VERBINDUNG ZUM BROWSER oder bei der WebDriver-Initialisierung:")
        print(str(e))
        print("Traceback (weitere Details):")
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Bitte stelle sicher, dass Chrome MANUELL mit dem korrekten Remote Debugging Port gestartet wurde.")
        print("Beispiel für macOS: \"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome\" --remote-debugging-port=9222")
        print("Beispiel für Windows: \"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\" --remote-debugging-port=9222")
        print("Das Skript kann nicht fortfahren, wenn die Verbindung fehlschlägt.")
        input("\nDrücke ENTER, um das Skript zu beenden.")
        return

    print(f"Beginne mit dem Eintragen der Gerichte in {MEDIUM_WAIT} Sekunden...")
    time.sleep(MEDIUM_WAIT)

    successful_uploads = 0
    failed_uploads = 0

    for i, dish in enumerate(dishes_to_upload):
        print(f"\nVerarbeite Gericht {i+1}/{len(dishes_to_upload)}: {dish['Name']}")

        try:
            # 1. Auf "Neues Gericht hinzufügen" klicken
            print("  Klicke auf 'Neues Gericht hinzufügen'...")
            add_button = wait.until(EC.element_to_be_clickable(ADD_NEW_DISH_BUTTON_SELECTOR))
            try:
                add_button.click()
            except ElementClickInterceptedException:
                print("  Normaler Klick auf 'Neues Gericht' abgefangen, versuche JavaScript-Klick...")
                driver.execute_script("arguments[0].click();", add_button)
            
            # Warten, bis das Formular (erstes Feld) erscheint, statt fester MEDIUM_WAIT
            try:
                print("  Warte auf Formular...")
                wait.until(EC.visibility_of_element_located(DISH_NAME_INPUT_SELECTOR))
                time.sleep(0.5) # Kurze Pause, um sicherzustellen, dass JS-Events abgeschlossen sind
            except TimeoutException:
                print("!! FEHLER: Formular (Namensfeld) erschien nicht rechtzeitig nach Klick auf 'Neues Gericht'.")
                raise # Fehler weitergeben, um zum nächsten Gericht zu springen

            # 2. Name eingeben
            print(f"  Fülle Namen aus: {dish['Name']}")
            name_input = driver.find_element(*DISH_NAME_INPUT_SELECTOR) # Erneutes Finden, falls Seite neu geladen
            name_input.clear()
            name_input.send_keys(dish['Name'])
            time.sleep(SHORT_WAIT)

            # 3. Preis eingeben
            price_str = dish['Preis'].replace(' €', '').replace(',', '.').strip()
            print(f"  Fülle Preis aus: {price_str}")
            price_input = driver.find_element(*DISH_PRICE_INPUT_SELECTOR)
            price_input.clear()
            price_input.send_keys(price_str)
            time.sleep(SHORT_WAIT)

            # 4. Beschreibung eingeben
            print(f"  Fülle Beschreibung aus: {dish['Beschreibung']}")
            desc_input = driver.find_element(*DISH_DESCRIPTION_INPUT_SELECTOR)
            desc_input.clear()
            desc_input.send_keys(dish['Beschreibung'])
            time.sleep(SHORT_WAIT)
            
            # 5. Steuersatz eingeben
            print("  Fülle Steuersatz aus: 10")
            tax_input = driver.find_element(*DISH_TAX_INPUT_SELECTOR)
            tax_input.clear()
            tax_input.send_keys("10")
            time.sleep(SHORT_WAIT)

            # 6. Allergene eingeben
            allergens_value = dish.get('Allergene', '')
            if not allergens_value or allergens_value.lower() == 'keine angabe':
                allergens_value = ''
            print(f"  Fülle Allergene aus: '{allergens_value}'")
            allergens_input = driver.find_element(*DISH_ALLERGENS_INPUT_SELECTOR)
            allergens_input.clear()
            allergens_input.send_keys(allergens_value)
            time.sleep(SHORT_WAIT)

            # 7. Auf "Speichern" klicken
            print("  Klicke auf 'Speichern'...")
            save_button = wait.until(EC.element_to_be_clickable(SAVE_DISH_BUTTON_SELECTOR))
            try:
                save_button.click()
            except ElementClickInterceptedException:
                print("  Normaler Klick auf 'Speichern' abgefangen, versuche JavaScript-Klick...")
                driver.execute_script("arguments[0].click();", save_button)
            
            print(f"  Warte {LONG_WAIT}s nach dem Speichern...")
            time.sleep(LONG_WAIT)

            print(f"  Gericht '{dish['Name']}' erfolgreich eingetragen (hoffentlich).")
            successful_uploads += 1

        except Exception as e:
            print(f"!! FEHLER beim Verarbeiten von Gericht '{dish['Name']}': {e}")
            current_url = driver.current_url
            print(f"  Aktuelle URL beim Fehler: {current_url}")
            print("  Das Skript wird versuchen, mit dem nächsten Gericht fortzufahren.")
            print("  Möglicherweise musst du dieses Gericht manuell korrigieren oder das Formular/Modal schließen.")
            # Optional: Screenshot bei Fehler machen
            # timestamp = time.strftime("%Y%m%d-%H%M%S")
            # driver.save_screenshot(f'error_screenshot_{timestamp}_{dish["Name"][:20]}.png')
            # print(f"    Screenshot gespeichert: error_screenshot_{timestamp}_{dish["Name"][:20]}.png")
            time.sleep(MEDIUM_WAIT) # Längere Pause nach einem Fehler, um manuell einzugreifen
            failed_uploads += 1
            continue

    print("\nAlle ausgewählten Gerichte wurden verarbeitet.")
    print(f"Erfolgreiche Uploads: {successful_uploads}")
    print(f"Fehlgeschlagene Uploads: {failed_uploads}")
    input("\nDrücke ENTER, um das Skript zu beenden und das Terminalfenster offen zu halten...")

if __name__ == '__main__':
    main() 