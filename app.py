import streamlit as st
import pandas as pd
from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
import os

st.title("🎬 YouTube Quote Video Automation")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    df_quotes = pd.read_excel(uploaded_file, sheet_name=0)
    df_music = pd.read_excel(uploaded_file, sheet_name=1)

    st.success("Excel uploaded and read successfully!")
    st.write("📄 Quotes Sheet", df_quotes)
    st.write("🎵 Music Sheet", df_music)

    def generate_video(quote, title, music_path, output_file="output.mp4"):
        try:
            txt_clip = TextClip(quote, fontsize=50, color='white', size=(1280, 720), bg_color='black', method='caption')
            txt_clip = txt_clip.set_duration(10).set_position('center')
            audio = AudioFileClip(music_path).subclip(0, 10)
            video = CompositeVideoClip([txt_clip]).set_audio(audio)
            video.write_videofile(output_file, fps=24, logger=None)
            return output_file
        except Exception as e:
            st.error(f"❌ Error generating video: {e}")
            return None

    def authenticate_youtube():
        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        creds_file = "client_secret_838402917099-ifslkerqpdcmqn57glb6c53r7ho8i7uc.apps.googleusercontent.com.json"
        if not os.path.exists(creds_file):
            st.error("❌ OAuth client_secrets file not found.")
            return None
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                creds_file, SCOPES, redirect_uri="http://localhost:8090/oauth2callback"
            )
            creds = flow.run_local_server(port=8090)
            return build("youtube", "v3", credentials=creds)
        except Exception as e:
            st.error(f"❌ Authentication failed: {e}")
            return None

    def upload_video(youtube, file, title, description, publish_time):
        try:
            request_body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["quote", "motivation", "shorts"],
                    "categoryId": "22",
                },
                "status": {
                    "privacyStatus": "private",
                    "publishAt": publish_time,
                    "selfDeclaredMadeForKids": False,
                }
            }
            media = MediaFileUpload(file, chunksize=-1, resumable=True, mimetype="video/*")
            request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)
            response = request.execute()
            return response
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")
            return None

    if st.button("▶️ Start Automation"):
        youtube = authenticate_youtube()
        if youtube is None:
            st.stop()

        for i in range(len(df_quotes)):
            quote = df_quotes.loc[i, "quote"]
            title = df_quotes.loc[i, "title"]
            schedule_time = df_quotes.loc[i, "scheduled_time"]
            music_file = df_music.loc[i, "music_file"]

            video_file = generate_video(quote, title, music_file, output_file=f"video_{i}.mp4")
            if video_file:
                publish_at = datetime.strptime(str(schedule_time), "%Y-%m-%d %H:%M:%S").isoformat() + "Z"
                response = upload_video(youtube, video_file, title, quote, publish_at)
                if response:
                    st.success(f"✅ Uploaded Video ID: {response['id']}")
