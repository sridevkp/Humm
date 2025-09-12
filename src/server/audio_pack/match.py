from pydub import AudioSegment
import librosa
import sys, os, io

from .spectogram import spectogram, find_constellation
from .fingerprint import generate_fingerprints, find_matches_fgp, stable_hash
from .utils import load_fingerprints

from matplotlib import pyplot as plt

db_path = "db/fingerprints.json"


cutoff_freq = 5000
n_fft = 4096
hop_length = 1024
fan_value = 15
target_zone = 200
threshold = 90
n_size = (5, 8)

def match_audio_clip(audio, file_name="query"):
    print(f"Loading audio file: {file_name}")

    try:
        if isinstance(audio, (str, bytes, os.PathLike)):
            sound = AudioSegment.from_file(audio)
        else:
            audio.seek(0)
            sound = AudioSegment.from_file(audio, format="webm")

        wav_io = io.BytesIO()
        sound.export(wav_io, format="wav")
        wav_io.seek(0)

        y, sr = librosa.load(wav_io, sr=22050) 
        y, _ = librosa.effects.trim(y, top_db=40)

        S = spectogram(y, sr=sr, hop_length=hop_length, n_fft=n_fft, fmax=cutoff_freq)

        peaks = find_constellation(S, threshold, n_size, hop_length=hop_length, sr=sr)
        print(f"Found {len(peaks)} peaks.")

        if not peaks:
            print("Warning: No peaks found. Try lowering the threshold.")
            return []

        q_fingerprint = generate_fingerprints(peaks, fan_value, target_zone)
        print(f"Generated {len(q_fingerprint)} fingerprints.")
        
        # Debug: Check fingerprint data types
        if q_fingerprint:
            print(f"Sample fingerprint: {q_fingerprint[0]} (types: {type(q_fingerprint[0][0])}, {type(q_fingerprint[0][1])})")
        
        if not q_fingerprint:
            print("Warning: No fingerprints generated.")
            return []
        
        # Create fingerprint mapping for matching
        sample_fingerprint_map = {}
        for fp, anchor_time_ms in q_fingerprint:
            sample_fingerprint_map[fp] = anchor_time_ms

        db = load_fingerprints(db_path)
        
        if not db:
            print("Warning: Database is empty. No songs to match against.")
            return []

        matches = find_matches_fgp(db, sample_fingerprint_map, 1)
        return matches
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return []

if __name__ == "__main__":
    audioPath = sys.argv[1] if len(sys.argv)>1  else r"audio\gym.mp3"
    file_name = os.path.basename(audioPath).split(".")[0]

    matches = match_audio_clip(audioPath, file_name)
    print(matches)
    



