import pickle
import random
import time
import json
import logging
from datetime import datetime
from apollo_client import ApolloClient

# Initialize Apollo Client
client = ApolloClient()

# Authenticate if needed
if not client.check_auth():
    # client.login("skhadke999@gmail.com", "hM5vy037ryR1")
    # client.login("dummymail17751@gmail.com", "xE38qO3Xn1LC")
    client.login("shreyaskhadke@reluconsultancy.in", "Pr3mLE8ZL3S8")
    # client.login("lee@sponsorscoutt.com", "j@&n.s@Qu.9AepW")
    # client.login("tushar@reluconsultancy.in", "Tushar@relu1234")
    # client.login("aashishguptaak470@gmail.com", "Relutest@520")
print("Authentication check:", client.check_auth())

# Load people data
input_file = r'C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\people_data\people_data_13.json'
output_file = r"C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\output_emails\new_emails_13.json"

with open(input_file, 'r', encoding='utf-8') as f:
    people = json.load(f)

# Load existing enriched data to append results
try:
    with open(output_file, 'r') as efile:
        enriched_data = json.load(efile)
except (FileNotFoundError, json.JSONDecodeError):
    enriched_data = []

# Process each person and append immediately
for person in people:
    try:
        person_obj = client.access_email(person['id'])
        if person_obj:
            person['email'] = person_obj.email
        else:
            person['email'] = None  # Mark as missing if no email found
        
        enriched_data.append(person)
        
        # Save to output file after processing each person
        with open(output_file, 'w') as e_file:
            json.dump(enriched_data, e_file, indent=4)
        
        sleep_time = random.randint(8, 9)
        print(f"Processed: {person['first_name']} {person['last_name']} - Sleeping for {sleep_time}s")
        time.sleep(sleep_time)
    except Exception as e:
        print(f"Error processing {person.get('first_name', 'Unknown')} {person.get('last_name', 'Unknown')}: {e}")

print("Processing complete. Data saved to:", output_file)
