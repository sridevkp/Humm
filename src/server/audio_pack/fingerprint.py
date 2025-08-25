import hashlib

def stable_hash(anchor_freq, point_freq, time_delta):
    s = f"{anchor_freq}-{point_freq}-{time_delta}".encode()
    return int(hashlib.sha1(s).hexdigest()[:15], 16)

def generate_fingerprints(peaks, fan_value=15, target_zone=200):
    fingerprints = []
    
    peaks = sorted(peaks, key=lambda x: x[0])
    
    for i, anchor in enumerate(peaks[:-1]):
        anchor_time, anchor_freq = anchor
        
        k = 0
        for j in range(i + 1, len(peaks)):
            point = peaks[j]
            point_time, point_freq = point
            
            time_delta = point_time - anchor_time
            if time_delta > target_zone:
                break
            
            if time_delta <= 0:
                continue
                
            k += 1
            if k > fan_value:
                break
                
            hash_value = stable_hash(anchor_freq, point_freq, time_delta)
            
            time_ms = anchor_time  
            
            fingerprints.append((hash_value, time_ms))
    
    return fingerprints


def find_matches_fgp(db, sample_fingerprint, min_score_threshold=1, tolerance_ms=100):
    matches = {}
    timestamps = {}
    target_zones = {}
    
    for address, sample_time in sample_fingerprint.items():
        if address in db:
            for song, db_time in db[address]:
                matches.setdefault(song, [])
                matches[song].append((sample_time, db_time))
                
                if song not in timestamps or db_time < timestamps[song]:
                    timestamps[song] = db_time
                    
                target_zones.setdefault(song, {})
                if db_time not in target_zones[song]:
                    target_zones[song][db_time] = 0
                target_zones[song][db_time] += 1

    scores = analyze_relative_timing(matches, tolerance_ms=tolerance_ms)
    
    filtered_scores = {k:v for k,v in scores.items() if v >= min_score_threshold}
    
    match_list = []
    for song_id, points in filtered_scores.items():
        confidence = points / len(sample_fingerprint) * 100  # Confidence percentage
        match = (song_id, timestamps[song_id], points, confidence)
        match_list.append(match)
        
    match_list.sort(key=lambda m: m[2], reverse=True)
    return match_list


def analyze_relative_timing(matches, tolerance_ms=200):
    scores = {}
    
    for song_id, times in matches.items():
        count = 0
        for i in range(len(times)):
            for j in range(i + 1, len(times)):
                sample_diff = abs(times[i][0] - times[j][0])
                db_diff = abs(times[i][1] - times[j][1])
                if abs(sample_diff - db_diff) < tolerance_ms:
                    count += 1
        scores[song_id] = count
        
    return scores