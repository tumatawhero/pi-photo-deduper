from flask import Flask, render_template, jsonify, request, send_file
import json
import os
import shutil
from pathlib import Path

app = Flask(__name__)

DUPLICATES_FILE = '/home/toby/pi-photo-deduper/duplicates.json'
TRASH_FOLDER = '/home/toby/pi-photo-deduper/trash'
DECISIONS_FILE = '/home/toby/pi-photo-deduper/decisions.json'

os.makedirs(TRASH_FOLDER, exist_ok=True)

def load_duplicates():
    with open(DUPLICATES_FILE) as f:
        return json.load(f)

def load_decisions():
    if os.path.exists(DECISIONS_FILE):
        with open(DECISIONS_FILE) as f:
            return json.load(f)
    return {}

def save_decisions(decisions):
    with open(DECISIONS_FILE, 'w') as f:
        json.dump(decisions, f, indent=2)

def get_pairs():
    dupes = load_duplicates()
    decisions = load_decisions()
    seen = set()
    pairs = []
    for source, matches in dupes.items():
        for match in matches:
            key = tuple(sorted([source, match]))
            if key not in seen:
                seen.add(key)
                status = decisions.get(str(key), 'pending')
                pairs.append({
                    'id': str(key),
                    'img1': source,
                    'img2': match,
                    'status': status
                })
    return pairs

@app.route('/')
def index():
    pairs = get_pairs()
    total = len(pairs)
    pending = sum(1 for p in pairs if p['status'] == 'pending')
    approved = sum(1 for p in pairs if p['status'] == 'approved')
    skipped = sum(1 for p in pairs if p['status'] == 'skipped')
    return render_template('index.html', pairs=pairs, total=total, 
                         pending=pending, approved=approved, skipped=skipped)

@app.route('/image')
def serve_image():
    path = request.args.get('path')
    if path and os.path.exists(path):
        return send_file(path)
    return '', 404

@app.route('/decide', methods=['POST'])
def decide():
    data = request.json
    decisions = load_decisions()
    decisions[data['id']] = data['action']
    save_decisions(decisions)
    return jsonify({'ok': True})

@app.route('/delete', methods=['POST'])
def delete():
    data = request.json
    path = data['path']
    if os.path.exists(path):
        dest = os.path.join(TRASH_FOLDER, os.path.basename(path))
        shutil.move(path, dest)
        return jsonify({'ok': True, 'moved_to': dest})
    return jsonify({'ok': False, 'error': 'File not found'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
