## 📄 Reproducible Research Paper Extractor & Summarizer

Author: Irfana Aslam
GitHub: https://github.com/yourusername

Contact: irfanaaslam69@gmail.com

## Overview

This project is a Streamlit-based application that extracts all valuable content from PDFs and DOCX research papers, including:

Full text extraction (even from scanned PDFs via OCR)

Table extraction (with Camelot and Tabula)

Image extraction (figures, graphs, charts)

Section-wise summaries using Hugging Face Transformers

Downloadable JSON output for structured storage and analysis

This tool is designed for researchers, students, and content writers who need to process multiple papers efficiently and accurately.

## Key Features

📄 Full text extraction from PDFs & DOCX files

🖼️ Image extraction from research papers

📊 Table extraction from PDFs (Camelot & Tabula)

🔍 OCR support for scanned content

✨ Automatic section-wise summarization

💾 Download results as structured JSON

📂 Upload multiple files at once (up to 200MB per file)

💡 User-friendly and visually appealing interface

##  Installation

Clone the repository

git clone https://github.com/IrfanaAslam/reproducible-pdf-extraction-pipeline.git
cd reproducible-pdf-extraction-pipeline


Create a virtual environment (optional but recommended)

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate


##  Install dependencies

pip install -r requirements.txt


## ⚠️ Make sure you have the following installed:

Tesseract OCR

Java (required for Tabula)

Poppler (required for pdfplumber for some PDFs)

Run the application

streamlit run app.py


Open in browser: Streamlit will automatically open a browser window at http://localhost:8501

##  Usage

Click “Browse files” or drag-and-drop PDF/DOCX research papers.

The app will automatically:

Extract all text, tables, and images

Perform OCR on scanned PDFs

Generate section-wise summaries

Download a structured JSON file with all extracted content.

## Example Output
{
  "file_name": "Sample_Research_Paper.pdf",
  "text": "Full text of the paper...",
  "images": ["figure1.png", "figure2.png"],
  "tables": [
      {"table_1": [["Header1", "Header2"], ["Value1", "Value2"]]}
  ],
  "summary": {
      "abstract": "Summary of abstract...",
      "introduction": "Summary of introduction...",
      "conclusion": "Summary of conclusion..."
  }
}

## Future Enhancements

Support for more complex layouts and multi-column PDFs

Advanced NLP-based topic extraction and key phrase detection

Integration with citation and reference extraction

Cloud deployment for large-scale processing

## Call for Collaboration

I am looking to collaborate with developers, data scientists, and researchers to improve this tool.

If you are interested in contributing:

Improving extraction accuracy

Adding new summarization models

Supporting more file formats

Feel free to fork this repository, raise issues, or submit pull requests.

## License

This project is licensed under the MIT License. See LICENSE
 for details.

🚀 Let’s make research more reproducible and accessible!

## Irfana Aslam | Python & AI Enthusiast | LinkedIn | www.linkedin.com/in/irfana-aslam-b26751176