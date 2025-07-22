import streamlit as st
from docx import Document
import json
import os
import zipfile
import io
import tempfile

# -------------------------------
def extract_articles_from_docx(file, law_name):
    doc = Document(file)
    articles = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text.startswith("مادة"):
            try:
                num_start = text.index("(") + 1
                num_end = text.index(")")
                article_number = int(text[num_start:num_end])
                article_text = text[num_end + 2:].strip()
                articles.append({
                    "law": law_name,
                    "article_number": article_number,
                    "text": article_text
                })
            except:
                continue

    return articles

# -------------------------------
st.set_page_config(page_title="محول القوانين إلى JSON", layout="centered")
st.title("📝 تحويل ملفات القوانين (Word) إلى JSON")
st.markdown("قم برفع ملفات .docx ليتم تحويل كل ملف إلى ملف JSON جاهز، وتحميلها جميعًا في ملف مضغوط واحد.")

uploaded_files = st.file_uploader("📂 اختر ملفات Word", type=["docx"], accept_multiple_files=True)

if uploaded_files:
    if st.button("🔄 تحويل وتحميل"):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_files = []

            for file in uploaded_files:
                law_name = os.path.splitext(file.name)[0]
                articles = extract_articles_from_docx(file, law_name)
                json_filename = f"{law_name}.json"
                json_path = os.path.join(tmpdir, json_filename)

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(articles, f, ensure_ascii=False, indent=2)
                    json_files.append(json_path)

            # إنشاء ملف zip
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for json_file in json_files:
                    zipf.write(json_file, arcname=os.path.basename(json_file))

            st.success("✅ تم التحويل بنجاح!")

            # زر تحميل zip
            st.download_button(
                label="📥 تحميل جميع الملفات بصيغة ZIP",
                data=zip_buffer.getvalue(),
                file_name="converted_json_files.zip",
                mime="application/zip"
                              )
