import json
import os
from pathlib import Path

def load_fingerprints(db_path):
    db = {}
    path = Path(db_path)
    if not path.exists():
        print(f"No existing database found at '{db_path}'")
        return db
    
    with open(db_path, "r") as f:
        db = json.load(f) 
        db = {int(k): v for k, v in db.items()} 
        print(f"Loaded {len(db)} fingerprints from '{db_path}'")

    print(f"Database entries {len(db)}.")
    return db



def save_fingerprints(db, db_path):
    if not db:
        print("No fingerprints to save.")
        return
    
    path = Path(db_path)
    print(f"Saving {len(db)} entries to '{path.name}'")
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(db_path, "w") as f:
        f.truncate(0)
        json.dump(db, f, indent=4)