import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # YouTube API Settings
    YOUTUBE_CLIENT_SECRET_FILE = 'config/client_secret_838402917099-ifslkerqpdcmqn57glb6c53r7ho8i7uc.apps.googleusercontent.com.json'
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    YOUTUBE_UPLOAD_SCOPE = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]
    
    # Video Settings
    VIDEO_WIDTH = 1920
    VIDEO_HEIGHT = 1080
    VIDEO_FPS = 30
    VIDEO_DURATION = 60  # seconds
    
    # Paths
    EXCEL_FILE_PATH = 'data/video_data.xlsx'
    TEMP_DIR = 'assets/temp'
    FONTS_DIR = 'assets/fonts'
    BACKGROUNDS_DIR = 'assets/backgrounds'
    LOGS_DIR = 'logs'
    
    # Sheets Configuration
    QUOTES_SHEET = 'Quotes Sheet'
    MUSIC_SHEET = 'Music Sheet'
    
    # Font Settings
    DEFAULT_FONT = 'assets/fonts/arial.ttf'
    FONT_SIZE = 60
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [cls.TEMP_DIR, cls.FONTS_DIR, cls.BACKGROUNDS_DIR, cls.LOGS_DIR]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)