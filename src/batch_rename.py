from pathlib import Path
from datetime import datetime

def batch_rename(processed_data, input_dir="data/temp", output_dir="data/renamed", pattern="{name}_{date}_{sentiment}"):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    for d in processed_data:
        meta = d['metadata']
        sentiment = d['sentiment'].get('label', 'NEUTRAL').upper()
        date_str = datetime.now().strftime("%Y-%m-%d")
        name = meta['filename'].split('.')[0]
        new_name = pattern.format(name=name, date=date_str, sentiment=sentiment, ext=meta['detected_format'].lower())
        new_name = f"{new_name}.{meta['detected_format'].lower()}"
        old_path = input_dir / meta['filename']
        new_path = output_dir / new_name
        try:
            old_path.rename(new_path)
        except Exception as e:
            print(f"Error renaming {meta['filename']}: {e}")
