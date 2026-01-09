#!/usr/bin/env python3
"""
Performance utilities for MUD Analyzer
"""

import time
import threading
from typing import Optional, Callable, Any
from functools import wraps


class ProgressIndicator:
    """Improved progress indicator with better performance"""
    
    def __init__(self, message: str, style: str = "spinner"):
        self.message = message
        self.style = style
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._start_time = 0
    
    def start(self):
        """Start the progress indicator"""
        self.running = True
        self._start_time = time.time()
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop the progress indicator"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        
        # Clear the line and move to next line
        print("\r" + " " * 80 + "\r", end="", flush=True)
    
    def _animate(self):
        """Animation loop"""
        if self.style == "spinner":
            self._spinner_animation()
        elif self.style == "dots":
            self._dots_animation()
        else:
            self._simple_animation()
    
    def _spinner_animation(self):
        """Spinner animation"""
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        i = 0
        while self.running:
            elapsed = time.time() - self._start_time
            print(f"\r{chars[i % len(chars)]} {self.message} ({elapsed:.1f}s)", 
                  end="", flush=True)
            time.sleep(0.1)
            i += 1
    
    def _dots_animation(self):
        """Dots animation"""
        i = 0
        while self.running:
            dots = "." * (i % 4)
            elapsed = time.time() - self._start_time
            print(f"\r{self.message}{dots:<3} ({elapsed:.1f}s)", 
                  end="", flush=True)
            time.sleep(0.5)
            i += 1
    
    def _simple_animation(self):
        """Simple animation"""
        while self.running:
            elapsed = time.time() - self._start_time
            print(f"\r{self.message} ({elapsed:.1f}s)", end="", flush=True)
            time.sleep(0.5)


def with_progress(message: str, style: str = "spinner"):
    """Decorator to show progress during function execution"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            progress = ProgressIndicator(message, style)
            progress.start()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                progress.stop()
        return wrapper
    return decorator


class Timer:
    """Simple timer for performance measurement"""
    
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = 0
        self.end_time = 0
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        print(f"⏱️ {self.name} took {elapsed:.2f} seconds")
    
    def elapsed(self) -> float:
        """Get elapsed time"""
        if self.end_time > 0:
            return self.end_time - self.start_time
        return time.time() - self.start_time


def batch_process(items: list, batch_size: int = 100, 
                 progress_message: str = "Processing items"):
    """Process items in batches with progress indication"""
    total_items = len(items)
    
    for i in range(0, total_items, batch_size):
        batch = items[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_items + batch_size - 1) // batch_size
        
        print(f"\r{progress_message} (batch {batch_num}/{total_batches})", 
              end="", flush=True)
        
        yield batch
    
    print()  # New line after completion


def format_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"