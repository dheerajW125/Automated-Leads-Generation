import json
import os
import random
import time
from apollo_client import ApolloClient

# === Apollo Login ===
client = ApolloClient()
if not client.check_auth():
    client.login("tushar@reluconsultancy.in", "Tushar@relu1234")
print("✅ Authentication check:", client.check_auth())

# === ✅ USER INPUT: Define Filtered File to Process ===
# Pass the full path to the filtered_companies_X.json file here:
filtered_file = r"C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\filtered_companies\filtered_companies_30.json"

# === Automatically extract index from filename ===
file_index = os.path.basename(filtered_file).split("_")[-1].replace(".json", "")

# === Output Directory for People Data ===
people_dir = r"C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\people_data"
os.makedirs(people_dir, exist_ok=True)

print(f"📁 Re-processing file: {filtered_file}")

# === Load Filtered Companies JSON File ===
with open(filtered_file, 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

# === ✅ Extract Unique Organization IDs from 'accounts'
organisation_ids = set()
if isinstance(data, list):
    for entry in data:
        if isinstance(entry, dict) and 'accounts' in entry:
            for acc in entry['accounts']:
                org_id = acc.get('organization_id')
                if org_id:
                    organisation_ids.add(org_id)

organisation_ids = sorted(organisation_ids)
print(f"🔍 Found {len(organisation_ids)} unique organization IDs.")

# === Search People ===
people = []
for index, organisation in enumerate(organisation_ids[:700]):
    try:
        peoplelist = client.search_people(organization_id=[organisation])
        if not peoplelist:
            print(f"⚠️  No people found for organization: {organisation}")
        people.extend(peoplelist)

        print(f"✅ {index + 1}/{len(organisation_ids)} processed. People collected: {len(people)}")
        time.sleep(random.randint(20, 35))

    except Exception as e:
        print(f"❌ Error fetching people for {organisation}: {e}")

# === Save People Data ===
output_file = os.path.join(people_dir, f"people_data_{file_index}.json")
people_data = [json.loads(person.model_dump_json()) for person in people if person]

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(people_data, f, indent=4)

print(f"✅ People data saved to: {output_file}")
