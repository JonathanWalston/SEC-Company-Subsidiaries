import pandas as pd
import csv
import requests
from requests import Session
from bs4 import BeautifulSoup
import re
import time
import logging


# Configure logging
logging.basicConfig(filename='subsidiaries_scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


# Step 1: Read the Excel file and filter companies
df = pd.read_excel('export_05222023101206.xlsx')
filtered_companies = df[df['EXCHANGE NAME'].isin(['NEW YORK STOCK EXCHANGE', 'NASDAQ', 'NYSE', 'NASDAQ OMX'])]


# Step 2: Load the Ticker-CIK mapping
ticker_cik_dict = {}
with open('ticker.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        try:
            ticker, cik = line.strip().split('\t')
            ticker_cik_dict[ticker.lower()] = cik  # Convert ticker to lowercase
        except ValueError:
            print(f"Skipping malformed line: {line.strip()}")

# Step 3: Create a CIK list to fetch
cik_list = []
for ticker in filtered_companies['TICKER SYMBOL']:
    cik = ticker_cik_dict.get(ticker.lower())  # Convert ticker to lowercase
    if cik:
        cik_list.append(cik)


# Step 4: Fetch subsidiaries
def fetch_subsidiaries(cik):
    session = requests.Session()
    headers = {'User-Agent': 'IndianaStateUniversity jwalston@sycamores.indstate.edu',
           'Accept-Encoding': 'gzip, deflate',
           'Host': 'www.sec.gov'}
    base_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/"

    time.sleep(0.2)  # Introduce a delay to respect rate-limiting

    try:
        response = session.get(base_url, headers=headers)
        if response.status_code == 403:
            logging.warning(f"Failed to fetch the base URL for CIK {cik}: 403")
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        logging.error(f"An error occurred while fetching base URL for CIK {cik}: {e}")
        return None

    for link in soup.find_all('a', href=True):
        href = link['href']
        if f"/Archives/edgar/data/{cik}/" in href:
            subdirectory_link = 'https://www.sec.gov' + href
            time.sleep(0.2)  # Introduce a delay to respect rate-limiting
            subdir_response = session.get(subdirectory_link, headers=headers)
            subdir_soup = BeautifulSoup(subdir_response.text, 'html.parser')

            for subdir_link in subdir_soup.find_all('a'):
                sub_href = subdir_link.get('href')
                if sub_href and re.search(r'ex21[^.]*\.htm[l]*', sub_href.lower()):  # Updated regular expression
                    subsidiaries_url = f"https://www.sec.gov{sub_href}"
                    time.sleep(0.2)  # Introduce a delay to respect rate-limiting
                    print(f"Found subsidiaries file: {subsidiaries_url}")

                    # Download the document content
                    subsidiaries_content = session.get(subsidiaries_url, headers=headers).text

                    # Check if the text contains "subsidiary" or "subsidiaries"
                    if "subsidiary" not in subsidiaries_content.lower() and "subsidiaries" not in subsidiaries_content.lower():
                        logging.info(
                            f"The file at {subsidiaries_url} does not seem to contain a list of subsidiaries for CIK {cik}. Skipping.")
                        continue

                    # Save the content to a text file
                    with open(f"{cik}_subsidiaries.txt", "w", encoding='utf-8') as f:
                        f.write(subsidiaries_content)

                    print(f"Saved subsidiaries content to {cik}_subsidiaries.txt")

                    # Initialize an empty list to store all subsidiary names
                    all_subsidiaries = []

                    # List of texts to exclude
                    exclude_texts = ["Name of Subsidiary", "", "NAME", "U.S. Subsidiaries:",
                                     "International Subsidiaries:"]

                    # Parse subsidiaries content to extract tables
                    soup = BeautifulSoup(subsidiaries_content, 'html.parser')
                    tables = soup.find_all('table')

                    for table in tables:
                        for row in table.find_all('tr'):
                            cells = row.find_all(['td', 'th'])
                            if cells:
                                subsidiary_name = cells[0].get_text().strip()

                                # Skip header row, empty names, and other unwanted texts
                                if subsidiary_name not in exclude_texts:
                                    all_subsidiaries.append([subsidiary_name])

                    # Write all_subsidiaries to a CSV file
                    with open(f"{cik}_subsidiaries.csv", 'w', newline='', encoding='utf-8') as csvfile:
                        csvwriter = csv.writer(csvfile)
                        csvwriter.writerows(all_subsidiaries)

                    print(f"Saved subsidiaries information to {cik}_subsidiaries.csv")
                    logging.info(f"Saved subsidiaries information to {cik}_subsidiaries.csv")
                    return subsidiaries_url

    print(f"No subsidiaries file found for CIK {cik}")
    return None


if __name__ == "__main__":
    # Use cik_list to fetch subsidiaries
    for cik in cik_list:
        subsidiaries_url = fetch_subsidiaries(cik)
        if subsidiaries_url:
            print(f"Subsidiaries URL for CIK {cik}: {subsidiaries_url}")
        else:
            print(f"No subsidiaries found for CIK {cik}")

    logging.info("Finished processing all CIKs.")
