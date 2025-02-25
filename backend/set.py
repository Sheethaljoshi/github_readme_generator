import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

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

def extract_textarea_content(driver, file_link):
    """Extracts and returns the text content from the textarea of a file page."""
    driver.get(file_link)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    textareas = soup.find_all('textarea', {'id': 'read-only-cursor-text-area'})
    
    if textareas:
        return [textarea.get_text(strip=True) for textarea in textareas]
    else:
        return []

def scrape_repository(url):
    """Recursively scrapes all files from a repository, ignoring 'node_modules'."""
    driver = setup_driver()
    visited_urls = set()  # Tracks visited directories
    visited_files = set()  # Tracks visited files (fix for duplicates)
    
    all_extracted_texts = []
    
    try:
        def process_directory(directory_url):
            """Processes a directory by extracting its files and recursively visiting subdirectories."""
            if directory_url in visited_urls or "node_modules" in directory_url:
                return  # Skip if already visited or is 'node_modules'
            visited_urls.add(directory_url)
            
            print(f"Processing directory: {directory_url}")
            
            file_links, directory_links = get_links(driver, directory_url)
            
            # Extract text content from files
            for file_link in file_links:
                if file_link in visited_files:
                    continue  # Skip if the file was already processed
                visited_files.add(file_link)  # Mark file as processed
                
                print(f"Extracting file: {file_link}")
                textarea_texts = extract_textarea_content(driver, file_link)
                
                if textarea_texts:
                    file_info = {
                        "url": file_link,
                        "texts": textarea_texts
                    }
                    all_extracted_texts.append(file_info)
            
            # Recursively process directories
            for sub_directory in directory_links:
                process_directory(sub_directory)
        
        # Start processing from the root URL
        process_directory(url)
        
        print(f"Extraction complete. {len(all_extracted_texts)} files processed.")
        return all_extracted_texts
    
    finally:
        driver.quit()

def display_results(extracted_data):
    """Displays the results of the extraction."""
    print("\n=== EXTRACTION RESULTS ===\n")
    
    for i, file_data in enumerate(extracted_data, 1):
        print(f"File {i}: {file_data['url']}")
        for j, text in enumerate(file_data['texts'], 1):
            print(f"  Textarea {j}: {text[:100]}..." if len(text) > 100 else f"  Textarea {j}: {text}")
        print()

# Example usage
if __name__ == "__main__":
    repo_url = input("Enter the repository URL: ")
    extracted_data = scrape_repository(repo_url)
    display_results(extracted_data)