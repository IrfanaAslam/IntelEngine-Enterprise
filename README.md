# 🛡️ IntelEngine Enterprise – Industrial Research Intelligence Platform

**Author:** Irfana Aslam  
**Email:** irfanaaslam0786@gmail.com  
**Location:** Pakistan  

---
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

## **Project Overview**

IntelEngine Enterprise is an **advanced, industrial-grade research data extraction and analysis platform**. It allows users to:

- Extract **full text** and hierarchical structure (sections/headings) from PDFs and DOCX documents.  
- Perform **sentiment analysis** and **language detection** on document content.  
- Automatically detect **tables** in PDFs and DOCX files and export them to structured formats.  
- Maintain **data integrity and file format verification**.  
- Provide **multi-format exports**: Excel (full text, sections, tables), CSV, and JSON.  
- Enable **batch renaming of files** based on metadata and content attributes.  
- Store extracted information in a **SQLite database** for efficient querying and dashboard visualizations.  
- Scale to **hundreds of documents in parallel** using multithreading safely.  

This project is designed for **researchers, analysts, and organizations** who deal with **large volumes of research documents** and need **automated insights and structured data**.

---

## **Project Features**

- **Full-text extraction** from PDF, DOCX, and other text files  
- **Hierarchical structure detection** (bold text in PDFs, headings in DOCX)  
- **Sentiment analysis** using VADER  
- **Language detection** using `langdetect`  
- **Entity extraction**: emails, project IDs, currency  
- **Table detection and extraction** for PDF and DOCX  
- **Batch rename utility** with pattern-based naming (`{name}_{date}_{sentiment}_{ext}`)  
- **SQLite database integration** with thread-safe operations  
- **Multi-format exports**: Excel, CSV, JSON  
- **Interactive Streamlit dashboard** for analytics, search, and exports  
- **Parallel processing** for speed and scalability  

---

## **Prerequisites & Installation**

1. **Clone the repository:**

```bash
git clone https://github.com/IrfanaAslam/IntelEngine-Enterprise.git
cd IntelEngine-Enterprise
Create and activate a virtual environment (recommended):

bash
Copy code
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
requirements.txt should contain:

rust
Copy code
pdfplumber
python-docx
pandas
openpyxl
tqdm
nltk
streamlit
plotly
wordcloud
matplotlib
filetype
pdfminer.six
xlsxwriter
langdetect
Download NLTK VADER lexicon (automatically handled in extractor.py)

Project Structure
powershell
Copy code
IntelEngine-Enterprise/
│
├── src/
│   ├── extractor.py          # AdvancedResearchExtractor class
│   ├── batch_rename.py       # Batch rename utility
│
├── data/
│   ├── temp/                 # Temporary uploaded files
│   ├── renamed/              # Renamed files
│   └── research.db           # SQLite database
│
├── logs/                     # Logs directory
├── app.py                    # Main Streamlit app
├── requirements.txt
└── README.md
How to Run the Project
Start the Streamlit app:

bash
Copy code
streamlit run app.py
Upload Documents:

PDFs, DOCX, or CSV files in the sidebar

Click Process Documents to analyze files

Dashboard Features:

Analytics Tab: Document count, sentiment, tables, languages, sunburst visualization

Search Tab: Full-text and section search across all documents

Integrity Map: Verify file format integrity

Batch Rename Tab: Preview and apply automated file renaming

Export Options:

Download extracted data in Excel, CSV, or JSON

Excel exports include Full Text, Sections, and Tables sheets

Example Rename Pattern
text
Copy code
{name}_{date}_{sentiment}.{ext}
name → Original file name

date → Current date (YYYY-MM-DD)

sentiment → Detected sentiment (POSITIVE, NEUTRAL, NEGATIVE)

ext → File extension (pdf, docx, etc.)

Example: Motivation_Letter_2026-01-27_POSITIVE.pdf

Contributing & Collaboration
Irfana Aslam is actively looking for researchers, developers, and data enthusiasts to contribute to this project and future AI-driven research automation tools.

If you are interested in:

Adding advanced NLP features

Improving table detection and auto-formatting

Integrating vision-based PDF parsing

Building enterprise-ready dashboards

Please feel free to fork the repo, submit pull requests, or reach out at:
Email: irfanaaslam0786@gmail.com

Let’s build the next generation of industrial research intelligence platforms together! 🚀

License
This project is released under the MIT License. See LICENSE file for details.

Acknowledgements
PDF processing: pdfplumber, pdfminer.six

DOCX parsing: python-docx

Sentiment analysis: NLTK VADER

Dashboard: Streamlit

Data visualization: Plotly, Matplotlib