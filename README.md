# SEC-Company-Subsidiaries
SEC-Company-Subsidiaries is a Python-based project that scrapes and processes data related to company subsidiaries from the SEC.

## Status

The script is currently optimized and tested for Windows. Other platforms have not been tested.

## Features

- Configures logging for the scraping process.
- Reads and processes an Excel file to filter companies.
- Loads Ticker-CIK mapping from a provided text file.
- Generates a CIK list based on the Ticker-CIK mapping.

## Requirements

**Libraries:**
- pandas
- csv
- requests
- BeautifulSoup (from bs4)
- re
- time
- logging

## Quickstart

1. Clone or download the repository: `git clone https://github.com/JonathanWalston/SEC-Company-Subsidiaries.git`
2. Install the required libraries using pip: pip install pandas requests beautifulsoup4
3. Open the project in PyCharm and ensure you're on a Windows platform.
4. Change name and information under headers
   def fetch_subsidiaries(cik):
    session = requests.Session()
    headers = {'User-Agent': 'Entity Email',
           'Accept-Encoding': 'gzip, deflate',
           'Host': 'www.sec.gov'}
6. Run the `Scrape.py` script.

## Note

The project was created with the assistance of generative AI tools for debugging and troubleshooting purposes.

## License

This project is open-source and free to use under the MIT license. Please ensure you follow the terms and conditions laid out in the LICENSE file.


