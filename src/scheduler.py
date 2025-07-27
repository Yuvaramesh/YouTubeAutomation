import schedule
import time
import threading
from datetime import datetime, timedelta
from src.excel_processor import ExcelProcessor
from src.video_generator import VideoGenerator
from src.youtube_uploader import YouTubeUploader
import logging
from config.settings import Config

class VideoScheduler:
    def __init__(self):
        self.excel_processor = ExcelProcessor()
        self.video_generator = VideoGenerator()
        self.youtube_uploader = YouTubeUploader()
        self.setup_logging()
        self.current_row = 0
    
    def setup_logging(self):
        logging.basicConfig(
            filename=f'{Config.LOGS_DIR}/scheduler.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def process_video(self):
        """Process one video from Excel data"""
        try:
            # Get video data
            video_data = self.excel_processor.get_video_data(self.current_row)
            
            # Generate video
            video_path = self.video_generator.generate_video(video_data)
            
            # Upload to YouTube
            video_id = self.youtube_uploader.upload_video(video_path, video_data)
            
            # Schedule if time specified
            scheduled_time = video_data['quote'].get('scheduled_time')
            if scheduled_time:
                self.youtube_uploader.schedule_video(video_id, scheduled_time)
            
            # Clean up video file
            import os
            if os.path.exists(video_path):
                os.remove(video_path)
            
            self.logger.info(f"Successfully processed video {self.current_row}")
            self.current_row += 1
            
        except Exception as e:
            self.logger.error(f"Error processing video: {str(e)}")
            raise
    
    def schedule_daily_video(self, time_str: str = "09:00"):
        """Schedule daily video creation"""
        schedule.every().day.at(time_str).do(self.process_video)
        self.logger.info(f"Scheduled daily video creation at {time_str}")
    
    def schedule_multiple_videos(self, times: list):
        """Schedule multiple videos per day"""
        for time_str in times:
            schedule.every().day.at(time_str).do(self.process_video)
        self.logger.info(f"Scheduled videos at times: {times}")
    
    def run_scheduler(self):
        """Run the scheduler in background"""
        def scheduler_thread():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        thread = threading.Thread(target=scheduler_thread, daemon=True)
        thread.start()
        self.logger.info("Scheduler started in background")