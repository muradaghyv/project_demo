import streamlit as st
from email.message import EmailMessage
import ssl
import smtplib
from llama_hub.youtube_transcript import YoutubeTranscriptReader
from transformers import pipeline
import time

import subprocess

subprocess.run(["pip", "install", "datasets", "llama_hub", "llama_index", "youtube_transcript_api"])

def upload_file():
  uploaded_file = st.file_uploader("Choose a file")
  from youtube_transcript_api import TranscriptsDisabled

  """try:
      transcripts = YouTubeTranscriptApi.get_transcript(video_id)
  except TranscriptsDisabled:
      print(f"Transcripts are disabled for the video with ID: {video_id}")
      transcripts = []"""
    
  if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
  return bytes_data


def main():
  st.title("YouTube Transcription and Summarization")
  
  with open('password.txt', 'r') as file:
      # Read the entire content of the file
      file_content = file.read()
    
  password = file_content

  # Upload YouTube link
  st.write("Upload a YouTube link:")
  youtube_link = st.text_input("YouTube link")

  # Transcribe YouTube video
  if st.button("Transcribe"):
    progress_text = 'Transcibing . . .'
    my_bar = st.sidebar.progress(0, text = progress_text)
    for percent_complete in range(100):
      time.sleep(0.01)
      my_bar.progress(percent_complete+1, text = progress_text)
    my_bar.empty()
    loader = YoutubeTranscriptReader()
    documents = loader.load_data(ytlinks=[youtube_link])
    var = str(documents).split('text')
    var2 = var[1][2:-43]
    summarizer = pipeline("summarization", model="Falconsai/text_summarization")
    t = summarizer(var2, max_length=230, min_length=30, do_sample=False)
    summary_text = t[0]['summary_text']
    txt_trans = var2.split('\\n')
    st.success('Trancription and summarization is done!')

    st.session_state['summary'] = summary_text
    st.session_state['transcription'] = var2
    st.session_state['clean'] = txt_trans
    
  # Show transcription or send summary text
  if 'transcription' in st.session_state:
    var2 = st.session_state['transcription']
    txt_trans = st.session_state['clean']
    summary_text = st.session_state['summary']
    st.write('Choose an option:')
    option = st.selectbox('Options:', ('-', 'Show transcription in a raw format', 'Show transcription in a neater format', 'Show summary', 'Send summary text'))
    if option == 'Show transcription in a raw format':
        st.write(var2)
    elif option == 'Show transcription in a neater format':
        st.write(txt_trans)
    elif option == 'Show summary':
        st.write(summary_text)
    elif option == 'Send summary text':
        receiver = st.text_input('Input your mail address: ')
        email_sender = 'agayev.m2002@gmail.com'
        email_password = password
        email_receiver = receiver
  
        subject = 'Youtube Transcription'
        body = summary_text
        
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
  
