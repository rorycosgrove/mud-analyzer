#!/usr/bin/env python3
"""
Error Handler - Centralized error handling for MUD Analyzer
"""

import sys
import traceback
from functools import wraps
from typing import Callable, Any


class MudAnalyzerError(Exception):
    """Base exception for MUD Analyzer"""
    pass


class DataLoadError(MudAnalyzerError):
    """Error loading data files"""
    pass


class CacheError(MudAnalyzerError):
    """Error with cache operations"""
    pass


class ValidationError(MudAnalyzerError):
    """Data validation error"""
    pass


def handle_errors(show_traceback: bool = False):
    """Decorator to handle errors gracefully"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                print("\\n⚠️ Operation cancelled by user")
                return None
            except MudAnalyzerError as e:
                print(f"❌ {e}")
                if show_traceback:
                    traceback.print_exc()
                return None
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                if show_traceback:
                    traceback.print_exc()
                return None
        return wrapper
    return decorator


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_str(value: Any, default: str = "") -> str:
    """Safely convert value to string"""
    try:
        return str(value) if value is not None else default
    except Exception:
        return default


def validate_vnum(vnum: Any) -> int:
    """Validate and convert vnum to int"""
    try:
        vnum_int = int(vnum)
        if vnum_int < 0:
            raise ValidationError(f"VNUM must be non-negative, got {vnum_int}")
        return vnum_int
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid VNUM: {vnum}")


def validate_zone_num(zone_num: Any) -> int:
    """Validate and convert zone number to int"""
    try:
        zone_int = int(zone_num)
        if zone_int < 0:
            raise ValidationError(f"Zone number must be non-negative, got {zone_int}")
        return zone_int
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid zone number: {zone_num}")


def log_error(message: str, exception: Exception = None) -> None:
    """Log error message"""
    print(f"❌ {message}")
    if exception and "--debug" in sys.argv:
        traceback.print_exception(type(exception), exception, exception.__traceback__)


def confirm_action(message: str, default: bool = False) -> bool:
    """Ask user to confirm an action"""
    suffix = " [Y/n]" if default else " [y/N]"
    try:
        response = input(f"{message}{suffix}: ").strip().lower()
        if not response:
            return default
        return response in ('y', 'yes', '1', 'true')
    except (KeyboardInterrupt, EOFError):
        return False