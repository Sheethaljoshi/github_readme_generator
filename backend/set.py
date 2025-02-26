import os
import json
import time
from urllib.parse import urlparse, unquote
from fastapi import FastAPI, HTTPException, Query
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from openai import OpenAI

app = FastAPI()

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

def extract_file_info_from_url(url):
    """Extracts file path and name from the GitHub URL."""
    parsed_url = urlparse(url)
    path_components = parsed_url.path.split('/')
    
    owner = path_components[1] if len(path_components) > 1 else ""
    repo = path_components[2] if len(path_components) > 2 else ""
    
    if len(path_components) > 4 and path_components[3] == "blob":
        file_path_components = path_components[5:]
        file_path = '/'.join(file_path_components)
        file_path = unquote(file_path)
        file_name = file_path_components[-1] if file_path_components else ""
        file_name = unquote(file_name)
        full_path = f"{repo}/{file_path}"
        
        return {
            "owner": owner,
            "repo": repo,
            "path": file_path,
            "full_path": full_path,
            "name": file_name
        }
    return {"owner": owner, "repo": repo, "path": "", "full_path": "", "name": ""}

def extract_textarea_content(driver, file_link):
    """Extracts and returns the text content from the textarea of a file page."""
    driver.get(file_link)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    textareas = soup.find_all('textarea', {'id': 'read-only-cursor-text-area'})
    
    return textareas[0].get_text(strip=False) if textareas else ""

def scrape_repository(url):
    driver = setup_driver()
    visited_urls = set()
    visited_files = set()
    all_extracted_files = []
    
    try:
        def process_directory(directory_url):
            if directory_url in visited_urls or "node_modules" in directory_url:
                return
            visited_urls.add(directory_url)
            file_links, directory_links = get_links(driver, directory_url)
            
            for file_link in file_links:
                if file_link in visited_files:
                    continue
                visited_files.add(file_link)
                file_info = extract_file_info_from_url(file_link)
                file_content = extract_textarea_content(driver, file_link)
                
                if file_content:
                    all_extracted_files.append({
                        "url": file_link,
                        "owner": file_info["owner"],
                        "repo": file_info["repo"],
                        "path": file_info["path"],
                        "full_path": file_info["full_path"],
                        "name": file_info["name"],
                        "content": file_content
                    })
            
            for sub_directory in directory_links:
                process_directory(sub_directory)
        
        process_directory(url)
        return all_extracted_files
    
    finally:
        driver.quit()

def create_readme(json_output):
    client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
    prompt = f"""Given the following file with file content: {json_output} generate a Readme file code of what the repository does and specify the technology, installed packages, language used and how to run the program as well. explain each functionality of the code in the Readme file.ONLY TAKE INFORMATION FROM THE GIVEN CONTENT AND DO NOT MAKE UP YOUR OWN!"""
    
    response = client.chat.completions.create(
        model="llama3.2",
        messages=[
            {"role": "system", "content": "You are a specialized assistant that generates high-quality GitHub README.md files. When given repository information, you will create a professional, well-structured README that follows best practices and highlights the repository's features. ONLY TAKE INFORMATION FROM THE GIVEN CONTENT AND DO NOT MAKE UP YOUR OWN!"},
            {"role": "user", "content": prompt},
        ],
    )
    
    return response.choices[0].message.content

@app.get("/scrape")
def scrape_and_generate_readme(repo_url: str = Query(..., title="Repository URL", description="The GitHub repository URL to scrape.")):
    if not repo_url:
        raise HTTPException(status_code=400, detail="Repository URL is required.")
    
    extracted_files = scrape_repository(repo_url)
    if not extracted_files:
        raise HTTPException(status_code=404, detail="No files extracted from the repository.")
    
    json_output = json.dumps(extracted_files, indent=2)
    readme_content = create_readme(json_output)
    return {"readme": readme_content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
