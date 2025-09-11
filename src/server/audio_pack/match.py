import librosa
from .spectogram import spectogram, find_constellation
from .fingerprint import generate_fingerprints, find_matches_fgp
from .utils import load_fingerprints
import sys, os


db_path = "db/fingerprints.json"


cutoff_freq = 5000
n_fft = 4096
hop_length = 1024
fan_value = 15
target_zone = 200
threshold = 90
n_size = (5, 8)

def match_audio_clip(audio, file_name="query"):
    print(f"Loading audio file: {audio}")
    y, sr = librosa.load(audio, sr=None)
    y, _ = librosa.effects.trim(y, top_db=40) 
    
    if isinstance(audio, str): 
        print(f"Audio file loaded successfully with sample rate: {sr}")
    else:
        print(f"Audio data loaded successfully with sample rate: {sr}")

    S = spectogram(y, sr=sr, hop_length=hop_length, n_fft=n_fft, fmax=cutoff_freq)

    peaks = find_constellation(S, threshold, n_size)
    print(f"Found {len(peaks)} peaks.")

    q_fingerprint = generate_fingerprints(peaks, fan_value, target_zone)
    print(f"Generated {len(q_fingerprint)} fingerprints.")
    
    song_id = file_name
    q_fingerprint = {hash(fp): (song_id, t) for fp, t in q_fingerprint}

    db = load_fingerprints(db_path)

    sample_fingerprint_map = {}
    for address, (_, anchor_time_ms) in q_fingerprint.items():
        sample_fingerprint_map[address] = anchor_time_ms

    matches = find_matches_fgp(db, sample_fingerprint_map, 2)
    return matches

if __name__ == "__main__":
    audioPath = sys.argv[1] if len(sys.argv)>1  else r"audio\gym.mp3"
    file_name = os.path.basename(audioPath).split(".")[0]

    matches = match_audio_clip(audioPath, file_name)
    print(matches)
    



