import os
import shutil
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
PDF_FILE = "input.pdf"     # put your PDF here
TEMP_DIR = "temp_images"

MAX_PAGES = 50             # security limit
MAX_SIZE_MB = 20           # file size limit
try:
    # 1️⃣ Check file size
    file_size = os.path.getsize(PDF_FILE) / (1024 * 1024)
    if file_size > MAX_SIZE_MB:
        raise Exception("PDF file too large")

    # 2️⃣ Read PDF & count pages
    reader = PdfReader(PDF_FILE)
    page_count = len(reader.pages)

    if page_count > MAX_PAGES:
        raise Exception("Too many pages")

    # 3️⃣ Create temp folder
    os.makedirs(TEMP_DIR, exist_ok=True)

    # 4️⃣ Convert pages one by one
    for page_number in range(1, page_count + 1):
        images = convert_from_path(
            PDF_FILE,
            first_page=page_number,
            last_page=page_number
        )

        image_path = os.path.join(
            TEMP_DIR,
            f"page_{page_number}.png"
        )
        images[0].save(image_path, "PNG")

    print("✅ PDF converted safely!")

except Exception as e:
    print("❌ Error:", e)
finally:
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        print("🧹 Temporary files cleaned")
