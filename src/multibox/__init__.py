"""
Multiboxes - Educational Multiplayer Physics Game

A simple multiplayer game demonstrating:
- Asyncio concurrent programming
- OSC network communication
- PyMunk physics simulation
- Pygame graphics and input
- Zeroconf service discovery
- Python package creation

This package provides:
- game_server: Physics simulation and multiplayer coordination
- game_client: Graphics, input, and network client
- player: Player representation and rendering
- avahi_utils: Network service discovery utilities

For students learning:
- How async/await works in Python
- Network programming with UDP and OSC
- Game development patterns
- Physics simulation concepts
- Python packaging and modules

To run:
    python -m multibox.game_server  # Start server
    python -m multibox.game_client  # Start client
    
Or use the launcher:
    python launcher.py server
    python launcher.py client
"""

# Package metadata
__version__ = "0.1.0"
__author__ = "Giovanni Lion"
__email__ = "giovanni.lion@gmail.com"

# Export main classes for easier importing
from .player import Player
from .avahi_utils import get_ip, make_service_info

__all__ = ["Player", "get_ip", "make_service_info"]