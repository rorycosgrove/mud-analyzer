#!/usr/bin/env python3
"""
MUD Analyzer Launcher
Easy launcher for all MUD Analyzer client applications
"""

import sys
import subprocess
import os


def print_menu():
    """Print main menu"""
    print("\n" + "="*60)
    print("MUD ANALYZER CLIENT - LAUNCHER")
    print("="*60)
    print("\nSelect an option:\n")
    print("1. Desktop GUI (Tkinter)")
    print("   - Local desktop application")
    print("   - No dependencies required")
    print()
    print("2. Web GUI (Flask)")
    print("   - Browser-based interface")
    print("   - Access via http://localhost:5000")
    print()
    print("3. REST API Examples")
    print("   - Command-line examples")
    print("   - Python code demonstrations")
    print()
    print("4. MCP Examples")
    print("   - Model Context Protocol examples")
    print("   - LLM integration demonstrations")
    print()
    print("5. Verify Integration")
    print("   - Test all systems")
    print("   - Check connections")
    print()
    print("6. Exit")
    print("\n" + "="*60 + "\n")


def launch_gui():
    """Launch desktop GUI"""
    print("Starting Desktop GUI (Tkinter)...")
    try:
        subprocess.run([sys.executable, "gui.py"], check=False)
    except Exception as e:
        print(f"Error: {e}")


def launch_web_gui():
    """Launch web GUI"""
    print("Starting Web GUI (Flask)...")
    print("Open http://localhost:5000 in your browser")
    try:
        subprocess.run([sys.executable, "web_gui.py"], check=False)
    except Exception as e:
        print(f"Error: {e}")


def launch_rest_examples():
    """Launch REST API examples"""
    print("Running REST API Examples...")
    try:
        subprocess.run([sys.executable, "examples_rest_api.py"], check=False)
    except Exception as e:
        print(f"Error: {e}")


def launch_mcp_examples():
    """Launch MCP examples"""
    print("Running MCP Examples...")
    try:
        subprocess.run([sys.executable, "examples_mcp.py"], check=False)
    except Exception as e:
        print(f"Error: {e}")


def verify_integration():
    """Verify integration"""
    print("Verifying integration...")
    try:
        subprocess.run([sys.executable, "verify_integration.py"], check=False)
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Main launcher"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == "1":
            launch_gui()
        elif choice == "2":
            launch_web_gui()
        elif choice == "3":
            launch_rest_examples()
        elif choice == "4":
            launch_mcp_examples()
        elif choice == "5":
            verify_integration()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
