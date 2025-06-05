from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import traceback
import csv

def scrape_example_restaurant_menu():
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    driver = webdriver.Chrome(service=service, options=options)
    url = "https://www.example-restaurant.com/menu" 
    all_dishes = []

    try:
        print(f"Navigiere zu {url}...")
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(translate(., 'AKZEPTIERENZUSTIMMENVERSTANDEN', 'akzeptierenzustimmenverstanden'), 'akzeptieren') or contains(translate(., 'AKZEPTIERENZUSTIMMENVERSTANDEN', 'akzeptierenzustimmenverstanden'), 'zustimmen') or contains(translate(., 'AKZEPTIERENZUSTIMMENVERSTANDEN', 'akzeptierenzustimmenverstanden'), 'verstanden')] | //a[contains(translate(., 'AKZEPTIEREN', 'akzeptieren'), 'akzeptieren')]"))
            ).click()
            print("Cookie-Banner akzeptiert.")
        except Exception:
            print("Konnte Cookie-Banner nicht automatisch akzeptieren oder Banner nicht gefunden.")

        print("Warte auf das Laden der Seite und scrolle zum Ende...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) # Allow time for any lazy loading triggered by full scroll
        driver.execute_script("window.scrollTo(0, 0);") # Scroll back to top
        time.sleep(1)

        print("Suche nach allen Kategorie-Containern...")
        # Find all main category containers. These are divs with class 'w100 category mt20' and contain an h2 title
        category_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'w100') and contains(@class, 'category') and contains(@class, 'mt20') and .//h2]")
        
        if not category_containers:
            print("Konnte keine Kategorie-Container finden. Überprüfe den XPath.")
            return []
            
        print(f"{len(category_containers)} Kategorie-Container gefunden.")

        for i, category_container in enumerate(category_containers):
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", category_container)
            time.sleep(0.5) # Give a moment for any JS to react if needed

            category_name = "Unbekannte Kategorie"
            try:
                category_name_element = category_container.find_element(By.XPATH, ".//div[contains(@class, 'categorytitle')]//h2")
                category_name = category_name_element.text.strip()
                print(f"\nVerarbeite Kategorie ({i+1}/{len(category_containers)}): {category_name}")
            except Exception as e_cat_name:
                print(f"WARNUNG: Konnte Kategorienamen nicht extrahieren: {e_cat_name}")
                # print(category_container.get_attribute('innerHTML')) # Debug: show inner HTML of problematic container

            products_container = None
            try:
                products_container = category_container.find_element(By.XPATH, ".//div[contains(@class, 'w100') and contains(@class, 'products')]")
            except Exception:
                print(f"  INFO: Kein 'products'-Container in Kategorie '{category_name}' gefunden. Überspringe.")
                continue
            
            # Refined XPath to find only actual product divs
            dish_elements = products_container.find_elements(By.XPATH, ".//div[contains(@class, 'product') and (contains(@class, 'selecter-product-direct') or contains(@class, 'selecter-product'))]")
            print(f"  {len(dish_elements)} Gerichte in '{category_name}' gefunden (mit präzisem XPath).")

            for dish_element in dish_elements:
                name, description, price, allergens_str = "N/A", "N/A", "N/A", "N/A"
                
                try:
                    name_element = dish_element.find_element(By.XPATH, ".//p[contains(@class, 'producttitle')]")
                    name = name_element.text.strip()
                except Exception: pass # Name not found

                try:
                    desc_element = dish_element.find_element(By.XPATH, ".//p[contains(@class, 'productdesc')]")
                    description = desc_element.text.strip()
                    if not description: description = "Keine Beschreibung verfügbar"
                except Exception: 
                    description = "Keine Beschreibung verfügbar"


                try:
                    price_element = dish_element.find_element(By.XPATH, ".//p[contains(@class, 'productprice')]")
                    price = price_element.text.strip()
                except Exception: pass # Price not found
                
                try:
                    allergen_element = dish_element.find_element(By.XPATH, ".//p[contains(@class, 'allergene')]")
                    allergens_raw = allergen_element.text.strip()
                    if allergens_raw.lower().startswith("allergene:"):
                        allergens_str = allergens_raw[len("allergene:"):].strip()
                    else:
                        allergens_str = allergens_raw # Fallback if format is different
                    if not allergens_str: allergens_str = "Keine Angabe"
                except Exception:
                    allergens_str = "Keine Angabe"

                if name != "N/A" and price != "N/A":
                    dish_data = {
                        "category": category_name,
                        "name": name,
                        "description": description,
                        "price": price,
                        "allergens": allergens_str
                    }
                    all_dishes.append(dish_data)
                    print(f"    + {name} ({price}) - Allergene: {allergens_str} - Desc: {description[:30]}...")
                else:
                    print(f"    - Konnte Name oder Preis nicht extrahieren für ein Element in '{category_name}'. Name='{name}', Preis='{price}'")

    except Exception as e:
        print(f"Ein schwerwiegender Fehler ist aufgetreten: {e}")
        print("Traceback:")
        traceback.print_exc()

    finally:
        if 'driver' in locals() and driver:
            driver.quit()
            print("\nBrowser geschlossen.")
    
    return all_dishes

if __name__ == '__main__':
    print("Starte Example Restaurant Scraper...")
    extracted_dishes = scrape_example_restaurant_menu()
    
    if extracted_dishes:
        print(f"\n--- {len(extracted_dishes)} Gerichte erfolgreich extrahiert ---")
        
        # CSV-Datei erstellen und schreiben
        csv_file_path = 'example_menu_data.csv'
        try:
            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Schreibe die Kopfzeile
                writer.writerow(['Kategorie', 'Name', 'Beschreibung', 'Preis', 'Allergene'])
                # Schreibe die Daten für jedes Gericht
                for dish in extracted_dishes:
                    writer.writerow([
                        dish.get('category', 'N/A'),
                        dish.get('name', 'N/A'),
                        dish.get('description', 'N/A'),
                        dish.get('price', 'N/A'),
                        dish.get('allergens', 'N/A')
                    ])
            print(f"\nDaten erfolgreich in '{csv_file_path}' gespeichert.")
        except IOError as e:
            print(f"\nFEHLER beim Schreiben der CSV-Datei: {e}")

        # Optionale gruppierte Terminal-Ausgabe (bleibt erhalten)
        dishes_by_category = {}
        for dish in extracted_dishes:
            cat = dish['category']
            if cat not in dishes_by_category:
                dishes_by_category[cat] = []
            dishes_by_category[cat].append(dish)
            
        for category, dishes_in_cat in dishes_by_category.items():
            print(f"\n Kategorie: {category} ({len(dishes_in_cat)} Gerichte)")
            for dish in dishes_in_cat:
                print(f"  Name: {dish['name']}")
                print(f"  Preis: {dish['price']}")
                print(f"  Beschreibung: {dish['description']}")
                print(f"  Allergene: {dish['allergens']}")
                print("  --------------------")
    else:
        print("\nKonnte keine Gerichte extrahieren oder keine gefunden.")

    print("\nAllergen-Legende (Beispiel, bitte von der Ziel-Webseite prüfen und ggf. anpassen):")
    print("A – Gluten, B – Krebstiere, C – Eier von Geflügel, D – Fisch, E – Erdnüsse, F – Sojabohnen,")
    print("G – Milch von Säugetieren, H – Schalenfrüchte, L – Sellerie, M – Senf, N – Sesamsamen,")
    print("O – Schwefeloxid und Sulfite, P – Lupinen, R – Weichtiere") 