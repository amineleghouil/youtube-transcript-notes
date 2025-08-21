import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_transcript(video_url):
    try:
        video_id = video_url.split("=")[1]
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcripts.find_transcript(['en'])
        except NoTranscriptFound:
            transcript = list(transcripts)[0]
        transcript_data = transcript.fetch()
        transcript_text = " ".join([item["text"] for item in transcript_data])
        return transcript_text
    except (TranscriptsDisabled, NoTranscriptFound):
        return None
    except Exception:
        return None

def generate_notes(input_text, prompt):
    model = genai.GenerativeModel("models/gemini-2.5-pro")
    response = model.generate_content(prompt + input_text)
    try:
        return response.text
    except ValueError:
        if hasattr(response, "candidates") and len(response.candidates) > 0:
            return response.candidates[0].content[0].text
        return "⚠️ Could not generate notes."

prompt = """
You are an expert note-taker. Your task is:
1. Summarize the YouTube transcript into clear, well-structured notes.
2. Break down the content by sections or topics.
3. Highlight key insights, definitions, and examples.
4. Provide a concise final summary at the end.
"""

st.title("🎥 YouTube Transcript → Detailed Notes Converter")
youtube_url = st.text_input("Enter YouTube Video Link:")

if youtube_url:
    video_id = youtube_url.split("=")[1]
    st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    transcript_text = extract_transcript(youtube_url)
    
    if st.button("Generate Notes"):
        if transcript_text:
            notes = generate_notes(transcript_text, prompt)
        else:
            fallback_text = f"Video title and description for {youtube_url}"
            notes = generate_notes(fallback_text, prompt)
        st.subheader("📝 Detailed Notes")
        st.write(notes)
