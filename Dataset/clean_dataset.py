import pandas as pd
import numpy as np
import re
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException 
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIG ---
INPUT_CSV = "french_names_dataset.csv"
OUTPUT_CSV = "french_names_dataset_repaired.csv"
PAGE_TIMEOUT = 15

def create_driver():
    """Creates a fast, headless browser instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false") 
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.set_page_load_timeout(PAGE_TIMEOUT)
    return driver

def get_page_data(driver, url, target_lang, fix_name=False):
    """Navigates to the URL, repairs corrupted names from the H1 header, and extracts pronunciation."""
    scraped_name = ""
    scraped_pron = ""
    
    try:
        try:
            driver.get(url)
        except TimeoutException:
            driver.execute_script("window.stop();")
            
        WebDriverWait(driver, PAGE_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 1. BULLETPROOF LIVE NAME REPAIR
        if fix_name:
            try:
                h1_text = driver.find_element(By.TAG_NAME, "h1").text.strip()
                
                # Handle structural page text adjustments if necessary
                if "the name" in h1_text.lower():
                    h1_text = h1_text.lower().split("the name")[-1].strip()
                
                # Step A: Remove parenthesized numbers if they exist (e.g., "Dina (2)" -> "Dina")
                clean_name = re.sub(r'\s*\(\d+\).*', '', h1_text)
                
                # Step B: Remove trailing numbers separated by spaces or hyphens (e.g., "Dina 2" or "Dick-1" -> "Dina"/"Dick")
                clean_name = re.sub(r'[- ]*\d+$', '', clean_name)
                
                # Step C: Strip ANY remaining digits anywhere in the string just to be completely safe
                clean_name = re.sub(r'\d+', '', clean_name)
                
                # Step D: Strip leftover trailing spaces/hyphens and apply title casing to preserve accents safely
                scraped_name = clean_name.strip("- ").title()
            except Exception as e:
                print(f"    [WARN] Could not scrape true name from H1: {e}")

        # 2. PRONUNCIATION EXTRACTION
        body_text = driver.find_element(By.TAG_NAME, "body").text
        pron_line = ""
        for line in body_text.split("\n"):
            if "Pronounced" in line:
                pron_line = line.strip()
                break
                
        if "/" in pron_line:
            try:
                toggle = driver.find_element(By.XPATH, "//a[contains(text(),'simplify')]")
                driver.execute_script("arguments[0].click();", toggle) 
                time.sleep(1.2)
                
                body_text = driver.find_element(By.TAG_NAME, "body").text
                for line in body_text.split("\n"):
                    if "Pronounced" in line:
                        pron_line = line.strip()
                        break
            except Exception:
                pass 
                
        if pron_line:
            clean_line = re.sub(r"^Pronounced\s*", "", pron_line).split("[key")[0].strip()
            pattern = r"([^()]+)(?:\(([^()]+)\))?"
            matches = re.findall(pattern, clean_line)
            
            if not matches and clean_line:
                fallback_raw = [p.strip() for p in clean_line.split(",") if p.strip()][0]
                scraped_pron = fallback_raw.replace("[", "").replace("]", "").replace("/", "").strip()
            else:
                for pron_block, langs_raw in matches:
                    pron_block = pron_block.lstrip(', ').rstrip(', ').strip()
                    langs = [l.strip() for l in langs_raw.split(",")] if langs_raw else ["English"]
                    
                    if target_lang in langs:
                        individual_prons = [p.strip() for p in pron_block.split(",") if p.strip()]
                        if individual_prons:
                            raw_string = individual_prons[0] 
                            scraped_pron = raw_string.replace("[", "").replace("]", "").replace("/", "").strip()
                            break
                            
    except Exception as e:
        print(f"    [ERROR] Failed retrieving data for {url}: {e}")
        
    return scraped_name, scraped_pron

def clean_and_repair_dataset():
    # 1. Load data with UTF-8 to safeguard complex accents (like Máirín)
    print(f"Loading {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV, encoding='utf-8-sig')
    
    # 2. Setup targeting masks
    df['Pronunciation_Text'] = df['Pronunciation_Text'].fillna("")
    
    # Target anything containing a number anywhere in the name field
    corrupt_name_mask = df['Name'].astype(str).str.contains(r'\d', regex=True)
    missing_pron_mask = df['Pronunciation_Text'] == ""
    
    target_mask = corrupt_name_mask | missing_pron_mask
    repair_indices = df[target_mask].index.tolist()
    
    if not repair_indices:
        print("No corrupt names or missing pronunciations found! Saving file.")
        df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
        return

    print(f"Found {len(repair_indices)} rows requiring repair. Starting browser session...")
    driver = create_driver()
    
    try:
        for counter, idx in enumerate(repair_indices, 1):
            current_name = df.loc[idx, 'Name']
            lang = df.loc[idx, 'Language']
            url = df.loc[idx, 'URL']
            
            needs_name_fix = bool(re.search(r'\d', str(current_name)))
            reason = "Name & Pronunciation" if (needs_name_fix and df.loc[idx, 'Pronunciation_Text'] == "") else ("Name Fix Only" if needs_name_fix else "Pronunciation Only")
            
            print(f"[{counter}/{len(repair_indices)}] Processing: {current_name} ({lang}) -> {reason}")
            
            # Fetch data from the live page
            true_name, fetched_pron = get_page_data(driver, url, lang, fix_name=needs_name_fix)
            
            if true_name:
                print(f"    -> Repaired Name: '{current_name}' to '{true_name}'")
                df.loc[idx, 'Name'] = true_name
                
            if fetched_pron:
                print(f"    -> Filled Pronunciation: {fetched_pron}")
                df.loc[idx, 'Pronunciation_Text'] = fetched_pron
            elif df.loc[idx, 'Pronunciation_Text'] == "":
                print(f"    -> No matching pronunciation found on page.")
                
            time.sleep(random.uniform(0.4, 0.8))
            
            if counter % 10 == 0:
                df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
                print("  [PROGRESS SAVE] Saved progress to disk.")
                
    finally:
        driver.quit()
        
    # Final check: Clean up any trailing structural artifacts globally just in case
    print("\nRunning final dataset sanity cleans...")
    df['Name'] = df['Name'].astype(str).str.replace(r'[- ]*\d+$', '', regex=True)
    df['Name'] = df['Name'].str.strip("- ")
    
    # Deduplicate rows now that corrected names create identical language pairs
    print("Performing final deduplication...")
    initial_count = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"  Removed {initial_count - len(df)} duplicate rows generated by the fixes.")
    
    df['Pronunciation_Text'] = df['Pronunciation_Text'].replace("", np.nan)
    df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"\nAll operations complete! Cleaned dataset saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    clean_and_repair_dataset()