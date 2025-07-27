import os
import random
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *
from moviepy.video.fx import resize
import textwrap
from config.settings import Config
import logging

class VideoGenerator:
    def __init__(self):
        self.setup_logging()
        Config.ensure_directories()
    
    def setup_logging(self):
        logging.basicConfig(
            filename=f'{Config.LOGS_DIR}/video_generator.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def create_background_image(self, width: int, height: int) -> str:
        """Create a gradient background image"""
        # Create gradient background
        img = Image.new('RGB', (width, height), color='black')
        draw = ImageDraw.Draw(img)
        
        # Create gradient effect
        for i in range(height):
            color_value = int(255 * (1 - i / height * 0.3))  # Dark gradient
            color = (color_value // 3, color_value // 4, color_value // 2)  # Blue-ish dark
            draw.line([(0, i), (width, i)], fill=color)
        
        bg_path = f"{Config.TEMP_DIR}/background.png"
        img.save(bg_path)
        return bg_path
    
    def create_text_image(self, text: str, width: int, height: int) -> str:
        """Create an image with text overlay"""
        # Create transparent image for text
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to load font, fallback to default if not available
        try:
            font = ImageFont.truetype(Config.DEFAULT_FONT, Config.FONT_SIZE)
        except:
            font = ImageFont.load_default()
            self.logger.warning("Using default font as custom font not found")
        
        # Wrap text to fit within image
        wrapped_text = textwrap.fill(text, width=40)  # Adjust based on font size
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        # Draw text with outline for better readability
        outline_width = 2
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.multiline_text((x + dx, y + dy), wrapped_text, 
                                      font=font, fill='black', align='center')
        
        # Draw main text
        draw.multiline_text((x, y), wrapped_text, font=font, fill='white', align='center')
        
        text_path = f"{Config.TEMP_DIR}/text_overlay.png"
        img.save(text_path)
        return text_path
    
    def generate_video(self, video_data: dict) -> str:
        """Generate video from quote and music data"""
        try:
            quote_text = video_data['quote']['quote']
            music_file = video_data['music']['music_file']
            
            self.logger.info(f"Generating video for quote: {quote_text[:50]}...")
            
            # Create background
            bg_path = self.create_background_image(Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT)
            
            # Create text overlay
            text_path = self.create_text_image(quote_text, Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT)
            
            # Create video clip from background
            bg_clip = ImageClip(bg_path, duration=Config.VIDEO_DURATION)
            
            # Create text clip
            text_clip = ImageClip(text_path, duration=Config.VIDEO_DURATION).set_opacity(0.9)
            
            # Composite video
            video = CompositeVideoClip([bg_clip, text_clip])
            
            # Add music if available
            if music_file and os.path.exists(music_file):
                audio = AudioFileClip(music_file)
                # Trim or loop audio to match video duration
                if audio.duration > Config.VIDEO_DURATION:
                    audio = audio.subclip(0, Config.VIDEO_DURATION)
                elif audio.duration < Config.VIDEO_DURATION:
                    # Loop audio to match video duration
                    loops = int(Config.VIDEO_DURATION / audio.duration) + 1
                    audio = concatenate_audioclips([audio] * loops).subclip(0, Config.VIDEO_DURATION)
                
                audio = audio.volumex(0.3)  # Lower volume for background music
                video = video.set_audio(audio)
            
            # Set video properties
            video = video.set_fps(Config.VIDEO_FPS)
            
            # Output path
            output_path = f"{Config.TEMP_DIR}/generated_video_{random.randint(1000, 9999)}.mp4"
            
            # Write video file
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=f"{Config.TEMP_DIR}/temp_audio.m4a",
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Clean up temporary files
            for temp_file in [bg_path, text_path]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            self.logger.info(f"Video generated successfully: {output_path}")
            return output_path
        
        except Exception as e:
            self.logger.error(f"Error generating video: {str(e)}")
            raise
