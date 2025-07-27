import os
import sys
from src.excel_processor import ExcelProcessor
from src.video_generator import VideoGenerator
from src.youtube_uploader import YouTubeUploader
from src.scheduler import VideoScheduler
from config.settings import Config
import logging
import time
def setup_main_logging():
    logging.basicConfig(
        filename=f'{Config.LOGS_DIR}/main.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def main():
    """Main function to run the YouTube automation system"""
    logger = setup_main_logging()
    
    try:
        # Ensure directories exist
        Config.ensure_directories()
        
        print("YouTube Video Automation System")
        print("=" * 40)
        
        # Initialize components
        excel_processor = ExcelProcessor()
        video_generator = VideoGenerator()
        youtube_uploader = YouTubeUploader()
        scheduler = VideoScheduler()
        
        # Menu options
        while True:
            print("\nOptions:")
            print("1. Process single video")
            print("2. Schedule daily videos")
            print("3. Schedule multiple videos per day")
            print("4. Test Excel data reading")
            print("5. Exit")
            
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                try:
                    row_index = int(input("Enter row index (0-based): "))
                    scheduler.current_row = row_index
                    scheduler.process_video()
                    print("Video processed successfully!")
                except Exception as e:
                    print(f"Error processing video: {str(e)}")
            
            elif choice == '2':
                time_str = input("Enter time (HH:MM format, default 09:00): ").strip()
                if not time_str:
                    time_str = "09:00"
                scheduler.schedule_daily_video(time_str)
                scheduler.run_scheduler()
                print(f"Daily video scheduled at {time_str}")
                print("Scheduler running in background. Press Ctrl+C to stop.")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nScheduler stopped.")
            
            elif choice == '3':
                times_input = input("Enter times separated by comma (e.g., 09:00,15:00,21:00): ")
                times = [t.strip() for t in times_input.split(',')]
                scheduler.schedule_multiple_videos(times)
                scheduler.run_scheduler()
                print(f"Videos scheduled at times: {times}")
                print("Scheduler running in background. Press Ctrl+C to stop.")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\nScheduler stopped.")
            
            elif choice == '4':
                try:
                    quotes_df, music_df = excel_processor.read_excel_data()
                    print(f"Quotes data shape: {quotes_df.shape}")
                    print(f"Music data shape: {music_df.shape}")
                    print("\nQuotes columns:", list(quotes_df.columns))
                    print("Music columns:", list(music_df.columns))
                    print("\nFirst quote:")
                    print(quotes_df.iloc[0].to_dict())
                except Exception as e:
                    print(f"Error reading Excel data: {str(e)}")
            
            elif choice == '5':
                print("Exiting...")
                break
            
            else:
                print("Invalid choice. Please try again.")
    
    except Exception as e:
        logger.error(f"Main application error: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()