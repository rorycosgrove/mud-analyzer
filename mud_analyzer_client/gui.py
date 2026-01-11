#!/usr/bin/env python3
"""
MUD Analyzer GUI Application
Graphical user interface for MUD Analyzer REST and MCP clients
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
from rest_client import MUDAnalyzerClient, MUDAnalyzerClientError
from mcp_client import MUDAnalyzerMCPClient, MCPClientError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MUDAnalyzerGUI:
    """Main GUI application for MUD Analyzer"""
    
    def __init__(self, root):
        """Initialize the GUI"""
        self.root = root
        self.root.title("MUD Analyzer Client")
        self.root.geometry("900x700")
        
        # Application state
        self.rest_client = None
        self.mcp_client = None
        self.api_url = tk.StringVar(value="http://localhost:8000")
        self.search_query = tk.StringVar()
        self.entity_type = tk.StringVar(value="all")
        self.zone_num = tk.StringVar()
        self.vnum = tk.StringVar()
        
        # Setup GUI
        self._setup_styles()
        self._create_menu()
        self._create_main_layout()
        self._update_connection_status()
        
    def _setup_styles(self):
        """Setup tkinter styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 9))
        
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings", command=self._show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_docs)
        
    def _create_main_layout(self):
        """Create main GUI layout"""
        # Top frame - Connection status
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(top_frame, text="MUD Analyzer Client", style='Title.TLabel').pack(anchor=tk.W)
        self.status_label = ttk.Label(top_frame, text="Status: Disconnected", style='Status.TLabel')
        self.status_label.pack(anchor=tk.W)
        
        # Notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Search tab
        search_frame = ttk.Frame(notebook)
        notebook.add(search_frame, text="Search")
        self._create_search_tab(search_frame)
        
        # Zone Info tab
        zone_frame = ttk.Frame(notebook)
        notebook.add(zone_frame, text="Zone Info")
        self._create_zone_tab(zone_frame)
        
        # Entity Details tab
        entity_frame = ttk.Frame(notebook)
        notebook.add(entity_frame, text="Entity Details")
        self._create_entity_tab(entity_frame)
        
        # Assemblies tab
        assembly_frame = ttk.Frame(notebook)
        notebook.add(assembly_frame, text="Assemblies")
        self._create_assembly_tab(assembly_frame)
        
        # Results tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Results")
        self._create_results_tab(results_frame)
        
    def _create_search_tab(self, parent):
        """Create search tab"""
        # Query input
        ttk.Label(parent, text="Search Query:", style='Heading.TLabel').pack(anchor=tk.W, padx=10, pady=(10, 0))
        ttk.Entry(parent, textvariable=self.search_query, width=50).pack(anchor=tk.W, padx=10, pady=5)
        
        # Entity type selection
        ttk.Label(parent, text="Entity Type:", style='Heading.TLabel').pack(anchor=tk.W, padx=10, pady=(10, 0))
        type_frame = ttk.Frame(parent)
        type_frame.pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Radiobutton(type_frame, text="All", variable=self.entity_type, value="all").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Objects", variable=self.entity_type, value="object").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Mobiles", variable=self.entity_type, value="mobile").pack(side=tk.LEFT, padx=5)
        
        # Limit input
        ttk.Label(parent, text="Limit Results:", style='Heading.TLabel').pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.search_limit = tk.IntVar(value=50)
        ttk.Spinbox(parent, from_=1, to=500, textvariable=self.search_limit, width=10).pack(anchor=tk.W, padx=10, pady=5)
        
        # Search button
        ttk.Button(parent, text="Search", command=self._perform_search).pack(pady=20)
        
    def _create_zone_tab(self, parent):
        """Create zone info tab"""
        ttk.Label(parent, text="Zone Number:", style='Heading.TLabel').pack(anchor=tk.W, padx=10, pady=(10, 0))
        ttk.Entry(parent, textvariable=self.zone_num, width=20).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Button(parent, text="Get Zone Info", command=self._get_zone_info).pack(pady=20)
        
    def _create_entity_tab(self, parent):
        """Create entity details tab"""
        ttk.Label(parent, text="Entity VNUM:", style='Heading.TLabel').pack(anchor=tk.W, padx=10, pady=(10, 0))
        ttk.Entry(parent, textvariable=self.vnum, width=20).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Label(parent, text="Entity Type:", style='Heading.TLabel').pack(anchor=tk.W, padx=10, pady=(10, 0))
        entity_type_frame = ttk.Frame(parent)
        entity_type_frame.pack(anchor=tk.W, padx=10, pady=5)
        
        self.detail_type = tk.StringVar(value="object")
        ttk.Radiobutton(entity_type_frame, text="Object", variable=self.detail_type, value="object").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(entity_type_frame, text="Mobile", variable=self.detail_type, value="mobile").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(parent, text="Get Details", command=self._get_entity_details).pack(pady=20)
        
    def _create_assembly_tab(self, parent):
        """Create assemblies tab"""
        ttk.Label(parent, text="Object VNUM:", style='Heading.TLabel').pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.assembly_vnum = tk.StringVar()
        ttk.Entry(parent, textvariable=self.assembly_vnum, width=20).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Label(parent, text="Limit Results:", style='Heading.TLabel').pack(anchor=tk.W, padx=10, pady=(10, 0))
        self.assembly_limit = tk.IntVar(value=50)
        ttk.Spinbox(parent, from_=1, to=500, textvariable=self.assembly_limit, width=10).pack(anchor=tk.W, padx=10, pady=5)
        
        ttk.Button(parent, text="Find Assemblies", command=self._find_assemblies).pack(pady=20)
        
    def _create_results_tab(self, parent):
        """Create results display tab"""
        ttk.Label(parent, text="Results:", style='Heading.TLabel').pack(anchor=tk.W, padx=10, pady=10)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(parent, height=25, width=80, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Copy button
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Copy Results", command=self._copy_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Results", command=self._clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export as JSON", command=self._export_results).pack(side=tk.LEFT, padx=5)
        
    def _perform_search(self):
        """Perform search"""
        query = self.search_query.get().strip()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a search query")
            return
        
        entity_type = self.entity_type.get()
        if entity_type == "all":
            entity_type = None
        
        limit = self.search_limit.get()
        
        # Run in separate thread to avoid blocking UI
        thread = threading.Thread(
            target=self._search_thread,
            args=(query, entity_type, limit),
            daemon=True
        )
        thread.start()
        
    def _search_thread(self, query, entity_type, limit):
        """Search in background thread"""
        try:
            self._display_result("Searching...")
            
            if not self.rest_client:
                self._connect_rest_api()
            
            if entity_type == "object":
                results = self.rest_client.search_objects(query, limit=limit)
            elif entity_type == "mobile":
                results = self.rest_client.search_mobiles(query, limit=limit)
            else:
                results = self.rest_client.search(query, limit=limit)
            
            if results:
                output = f"Search Results for '{query}' ({len(results)} found):\n\n"
                for result in results:
                    output += f"VNUM: {result.vnum}\n"
                    output += f"Name: {result.name}\n"
                    output += f"Zone: {result.zone}\n"
                    output += f"Type: {result.entity_type}\n"
                    output += "-" * 40 + "\n"
            else:
                output = f"No results found for '{query}'"
            
            self._display_result(output)
        except MUDAnalyzerClientError as e:
            self._display_result(f"API Error: {e}")
        except Exception as e:
            self._display_result(f"Error: {e}")
            
    def _get_zone_info(self):
        """Get zone information"""
        zone_str = self.zone_num.get().strip()
        if not zone_str:
            messagebox.showwarning("Input Error", "Please enter a zone number")
            return
        
        try:
            zone_num = int(zone_str)
        except ValueError:
            messagebox.showerror("Input Error", "Zone number must be an integer")
            return
        
        thread = threading.Thread(
            target=self._zone_thread,
            args=(zone_num,),
            daemon=True
        )
        thread.start()
        
    def _zone_thread(self, zone_num):
        """Get zone info in background thread"""
        try:
            self._display_result(f"Getting zone {zone_num}...")
            
            if not self.rest_client:
                self._connect_rest_api()
            
            zone_info = self.rest_client.get_zone(zone_num)
            
            output = f"Zone {zone_num} Information:\n\n"
            for key, value in zone_info.items():
                output += f"{key}: {value}\n"
            
            self._display_result(output)
        except MUDAnalyzerClientError as e:
            self._display_result(f"API Error: {e}")
        except Exception as e:
            self._display_result(f"Error: {e}")
            
    def _get_entity_details(self):
        """Get entity details"""
        vnum_str = self.vnum.get().strip()
        if not vnum_str:
            messagebox.showwarning("Input Error", "Please enter a VNUM")
            return
        
        try:
            vnum = int(vnum_str)
        except ValueError:
            messagebox.showerror("Input Error", "VNUM must be an integer")
            return
        
        entity_type = self.detail_type.get()
        
        thread = threading.Thread(
            target=self._entity_thread,
            args=(vnum, entity_type),
            daemon=True
        )
        thread.start()
        
    def _entity_thread(self, vnum, entity_type):
        """Get entity details in background thread"""
        try:
            self._display_result(f"Getting {entity_type} {vnum}...")
            
            if not self.rest_client:
                self._connect_rest_api()
            
            if entity_type == "object":
                details = self.rest_client.get_object(vnum)
            else:
                details = self.rest_client.get_mobile(vnum)
            
            output = f"{entity_type.capitalize()} {vnum} Details:\n\n"
            for key, value in details.items():
                output += f"{key}: {value}\n"
            
            self._display_result(output)
        except MUDAnalyzerClientError as e:
            self._display_result(f"API Error: {e}")
        except Exception as e:
            self._display_result(f"Error: {e}")
            
    def _find_assemblies(self):
        """Find assemblies"""
        vnum_str = self.assembly_vnum.get().strip()
        if not vnum_str:
            messagebox.showwarning("Input Error", "Please enter an object VNUM")
            return
        
        try:
            vnum = int(vnum_str)
        except ValueError:
            messagebox.showerror("Input Error", "VNUM must be an integer")
            return
        
        limit = self.assembly_limit.get()
        
        thread = threading.Thread(
            target=self._assembly_thread,
            args=(vnum, limit),
            daemon=True
        )
        thread.start()
        
    def _assembly_thread(self, vnum, limit):
        """Find assemblies in background thread"""
        try:
            self._display_result(f"Finding assemblies for object {vnum}...")
            
            if not self.rest_client:
                self._connect_rest_api()
            
            assemblies = self.rest_client.find_assemblies(vnum, limit=limit)
            
            output = f"Assemblies for Object {vnum}:\n\n"
            output += json.dumps(assemblies, indent=2)
            
            self._display_result(output)
        except MUDAnalyzerClientError as e:
            self._display_result(f"API Error: {e}")
        except Exception as e:
            self._display_result(f"Error: {e}")
            
    def _connect_rest_api(self):
        """Connect to REST API"""
        try:
            self.rest_client = MUDAnalyzerClient(self.api_url.get())
            self._update_connection_status()
        except Exception as e:
            raise MUDAnalyzerClientError(f"Cannot connect to REST API: {e}")
            
    def _update_connection_status(self):
        """Update connection status"""
        try:
            if not self.rest_client:
                self.rest_client = MUDAnalyzerClient(self.api_url.get())
            
            # Try a simple request to verify connection
            try:
                self.rest_client.get_zones(limit=1)
                self.status_label.config(text=f"Status: Connected ({self.api_url.get()})")
            except:
                self.status_label.config(text=f"Status: API unreachable (trying {self.api_url.get()})")
        except Exception as e:
            self.status_label.config(text=f"Status: Error - {e}")
            
    def _display_result(self, text):
        """Display result in results tab"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, text)
        self.results_text.config(state=tk.DISABLED)
        
    def _copy_results(self):
        """Copy results to clipboard"""
        try:
            text = self.results_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Success", "Results copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {e}")
            
    def _clear_results(self):
        """Clear results"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        
    def _export_results(self):
        """Export results as JSON"""
        try:
            text = self.results_text.get(1.0, tk.END)
            filename = "mud_analyzer_results.txt"
            with open(filename, 'w') as f:
                f.write(text)
            messagebox.showinfo("Success", f"Results exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
            
    def _show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x200")
        
        # API URL setting
        ttk.Label(settings_window, text="REST API URL:").pack(anchor=tk.W, padx=10, pady=10)
        url_entry = ttk.Entry(settings_window, textvariable=self.api_url, width=40)
        url_entry.pack(anchor=tk.W, padx=10, pady=5)
        
        # Save button
        def save_settings():
            self.rest_client = None  # Reset client
            self._update_connection_status()
            messagebox.showinfo("Success", "Settings saved")
            settings_window.destroy()
        
        ttk.Button(settings_window, text="Save Settings", command=save_settings).pack(pady=20)
        
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About MUD Analyzer",
            "MUD Analyzer Client v1.0\n\n"
            "A graphical interface for searching and analyzing MUD data.\n\n"
            "Features:\n"
            "- Search for objects and mobiles\n"
            "- View zone information\n"
            "- Get entity details\n"
            "- Find item assemblies\n"
            "- Export results\n\n"
            "© 2026 MUD Analyzer Project"
        )
        
    def _show_docs(self):
        """Show documentation"""
        messagebox.showinfo(
            "Documentation",
            "MUD Analyzer Client Documentation\n\n"
            "Search:\n"
            "- Enter a query and select entity type\n"
            "- Results appear in the Results tab\n\n"
            "Zone Info:\n"
            "- Enter zone number to get details\n\n"
            "Entity Details:\n"
            "- Enter VNUM and select type (Object/Mobile)\n\n"
            "Assemblies:\n"
            "- Enter object VNUM to find assemblies\n\n"
            "Settings:\n"
            "- Configure REST API URL in File > Settings"
        )


def main():
    """Main entry point"""
    root = tk.Tk()
    app = MUDAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
