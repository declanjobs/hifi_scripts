import os
import subprocess
import sys
import logging
import tarfile
from glob import glob
from multiprocessing import Pool, cpu_count
import mutagen.flac

# === SETTINGS ===
SKIP_ALREADY_TAGGED = True  # Skip tagging if FLAC already has tags
COMPRESS_APE_BACKUP = True  # Compress and delete original .ape file after success

# === LOGGING SETUP ===
logging.basicConfig(
    filename="split_conversion.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("[%(levelname)s] %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# === FIND MATCHING .APE + .CUE PAIRS ===
def find_ape_cue_pairs(root_dir):
    pairs = []
    for dirpath, _, filenames in os.walk(root_dir):
        cue_files = [f for f in filenames if f.lower().endswith(".cue")]
        for cue_file in cue_files:
            cue_path = os.path.join(dirpath, cue_file)
            base = os.path.splitext(cue_file)[0]
            possible_ape = os.path.join(dirpath, base + ".ape")
            if os.path.exists(possible_ape):
                pairs.append((possible_ape, cue_path))
            else:
                logging.warning(f"No matching APE file for: {cue_path}")
    return pairs

# === CHECK IF FLAC FILE IS TAGGED ===
def is_flac_tagged(file_path):
    try:
        tags = mutagen.flac.FLAC(file_path).tags
        return bool(tags)
    except Exception:
        return False

# === COMPRESS ORIGINAL APE FILE ===
def compress_and_delete_ape(ape_path):
    dir_path = os.path.dirname(ape_path)
    base_name = os.path.splitext(os.path.basename(ape_path))[0]
    archive_path = os.path.join(dir_path, base_name + ".tar.gz")
    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(ape_path, arcname=os.path.basename(ape_path))
        os.remove(ape_path)
        logging.info(f"📦 Compressed and removed original APE: {archive_path}")
    except Exception as e:
        logging.error(f"⚠️ Failed to compress {ape_path}: {e}")

# === SPLIT APE TO FLAC ===
def split_ape_to_flac(ape_path, cue_path):
    base_dir = os.path.dirname(ape_path)
    base_name = os.path.splitext(os.path.basename(ape_path))[0]
    wav_path = os.path.join(base_dir, base_name + ".wav")

    logging.info(f"🎵 Processing: {ape_path} with {cue_path}")

    try:
        # Step 1: Decode APE to WAV
        subprocess.run(["mac", ape_path, wav_path, "-d"], check=True)

        # Step 2: Split WAV to FLAC with named output
        subprocess.run([
            "shntool", "split", "-f", cue_path, "-t", "%n - %t", "-o", "flac", wav_path
        ], check=True, cwd=base_dir)

        # Step 3: Tag files only if they are not tagged yet
        flacs = sorted(glob(os.path.join(base_dir, "[0-9][0-9] - *.flac")))
        flacs_to_tag = [
            f for f in flacs if not is_flac_tagged(f)
        ] if SKIP_ALREADY_TAGGED else flacs

        # Remove and exclude *pregap.flac
        filtered_flacs = []
        for f in flacs_to_tag:
            if f.lower().endswith("pregap.flac"):
                try:
                    os.remove(f)
                    logging.info(f"🗑️ Removed pregap FLAC: {f}")
                except Exception as e:
                    logging.warning(f"⚠️ Could not delete {f}: {e}")
            else:
                filtered_flacs.append(f)

        if not filtered_flacs:
            logging.warning(f"No taggable FLACs in: {base_dir}")
            return

        if filtered_flacs:
            subprocess.run(["cuetag", cue_path] + filtered_flacs, check=True)
            logging.info(f"🏷️ Tagged {len(filtered_flacs)} tracks")
        else:
            logging.info("ℹ️ Skipped tagging: files already tagged")

        # Step 4: Cleanup WAV
        os.remove(wav_path)
        logging.info(f"✅ Complete: {ape_path}")

        # Step 5: Compress and delete original APE
        if COMPRESS_APE_BACKUP:
            compress_and_delete_ape(ape_path)


    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Failed to process {ape_path}: {e}")
    except Exception as ex:
        logging.error(f"⚠️ Unexpected error: {ex}")

def find_dirs_with_ape_cue(root_dir):
    work = []
    for dirpath, _, filenames in os.walk(root_dir):
        cue_files = [f for f in filenames if f.lower().endswith(".cue")]
        for cue_file in cue_files:
            cue_path = os.path.join(dirpath, cue_file)
            base = os.path.splitext(cue_file)[0]
            ape_path = os.path.join(dirpath, base + ".ape")
            if os.path.exists(ape_path):
                work.append((ape_path, cue_path))
            else:
                logging.warning(f"No matching APE for: {cue_path}")
    return work

def main(root_dir):
    tasks = find_dirs_with_ape_cue(root_dir)
    core = max(cpu_count()-2, 1)
    logging.info(f"🧠 Using {core} cores")
    logging.info(f"📁 Found {len(tasks)} APE+CUE pairs")

    with Pool(processes=core) as pool:
        pool.starmap(split_ape_to_flac, tasks)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python split_ape_with_cue.py /path/to/music")
    else:
        main(sys.argv[1])
