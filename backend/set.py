import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Sets up a headless Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_links(driver, url):
    """Extracts file and directory links from the given page."""
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "Link--primary")))

    elements = driver.find_elements(By.CLASS_NAME, "Link--primary")

    file_links = []
    directory_links = []

    for element in elements:
        aria_label = element.get_attribute("aria-label")
        href = element.get_attribute("href")

        if aria_label and href:
            if "(File)" in aria_label:
                file_links.append(href)
            elif "(Directory)" in aria_label and "node_modules" not in href:
                directory_links.append(href)

    return file_links, directory_links

def extract_html(driver, file_link):
    """Extracts and returns the HTML content of a file page."""
    driver.get(file_link)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    return driver.page_source

def scrape_repository(url, output_file):
    """Recursively scrapes all files from a repository, ignoring 'node_modules'."""
    driver = setup_driver()
    visited_urls = set()  # Tracks visited directories
    visited_files = set()  # Tracks visited files (fix for duplicates)

    try:
        def process_directory(directory_url):
            """Processes a directory by extracting its files and recursively visiting subdirectories."""
            if directory_url in visited_urls or "node_modules" in directory_url:
                return  # Skip if already visited or is 'node_modules'
            visited_urls.add(directory_url)

            print(f"Processing directory: {directory_url}")

            file_links, directory_links = get_links(driver, directory_url)

            # Extract and append file HTML
            with open(output_file, "a", encoding="utf-8") as file:
                for file_link in file_links:
                    if file_link in visited_files:
                        continue  # Skip if the file was already processed
                    visited_files.add(file_link)  # Mark file as processed

                    print(f"Extracting file: {file_link}")
                    file_html = extract_html(driver, file_link)
                    file.write(file_html + "\n\n")  

            # Recursively process directories
            for sub_directory in directory_links:
                process_directory(sub_directory)

        # Start processing from the root URL
        process_directory(url)

        print(f"Extraction complete. Data saved to {output_file}")

    finally:
        driver.quit()

# Example usage
repo_url = input("Enter the repository URL: ")
output_filename = "extracted_repo_html.html"
scrape_repository(repo_url, output_filename)
