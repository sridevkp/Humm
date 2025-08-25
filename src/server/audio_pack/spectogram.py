import numpy as np
import librosa


def spectogram(y, sr=22050, n_mels=128, fmax=8000, hop_length = 512, n_fft=2048):    
    S = librosa.feature.melspectrogram(
        y=y, 
        sr=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        n_mels=n_mels,
        fmax=fmax
    )
    
    S = librosa.power_to_db(S, ref=np.max)
    
    return S


def find_constellation(S, threshold=95, n_size=(5, 5)):
    freq_bins, time_bins = S.shape
    peaks = []
    threshold = np.percentile(S, threshold)

    for t in range(time_bins):
        for f in range(freq_bins):
            mag = S[f, t]
            if mag < threshold:
                continue
            f_min = max(0, f - n_size[0] // 2)
            f_max = min(freq_bins, f + n_size[0] // 2)
            t_min = max(0, t - n_size[1] // 2)
            t_max = min(time_bins, t + n_size[1] // 2)

            local_patch = S[f_min:f_max, t_min:t_max]
            if mag == np.max(local_patch):
                peaks.append((f, t))  # (frequency_bin, time_bin)
    return peaks
