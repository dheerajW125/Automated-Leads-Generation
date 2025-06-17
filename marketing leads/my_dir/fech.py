import pandas as pd
import json
import os
from apollo_client import ApolloClient

# === Initialize Apollo Client ===
client = ApolloClient()

if not client.check_auth():
    client.login("your@email.com", "password")
    

# === Search Companies ===
technologies = []
org_tags = ["webscraping", "Data Aggregation"]
companies_data = client.search_companies_by_filters(technologies, org_tags)

# === Define Output Directories ===
new_dir = r"C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\new_companies"
filtered_dir = r"C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\filtered_companies"
os.makedirs(new_dir, exist_ok=True)
os.makedirs(filtered_dir, exist_ok=True)

# === Get next available file number based on new_companies_*.json ===
existing_files = [f for f in os.listdir(new_dir) if f.startswith("new_companies_") and f.endswith(".json")]
file_numbers = [int(f.split("_")[-1].split(".")[0]) for f in existing_files if f.split("_")[-1].split(".")[0].isdigit()]
next_number = max(file_numbers, default=0) + 1

# === Output file paths ===
new_file_path = os.path.join(new_dir, f"new_companies_{next_number}.json")
filtered_file_path = os.path.join(filtered_dir, f"filtered_companies_{next_number}.json")

# === Save raw (unfiltered) data ===
with open(new_file_path, "w") as f:
    json.dump(companies_data, f, indent=4)

print(f"Saved raw companies data to: {new_file_path}")

# === Load Website URLs from Excel & CSV files ===
excel_files = [
    r"C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\fech_new_output1.csv",
    r"C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\fech_new_output111.csv",
    r"C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\filtered_data (1).xlsx",
    r"C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\final_data4 1.xlsx"
]

website_column_name = "Website"
existing_websites = set()

# Load CSVs
for path in excel_files[:2]:
    df = pd.read_csv(path)
    if website_column_name in df.columns:
        existing_websites.update(df[website_column_name].dropna().tolist())

# Load Excel files
for path in excel_files[2:]:
    df = pd.read_excel(path)
    if website_column_name in df.columns:
        existing_websites.update(df[website_column_name].dropna().tolist())

print(f"Loaded {len(existing_websites)} websites from Excel/CSV files.")

# === Filter out companies with matching websites ===
filtered_data = []
removed_count = 0
for company in companies_data:
    if "website_url" in company and company["website_url"] in existing_websites:
        removed_count += 1
    else:
        filtered_data.append(company)

# === Save filtered data ===
with open(filtered_file_path, "w") as f:
    json.dump(filtered_data, f, indent=4)

print(f"Removed {removed_count} duplicate companies based on website URL.")
print(f"Saved filtered companies to: {filtered_file_path}")
