from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def get_elements_with_class(url, class_name):
    """Fetches elements with the specified class name from a given webpage using Selenium."""
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no UI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Use webdriver-manager to auto-install ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)  # Open the webpage

        # Find all elements with the specified class name
        elements = driver.find_elements(By.CLASS_NAME, class_name)

        # Define words to exclude
        exclude_texts = {"Releases", "Packages", "Contributors"}

        # Extract full HTML, filtering out empty and excluded elements
        extracted_data = [
            el.get_attribute("outerHTML")
            for el in elements
            if el.text.strip() and el.text.strip() not in exclude_texts
        ]

        return extracted_data

    finally:
        driver.quit()  # Close the browser

# Example usage
url = input("Enter the URL: ")
class_name = "Link--primary"
elements = get_elements_with_class(url, class_name)

# Print the extracted full HTML elements
for element_html in elements:
    print(element_html)
