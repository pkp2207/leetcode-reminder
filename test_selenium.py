# test_selenium.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

print("--- Starting Minimal Selenium Test ---")

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

try:
    # Let Selenium Manager handle the driver automatically
    driver = webdriver.Chrome(options=chrome_options)
    
    print("Browser launched successfully. Navigating to Google.")
    driver.get("https://www.google.com")
    
    # Wait a moment for the page to load
    time.sleep(2)
    
    print(f"Successfully loaded page. Title is: '{driver.title}'")
    
    driver.quit()
    print("--- Test Passed! ---")

except Exception as e:
    print(f"--- Test FAILED with an error: {e} ---")