from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Set up the WebDriver (make sure to specify the path to your WebDriver if needed)
driver = webdriver.Chrome()

# Open the target web page
driver.get('https://tulospalvelu.leijonat.fi/serie/?lang=fi')

# Wait for the page to load
wait = WebDriverWait(driver, 10)  # 10 seconds timeout
time.sleep(2)

# Handle the cookie popup
try:
    cookie_popup = wait.until(EC.presence_of_element_located(
        (By.ID, "CybotCookiebotDialogBodyUnderlay")))
    close_button = driver.find_element(
        By.ID, "CybotCookiebotDialogBodyButtonDecline")
    close_button.click()
    print("✅ Evästeilmoitus suljettu!")
    time.sleep(2)
except Exception as e:
    print(f"Evästeilmoitusta ei löytynyt, jatketaan normaalisti. Virhe: {e}")

time.sleep(2)

# Fill the text input field
try:
    text_area_1 = driver.find_element(
        By.CSS_SELECTOR, '[placeholder="Hae sarjaa joukkueen nimellä"]')
    text_area_1.send_keys('Tornados')
    print("✅ Tekstikenttä täytetty!")
except Exception as e:
    print(f"Kenttä ei löytynyt. Virhe: {e}")

# Locate and activate the submit button
try:
    # Find the submit button
    submit_button = driver.find_element(By.CSS_SELECTOR, '.text-search-btn')

    # Odotetaan, että painike on klikattavissa (aktivoi painike)
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(submit_button))

    # Poistetaan 'disabled' -attribuutti, jos se on olemassa
    driver.execute_script(
        "arguments[0].removeAttribute('disabled')", submit_button)

    # Klikataan painiketta
    submit_button.click()
    print("✅ Painike klikattu onnistuneesti!")
except Exception as e:
    print(f"Klikkaus ei onnistunut. Virhe: {e}")

# Wait for a moment to see the result
time.sleep(5)

# Close the browser
driver.quit()
