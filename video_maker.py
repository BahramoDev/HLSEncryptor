from pathlib import Path
import subprocess
import secrets
import shutil
import sys
import zipfile


# =========================================================
# Settings
# =========================================================

# URL used by the player to fetch the AES key
KEY_URL = "https://linokala.ir/secure-video/enc.key"

# Approximate duration of each HLS Segment (in seconds)
HLS_TIME = 6

# Video compression quality (Constant Rate Factor)
CRF = 23

# x264 encoding preset
PRESET = "medium"


# =========================================================
# Paths
# =========================================================

# The directory where the script itself is located
SCRIPT_DIR = Path(__file__).resolve().parent

# The 'maker' directory next to the script
MAKER_DIR = SCRIPT_DIR / "maker"

# The output directory
OUTPUT_DIR = SCRIPT_DIR / "output"


# =========================================================
# Find Input Video
# =========================================================

def find_input_video():
    """
    Searches for a file named 'input' in the maker folder.
    For example:
        input.mp4
        input.mkv
        input.mov
    """

    possible_files = []

    for file in MAKER_DIR.iterdir():

        if not file.is_file():
            continue

        if file.stem.lower() == "input":
            possible_files.append(file)

    if not possible_files:
        print("❌ Error: No input file was found in the maker folder.")
        print(f"Checked path: {MAKER_DIR}")
        sys.exit(1)

    if len(possible_files) > 1:
        print("❌ Error: Multiple files with the name 'input' were found:")

        for file in possible_files:
            print(f"   - {file.name}")

        print("\nPlease keep only one file named 'input' in the maker folder.")
        sys.exit(1)

    return possible_files[0]


# =========================================================
# Check FFmpeg
# =========================================================

def check_ffmpeg():

    if shutil.which("ffmpeg") is None:

        print("❌ Error: FFmpeg was not found.")

        print(
            "\nFFmpeg must be added to the Windows PATH "
            "so the 'ffmpeg' command can be executed from PowerShell or CMD."
        )

        sys.exit(1)


# =========================================================
# Generate AES Key
# =========================================================

def create_key(key_path):

    # AES-128 requires exactly a 16-byte key
    key = secrets.token_bytes(16)

    with open(key_path, "wb") as f:
        f.write(key)


# =========================================================
# Create key_info.txt
# =========================================================

def create_key_info(key_info_path, key_path):
    """
    First line:
        The Key URL that will be placed inside the m3u8 playlist.

    Second line:
        The actual local path to the key on the computer,
        which FFmpeg uses for encryption.
    """

    content = f"{KEY_URL}\n{key_path.resolve()}\n"

    key_info_path.write_text(
        content,
        encoding="utf-8"
    )


# =========================================================
# Execute FFmpeg
# =========================================================

def convert_to_hls(input_video, output_dir, key_info_path):

    playlist = output_dir / "output.m3u8"
    segment_pattern = output_dir / "segment_%03d.ts"

    command = [
        "ffmpeg",

        "-y",

        "-i",
        str(input_video),

        # Video
        "-c:v",
        "libx264",

        # Audio
        "-c:a",
        "aac",

        # Quality
        "-preset",
        PRESET,

        "-crf",
        str(CRF),

        # HLS
        "-hls_time",
        str(HLS_TIME),

        "-hls_playlist_type",
        "vod",

        # AES-128
        "-hls_key_info_file",
        str(key_info_path),

        # Segment filenames
        "-hls_segment_filename",
        str(segment_pattern),

        # m3u8 playlist file
        str(playlist),
    ]

    print("\n⏳ Starting video conversion to HLS + AES-128 ...")
    print()

    result = subprocess.run(command)

    if result.returncode != 0:

        print("\n❌ Error: FFmpeg failed during video conversion.")
        sys.exit(result.returncode)


def create_zip(output_dir):
    zip_path = output_dir / "video_hls.zip"

    print("\n📦 Creating ZIP file ...")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:

        for file in output_dir.iterdir():

            # Do not put the ZIP file inside itself
            if file == zip_path:
                continue

            # key_info.txt should not be included in the ZIP
            if file.name == "key_info.txt":
                continue

            if file.is_file():
                zip_file.write(
                    file,
                    arcname=file.name
                )

    print(f"✅ ZIP file created: {zip_path.name}")
    
    

# =========================================================
# Main
# =========================================================

def main():

    print("=" * 60)
    print("        VIDEO MAKER - HLS + AES-128")
    print("=" * 60)

    # Check FFmpeg
    check_ffmpeg()

    # Check maker folder
    if not MAKER_DIR.exists():

        print("\n❌ Error: The 'maker' folder does not exist.")
        print(f"Expected path: {MAKER_DIR}")

        sys.exit(1)

    # Find input file
    input_video = find_input_video()

    print(f"\n🎬 Input:")
    print(f"   {input_video.name}")

    # If the output folder already exists
    if OUTPUT_DIR.exists():

        print("\n⚠️ The output folder already exists.")

        answer = input(
            "Do you want to delete the previous output? (y/n): "
        ).strip().lower()

        if answer != "y":

            print("\n❌ Operation canceled.")
            sys.exit(0)

        shutil.rmtree(OUTPUT_DIR)

    # Create output folder
    OUTPUT_DIR.mkdir(parents=True)

    # Key path
    key_path = OUTPUT_DIR / "enc.key"

    # key_info path
    key_info_path = OUTPUT_DIR / "key_info.txt"

    # Generate key
    print("\n🔐 Generating AES-128 key ...")
    create_key(key_path)

    # Create key_info
    create_key_info(
        key_info_path,
        key_path
    )

    # Execute FFmpeg
    convert_to_hls(
        input_video,
        OUTPUT_DIR,
        key_info_path
    )

    # key_info is just a temporary file, delete it afterwards
    if key_info_path.exists():
        key_info_path.unlink()
        
    create_zip(OUTPUT_DIR)

    # Check output
    playlist = OUTPUT_DIR / "output.m3u8"

    segments = list(
        OUTPUT_DIR.glob("segment_*.ts")
    )

    print("\n" + "=" * 60)

    if playlist.exists() and segments:

        print("✅ Operation completed successfully.")

        print("\n📁 Output:")
        print(f"   {OUTPUT_DIR}")

        print("\n📄 Playlist:")
        print(f"   {playlist.name}")

        print(f"\n🎞 Number of Segments:")
        print(f"   {len(segments)}")

        print("\n🔑 Encryption Key:")
        print(f"   {key_path.name}")

        print("\n⚠️ Note:")
        print("   key_info.txt has been deleted and should not be uploaded to the host.")

        print("\n" + "=" * 60)

    else:

        print("❌ Error: The output files were not created completely.")
        sys.exit(1)


if __name__ == "__main__":
    main()