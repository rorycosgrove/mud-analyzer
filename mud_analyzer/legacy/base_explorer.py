#!/usr/bin/env python3
"""
Base Explorer - Common functionality for all explorers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from mud_analyzer.data_service import data_service
from mud_analyzer.shared.config import config
from mud_analyzer.shared.error_handler import handle_errors, log_error


class BaseExplorer(ABC):
    """Base class for all explorers with common functionality"""
    
    def __init__(self):
        try:
            config.setup_working_directory()
            self.page_size = config.default_page_size
        except Exception as e:
            log_error(f"Failed to initialize base explorer: {e}")
            raise
    
    @abstractmethod
    def get_items(self) -> List[Dict[str, Any]]:
        """Get items to display - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def format_item(self, item: Dict[str, Any]) -> str:
        """Format item for display - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def show_item_details(self, item: Dict[str, Any]) -> None:
        """Show detailed item information - must be implemented by subclasses"""
        pass
    
    @handle_errors(show_traceback=False)
    def display_items(self, title: str, items: List[Dict[str, Any]]) -> None:
        """Generic paginated item display"""
        if not items:
            print(f"❌ No {title.lower()} found!")
            input("Press Enter to continue...")
            return
        
        page = 0
        
        while True:
            try:
                start_idx = page * self.page_size
                end_idx = min(start_idx + self.page_size, len(items))
                
                print(f"\n{title}")
                print(f"Page {page + 1} of {(len(items) - 1) // self.page_size + 1} | Total: {len(items)} items")
                print("=" * 80)
                
                for i, item in enumerate(items[start_idx:end_idx], 1):
                    formatted = self.format_item(item)
                    print(f"{i:2d}. {formatted}")
                
                print("\n" + "=" * 80)
                print("0. ← Back to menu")
                if page > 0:
                    print("p. ← Previous page")
                if end_idx < len(items):
                    print("n. → Next page")
                
                choice = input("\n➤ Select item number, n/p for pages, or 0: ").strip().lower()
                
                if choice == "0":
                    break
                elif choice == "n" and end_idx < len(items):
                    page += 1
                elif choice == "p" and page > 0:
                    page -= 1
                else:
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < (end_idx - start_idx):
                            item = items[start_idx + idx]
                            self.show_item_details(item)
                    except ValueError:
                        print("❌ Invalid choice! Please enter a number, 'n', 'p', or '0'.")
                        input("Press Enter to continue...")
            except KeyboardInterrupt:
                print("\n⚠️ Returning to menu...")
                break
            except Exception as e:
                log_error(f"Error displaying items: {e}")
                input("Press Enter to continue...")
                break
    
    def search_items(self, items: List[Dict[str, Any]], search_field: str) -> List[Dict[str, Any]]:
        """Generic search functionality"""
        search_term = input(f"\n🔍 Enter {search_field} to search for (or 'back' to return): ").strip().lower()
        if not search_term or search_term in ['back', 'b']:
            return []
        
        matches = []
        for item in items:
            # Extract searchable text based on item type
            searchable_text = self._get_searchable_text(item).lower()
            if search_term in searchable_text:
                matches.append(item)
        
        if not matches:
            print(f"❌ No items found matching '{search_term}'")
            input("Press Enter to continue...")
            return []
        
        print(f"Found {len(matches)} matches")
        return matches
    
    def _get_searchable_text(self, item: Dict[str, Any]) -> str:
        """Extract searchable text from item - can be overridden"""
        return str(item.get('name', ''))
    
    def show_menu(self, title: str, options: List[tuple]) -> Optional[str]:
        """Generic menu display"""
        print(f"\n{title}")
        print("=" * len(title))
        
        for key, description in options:
            print(f"{key}. {description}")
        
        return input("\n➤ Select option: ").strip()


class MenuMixin:
    """Mixin for common menu functionality"""
    
    def run_menu_loop(self, title: str, menu_options: Dict[str, tuple]) -> None:
        """Run a standard menu loop"""
        while True:
            try:
                print(f"\n{title}")
                print("=" * len(title))
                
                for key, (description, _) in menu_options.items():
                    print(f"{key}. {description}")
                
                choice = input("\n➤ Select option: ").strip()
                
                if choice == "0":
                    break
                elif choice in menu_options:
                    _, handler = menu_options[choice]
                    try:
                        handler()
                    except KeyboardInterrupt:
                        print("\n⚠️ Operation cancelled")
                    except Exception as e:
                        log_error(f"Menu handler error: {e}")
                        input("Press Enter to continue...")
                else:
                    valid_options = ", ".join(sorted(menu_options.keys()))
                    print(f"❌ Invalid choice! Please select from: {valid_options}")
                    input("Press Enter to continue...")
            except KeyboardInterrupt:
                print("\n⚠️ Returning to previous menu...")
                break
            except Exception as e:
                log_error(f"Menu loop error: {e}")
                input("Press Enter to continue...")