import gdown
import os

# Google Drive file ID from your link
file_id = "1c4VDb0Pf7RCgps4aLMiSuLtdaUpU_X49"
output_path = "nassau_candy_data.csv"

print("📥 Downloading dataset from Google Drive...")
gdown.download(f"https://drive.google.com/uc?id={file_id}", output_path, quiet=False)

if os.path.exists(output_path):
    print(f"✅ Dataset downloaded successfully: {output_path}")
else:
    print("❌ Download failed. Please check the link.")