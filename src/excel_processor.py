import pandas as pd
import logging
from typing import Dict, List, Tuple
from config.settings import Config

class ExcelProcessor:
    def __init__(self, excel_path: str = None):
        self.excel_path = excel_path or Config.EXCEL_FILE_PATH
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            filename=f'{Config.LOGS_DIR}/excel_processor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def read_excel_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Read quotes and music data from Excel file"""
        try:
            quotes_df = pd.read_excel(self.excel_path, sheet_name=Config.QUOTES_SHEET)
            music_df = pd.read_excel(self.excel_path, sheet_name=Config.MUSIC_SHEET)
            
            self.logger.info(f"Successfully read Excel data: {len(quotes_df)} quotes, {len(music_df)} music tracks")
            return quotes_df, music_df
        
        except Exception as e:
            self.logger.error(f"Error reading Excel file: {str(e)}")
            raise
    
    def validate_data(self, quotes_df: pd.DataFrame, music_df: pd.DataFrame) -> bool:
        """Validate required columns exist in dataframes"""
        required_quote_columns = ['quote', 'title', 'description', 'tags', 'scheduled_time']
        required_music_columns = ['music_file', 'duration', 'genre']
        
        quote_columns_valid = all(col in quotes_df.columns for col in required_quote_columns)
        music_columns_valid = all(col in music_df.columns for col in required_music_columns)
        
        if not quote_columns_valid:
            self.logger.error(f"Missing required columns in quotes sheet: {required_quote_columns}")
        
        if not music_columns_valid:
            self.logger.error(f"Missing required columns in music sheet: {required_music_columns}")
        
        return quote_columns_valid and music_columns_valid
    
    def get_video_data(self, row_index: int = 0) -> Dict:
        """Get video data for specific row"""
        quotes_df, music_df = self.read_excel_data()
        
        if not self.validate_data(quotes_df, music_df):
            raise ValueError("Invalid Excel data structure")
        
        if row_index >= len(quotes_df):
            raise IndexError(f"Row index {row_index} out of range")
        
        quote_data = quotes_df.iloc[row_index].to_dict()
        
        # Select random music if not specified
        import random
        music_data = music_df.iloc[random.randint(0, len(music_df) - 1)].to_dict()
        
        return {
            'quote': quote_data,
            'music': music_data
        }
