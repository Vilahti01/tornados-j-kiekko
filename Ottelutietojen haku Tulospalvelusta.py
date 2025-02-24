from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Asennetaan WebDriver
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

# Avaa Tulospalvelun sivu
URL = "https://tulospalvelu.leijonat.fi/serie/?lang=fi"
driver.get(URL)

wait = WebDriverWait(driver, 10)

# ***1️⃣ Suljetaan evästeilmoitus, jos se löytyy***
try:
    cookie_popup = wait.until(EC.presence_of_element_located(
        (By.ID, "CybotCookiebotDialogBodyUnderlay")))
    close_button = driver.find_element(
        By.ID, "CybotCookiebotDialogBodyButtonDecline")
    close_button.click()
    print("✅ Evästeilmoitus suljettu!")
    time.sleep(2)
except:
    print("✅ Evästeilmoitusta ei löytynyt, jatketaan normaalisti.")

# ***2️⃣ Valitaan sarjataso "Harrastesarjat"***
try:
    level_dropdown = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, "level-selection")))
    print("✅ Sarjatasovalikko löydetty!")

    driver.execute_script("ui.LevelChanged(71);")  # 71 = "Harrastesarjat"
    time.sleep(5)  # Odotetaan, että uusi valikko latautuu

    print("✅ Harrastesarjat valittu onnistuneesti!")

except Exception as e:
    print(f"❌ Sarjatasovalikon valinta epäonnistui: {e}")

# ***3️⃣ Odotetaan ja valitaan alue "Häme"***
try:
    print("⏳ Odotetaan, että aluevalikko ilmestyy uudelleen...")
    district_dropdown = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, "district-selection")))
    time.sleep(3)  # Odotetaan, että vaihtoehdot tulevat näkyviin

    # Etsitään ja valitaan "Häme"
    options = district_dropdown.find_elements(By.TAG_NAME, "option")
    for option in options:
        if "Häme" in option.text:
            option.click()
            print("✅ Alue 'Häme' valittu!")
            break

    time.sleep(5)  # Odotetaan, että sarjavalikko latautuu

except Exception as e:
    print(f"❌ Aluevalikon valinta epäonnistui: {e}")

# ***4️⃣ Valitaan sarja "Harrastesarja 3 (1537)"***
try:
    print("⏳ Odotetaan, että sarjavalikko ilmestyy...")
    statgroup_dropdown = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, "statgroup-selection")))
    time.sleep(3)  # Odotetaan, että vaihtoehdot tulevat näkyviin

    # Etsitään ja valitaan "Harrastesarja 3 (1537)"
    options = statgroup_dropdown.find_elements(By.TAG_NAME, "option")
    sarja_valittu = False
    for option in options:
        if "Harrastesarja 3 (1537)" in option.text:
            option.click()
            sarja_valittu = True
            print("✅ Sarja 'Harrastesarja 3 (1537)' valittu!")
            break

    if not sarja_valittu:
        print("⚠️ Sarjaa 'Harrastesarja 3 (1537)' ei löytynyt!")

    time.sleep(5)  # Odotetaan, että ottelut latautuvat

except Exception as e:
    print(f"❌ Sarjavalikon valinta epäonnistui: {e}")

# ***5️⃣ Haetaan sarjataulukko***
try:
    print("⏳ Haetaan sarjataulukko...")
    # Klikataan Sarjataulukko-linkkiä
    sarjataulukko_button = wait.until(
        EC.presence_of_element_located((By.LINK_TEXT, "Sarjataulukko")))
    sarjataulukko_button.click()
    print("✅ 'Sarjataulukko' valittu!")

    time.sleep(5)  # Odotetaan, että taulukko latautuu

except Exception as e:
    print(f"❌ Sarjataulukon valinta epäonnistui: {e}")

# ***6️⃣ Haetaan joukkueet ja niiden pelatut ottelut***
try:
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Etsitään sarjataulukko
    table = soup.find("table", {"class": "table"})
    if table:
        print("✅ Sarjataulukko löytyi!")

        rows = table.find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            if len(columns) > 2:  # Tarkistetaan, että sarakkeita on vähintään 3 (nimi, pelatut ottelut)
                team_name = columns[1].get_text(strip=True)
                played_games = columns[2].get_text(strip=True)
                print(f"Joukkue: {team_name}, Pelatut ottelut: {played_games}")
            else:
                print("⚠️ Rivillä ei ole tarpeeksi sarakkeita.")
    else:
        print("⚠️ Sarjataulukkoa ei löytynyt!")

except Exception as e:
    print(f"❌ Joukkueiden ja pelattujen otteluiden hakeminen epäonnistui: {e}")

# ***ÄLÄ SULJE SELAINTA AUTOMAATTISESTI, VAAN KATSO, MITÄ SE NÄYTTÄÄ!***
input("Paina ENTER sulkeaksesi selaimen...")

# Suljetaan selain käyttäjän hyväksynnällä
driver.quit()
