# test-ver5.py
# Scrape ALL English names from BehindTheName
# Extract:
# - Name
# - IPA
# - Pronunciation Text
# - Language
# - URL
#
# IMPROVEMENTS over ver4:
# - Headless Chrome mode to reduce memory usage
# - WebDriverWait instead of time.sleep for reliability
# - Retry mechanism for tab crashes
# - Driver restart on repeated failures
# - Progress auto-save every 50 names (crash-safe)
# - Resume from checkpoint if interrupted
# - Randomized delays to avoid rate limiting

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import time
import re
import os
import random

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL          = "https://www.behindthename.com/names/usage/english"
TOTAL_PAGES       = 16
DEFAULT_LANGUAGE  = "English"
OUTPUT_CSV        = "english_names_dataset.csv"
CHECKPOINT_CSV    = "english_names_checkpoint.csv"
VISITED_LOG       = "visited_urls.txt"
AUTOSAVE_EVERY    = 50       # Save progress every N names
MAX_RETRIES       = 3        # Retry attempts per URL
PAGE_TIMEOUT      = 15       # Seconds to wait for page load
DELAY_MIN = 0.3
DELAY_MAX = 0.8     # Max seconds between requests

# -----------------------------
# DRIVER FACTORY

# -----------------------------
def create_driver():
    """Create a fresh headless Chrome driver."""

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")           # Headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,900")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # Skip images
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    driver.set_page_load_timeout(PAGE_TIMEOUT)

    return driver


# -----------------------------
# LOAD CHECKPOINT
# -----------------------------
def load_checkpoint():
    """Load already-visited URLs and saved dataset rows."""

    visited = set()
    dataset = []

    if os.path.exists(VISITED_LOG):
        with open(VISITED_LOG, "r") as f:
            for line in f:
                visited.add(line.strip())
        print(f"[CHECKPOINT] Resuming — {len(visited)} URLs already visited.")

    if os.path.exists(CHECKPOINT_CSV):
        df = pd.read_csv(CHECKPOINT_CSV)
        dataset = df.to_dict("records")
        print(f"[CHECKPOINT] Loaded {len(dataset)} existing rows.")

    return visited, dataset


# -----------------------------
# SAVE CHECKPOINT
# -----------------------------
def save_checkpoint(dataset, visited):
    """Auto-save progress to disk."""

    pd.DataFrame(dataset).to_csv(CHECKPOINT_CSV, index=False)

    with open(VISITED_LOG, "w") as f:
        for url in visited:
            f.write(url + "\n")

    print(f"  [AUTOSAVE] {len(dataset)} rows saved to checkpoint.")


# -----------------------------
# GET ALL NAME URLS
# -----------------------------
def get_all_name_urls(driver):
    """Scrape all name page URLs from the listing pages."""

    all_urls = []
    seen     = set()

    for page in range(1, TOTAL_PAGES + 1):

        url = BASE_URL if page == 1 else f"{BASE_URL}/{page}"

        print(f"\n[PAGE {page}] {url}")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                driver.get(url)
                WebDriverWait(driver, PAGE_TIMEOUT).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/name/')]"))
                )
                break
            except (WebDriverException, TimeoutException) as e:
                print(f"  [RETRY {attempt}/{MAX_RETRIES}] Page load failed: {e}")
                time.sleep(3)
        else:
            print(f"  [SKIP] Could not load page {page} after {MAX_RETRIES} attempts.")
            continue

        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/name/')]")

        for link in links:
            href = link.get_attribute("href")
            if (
                href
                and "/name/" in href
                and "surnames" not in href
                and href not in seen
            ):
                seen.add(href)
                all_urls.append(href)

        print(f"  Collected so far: {len(all_urls)} URLs")
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    return all_urls



# -----------------------------
# IPA EXTRACTION (REPLACED)
# -----------------------------
def extract_ipa_entries(ipa_line):
    """Extract IPA transcriptions and their language labels."""
    if not ipa_line:
        return []

    entries = []
    # Strip out "Pronounced" prefixes and key metadata safely
    clean_line = re.sub(r"^Pronounced\s*", "", ipa_line.strip())
    clean_line = clean_line.split("[key")[0].strip()
    
    # Matches /.../ and captures trailing language brackets
    pattern = r"(/[^\/]+/)\s*(?:\(([^)]+)\))?"
    matches = re.findall(pattern, clean_line)

    for ipa, languages_raw in matches:
        ipa = ipa.strip()
        languages_raw = languages_raw.strip()
        
        # If the bracket lists multiple languages like (Italian, Polish, German)
        if languages_raw and "," in languages_raw:
            individual_languages = [lang.strip() for lang in languages_raw.split(",")]
            for lang in individual_languages:
                if lang:
                    entries.append((ipa, lang))
        else:
            lang = languages_raw if languages_raw else DEFAULT_LANGUAGE
            entries.append((ipa, lang))

    return entries
# -----------------------------
# GET PRONOUNCED LINE
# -----------------------------
def get_pronounced_line(driver):
    body_text = driver.find_element(By.TAG_NAME, "body").text

    for line in body_text.split("\n"):
        if "Pronounced" in line:
            return line.strip()

    return ""
# -----------------------------
# PRONUNCIATION EXTRACTION (FIXED FOR MULTIPLE LANGUAGES)
# -----------------------------
def extract_pronunciation_entries(pron_line):
    """Extract simplified pronunciation strings and their language labels."""
    if not pron_line:
        return []

    entries = []
    # Strip out "Pronounced" prefixes cleanly regardless of layout spacing
    clean_line = re.sub(r"^Pronounced\s*", "", pron_line.strip())
    clean_line = clean_line.split("[key")[0].strip()
    
    # Captures text followed by a language parenthesis
    pattern = r"([^\s()][^()]*?)\s*(?:\(([^()]+)\))"
    matches = re.findall(pattern, clean_line)
    
    # Fallback if no language brackets exist on the line
    if not matches and clean_line:
        if clean_line.lower() not in {"key", "ipa", "pronounced"}:
            entries.append((clean_line, DEFAULT_LANGUAGE))
        return entries

    for pronunciation, languages_raw in matches:
        # Strip trailing commas or stray punctuation left from split boundaries
        pronunciation = pronunciation.lstrip(', ').strip()
        languages_raw = languages_raw.strip()
        
        if not pronunciation or pronunciation.lower() in {"key", "ipa", "pronounced"}:
            continue
            
        # Split shared multi-language brackets up into individual rows
        if languages_raw and "," in languages_raw:
            individual_languages = [lang.strip() for lang in languages_raw.split(",")]
            for lang in individual_languages:
                if lang:
                    entries.append((pronunciation, lang))
        else:
            lang = languages_raw if languages_raw else DEFAULT_LANGUAGE
            entries.append((pronunciation, lang))
            
    return entries
# -----------------------------
# SCRAPE SINGLE NAME PAGE
# -----------------------------
def scrape_name_page(driver, url):
    """
    Scrape IPA and pronunciation data from a single name page.
    Returns a list of row dicts.
    Raises WebDriverException on unrecoverable tab crashes.
    """

    name = url.split("/")[-1].capitalize()

    driver.get(url)

    WebDriverWait(driver, PAGE_TIMEOUT).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

# -----------------------------
# FIRST READ
# -----------------------------
    line1 = get_pronounced_line(driver)

    print("  BEFORE:", line1)

    # --- Toggle pronunciation view ---
    try:
        toggle = driver.find_element(
            By.XPATH,
            "//a[contains(text(),'IPA') or contains(text(),'simplify')]"
        )

        print("FOUND TOGGLE:", toggle.text)

        toggle.click()

        time.sleep(2)

        print("CURRENT URL:", driver.current_url)

        body_text = driver.find_element(By.TAG_NAME, "body").text

        if "ˈ" in body_text:
            print("IPA symbols found in page")
        else:
            print("No IPA symbols found")

    except Exception as e:
        print("TOGGLE ERROR:", e)

# -----------------------------
# SECOND READ
# -----------------------------
    line2 = get_pronounced_line(driver)

    print("BEFORE:")
    print(line1)

    print("AFTER:")
    print(line2)

    if line1 == line2:
        print("TOGGLE FAILED")

    print("  AFTER :", line2)

    ipa_line = ""
    pron_line = ""

    for line in [line1, line2]:

        if "/" in line:
            ipa_line = line

        else:
            pron_line = line

    # --- Debug output ---
    print(f"  IPA  : {ipa_line or '(none)'}")
    print(f"  PRON : {pron_line or '(none)'}")

    # --- Extract entries ---
    ipa_entries  = extract_ipa_entries(ipa_line)
    pron_entries = extract_pronunciation_entries(pron_line)

    print(f"  IPA entries  : {ipa_entries}")
    print(f"  Pron entries : {pron_entries}")

    # --- Build rows ---
# --- Build rows matching by Language ---
    languages = []
    for _, lang in ipa_entries:
        if lang not in languages:
            languages.append(lang)
    for _, lang in pron_entries:
        if lang not in languages:
            languages.append(lang)
            
    if not languages:
        languages = [DEFAULT_LANGUAGE]

    rows = []
    for lang in languages:
        # Filter entries matching ONLY this specific language block
        lang_ipas = [v for v, l in ipa_entries if l == lang]
        lang_prons = [v for v, l in pron_entries if l == lang]
        
        # Max entries for this language (handles multiple variants under one language)
        lang_max_len = max(len(lang_ipas), len(lang_prons))
        for i in range(lang_max_len):
            ipa_value = lang_ipas[i] if i < len(lang_ipas) else ""
            pron_value = lang_prons[i] if i < len(lang_prons) else ""
            
            rows.append({
                "Name":               name,
                "Language":           lang,
                "IPA":                ipa_value,
                "Pronunciation_Text": pron_value,
                "URL":                url,
            })

    return rows


# -----------------------------
# MAIN
# -----------------------------
def main():

    # --- Load checkpoint ---
    visited, dataset = load_checkpoint()

    # --- Start driver ---
    driver = create_driver()

    try:
        # --- Collect URLs ---
        all_urls = get_all_name_urls(driver)

        print("\n============================")
        print(f"TOTAL URLS FOUND : {len(all_urls)}")
        print(f"ALREADY VISITED  : {len(visited)}")
        print(f"REMAINING        : {len([u for u in all_urls if u not in visited])}")
        print("============================\n")

        # --- Main scraping loop ---
        consecutive_crashes = 0

        for index, url in enumerate(all_urls):

            if url in visited:
                print(f"[{index+1}/{len(all_urls)}] SKIP (already visited): {url}")
                continue

            print(f"\n[{index+1}/{len(all_urls)}] {url}")

            success = False

            for attempt in range(1, MAX_RETRIES + 1):

                # Restart driver after 3 consecutive crashes
                if consecutive_crashes >= 3:
                    print("  [DRIVER RESTART] Too many consecutive crashes — restarting Chrome...")
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    driver = create_driver()
                    consecutive_crashes = 0
                    time.sleep(3)

                try:
                    rows = scrape_name_page(driver, url)
                    dataset.extend(rows)
                    visited.add(url)
                    consecutive_crashes = 0
                    success = True
                    break

                except (WebDriverException, TimeoutException) as e:
                    consecutive_crashes += 1
                    print(f"  [RETRY {attempt}/{MAX_RETRIES}] Error: {e}")
                    time.sleep(2 * attempt)  # Back-off delay

                except Exception as e:
                    print(f"  [ERROR] Unexpected error: {e}")
                    break

            if not success:
                print(f"  [SKIP] Failed after {MAX_RETRIES} retries: {url}")

            # --- Auto-save checkpoint ---
            if len(visited) % AUTOSAVE_EVERY == 0:
                save_checkpoint(dataset, visited)

            # --- Polite delay between requests ---
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    finally:
        # Always save and quit cleanly
        save_checkpoint(dataset, visited)
        driver.quit()

    # --- Final CSV output ---
    df = pd.DataFrame(dataset)

    print("\n============================")
    print("FINAL DATASET")
    print("============================")
    print(df.head(10))
    print(f"\nTotal rows : {len(df)}")

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nDataset saved to: {OUTPUT_CSV}")

    # --- Cleanup checkpoint files on success ---
    if os.path.exists(CHECKPOINT_CSV):
        os.remove(CHECKPOINT_CSV)
    if os.path.exists(VISITED_LOG):
        os.remove(VISITED_LOG)

    print("Checkpoint files cleaned up. Done!")


if __name__ == "__main__":
    main()
