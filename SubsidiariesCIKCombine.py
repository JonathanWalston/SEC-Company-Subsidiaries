import os
import csv
import pandas as pd

# Read the ticker.txt into a dictionary for quick lookup
ticker_dict = {}
with open('ticker.txt', 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        ticker, cik = row
        ticker_dict[cik] = ticker

# Initialize an empty list to hold the rows for the master CSV
master_list = []

# Iterate through each file in the directory
for filename in os.listdir('.'):
    if filename.endswith('_subsidiaries.csv'):
        # Extract CIK number from the filename
        cik = filename.split('_')[0]

        # Fetch the ticker using the CIK
        ticker = ticker_dict.get(cik, 'Unknown')

        try:
            # Read the csv file into a pandas DataFrame
            df = pd.read_csv(filename, encoding='ISO-8859-1', error_bad_lines=False)

            # Iterate through each subsidiary in the file
            for index, row in df.iterrows():
                subsidiary = row[0]

                # Append a new row to the master list
                master_list.append([cik, ticker, subsidiary])
        except Exception as e:
            print(f"An error occurred while processing {filename}: {e}")

# Write the master list to a master CSV file
with open('master_list.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    # Write the header
    writer.writerow(['CIK#', 'Ticker', 'Subsidiaries'])

    # Write the data rows
    writer.writerows(master_list)

print("Master CSV has been created as master_list.csv")
