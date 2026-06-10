from imagededup.methods import PHash
from pathlib import Path
import json

PHOTO_PATH = '/mnt/nas/tumatawhero/Photos'
OUTPUT_FILE = '/home/toby/pi-photo-deduper/duplicates.json'

def scan_duplicates():
    print(f"Scanning {PHOTO_PATH}...")
    phasher = PHash()
    encodings = phasher.encode_images(image_dir=PHOTO_PATH)
    duplicates = phasher.find_duplicates(encoding_map=encodings, max_distance_threshold=10)
    
    # Filter to only entries that have duplicates
    dupes = {k: v for k, v in duplicates.items() if len(v) > 0}
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(dupes, f, indent=2)
    
    print(f"Found {len(dupes)} images with duplicates")
    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    scan_duplicates()
