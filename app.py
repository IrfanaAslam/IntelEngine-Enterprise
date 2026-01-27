# app.py
import streamlit as st
import pandas as pd
import json
import io
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
from datetime import datetime

from src.extractor import AdvancedResearchExtractor
from src.batch_rename import batch_rename

# --- ENSURE DIRECTORIES & DB ---
for folder in ["logs", "data/temp", "data/renamed"]:
    os.makedirs(folder, exist_ok=True)

DB_PATH = "data/research.db"

# Create tables if they don't exist (main thread)
main_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = main_conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS document_sections (
    filename TEXT,
    level INTEGER,
    text TEXT,
    sentiment TEXT,
    language TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS document_tables (
    filename TEXT,
    table_id INTEGER,
    page INTEGER,
    table_json TEXT
)
""")
main_conn.commit()
main_conn.close()

# --- CONFIG ---
st.set_page_config(page_title="IntelEngine Enterprise", layout="wide", page_icon="🛡️")
st.title("🔬 IntelEngine Enterprise – Industrial Research Intelligence Platform")

# --- SESSION STATE ---
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = []
if 'rename_preview' not in st.session_state:
    st.session_state.rename_preview = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("📂 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDFs, DOCX, or CSVs",
        accept_multiple_files=True
    )

    st.markdown("---")
    st.header("⚙️ Options")
    max_workers = st.number_input("Parallel Workers", min_value=1, max_value=16, value=4)
    rename_pattern = st.text_input("Rename Pattern", "{name}_{date}_{sentiment}", help="Use {name}, {date}, {sentiment}, {ext}")

# --- PROCESS DOCUMENTS ---
if uploaded_files and st.sidebar.button("🚀 Process Documents"):
    temp_dir = Path("data/temp")
    temp_dir.mkdir(exist_ok=True, parents=True)

    results = []
    progress_bar = st.progress(0)
    total_files = len(uploaded_files)

    def process_file(f):
        fpath = temp_dir / f.name
        with open(fpath, "wb") as out:
            out.write(f.getbuffer())

        extractor = AdvancedResearchExtractor(fpath)
        res = extractor.process()

        # Tables
        if res['metadata']['detected_format'].lower() == 'pdf':
            res['tables'] = extractor._parse_pdf_tables()
        elif res['metadata']['detected_format'].lower() in ['doc', 'docx']:
            res['tables'] = extractor._parse_docx_tables()
        else:
            res['tables'] = []

        # ===== THREAD-SAFE SQLITE =====
        thread_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        thread_cursor = thread_conn.cursor()

        # Sections
        for sec in res.get('structure', []):
            thread_cursor.execute(
                "INSERT INTO document_sections VALUES (?, ?, ?, ?, ?)",
                (
                    res['metadata']['filename'],
                    sec.get('level'),
                    sec.get('text'),
                    res['sentiment'].get('label', 'neutral'),
                    res['metadata'].get('language', 'unknown')
                )
            )

        # Tables
        for idx, tbl in enumerate(res.get('tables', []), 1):
            thread_cursor.execute(
                "INSERT INTO document_tables VALUES (?, ?, ?, ?)",
                (
                    res['metadata']['filename'],
                    idx,
                    tbl.get('page', 0),
                    json.dumps(tbl.get('table'))
                )
            )
        thread_conn.commit()
        thread_conn.close()
        # ============================

        return res

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_file, f): f for f in uploaded_files}
        for i, future in enumerate(as_completed(future_to_file)):
            try:
                results.append(future.result())
            except Exception as e:
                st.error(f"Error processing {future_to_file[future].name}: {e}")
            progress_bar.progress((i + 1) / total_files)

    st.session_state.processed_data = results
    st.success("✅ Document Processing Complete!")

# --- DASHBOARD ---
if st.session_state.processed_data:
    df = pd.DataFrame([{
        "Filename": d['metadata']['filename'],
        "Format": d['metadata']['detected_format'],
        "Sentiment": d['sentiment'].get('label', 'neutral'),
        "Score": d['sentiment'].get('compound', 0),
        "Integrity": d['metadata']['integrity'],
        "Language": d['metadata'].get('language', 'unknown'),
        "Tables": len(d.get('tables', []))
    } for d in st.session_state.processed_data])

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Analytics", "🔎 Search", "🛡️ Integrity Map", "📁 Batch Rename"]
    )

    # --- TAB 1: Analytics ---
    with tab1:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Docs", len(df))
        c2.metric("Avg Sentiment", round(df['Score'].mean(), 2))
        c3.metric("Integrity Issues", (df['Integrity'] != "✅ Match").sum())
        c4.metric("Languages Detected", df['Language'].nunique())
        c5.metric("Tables Detected", df['Tables'].sum())

        import plotly.express as px
        fig = px.sunburst(df, path=['Format', 'Sentiment'], values='Score',
                          color='Score', color_continuous_scale='RdYlGn',
                          title="Document Landscape by Format & Sentiment")
        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 2: Full-Text & Section Search ---
    with tab2:
        query = st.text_input("Search Full Text or Section Titles")
        if query:
            hits = []
            for d in st.session_state.processed_data:
                if query.lower() in d['text'].lower():
                    snippet = d['text'][:500] + "..." if len(d['text']) > 500 else d['text']
                    hits.append({"file": d['metadata']['filename'], "type": "Full Text", "snippet": snippet})
                for sec in d.get('structure', []):
                    if query.lower() in sec['text'].lower():
                        hits.append({"file": d['metadata']['filename'], "type": "Section", "snippet": sec['text']})
            if hits:
                for h in hits:
                    with st.expander(f"📄 {h['file']} ({h['type']})"):
                        st.write(f"**Context:** {h['snippet']}")
            else:
                st.warning("No matches found.")

    # --- TAB 3: Integrity Map ---
    with tab3:
        st.write("#### Document Integrity Overview")
        st.dataframe(df[["Filename", "Format", "Integrity", "Language", "Tables"]], use_container_width=True)

    # --- TAB 4: Batch Rename ---
    with tab4:
        if st.button("Preview Rename"):
            preview = []
            for d in st.session_state.processed_data:
                meta = d['metadata']
                sentiment = d['sentiment'].get('label', 'NEUTRAL').upper()
                date_str = pd.Timestamp.now().strftime("%Y-%m-%d")
                name = meta['filename'].split('.')[0]
                new_name = rename_pattern.format(
                    name=name, date=date_str, sentiment=sentiment, ext=meta['detected_format'].lower()
                )
                new_name = f"{new_name}.{meta['detected_format'].lower()}"
                preview.append({"Original": meta['filename'], "New Name": new_name})
            st.session_state.rename_preview = preview

        if st.session_state.rename_preview:
            st.write("#### Rename Preview")
            st.table(st.session_state.rename_preview)

            if st.button("✅ Apply Rename"):
                batch_rename(
                    st.session_state.processed_data,
                    input_dir="data/temp",
                    output_dir="data/renamed",
                    pattern=rename_pattern
                )
                st.success("Files renamed successfully!")

    # --- EXPORT OPTIONS ---
    st.markdown("---")
    st.header("📥 Multi-Format Export")

    export_list = []
    for d in st.session_state.processed_data:
        export_list.append({
            "Filename": d['metadata']['filename'],
            "Detected_Format": d['metadata']['detected_format'],
            "MIME_Type": d['metadata']['mime'],
            "Integrity": d['metadata']['integrity'],
            "Sentiment": d['sentiment'].get('label'),
            "Score": d['sentiment'].get('compound'),
            "Project_IDs": ", ".join(d['entities'].get('project_ids', [])),
            "Full_Extracted_Text": d.get('text', ''),
            "Sections": json.dumps(d.get('structure', [])),
            "Tables": len(d.get('tables', []))
        })
    df_export = pd.DataFrame(export_list)

    # Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        pd.DataFrame([{"Full Text": d.get("text", "")} for d in st.session_state.processed_data]).to_excel(writer, index=False, sheet_name="FullText")
        sections = []
        for d in st.session_state.processed_data:
            for sec in d.get("structure", []):
                sections.append({
                    "Filename": d['metadata']['filename'],
                    "Level": sec.get("level"),
                    "Text": sec.get("text"),
                    "Sentiment": d['sentiment'].get('label', 'neutral')
                })
        pd.DataFrame(sections).to_excel(writer, index=False, sheet_name="Sections")
        for d in st.session_state.processed_data:
            for idx, tbl in enumerate(d.get("tables", []), 1):
                pd.DataFrame(tbl.get("table")).to_excel(writer, index=False, sheet_name=f"{d['metadata']['filename']}_Tbl{idx}")
    st.download_button("📊 Download Excel (Full)", buffer.getvalue(), "research_report_full.xlsx")

    # JSON
    st.download_button("📦 Download JSON", json.dumps(st.session_state.processed_data, indent=4), "research_data.json")

    # CSV
    st.download_button("📄 Download CSV", df_export.to_csv(index=False).encode(), "research_report.csv")

else:
    st.info("Upload documents on the sidebar to begin analysis.")
