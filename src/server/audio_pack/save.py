import librosa
from .spectogram import spectogram, find_constellation 
from .fingerprint import generate_fingerprints
from .utils import load_fingerprints, save_fingerprints
import sys, os


db_path = "db/fingerprints.json"

cutoff_freq = 5000
n_fft = 4096
hop_length = 1024
fan_value = 15
target_zone = 200
threshold = 90
n_size = (5, 8)


def save_song(audio, file_name):
    y, sr = librosa.load(audio, sr=None)
    y, idx = librosa.effects.trim(y, top_db=40) 

    if isinstance(audio, str): 
        print(f"Audio file loaded successfully with sample rate: {sr}")
    else:
        print(f"Audio data loaded successfully with sample rate: {sr}")

    S = spectogram(y, sr=sr, hop_length=hop_length, n_fft=n_fft, fmax=cutoff_freq)

    peaks = find_constellation(S, threshold, n_size)
    print(f"Found {len(peaks)} peaks.")

    fingerprints = generate_fingerprints(peaks, fan_value, target_zone)
    print(f"Generated {len(fingerprints)} fingerprints.")   
    
    song_id = file_name
    db = load_fingerprints(db_path)
    for h, t in fingerprints:
        db.setdefault(h, [])
        if (song_id, t) not in db[h]:
            db[h].append((song_id, t))

    save_fingerprints(db, db_path)

if __name__ == "__main__":
    audioPath = sys.argv[1] if len(sys.argv)>1  else r"audio\Gym Class Heroes_ Stereo Hearts.mp3"
    file_name = os.path.basename(audioPath).split(".")[0]
    save_song(audioPath, file_name)
