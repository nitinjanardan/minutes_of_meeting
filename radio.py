import time
import streamlit as st

genre = st.radio(
    "Select mode for uploading your video",
    ["File Upload", "S3 URI"],
    )

if genre == "File Upload":
    st.write(f"You selected {genre}")
    form = st.form("Basic")
    video_upload = form.file_uploader("Upload Video", type=["mp4","mov","mkv","flv"])
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
        alert = st.success("Uploaded🤘🤘🤘🤘")
        time.sleep(2)
        alert.empty()
if genre == "S3 URI":
    st.write(f'You selected {genre}')
    st.text_input