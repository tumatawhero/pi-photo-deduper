from imagededup.methods import PHash
from pathlib import Path
import json
import shutil
import tempfile
import os

PHOTO_PATH = '/mnt/nas/tumatawhero/Photos/PhotoLibrary'
OUTPUT_FILE = '/home/toby/pi-photo-deduper/duplicates.json'

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic'}

def scan_duplicates():
    print(f"Scanning {PHOTO_PATH} recursively...")
    
    image_files = [f for f in Path(PHOTO_PATH).rglob('*') 
                   if f.suffix.lower() in IMAGE_EXTENSIONS]
    print(f"Found {len(image_files)} images (videos excluded)")
    
    # Build encoding map manually per file
    phasher = PHash()
    encodings = {}
    for i, f in enumerate(image_files):
        try:
            encoding = phasher.encode_image(image_file=str(f))
            if encoding is not None:
                encodings[str(f)] = encoding
        except Exception:
            pass
        if i % 100 == 0:
            print(f"Processed {i}/{len(image_files)}...")
    
    print(f"Encoded {len(encodings)} images, finding duplicates...")
    duplicates = phasher.find_duplicates(encoding_map=encodings, max_distance_threshold=10)
    dupes = {k: v for k, v in duplicates.items() if len(v) > 0}
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(dupes, f, indent=2)
    
    print(f"Found {len(dupes)} images with duplicates")
    print(f"Results saved to {OUTPUT_FILE}")

if __name__ == '__main__':
    scan_duplicates()
