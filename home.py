# prompt: Create a streamlit app with a button to upload a youtube link, after uploading link, one button for transcription process. Then 2 options are popped up: showing transcription or sending summary text of that transcription. Do all these processes according to this notebook and these codes

import streamlit as st
from email.message import EmailMessage
import ssl
import smtplib
from llama_hub.youtube_transcript import YoutubeTranscriptReader
from transformers import pipeline
#!pip install datasets llama_hub llama_index youtube_transcript_api

import subprocess

subprocess.run(["pip", "install", "datasets", "llama_hub", "llama_index", "youtube_transcript_api"])


def upload_file():
  uploaded_file = st.file_uploader("Choose a file")
  from youtube_transcript_api import TranscriptsDisabled

  try:
      transcripts = YouTubeTranscriptApi.get_transcript(video_id)
  except TranscriptsDisabled:
      print(f"Transcripts are disabled for the video with ID: {video_id}")
      transcripts = []
    
  if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    return bytes_data


def main():
  st.title("YouTube Transcription and Summarization")

  # Upload YouTube link
  st.write("Upload a YouTube link:")
  youtube_link = st.text_input("YouTube link")

  # Transcribe YouTube video
  if st.button("Transcribe"):
    loader = YoutubeTranscriptReader()
    documents = loader.load_data(ytlinks=[youtube_link])
    var = str(documents).split('text')
    var2 = var[1][2:-1]
    summarizer = pipeline("summarization", model="Falconsai/text_summarization")
    t = summarizer(var2, max_length=230, min_length=30, do_sample=False)
    summary_text = t[0]['summary_text']
    txt_sum = var2.split('\\n')

    st.session_state['summary'] = summary_text
    st.session_state['transciption'] = var2
  

  if 'transcription' in st.session_state:
    # Show transcription or send summary text
    st.write('Choose an option:')
    option = st.selectbox('Options:', ('-', 'Show transcription', 'Send summary text'))
    if option == 'Show transcription':
        #st.write(var2)
      st.write('Hello')
    elif option == 'Send summary text':
      email_sender = 'agayev.m2002@gmail.com'
      email_password = 'aaku gufo lswj ekqx'
      email_receiver = 'murad.02.mm@gmail.com'
  
      subject = 'Youtube Transcription'
      body = summary_text
  
      em = EmailMessage()
      em['From'] = email_sender
      em['To'] = email_receiver
      em['Subject'] = subject
      em.set_content(body)
  
      context = ssl.create_default_context()
  
      """try:
          with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
              smtp.set_debuglevel(1)  # Enable SMTP debugging
              smtp.login(email_sender, email_password)
              smtp.sendmail(email_sender, email_receiver, em.as_string())
          st.write("Email sent successfully!")
      except Exception as e:
          st.error(f"Error sending email: {str(e)}")"""
        
      with smtplib.SMTP_SSL('smtp.gmail.com', 465, context = context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
        st.write("Email sent successfully!")
    else:
      st.write('Transcribe first!')


if __name__ == "__main__":
  main()
