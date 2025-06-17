import os
import pandas as pd

# 🔧 Folder containing CSV files
input_folder = r'C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\output_excel'
output_file = r'C:\dheeraj_work\marketing_leads\marketing_leads\my_dir\merged_csv\merged_output.csv'

# 📂 List all CSV files in the folder
csv_files = [file for file in os.listdir(input_folder) if file.endswith('.csv')]

# 📊 Read and combine CSVs
merged_df = pd.DataFrame()
for file in csv_files:
    file_path = os.path.join(input_folder, file)
    df = pd.read_csv(file_path)
    merged_df = pd.concat([merged_df, df], ignore_index=True)

# 💾 Save merged CSV
merged_df.to_csv(output_file, index=False)
print(f"Merged {len(csv_files)} files into: {output_file}")
