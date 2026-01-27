# app.py
import streamlit as st
import pandas as pd
import json
import io
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.extractor import AdvancedResearchExtractor
from src.batch_rename import batch_rename

# --- ENSURE REQUIRED DIRECTORIES EXIST ---
for folder in ["logs", "data/temp", "data/renamed"]:
    os.makedirs(folder, exist_ok=True)

# --- CONFIG ---
st.set_page_config(page_title="IntelEngine Ultra Pro", layout="wide", page_icon="🛡️")
st.title("🔬 IntelEngine Ultra Pro – Industrial Research Pipeline")

# --- SESSION STATE ---
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = []

if 'rename_preview' not in st.session_state:
    st.session_state.rename_preview = []

# --- SIDEBAR: FILE INGESTION ---
with st.sidebar:
    st.header("📂 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload PDFs, DOCX, or CSVs",
        accept_multiple_files=True
    )

    st.markdown("---")
    st.header("⚙️ Options")
    max_workers = st.number_input(
        "Parallel Workers", min_value=1, max_value=16, value=4
    )
    rename_pattern = st.text_input(
        "Rename Pattern", "{name}_{date}_{sentiment}",
        help="Use {name}, {date}, {sentiment}, {ext}"
    )

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
        return AdvancedResearchExtractor(fpath).process()

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
        "Language": d['metadata'].get('language', 'unknown')
    } for d in st.session_state.processed_data])

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Analytics", "🔎 Search", "🛡️ Integrity Map", "📁 Batch Rename"]
    )

    # --- TAB 1: Analytics ---
    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Docs", len(df))
        c2.metric("Avg Sentiment", round(df['Score'].mean(), 2))
        c3.metric("Integrity Issues", (df['Integrity'] != "✅ Match").sum())
        c4.metric("Languages Detected", df['Language'].nunique())

        import plotly.express as px
        fig = px.sunburst(
            df, path=['Format', 'Sentiment'], values='Score',
            color='Score', color_continuous_scale='RdYlGn',
            title="Document Landscape by Format & Sentiment"
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 2: Full-Text Search ---
    with tab2:
        query = st.text_input("Search Extracted Text")
        if query:
            hits = []
            for d in st.session_state.processed_data:
                if query.lower() in d['text'].lower():
                    snippet = d['text'][:500] + "..." if len(d['text']) > 500 else d['text']
                    hits.append({"file": d['metadata']['filename'], "snippet": snippet, "entities": d['entities']})
            if hits:
                for h in hits:
                    with st.expander(f"📄 {h['file']}"):
                        st.write(f"**Context:** {h['snippet']}")
                        st.json(h['entities'])
            else:
                st.warning("No matches found.")

    # --- TAB 3: Integrity Map ---
    with tab3:
        st.write("#### Document Integrity Overview")
        st.dataframe(df[["Filename", "Format", "Integrity", "Language"]], use_container_width=True)

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
            "Full_Extracted_Text": d.get('text', '')
        })
    df_export = pd.DataFrame(export_list)

    # Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, index=False, sheet_name='ResearchResults')
        workbook  = writer.book
        worksheet = writer.sheets['ResearchResults']
        wrap_fmt = workbook.add_format({'text_wrap': True, 'valign': 'top'})
        worksheet.set_column('H:H', 60, wrap_fmt)
    st.download_button("📊 Download Excel", buffer.getvalue(), "research_report.xlsx")

    # JSON
    st.download_button("📦 Download JSON", json.dumps(st.session_state.processed_data, indent=4), "research_data.json")

    # CSV
    st.download_button("📄 Download CSV", df_export.to_csv(index=False).encode(), "research_report.csv")

else:
    st.info("Upload documents on the sidebar to begin analysis.")
