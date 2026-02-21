import random
from pydub import AudioSegment
import numpy as np
from scipy.signal import resample, butter, lfilter
import shutil
import datetime
import os

def low_pass(samples, cutoff, sr):
	b, a = butter(4, cutoff / (sr / 2), btype='low')
	return lfilter(b, a, samples, axis=0)

def simulate_rot():
    print("=== Asmongoldify: Simulate bit rot, and corruption, in audio, for FREE! ===")
    print("=== By GMD King ===")
    src = input("Enter source audio filename (e.g. song.flac): ").strip()
    if not os.path.exists(src):
        print("File not found. Is the file name correct? Did you include the extension?")
        return

    corruption_percent = float(input("Enter byte corruption percent (0.00–1.00): "))
    if not (0 <= corruption_percent <= 1):
        print("Invalid corruption percent. Use 0.00–1.00.")
        return

    print("If youre unsure of any settings, leave them to the example number given.")

    # Adjust settings
    apply_lowpass = input("Add low pass filter? (y/n): ").strip().lower() == "y"
    if apply_lowpass:
        lowpass_cutoff = float(input("Lowpass cutoff frequency (e.g. 7000): "))

    enable_lofi = input("Enable lo-fi downsampling? (y/n): ").strip().lower() == "y"
    if enable_lofi:
        min_sr = int(input("Min lo-fi sample rate (e.g. 8000): "))
        max_sr = int(input("Max lo-fi sample rate (e.g. 11025): "))

    enable_wowflutter = input("Enable wow & flutter? (y/n): ").strip().lower() == "y"
    if enable_wowflutter:
        depth_cents = int(input("Wow/flutter depth in cents (e.g. 150): "))
        window_size = int(input("Wow/flutter window size (e.g. 512): "))

    enable_skipping = input("Enable skipping effects? (y/n): ").strip().lower() == "y"
    if enable_skipping:
        skip_density = int(input("Skip density (higher = more skips, e.g. 8000): "))

    enable_noise = input("Enable noise bursts? (y/n): ").strip().lower() == "y"
    if enable_noise:
        noise_density = int(input("Noise burst density (e.g. 8000): "))
        noise_amplitude = int(input("Noise amplitude (e.g. 4000): "))

    enable_stereo_shift = input("Enable stereo channel misalignment? (y/n): ").strip().lower() == "y"
    if enable_stereo_shift:
        shift_range = int(input("Stereo shift range in samples (e.g. 200): "))

    enable_jumble = input("Enable random chunk jumbling? (y/n): ").strip().lower() == "y"
    if enable_jumble:
        jumble_chunk_len = int(input("Chunk size for jumbling (e.g. 1024): "))

	# Load source file
    audio = AudioSegment.from_file(src)
    samples = np.array(audio.get_array_of_samples()).astype(np.float32)
    channels = audio.channels
    sr = audio.frame_rate

    if channels == 2:
        samples = samples.reshape((-1, 2))

    # Step 1: Low-pass
    if apply_lowpass:
        print("Running step 1: Low pass filter")
        samples = low_pass(samples, cutoff=lowpass_cutoff, sr=sr)
    else:
        print("Skipping step 1...")

    # Step 2: Lo-fi
    if enable_lofi:
        print("Running step 2: Lo-fi degradation")
        target_sr = random.randint(min_sr, max_sr)
        num_samples = int(len(samples) * target_sr / sr)
        samples = resample(samples, num_samples)
        samples = np.round(samples / 256) * 256
    else:
        target_sr = sr
        print("Skipping step 2...")

    # Step 3: Wow/flutter
    if enable_wowflutter:
        print("Running step 3: Wow and flutter")
        jittered = np.zeros_like(samples)
        for i in range(0, len(samples), window_size):
            shift = 2 ** (random.uniform(-depth_cents, depth_cents) / 1200)
            end = min(i + window_size, len(samples))
            jittered[i:end] = samples[i:end] * shift
        samples = jittered
    else:
        print("Skipping step 3...")

    # Step 4: Skipping
    if enable_skipping:
        print("Running step 4: Skipping effects")
        for _ in range(int(len(samples) / skip_density)):
            start = random.randint(0, len(samples) - 2000)
            length = random.randint(100, 800)
            if random.random() < 0.5:
                samples[start:start+length] = 0
            else:
                snippet = samples[start:start+10]
                for i in range(start, start+length, 10):
                    samples[i:i+10] = snippet
    else:
        print("Skipping step 4...")

	# Step 5: Noise bursts
    if enable_noise:
        print("Running step 5: Noise bursts")
        for _ in range(int(len(samples) / noise_density)):
            idx = random.randint(0, len(samples) - 500)
            noise = np.random.normal(0, noise_amplitude, (500, channels if channels==2 else 1))
            samples[idx:idx+500] += noise
    else:
        print("Skipping step 5...")

    # Step 6: Stereo misalignment
    if enable_stereo_shift and channels == 2:
        print("Running step 6: Stereo shift")
        shift = random.randint(-shift_range, shift_range)
        samples[:, 0] = np.roll(samples[:, 0], shift)
    else:
        print("Skipping step 6...")

    # Step 7: Chunk jumbling
    if enable_jumble:
        print("Running step 7: Chunk jumbling")
        chunks = [samples[i:i+jumble_chunk_len] for i in range(0, len(samples), jumble_chunk_len)]
        new_samples = []
        for chunk in chunks:
            r = random.random()
            if r < 0.05:
                continue
            elif r < 0.15:
                new_samples.append(chunk)
                new_samples.append(chunk)
            elif r < 0.25:
                swap_chunk = chunks[random.randint(0, len(chunks)-1)]
                new_samples.append(swap_chunk)
            else:
                new_samples.append(chunk)
        samples = np.concatenate(new_samples)
    else:
        print("Skipping step 7...")

    print("Running step 8: Resampling to original rate")
    samples = resample(samples, int(len(samples) * sr / target_sr))
    samples = np.clip(samples, -32768, 32767).astype(np.int16)

    if channels == 2:
        samples = samples.reshape((-1,))

    print("Running step 9: Exporting uncorrupted version")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base, _ = os.path.splitext(src)
    intermediate = f"{base}_intermediate_{timestamp}.wav"
    final_out = f"{base}_rotted_{timestamp}.wav"

    rot_audio = AudioSegment(
        samples.tobytes(),
        frame_rate=sr,
        sample_width=2,
        channels=channels
    )
    rot_audio.export(intermediate, format="wav")

    print("Running step 10: Byte-level corruption")
    shutil.copy(intermediate, final_out)
    with open(final_out, "r+b") as f:
        data = bytearray(f.read())
        header_size = min(4096, len(data)//20)
        start_index = header_size
        corruptible_len = len(data) - start_index
        bytes_to_corrupt = int(corruptible_len * corruption_percent)
        for _ in range(bytes_to_corrupt):
            idx = random.randint(start_index, len(data) - 1)
            data[idx] = random.randint(0, 255)
        f.seek(0)
        f.write(data)

    print(f"Full rot complete! Output: {final_out}")

if __name__ == "__main__":
    simulate_rot()

