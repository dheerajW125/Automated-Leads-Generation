import json

# Define file paths
companies_file_path = r'C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\filtered_companies\filtered_companies_13.json'
people_file_path = r'C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\output_emails\new_emails_13.json'
output_file_path = r'C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\merged_new_13.json'

with open(companies_file_path, 'r', encoding='utf-8') as comp_file:
    data = json.load(comp_file)

# Extract all organizations into a list
all_organizations = []
if isinstance(data, list):  # Ensure the data is a list
    for entry in data:
        if isinstance(entry, dict) and 'organizations' in entry:
            all_organizations.extend(entry['organizations'])  # Append all organization details
else:
    raise ValueError("Invalid JSON structure: Expected a list of dictionaries.")

# Load people data
with open(people_file_path, 'r') as people_file:
    people = json.load(people_file)

# ✅ Create a dictionary mapping from company ID to company details
company_dict = {org["id"]: org for org in all_organizations}  # Ensure it stores full org data

# ✅ Merge company data into each person record based on organization_id
merged_data = []
for person in people:
    org_id = person.get("organization_id")  # Ensure this key exists
    person["company_data"] = company_dict.get(org_id, None)  # Add company details if found
    merged_data.append(person)

# ✅ Write the merged data to an output JSON file
with open(output_file_path, 'w') as output_file:
    json.dump(merged_data, output_file, indent=2)

print("✅ Merged data written to:", output_file_path)