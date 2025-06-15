# app01.py

import streamlit as st
from utils01 import extract_text_from_pdf, split_text, summarize_chunks, generate_dialogue, generate_audio, trim_summary
import os

# Set page layout and metadata
st.set_page_config(page_title="Research Buddy", layout="wide")

# Sticky app header
st.markdown("""
<div style="position:sticky; top:0; background-color:white; z-index:999; padding:10px 0 10px 0; border-bottom:1px solid #eee; text-align:center;">
    <h1 style='margin-bottom:0;'>🤖 Research Buddy</h1>
    <h3 style='margin-top:0;'>🎧 Turn Research Papers into Podcast-Style Summaries</h3>
    <p style='margin-top:-8px;'>Effortlessly upload your research paper, listen to a podcast-like summary — all in one seamless app.</p>
</div>
""", unsafe_allow_html=True)

# Step 1: Header
st.markdown("### 📄 Upload Your Research Paper")

# Step 1: File Uploader
uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

# Detect re-upload and reprocess if new file
if uploaded_pdf:
    if "last_filename" not in st.session_state or st.session_state["last_filename"] != uploaded_pdf.name:
        # Clear previous session states
        for key in list(st.session_state.keys()):
            if key not in ("last_filename",):
                del st.session_state[key]

        with st.spinner("Extracting and processing your paper..."):
            full_text = extract_text_from_pdf(uploaded_pdf)

            total_chars = len(full_text)
            if total_chars < 5000:
                msg = "🚀 Quick read! Your podcast will be ready in under 30 seconds."
            elif total_chars < 10000:
                msg = "⏱️ Hang tight! Cooking up your podcast — about a minute to go."
            elif total_chars < 20000:
                msg = "🧠 Big brain alert! This one will take ~3 minutes. Stay tuned."
            else:
                msg = "📚 Long paper detected! Give us ~5 mins to podcastify your research."
            st.info(msg)

            chunks = split_text(full_text)
            summaries = summarize_chunks(chunks)
            combined_summary = "\n\n".join(summaries)

            st.session_state["full_text"] = full_text
            st.session_state["summary"] = combined_summary
            st.session_state["chunks"] = chunks

            for lvl in ["Summarize", "Brief", "Deep Dive"]:
                trimmed_sum = trim_summary(combined_summary, lvl)
                trimmed_dia = generate_dialogue(trimmed_sum)
                st.session_state[f"dialogue_{lvl}"] = trimmed_dia
                st.session_state[f"audio_{lvl}"] = generate_audio(trimmed_dia, level=lvl)

            st.session_state["last_filename"] = uploaded_pdf.name

        st.success("🎉 All set! Your podcast is ready — pick your style, press play, and enjoy the research ride! 🎧")

# Step 2: Audio and Script
if "summary" in st.session_state:
    st.markdown("### 🎧 Listen to the Podcast & Read Script")

    level = st.radio("Select podcast detail level:", ["Summarize", "Brief", "Deep Dive"], horizontal=True)

    trimmed_dialogue = st.session_state.get(f"dialogue_{level}", "")
    audio_path = st.session_state.get(f"audio_{level}", "")

    # Center the podcast content
    with st.container():
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)

        st.markdown("#### 🔊 Audio Player")
        st.audio(audio_path, format="audio/mp3")

        with open(audio_path, "rb") as file:
            st.download_button(
                label=f"⬇️ Download {level} Audio",
                data=file,
                file_name=os.path.basename(audio_path),
                mime="audio/mpeg"
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Podcast script section below audio
        st.markdown("#### 📝 Podcast Script", unsafe_allow_html=True)
        html_script = (
                "<div style='height:300px; overflow-y:auto; border:1px solid #ddd; padding:10px; text-align:left;'>"
                + trimmed_dialogue.replace("\n", "<br>") +
                "</div>"
        )
        st.markdown(html_script, unsafe_allow_html=True)

        # Download script button below the script
        st.download_button(
            label=f"⬇️ Download {level} Script",
            data=trimmed_dialogue,
            file_name=f"podcast_script_{level.lower().replace(' ', '_')}.txt",
            mime="text/plain"
        )
