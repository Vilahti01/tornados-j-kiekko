from selenium import webdriver

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

driver.get("https://www.google.com")
print(driver.title)  # Pitäisi tulostaa "Google"
driver.quit()
