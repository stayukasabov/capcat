#!/usr/bin/env python3
import sys
import json

def analyze(path):
    try:
        import librosa
        y, sr = librosa.load(path, sr=None, mono=True)
        onset_times = librosa.onset.onset_detect(y=y, sr=sr, units='time', hop_length=512, backtrack=True)
        times = [round(float(t), 3) for t in onset_times]
        print(json.dumps(times))
    except ImportError:
        print("librosa not available", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    analyze(sys.argv[1])
