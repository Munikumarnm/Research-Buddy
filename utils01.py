# utils01.py

# -----------------------------------------------------------------------------
# 📦 Utility Functions for Research Buddy (PDF-to-Podcast Generator)
# -----------------------------------------------------------------------------
# This module includes helper functions to:
# - Extract text from PDF
# - Split long text into manageable chunks
# - Summarize content using a Hugging Face transformer
# - Generate podcast-style dialogue script
# - Convert script to audio using gTTS
# - Trim summaries to match selected detail level
# -----------------------------------------------------------------------------

import os
import fitz  # PyMuPDF
import tempfile
import uuid
import textwrap
from gtts import gTTS
from transformers import pipeline

# -----------------------------------------------------------------------------
# Load the summarizer once using Hugging Face pipeline
# Using 'distilbart-cnn' for faster, lightweight summarization
# -----------------------------------------------------------------------------
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# -----------------------------------------------------------------------------
# 1. Extract raw text from a PDF using PyMuPDF
# -----------------------------------------------------------------------------
def extract_text_from_pdf(uploaded_file):
    """
    Extracts and returns text content from an uploaded PDF file.

    Args:
        uploaded_file: Streamlit file uploader object

    Returns:
        str: Complete extracted text from the PDF
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name

        # Open the PDF and extract text
        doc = fitz.open(tmp_file_path)
        text = " ".join([page.get_text() for page in doc])
        doc.close()

        # Delete temp file
        os.remove(tmp_file_path)

        return text

    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# -----------------------------------------------------------------------------
# 2. Split text into chunks for summarization
# -----------------------------------------------------------------------------
def split_text(text, max_length=2000):
    """
    Splits large text into smaller fixed-length chunks.

    Args:
        text (str): Raw extracted text
        max_length (int): Maximum characters per chunk

    Returns:
        list: List of text chunks
    """
    return textwrap.wrap(text, width=max_length)

# -----------------------------------------------------------------------------
# 3. Summarize each chunk using transformer model
# -----------------------------------------------------------------------------
def summarize_chunks(chunks):
    """
    Generates summaries for each text chunk.

    Args:
        chunks (list): List of raw text chunks

    Returns:
        list: List of summarized strings
    """
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=200, min_length=50, do_sample=False)[0]['summary_text']
        summaries.append(summary)
    return summaries

# -----------------------------------------------------------------------------
# 4. Generate podcast-style dialogue from summary text
# -----------------------------------------------------------------------------
def generate_dialogue(summary_text):
    """
    Wraps summary into a podcast script format.

    Args:
        summary_text (str): Summarized content

    Returns:
        str: Dialogue-style podcast script
    """
    return f"""
Hi everyone, welcome to this podcast.
Today, we are discussing a fascinating research paper.

Let me give you an overview of the content:
{summary_text}

Hope you find this episode insightful!
"""

# -----------------------------------------------------------------------------
# 5. Convert dialogue to MP3 using Google Text-to-Speech
# -----------------------------------------------------------------------------
def generate_audio(text, level="DeepDive", output_dir="audio"):
    """
    Converts script text to speech and saves as an MP3 file.

    Args:
        text (str): The podcast script
        level (str): Summary level (for naming)
        output_dir (str): Output folder for audio files

    Returns:
        str: File path to saved MP3 audio
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = f"podcast_{level}_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(output_dir, filename)
    tts = gTTS(text)
    tts.save(filepath)
    return filepath

# -----------------------------------------------------------------------------
# 6. Trim summary based on user's selected detail level
# -----------------------------------------------------------------------------
def trim_summary(summary_text, level):
    """
    Trims the full summary based on user-selected detail level.

    Args:
        summary_text (str): The full combined summary
        level (str): One of 'Summarize', 'Brief', or 'Deep Dive'

    Returns:
        str: Trimmed summary
    """
    paragraphs = summary_text.split("\n\n")
    if level == "Summarize":
        return paragraphs[0] if paragraphs else summary_text
    elif level == "Brief":
        return "\n\n".join(paragraphs[:3]) if len(paragraphs) >= 3 else summary_text
    else:  # Deep Dive
        return summary_text
