import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from config.settings import Config
import logging

class YouTubeUploader:
    def __init__(self):
        self.setup_logging()
        self.youtube = None
    
    def setup_logging(self):
        logging.basicConfig(
            filename=f'{Config.LOGS_DIR}/youtube_uploader.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        token_file = 'config/token.pickle'  # Define token path

    # Load existing credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)

    # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.YOUTUBE_CLIENT_SECRET_FILE, Config.YOUTUBE_UPLOAD_SCOPE)
                creds = flow.run_local_server(port=0)

        # Save credentials for next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.youtube = build(Config.YOUTUBE_API_SERVICE_NAME, Config.YOUTUBE_API_VERSION, credentials=creds)
        self.logger.info("YouTube API authenticated successfully")

    def upload_video(self, video_path: str, video_data: dict) -> str:
        """Upload video to YouTube"""
        if not self.youtube:
            self.authenticate()
        
        try:
            title = video_data['quote']['title']
            description = video_data['quote']['description']
            tags = video_data['quote']['tags'].split(',') if video_data['quote']['tags'] else []
            
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': [tag.strip() for tag in tags],
                    'categoryId': '22'  # People & Blogs category
                },
                'status': {
                    'privacyStatus': 'private',  # Start as private, can be changed later
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload object
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            
            # Execute upload
            insert_request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = insert_request.execute()
            video_id = response['id']
            
            self.logger.info(f"Video uploaded successfully. Video ID: {video_id}")
            return video_id
        
        except Exception as e:
            self.logger.error(f"Error uploading video: {str(e)}")
            raise
    
    def schedule_video(self, video_id: str, publish_time: str):
        """Schedule video for publishing"""
        try:
            # Update video to be scheduled
            self.youtube.videos().update(
                part='status',
                body={
                    'id': video_id,
                    'status': {
                        'privacyStatus': 'private',
                        'publishAt': publish_time,
                        'selfDeclaredMadeForKids': False
                    }
                }
            ).execute()
            
            self.logger.info(f"Video {video_id} scheduled for {publish_time}")
        
        except Exception as e:
            self.logger.error(f"Error scheduling video: {str(e)}")
            raise