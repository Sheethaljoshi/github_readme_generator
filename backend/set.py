from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_full_page_htmls(url, class_name):
    """Extracts HTML content from all pages linked by elements with a specific class."""
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)  # Open the main page
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

        # Find all elements with the specified class name
        elements = driver.find_elements(By.CLASS_NAME, class_name)

        # Define words to exclude
        exclude_texts = {"Releases", "Packages", "Contributors"}

        # Extract links and texts, filtering out excluded elements
        links = [
            el for el in elements 
            if el.text.strip() and el.text.strip() not in exclude_texts
        ]

        extracted_htmls = []

        for link in links:
            try:
                # Scroll into view before clicking
                driver.execute_script("arguments[0].scrollIntoView();", link)
                time.sleep(1)

                # Open link in a new tab
                action = ActionChains(driver)
                action.key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
                time.sleep(5)  # Increase wait time to allow full loading

                # Switch to the new tab
                driver.switch_to.window(driver.window_handles[-1])

                # Wait until the page fully loads
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                # Extract full HTML of the page
                page_html = driver.page_source
                extracted_htmls.append(page_html)

                # Close the tab and return to the main page
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"Error processing link {link.text}: {e}")

        return extracted_htmls

    finally:
        driver.quit()

# Example usage
url = input("Enter the URL: ")
class_name = "Link--primary"
html_pages = get_full_page_htmls(url, class_name)

# Print the extracted HTML for each page
for i, html in enumerate(html_pages, 1):
    print(f"\n=== Page {i} HTML ===\n")
    print(html[:1000])  # Print first 1000 characters for preview
