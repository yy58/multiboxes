#!/usr/bin/env python3
"""
Simple launcher script for the multiplayer game.

This script makes it easier for students to run the server and client
without remembering the exact module commands.

Usage:
    python launcher.py server    # Start the game server
    python launcher.py client    # Start a game client
    python launcher.py test      # Run the tests
"""

import sys
import subprocess


def print_usage():
    """Print usage instructions."""
    print("Multiboxes Game Launcher")
    print("=" * 40)
    print("Usage:")
    print("  python launcher.py server    # Start the game server")
    print("  python launcher.py client    # Start a game client") 
    print("  python launcher.py test      # Run the tests")
    print()
    print("First time setup:")
    print("  1. uv venv                   # Create virtual environment")
    print("  2. .venv\\Scripts\\activate    # Activate environment (Windows)")
    print("     source .venv/bin/activate   # Activate environment (Linux/Mac)")
    print("  3. uv pip install -e .       # Install the package")
    print()


def run_server():
    """Start the game server."""
    print("Starting game server...")
    print("Players can now connect with: python launcher.py client")
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "multibox.game_server"])
    except KeyboardInterrupt:
        print("\nServer stopped.")


def run_client():
    """Start a game client."""
    print("Starting game client...")
    print("Make sure the server is running first!")
    print("Controls: Arrow keys to move, ESC to quit")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "multibox.game_client"])
    except KeyboardInterrupt:
        print("\nClient stopped.")


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
    except FileNotFoundError:
        print("Error: pytest not found. Install it with: uv pip install pytest pytest-asyncio")


def main():
    """Main launcher function."""
    if len(sys.argv) != 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "server":
        run_server()
    elif command == "client":
        run_client()
    elif command == "test":
        run_tests()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()