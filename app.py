from flask import Flask, render_template, request, send_file
import os
import pdfplumber
import pandas as pd
from docx import Document
from PIL import Image
from pdf2image import convert_from_path
import zipfile

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert_file():
    file = request.files['file']
    convert_to = request.form['convert_to']
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    output_path = os.path.join(OUTPUT_FOLDER, f'output.{convert_to}')

    # PDF → Excel
    if convert_to == 'excel':
        with pdfplumber.open(filepath) as pdf:
            tables = []
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    tables.extend(table)

        df = pd.DataFrame(tables)
        df.to_excel(output_path, index=False)
        return send_file(output_path, as_attachment=True)

    # PDF → Word
    elif convert_to == 'word':
        doc = Document()
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                doc.add_paragraph(page.extract_text() or "")
        doc.save(output_path)
        return send_file(output_path, as_attachment=True)

    # Excel → CSV
    elif convert_to == 'csv':
        df = pd.read_excel(filepath)
        df.to_csv(output_path, index=False)
        return send_file(output_path, as_attachment=True)

    # Image → PDF
    elif convert_to == 'pdf':
        image = Image.open(filepath)
        image.save(output_path, "PDF")
        return send_file(output_path, as_attachment=True)

    # PDF → Images (ZIP)
    elif convert_to == 'pdf_to_images':
        images = convert_from_path(filepath, dpi=200)
        zip_path = os.path.join(OUTPUT_FOLDER, "pdf_images.zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i, image in enumerate(images):
                image_name = f"page_{i+1}.png"
                image_path = os.path.join(OUTPUT_FOLDER, image_name)
                image.save(image_path, "PNG")
                zipf.write(image_path, image_name)

        return send_file(zip_path, as_attachment=True)

    else:
        return "Invalid conversion type", 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)