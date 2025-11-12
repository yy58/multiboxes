"""
Network service discovery utilities using Zeroconf/Avahi.

This module provides utilities for:
1. Getting the local IP address
2. Registering network services for automatic discovery
3. Creating service information for the game server

Zeroconf (also known as Avahi on Linux) allows devices on a local network
to discover services automatically without manual configuration.
"""

import asyncio
from zeroconf.asyncio import AsyncZeroconf
from zeroconf import ServiceInfo
import socket

# Service type identifier for our game service
# The format is "_servicename._protocol.local."
service_type = "_pygame._udp.local."

# Specific name for our game server service
service_name = "gameserver._pygame._udp.local."

# Default port for the game server
default_port = 11337

def get_ip():
    """
    Get the local IP address of this machine.
    
    This function creates a UDP socket and connects to a public DNS server
    to determine what IP address this machine would use for outbound connections.
    No actual data is sent.
    
    Returns:
        str: The local IP address as a string

    Raises:
        RuntimeError: If unable to determine the local IP address due to network issues.
    """
    try:
        # Create a UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to Google's public DNS (no data is actually sent)
        s.connect(('8.8.8.8', 1))
        # Get the local IP address that would be used for this connection
        local_ip = s.getsockname()[0]
        # Close the socket
        s.close()
        return local_ip
    except Exception as e:
        raise RuntimeError(f"Unable to determine local IP address: {e}")

async def register_service(service_info):
    """
    Register a service with Zeroconf for network discovery.
    
    This function runs indefinitely, keeping the service registered
    so other devices on the network can find it.
    
    Args:
        service_info (ServiceInfo): The service information to register
    """
    # Create an async Zeroconf instance
    zeroconf = AsyncZeroconf()
    
    # Register the service (strict=False allows some flexibility in registration)
    await zeroconf.async_register_service(info=service_info, strict=False)
    
    # Keep the service registered by running forever
    # In a real application, you'd want a way to cleanly shut this down
    while True:
        await asyncio.sleep(0.1)

def make_service_info(port=default_port, name=service_name):
    """
    Create service information for Zeroconf registration.
    
    This creates a ServiceInfo object that describes our game server
    so other devices can discover and connect to it.
    
    Args:
        port (int): The port number the service runs on
        name (str): The service name
        
    Returns:
        ServiceInfo: A service info object ready for registration
    """
    return ServiceInfo(
        type_=service_type,        # What type of service this is
        name=name,                 # The specific name of this service instance
        port=port,                 # What port the service listens on
        addresses=[socket.inet_aton(get_ip())]  # IP address(es) in bytes format
    )

