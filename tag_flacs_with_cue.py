import os
import subprocess
import sys
import logging
from glob import glob

# === LOGGING SETUP ===
logging.basicConfig(
    filename="cuetag_run.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("[%(levelname)s] %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

def tag_flacs_in_dir(cue_path):
    dir_path = os.path.dirname(cue_path)
    all_flacs = sorted(glob(os.path.join(dir_path, "[0-9][0-9] - *.flac")))

    # Remove and exclude *pregap.flac
    filtered_flacs = []
    for f in all_flacs:
        if f.lower().endswith("pregap.flac"):
            try:
                os.remove(f)
                logging.info(f"🗑️ Removed pregap FLAC: {f}")
            except Exception as e:
                logging.warning(f"⚠️ Could not delete {f}: {e}")
        else:
            filtered_flacs.append(f)

    if not filtered_flacs:
        logging.warning(f"No taggable FLACs in: {dir_path}")
        return

    try:
        subprocess.run(["cuetag", cue_path] + filtered_flacs, check=True)
        logging.info(f"🏷️ Tagged {len(filtered_flacs)} FLACs in {dir_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ cuetag failed in {dir_path}: {e}")

def find_and_tag_all(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.lower().endswith(".cue"):
                cue_path = os.path.join(dirpath, file)
                tag_flacs_in_dir(cue_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tag_flacs_with_cue.py /path/to/music")
    else:
        find_and_tag_all(sys.argv[1])
