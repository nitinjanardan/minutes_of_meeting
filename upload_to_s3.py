import pathlib
import time
import boto3.session
import streamlit as st
import boto3
import os
import requests
import random
import string
import secrets
import json
import openai
from openai import OpenAI
from dotenv import load_dotenv, dotenv_values, find_dotenv
import csv
import datetime
from datetime import datetime
# ------------------------------------------------------------------------

#  Aws cred
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
#AWS_DEFAULT_REGION = "ap-south-1"
region = os.getenv("region")
bucket_name  = os.getenv("bucket_name")

#------------------------------------------------------------------------
# open ai cred
COMPLETIONS_MODEL = os.getenv("COMPLETIONS_MODEL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
openai.api_key = OPENAI_API_KEY
#---------------------------------------------------------------------------

# --------------------------------------------------------------------
# initializing boto client globally for all function
s3 = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name = region)
transcribe_client = boto3.client("transcribe",aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,region_name = region)

#----------------------------------------------------------------------------
# function to upload file to s3 bucket
def upload_to_bucket(video):
    #add random string before video file name
    uploaded_video = secrets.token_hex(5)+video.name
    st.session_state.video_name = uploaded_video
    #st.write(uploaded_video)
    with open(uploaded_video, "wb") as f:
        f.write(video.getvalue())
    #st.write(uploaded_video)
    file_upload = s3.upload_file(uploaded_video,bucket_name,uploaded_video)
    alert = st.success(f"File '{uploaded_video}' uploaded to '{bucket_name}'")
    time.sleep(2)
    alert.empty()
    return uploaded_video

#----------------------------------------------------------------------------
# function to initialize AWS transcribe and take data from s3 URI
def transcribe_init(updated_file_name):
    transcribe_client = boto3.client("transcribe",aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,region_name = region)
    file_uri = f's3://{bucket_name}/{updated_file_name}'
    global job_name
    job_name = f'mom_{secrets.token_hex(5)}'
   
    transcribe_job = transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={"MediaFileUri": file_uri},
        MediaFormat="mp4",
        LanguageCode="en-US",
    )

    job_name = transcribe_job['TranscriptionJob']['TranscriptionJobName']
    trans_job_status = transcribe_job['TranscriptionJob']['TranscriptionJobStatus']
    max_tries= 10
    job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
    # st.write(f'get transcription job : {job}')

       
    # function that extract text from speech 
       
    convert_speech_to_text(job_name)

#------------------------------------------------------------------------------
# function to extract text from speech
def convert_speech_to_text(job_name):
    s = st.info("Converting Speech to Text, Please wait...")
    time.sleep(2)
    s.empty()
    max_tries = 60
    while max_tries >0:
        max_tries -=1
        job = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = job['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ["COMPLETED"]:
            # st.write(f'Job Status {job_status}')
            link = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
            y = requests.get(link)
            text_speech = y.text
            
            global transcript
            json_object = json.loads(text_speech)
            transcript = json_object['results']['transcripts'][0]['transcript']
            
            call_llm_func(transcript)
            break
        else:
            # print(f"Waiting for {job_name}. Current status is {job_status}.")
            alert = st.text(f"Current status : {job_status}.")
            time.sleep(1)
            alert.empty()
        time.sleep(10)
    
#------------------------------------------------------------------------------
# fucntion to call LLM Function
def call_llm_func(transcript):
    # st.write("Inside call llmm final step")
    client = OpenAI()
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": f'The following is the transcript of a meeting. Please summarize the meeting in 5 actionable point: {transcript} '}
  ])

    res_message =response.choices[0].message.content
    global text
    text = res_message.split("\n\n")
    for i in text:
        st.write(i)
    store_trancript_llm()

# get llm function and json file 

def store_trancript_llm():
    bucketname ="transcriptandllmoutput"
    transcript_output =transcript
    llm_output = text
    mom_job_name =job_name
    with open(f'transcript_output.csv', 'w',encoding='utf-8') as transcript_output1:
        writer = csv.writer(transcript_output1)
        writer.writerow([transcript_output])
    print(transcript_output1.name)
    with open(f'llm_output.csv', 'w',encoding='utf-8') as llm_output1:
        writer = csv.writer(llm_output1)
        writer.writerow([llm_output])
    print(llm_output1.name)
    folder_name = mom_job_name
    date_time = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
    folder =f'{folder_name}-{date_time}'
    print(date_time)
    s3.put_object(Bucket=bucketname, Key=(folder+'/'))
    s3.upload_file(transcript_output1.name, bucketname,f'{folder}/{transcript_output1.name}')
    s3.upload_file(llm_output1.name, bucketname,f'{folder}/{llm_output1.name}')
    os.remove()


