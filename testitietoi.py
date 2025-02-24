import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Avaa sivu
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
URL = "https://tulospalvelu.leijonat.fi/serie/?lang=fi"
driver.get(URL)

wait = WebDriverWait(driver, 10)

# Odotetaan, että sivu latautuu
time.sleep(5)  # Voit lisätä tätä odotusta, että taulukot ehtivät latautua

# Hae sivun HTML
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# Etsi kaikki taulukot
tables = soup.find_all("table")

# Tarkista, kuinka monta taulukkoa löytyy ja tulosta niiden sisältö
print(f"Sivulta löytyi {len(tables)} taulukkoa.")


# Oletetaan, että olet saanut HTML-sisällön jollain tavalla (esim. Seleniumin avulla)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# Etsitään taulukko, jonka luokka on "table"
table = soup.find("table", {"class": "table"})

# Haetaan kaikki rivit (tr) taulukosta
rows = table.find_all("tr")

# Käydään läpi rivit ja etsitään joukkueiden nimet
for row in rows:
    cols = row.find_all("td")
    if len(cols) > 2:  # Tarkistetaan, että rivillä on tarpeeksi sarakkeita
        # Joukkueen nimi on kolmannessa sarakkeessa
        team_name = cols[2].text.strip()
        print(f"Joukkue: {team_name}")


# Sulje selain
driver.quit()
