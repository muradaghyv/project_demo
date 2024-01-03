# Transcription Agent

Final project of an Artificial Intelligence Bootcamp. 

This project consists of creating an agent for multiple purposes. This agent tool receives a YouTube link and prepares transcription of that video. 
Moreover, it summarizes this transcription and send it via e-mail.
That application can be used in various fields, for example it can be quite useful in terms of providing transcription of any video available on YouTube for disabled people. Furthermore, as because it summarizes the transcription, this summarization may be utilized for saving time, and so on.
I would like to mention which sources I have used to create that agent tool briefly.
2 main open sources have played a great role in this project: pipeline model from transformers library and YoutubeTranscriptReader from llama_hub.
YoutubeTranscriptReader is a data loader uploaded from llama_hub used for transcribing youtube videos, whereas pipeline model consists of multiple sub-models for distinct purposes. I have used this model for summarization. 
So, the agent takes youtube link as an input, transcribes it which is led into the pipeline and summarization is prepared and sent to the mail.
Other python libraries have been used for different objectives.
ssl, smtplib are used to send messages via e-mail, whereas email.message libray is used for constructing an e-mail message. This application has been deployed in streamlit, therefore streamlit library is applied.
