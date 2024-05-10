import time
import streamlit as st
import upload_to_s3

# title
st.title("Minute of Meeting Generator")


file = st.radio(
    "Choose option:",
    ["File Upload", "S3 URI"])
    
# created form to upload file
if file == "File Upload":
    form = st.form("Basic")
    video_upload = form.file_uploader("Upload Video", type=["mp4"])
    submit = form.form_submit_button("Upload")
    # vlaidating the form.
    if submit:
        if video_upload is None:
            alert = st.warning("Please upload a file 💀💀")
            time.sleep(2)
            alert.empty()
        else:
            with st.spinner("uploading........"):
                time.sleep(10)
            #st.write(video_upload)
            alert = st.success("Uploaded to S3 Bucket🤘🤘🤘🤘")
            time.sleep(2)
            alert.empty()
            upload_to_s3.upload_to_bucket(video_upload)
            # s3_file_name = upload_to_s3.upload_to_bucket(video_upload)
            # st.write(s3_file_name)
            s3_file_name = st.session_state.video_name
            # st.write(s3_file_name)
            st.info("Intializing Speech to Text")
            upload_to_s3.transcribe_init(s3_file_name)

            
            st.snow()

if file == "S3 URI":
    s3_file_name = st.text_input("Paste your S3 URI here....")
    # time.sleep(4)
    if s3_file_name == "":
        alert = st.warning("Paste your S3 URI.....")
        time.sleep(1.2)
        alert.empty()
    else:
        #st.write(s3_file_name)
        text = s3_file_name.split('/')
        s3_bucket_name = text[2]
        s3_file_name = text[3]
        # st.write(f'{s3_bucket_name}/{s3_file_name}')
        upload_to_s3.transcribe_init(s3_file_name)
        
# s3://minuteofmeetingbucket/858eb6ac7cWeekly Meeting Example.mp4
# vlaidating the form.
# if submit:
#     if video_upload is None:
#         alert = st.warning("Please upload a file 💀💀")
#         time.sleep(2)
#         alert.empty()
#     else:
#         with st.spinner("uploading........"):
#             time.sleep(10)
#         #st.write(video_upload)
#         alert = st.success("Uploaded🤘🤘🤘🤘")
#         time.sleep(2)
#         alert.empty()
#         upload_to_s3.upload_to_bucket(video_upload)
#         # s3_file_name = upload_to_s3.upload_to_bucket(video_upload)
#         # st.write(s3_file_name)
#         s3_file_name = st.session_state.video_name
#         st.write(s3_file_name)
#         # upload_to_s3.transcribe_init(s3_file_name)
        


        #st.snow()
        


    