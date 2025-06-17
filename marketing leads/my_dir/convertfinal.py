import json
import csv

def flatten_dict(d, parent_key='', sep='_'):
    """Recursively flattens a nested dictionary."""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            # Convert lists to a comma separated string
            items[new_key] = ','.join(str(item) for item in v)
        else:
            items[new_key] = v
    return items

def json_to_csv(json_filename, csv_filename):
    # Load the JSON data
    with open(json_filename, 'r') as f:
        data = json.load(f)

    # Flatten each JSON record
    flattened_data = [flatten_dict(record) for record in data]

    # Determine CSV header from all keys (union of keys from each record)
    header = sorted({key for record in flattened_data for key in record.keys()})

    # Write the CSV file
    with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for record in flattened_data:
            writer.writerow(record)

if __name__ == '__main__':
    # Replace 'data.json' with your JSON file name and 'output.csv' with your desired CSV output file.
    json_to_csv(r'C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\merged_new_13.json', 'fech_new_output113.csv')
