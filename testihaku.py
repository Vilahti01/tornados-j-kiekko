from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
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

# ***5️⃣ Haetaan ja tulostetaan joukkueiden tiedot***
try:
    # Odotetaan, että taulukko on ladattu
    team_table = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "table")))

    # Haetaan kaikki joukkueet
    teams = team_table.find_elements(By.CLASS_NAME, "team-name")
    print("✅ Joukkueet löytyivät!")

    for team in teams:
        print(team.text)
except Exception as e:
    print(f"❌ Joukkueiden tietojen hakeminen epäonnistui: {e}")

# ***6️⃣ Haetaan ja tulostetaan tilastot***
try:
    # Odotetaan, että tilastotaulukko on ladattu
    stats_table = wait.until(EC.presence_of_element_located(
        (By.XPATH, "//table[contains(@style, 'min-width: 360px;')]")))

    stats_rows = stats_table.find_elements(By.TAG_NAME, "tr")

    print("✅ Tilastot löytyivät!")
    for index, row in enumerate(stats_rows):
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) > 1:
            # Poimitaan ensimmäiset 8 saraketta
            stats = [col.text.strip() for col in cols[:8]]
            print(f"Tilastot: {stats}")
except Exception as e:
    print(f"❌ Tilastojen hakeminen epäonnistui: {e}")

# ***7️⃣ Haetaan ja tulostetaan joukkueiden pelatut ottelut***
try:
    print("⏳ Haetaan joukkueiden pelatut ottelut...")

    # Haetaan joukkueiden rivit
    team_rows = team_table.find_elements(By.TAG_NAME, "tr")

    for row in team_rows:
        columns = row.find_elements(By.TAG_NAME, "td")

        if len(columns) > 1:  # Varmistetaan, että rivillä on tarpeeksi sarakkeita
            try:
                team_name = columns[1].text.strip()  # Joukkueen nimi
                # Pelatut ottelut, oletetaan että tämä on toisessa sarakkeessa
                played_games = columns[2].text.strip()

                print(f"Joukkue: {team_name}, Pelatut ottelut: {played_games}")
            except IndexError:
                print("⚠️ Puuttuvaa tietoa jollain rivillä.")
except Exception as e:
    print(f"❌ Joukkueiden pelattujen otteluiden hakeminen epäonnistui: {e}")

# ***ÄLÄ SULJE SELAINTA AUTOMAATTISESTI, VAAN KATSO, MITÄ SE NÄYTTÄÄ!***
input("Paina ENTER sulkeaksesi selaimen...")

# Suljetaan selain käyttäjän hyväksynnällä
driver.quit()
