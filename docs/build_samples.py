from pathlib import Path
import wave
import numpy as np

src = Path('docs/guitar.wav')
out_dir = Path('docs/samples')
out_dir.mkdir(parents=True, exist_ok=True)

with wave.open(str(src), 'rb') as w:
    channels = w.getnchannels()
    sample_width = w.getsampwidth()
    frame_rate = w.getframerate()
    frame_count = w.getnframes()
    raw = w.readframes(frame_count)

if sample_width != 2:
    raise RuntimeError('Only 16-bit PCM WAV is supported')

arr = np.frombuffer(raw, dtype='<i2').astype(np.float32).reshape(-1, channels)

def pitch_shift_simple(sig: np.ndarray, factor: float) -> np.ndarray:
    old_len = sig.shape[0]
    new_len = max(1, int(round(old_len / factor)))
    x_old = np.arange(old_len)
    x_new = np.linspace(0, old_len - 1, new_len)
    out = np.zeros((new_len, sig.shape[1]), dtype=np.float32)
    for c in range(sig.shape[1]):
        out[:, c] = np.interp(x_new, x_old, sig[:, c])
    return out

samples = {
    'C2.wav': 1.0,
    'C3.wav': 2.0,
    'C4.wav': 4.0,
}

for name, factor in samples.items():
    data = pitch_shift_simple(arr, factor)
    data = np.clip(data, -32768, 32767).astype('<i2')
    with wave.open(str(out_dir / name), 'wb') as w:
        w.setnchannels(channels)
        w.setsampwidth(sample_width)
        w.setframerate(frame_rate)
        w.writeframes(data.tobytes())

print('Generated:', ', '.join(samples.keys()))
