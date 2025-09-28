import subprocess
import sys
import os
from PIL import Image
import glob
import pytesseract

# Explicit Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if len(sys.argv) < 2:
    print("Usage: python grab_thumbnail_ocr.py [URL]")
    sys.exit(1)

url = sys.argv[1]
log_file = "downloaded.txt"

# Check log to skip duplicates
if os.path.exists(log_file):
    with open(log_file, "r") as f:
        downloaded = set(line.strip() for line in f)
else:
    downloaded = set()

if url in downloaded:
    print(f"Skipping {url}, already downloaded.")
    sys.exit(0)

# Cookies file
cookies_file = "cookies.txt"

# Download thumbnail as JPG
yt_dlp_cmd = [
    "yt-dlp",
    "--cookies", cookies_file,
    "--skip-download",
    "--write-thumbnail",
    "--convert-thumbnails", "jpg",
    "-o", "output",  # yt-dlp will convert to JPG
    url
]

subprocess.run(yt_dlp_cmd, check=True)
print(f"Downloaded thumbnail for {url}")

# Find the actual JPG file (yt-dlp may add numbers or extensions)
jpg_files = glob.glob("output*.jpg")
if not jpg_files:
    print("No JPG thumbnail found. Files in directory:", os.listdir("."))
    sys.exit(1)

image_path = jpg_files[0]

# OCR with English + Simplified + Traditional + Vertical Simplified Chinese
ocr_output_file = "prefiltered_ocr.txt"
text = pytesseract.image_to_string(
    Image.open(image_path),
    lang="eng+chi_sim+chi_tra+chi_sim_vert"
)

with open(ocr_output_file, "w", encoding="utf-8") as f:
    f.write(text)

print(f"OCR result saved to {ocr_output_file}")

# Add URL to log
with open(log_file, "a") as f:
    f.write(url + "\n")
