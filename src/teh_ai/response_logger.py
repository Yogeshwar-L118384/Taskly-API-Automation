"""
Module to log API responses to Excel file with metadata.
"""
import json
import time
from pathlib import Path
from datetime import datetime
import pandas as pd 
import os

# class ResponseLogger:
#     """Log API responses to Excel with query, response, status_code, and execution time."""
    
#     def __init__(self, output_dir="test_results"):
#         """Initialize logger with output directory."""
#         self.output_dir = Path(output_dir)
#         self.output_dir.mkdir(parents=True, exist_ok=True)
#         self.responses_file = self.output_dir / f"api_responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
#         self.data = []

class ResponseLogger:
    """Log API responses to Excel with query, response, status_code, and execution time."""

    def __init__(self, output_dir="test_results"):
        """Initialize logger with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Delete old Excel files before starting new logging
        self.cleanup_old_excels()

        # Create new Excel filename
        self.responses_file = self.output_dir / f"api_responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        self.data = []

    def cleanup_old_excels(self):
        """Delete old Excel files from previous runs."""
        for file in self.output_dir.glob("api_responses_*.xlsx"):
            try:
                file.unlink()
                print(f"Deleted old log file: {file}")
            except Exception as e:
                print(f"Could not delete file {file}: {e}")
    
    def log_response(self, query, response, status_code=200, execution_time=0):
        """Log a single API response to the list (will be written to Excel later).
        
        Args:
            query: The question/query sent to the API
            response: The response from the API (dict or str)
            status_code: HTTP status code (default 200)
            execution_time: Time taken to execute the request in seconds
        """
        # Convert response to JSON string if it's a dict
        response_str = json.dumps(response, indent=2) if isinstance(response, dict) else str(response)
        
        self.data.append({
            'Query': query,
            'Response': response_str,
            'Status_Code': status_code,
            'Execution_Time_Seconds': round(execution_time, 2),
            'Timestamp': datetime.now().isoformat()
        })
    
    def save_to_excel(self):
        """Save all logged responses to Excel file."""
        if not self.data:
            print("No responses to log.")
            return None
        
        df = pd.DataFrame(self.data)
        
        # Create Excel writer with formatting
        with pd.ExcelWriter(self.responses_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Responses')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Responses']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 for readability
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Responses logged to: {self.responses_file}")
        return self.responses_file
    
    def get_dataframe(self):
        """Get logged responses as a pandas DataFrame."""
        return pd.DataFrame(self.data)
    
    def clear(self):
        """Clear logged responses."""
        self.data = []


# Global logger instance (optional, for convenience)
_global_logger = None

def get_logger():
    """Get or create global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = ResponseLogger()
    return _global_logger


# def cleanup_old_excels(self):
#     """Delete old Excel files."""
#     for file in self.output_dir.glob("api_responses_*.xlsx"):
#         try:
#             file.unlink()
#         except Exception as e:
#             print(f"Could not delete file {file}: {e}")