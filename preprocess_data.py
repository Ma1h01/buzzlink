import os
import csv
import json

class Preprocessor:
    def __init__(self, raw_data_path: str, processed_data_path: str):
        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path

    def convert_to_json(self):
        """Convert all raw user profile data CSV files to one raw JSON file"""
        profile_data = []
        for file in os.listdir(self.raw_data_path):
            if file.endswith('.csv'):
                with open(os.path.join(self.raw_data_path, file), 'r') as f:
                    reader = csv.reader(f)
                    next(reader)
                    for row in reader:
                        data = json.loads(row[1])
                        profile_data.append(data)
        profile_data = self.concate_data(profile_data, 'old_profile_data_no_ai.json')
        with open(os.path.join(self.raw_data_path, 'profile_data.json'), 'w') as f:
            json.dump(profile_data, f)
        print(f"Converted {len(profile_data)} profiles to JSON")

    def concate_data(self, profile_data: list[dict], old_profile_data_file_name: str):
        """Concatenate profile data scraped withour AI with profile data scraped with AI into one JSON file"""
        old_profile_data = json.load(open(os.path.join(self.raw_data_path, old_profile_data_file_name), 'r'))
        profile_data += old_profile_data
        return profile_data

if __name__ == '__main__':
    preprocessor = Preprocessor('data/raw-profile-data', 'data/clean-profile-data')
    preprocessor.convert_to_json()
