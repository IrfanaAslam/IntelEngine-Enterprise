import json
from pathlib import Path

def check_quality(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    issues = []
    for entry in data:
        if not entry.get('text') and not entry.get('data_preview'):
            issues.append(f"Warning: No content found in {entry['metadata']['source_file']}")
            
    if not issues:
        print("💎 Data quality looks great!")
    else:
        for issue in issues:
            print(issue)

if __name__ == "__main__":
    check_quality("data/processed/extracted_data.json")