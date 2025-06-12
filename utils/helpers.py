import re
import os
import sys
from typing import Optional, Dict, Any, Union

def validate_youtube_url(url: str) -> bool:
    """
    Validate if a string is a valid YouTube URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if valid YouTube URL, False otherwise
    """
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    match = re.match(youtube_regex, url)
    return bool(match)

def format_time(seconds: int) -> str:
    """
    Format seconds into a readable time string (HH:MM:SS).
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Formatted time string
    """
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def format_number(number: Union[int, float]) -> str:
    """
    Format a large number with commas for readability.
    
    Args:
        number: The number to format
        
    Returns:
        Formatted number string
    """
    if isinstance(number, int):
        return f"{number:,}"
    elif isinstance(number, float):
        return f"{number:,.2f}"
    return str(number)

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length and add ellipsis if needed.
    
    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_progress(iteration: int, total: int, prefix: str = '', suffix: str = '', 
                  bar_length: int = 50, fill: str = '█', print_end: str = "\r") -> None:
    """
    Print a progress bar to the terminal.
    
    Args:
        iteration: Current iteration
        total: Total iterations
        prefix: Prefix string
        suffix: Suffix string
        bar_length: Length of the progress bar
        fill: Fill character for the progress bar
        print_end: End character (e.g. "\r", "\n")
    """
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(bar_length * iteration // total)
    bar = fill * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    
    # Print new line when complete
    if iteration == total:
        print()

def get_file_size(file_path: str, format_size: bool = True) -> Union[int, str]:
    """
    Get the size of a file.
    
    Args:
        file_path: Path to the file
        format_size: Whether to format the size (e.g., KB, MB)
        
    Returns:
        File size in bytes or formatted string
    """
    if not os.path.isfile(file_path):
        return 0 if not format_size else "0 B"
    
    size_in_bytes = os.path.getsize(file_path)
    
    if not format_size:
        return size_in_bytes
    
    # Format the size
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0 or unit == 'TB':
            break
        size_in_bytes /= 1024.0
    
    return f"{size_in_bytes:.2f} {unit}"

def check_dependencies() -> Dict[str, bool]:
    """
    Check if required dependencies are installed.
    
    Returns:
        Dictionary mapping dependency names to installation status
    """
    dependencies = {
        "pytube": False,
        "whisper": False,
        "moviepy": False,
        "ollama": False,
        "chromadb": False,
        "sentence_transformers": False,
        "pyttsx3": False
    }
    
    # Check each dependency
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            pass
    
    return dependencies