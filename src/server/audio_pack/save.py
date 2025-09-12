import sys, os, json, librosa
from matplotlib import pyplot as plt

from .spectogram import spectogram, find_constellation
from .fingerprint import generate_fingerprints
from .utils import load_fingerprints, save_fingerprints


db_path = "db/fingerprints.json"

cutoff_freq = 5000
n_fft = 4096
hop_length = 1024
fan_value = 15
target_zone = 200
threshold = 90  
n_size = (5, 8)
fixed_sr = 22050  

def save_song(audio, file_name):
    try:
        y, sr = librosa.load(audio, sr=fixed_sr, mono=True)
        y, idx = librosa.effects.trim(y, top_db=40)

        if isinstance(audio, str):
            print(f"Audio file loaded successfully with sample rate: {sr}")
        else:
            print(f"Audio data loaded successfully with sample rate: {sr}")

        S = spectogram(y, sr=sr, hop_length=hop_length, n_fft=n_fft, fmax=cutoff_freq)

        # Find peaks
        peaks = find_constellation(S, threshold, n_size, hop_length=hop_length, sr=sr)
        print(f"Found {len(peaks)} peaks.")

        if not peaks:
            print("Warning: No peaks found. Try lowering the threshold.")
            return

        fingerprints = generate_fingerprints(peaks, fan_value, target_zone)
        print(f"Generated {len(fingerprints)} fingerprints.")

        if not fingerprints:
            print("Warning: No fingerprints generated.")
            return

        # Load existing DB
        db = load_fingerprints(db_path)

        # Store fingerprints consistently
        for h, t in fingerprints:
            db.setdefault(h, []) 
            entry = {"song_id": file_name, "time": int(t)}
            # Check for duplicates
            if entry not in db[h]:
                db[h].append(entry)

        # Save DB
        save_fingerprints(db, db_path)
        print(f"Saved {len(fingerprints)} fingerprints for {file_name}.")
        
    except Exception as e:
        print(f"Error processing {file_name}: {str(e)}")


if __name__ == "__main__":
    audioPath = sys.argv[1] if len(sys.argv) > 1 else r"audio\Gym Class Heroes_ Stereo Hearts.mp3"
    file_name = os.path.basename(audioPath).split(".")[0]
    save_song(audioPath, file_name)
