import streamlit as st
from email.message import EmailMessage
import ssl
import smtplib
import time
import subprocess
import os

# Install dependencies first
subprocess.run(["pip", "install", "youtube_transcript_api"])

# Direct implementation of YouTube transcript reading without using llama_hub
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(youtube_url):
    """Extract video ID from YouTube URL."""
    if "youtu.be" in youtube_url:
        return youtube_url.split("/")[-1].split("?")[0]
    elif "youtube.com" in youtube_url:
        if "v=" in youtube_url:
            return youtube_url.split("v=")[1].split("&")[0]
    return youtube_url  # Return as is if already a video ID

def load_youtube_transcript(youtube_url, language='en'):
    """Load transcript from YouTube video with language support."""
    video_id = get_video_id(youtube_url)
    try:
        # First, try to get transcript in specified language
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        transcript_text = " ".join([entry["text"] for entry in transcript_list])
        return transcript_text, language
    except Exception as e:
        # If specified language fails, try to find available languages
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_languages = []
            
            # Try to find auto-generated transcripts
            for transcript in transcript_list:
                lang_code = transcript.language_code
                is_generated = transcript.is_generated
                is_translatable = transcript.is_translatable
                available_languages.append({
                    "code": lang_code,
                    "generated": is_generated,
                    "translatable": is_translatable
                })
                
                # If we find a transcript, use it
                if is_generated or lang_code == 'de':
                    transcript_data = transcript.fetch()
                    transcript_text = " ".join([entry["text"] for entry in transcript_data])
                    return transcript_text, lang_code
                    
            # If we get here, no suitable transcript was found
            return f"No suitable transcript found. Available languages: {available_languages}", None
            
        except Exception as sub_e:
            return f"Error loading transcript: {str(e)}\nAdditional error: {str(sub_e)}", None

def try_load_summarizer():
    """Try to load the summarizer model, with error handling."""
    try:
        from transformers import pipeline
        # Set environment variable to disable SSL verification if that's the issue
        os.environ['CURL_CA_BUNDLE'] = ''
        os.environ['REQUESTS_CA_BUNDLE'] = ''
        summarizer = pipeline("summarization", model="Falconsai/text_summarization")
        return summarizer, None
    except Exception as e:
        return None, str(e)

def main():
    st.title("YouTube Transcription and Summarization")
    
    # Try to read password file
    try:
    # First try to get from Streamlit secrets (for cloud deployment)
        password = st.secrets["gmail"]["password"]
        st.write("Password accessed successfully!")

    except Exception:
        try:
            # Fall back to local file (for local development)
            with open('password.txt', 'r') as file:
                password = file.read().strip()
        except Exception as e:
            password = ""
            st.warning("Unable to load password. Email functionality may not work.")

    # Upload YouTube link
    st.write("Upload a YouTube link:")
    youtube_link = st.text_input("YouTube link")
    
    # Language selection
    language_options = ['en', 'de']
    selected_language = st.selectbox("Select preferred language", language_options)

    # Initialize session state for summarizer status
    if 'summarizer_loaded' not in st.session_state:
        st.session_state['summarizer_loaded'] = False
        st.session_state['summarizer_error'] = None
    
    # Try loading the summarizer only once
    if not st.session_state['summarizer_loaded'] and st.session_state['summarizer_error'] is None:
        summarizer, error = try_load_summarizer()
        if summarizer:
            st.session_state['summarizer'] = summarizer
            st.session_state['summarizer_loaded'] = True
        else:
            st.session_state['summarizer_error'] = error
            st.warning(f"Unable to load summarization model. Only transcription will be available. Error: {error}")

    # Transcribe YouTube video
    if st.button("Transcribe"):
        progress_text = 'Transcribing . . .'
        my_bar = st.sidebar.progress(0, text=progress_text)
        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar.progress(percent_complete+1, text=progress_text)
        my_bar.empty()
        
        # Use our new function with language support
        transcript_text, detected_language = load_youtube_transcript(youtube_link, selected_language)
        
        # Check if transcript loading was successful
        if transcript_text.startswith("Error") or transcript_text.startswith("No suitable"):
            st.error(transcript_text)
            return
            
        # Split text for 'cleaner' display
        txt_trans = transcript_text.split('. ')
        
        # Only try summarization if model loaded successfully
        if st.session_state['summarizer_loaded']:
            try:
                # Summarize the transcript
                summary_input = transcript_text[:4000]
                t = st.session_state['summarizer'](summary_input, max_length=230, min_length=30, do_sample=False)
                summary_text = t[0]['summary_text']
                st.session_state['summary'] = summary_text
                st.success(f'Transcription (in {detected_language}) and summarization is done!')
            except Exception as e:
                st.warning(f"Summarization failed: {str(e)}")
                st.session_state['summary'] = "Summarization failed due to an error."
                st.success(f'Transcription (in {detected_language}) is done!')
        else:
            st.session_state['summary'] = "Summarization not available due to model loading error."
            st.success(f'Transcription (in {detected_language}) is done!')

        # Store in session state
        st.session_state['transcription'] = transcript_text
        st.session_state['clean'] = txt_trans
        st.session_state['language'] = detected_language
    
    # Show transcription or send text
    if 'transcription' in st.session_state:
        transcript_text = st.session_state['transcription']
        txt_trans = st.session_state['clean']
        summary_text = st.session_state.get('summary', "Summarization not available")
        detected_language = st.session_state.get('language', 'unknown')
        
        options = [
            '-', 
            'Show transcription in a raw format', 
            'Show transcription in a neater format', 
            'Send transcription text via email'
        ]
        
        # Only add summary options if summarization was successful
        if st.session_state['summarizer_loaded'] and not summary_text.startswith("Summarization failed"):
            options.extend(['Show summary', 'Send summary text via email'])
        
        st.write('Choose an option:')
        option = st.selectbox('Options:', options)
        
        if option == 'Show transcription in a raw format':
            st.write(f"Language: {detected_language}")
            st.write(transcript_text)
        elif option == 'Show transcription in a neater format':
            st.write(f"Language: {detected_language}")
            st.write(txt_trans)
        elif option == 'Show summary' and st.session_state['summarizer_loaded']:
            st.write(summary_text)
        elif option == 'Send summary text via email' or option == 'Send transcription text via email':
            receiver = st.text_input('Input your mail address: ')
            email_sender = 'agayev.m2002@gmail.com'
            email_password = password
            email_receiver = receiver
            
            # Determine which content to send
            if option == 'Send summary text via email':
                subject = 'YouTube Video Summary'
                body = summary_text
            else:  # Send transcription
                subject = f'YouTube Video Transcription (in {detected_language})'
                body = transcript_text
            
            if st.button("Send Email"):
                if not password:
                    st.error("Email password is not available. Please check your password.txt file.")
                    return
                    
                em = EmailMessage()
                em['From'] = email_sender
                em['To'] = email_receiver
                em['Subject'] = subject
                em.set_content(body)
                
                context = ssl.create_default_context()
                
                try:
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                        smtp.set_debuglevel(1)  # Enable SMTP debugging
                        smtp.login(email_sender, email_password)
                        smtp.sendmail(email_sender, email_receiver, em.as_string())
                    st.write("Email sent successfully!")
                except Exception as e:
                    st.error(f"Error sending email: {str(e)}")

if __name__ == "__main__":
    main()