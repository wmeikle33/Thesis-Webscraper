from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fetch_html(driver, url: str, timeout: int = 10) -> str:
    driver.get(url)

    # wait for something that indicates page loaded
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    return driver.page_source
