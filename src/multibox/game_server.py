"""
Multiplayer Game Server

This is the main game server that handles:
1. Physics simulation using PyMunk
2. Network communication using OSC (Open Sound Control)
3. Service discovery using Zeroconf
4. Real-time multiplayer game coordination

The server runs an async game loop that updates physics and sends
position updates to all connected clients.

Key concepts demonstrated:
- Asyncio for concurrent programming
- OSC for network messaging
- Physics simulation
- Service discovery
"""

import asyncio
import pymunk
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from .avahi_utils import get_ip, register_service, make_service_info
import socket

async def game_loop():
    """
    The main game loop that runs continuously.
    
    This function:
    1. Updates the physics simulation (60 times per second)
    2. Collects all player positions
    3. Enforces maximum velocity limits
    4. Sends position updates to all connected clients
    5. Waits for the next frame
    
    This demonstrates the core server loop pattern in multiplayer games.
    """
    while True:
        # Step the physics simulation forward by 1/60th of a second
        # This updates all physics objects (players, collisions, etc.)
        space.step(1/60)  # Update physics at 60 FPS
        
        # Collect current positions and rotations of all players
        # This creates a dictionary mapping player IDs to their (x, y, angle) data
        player_positions = {
            player_id: (body.position.x, body.position.y, body.angle) 
            for player_id, body in players.items()
        }
        
        # Enforce maximum velocity to prevent players from moving too fast
        for player_id, body in players.items():
            if body.velocity.length > max_velocity:
                # Normalize the velocity vector and scale it to max_velocity
                body.velocity = body.velocity.normalized() * max_velocity
        
        # Send position updates to all connected clients
        # We use run_in_executor to avoid blocking the async loop with network I/O
        for client in clients:
            for player_id, position in player_positions.items():                
                asyncio.get_running_loop().run_in_executor(
                    None, 
                    client.send_message, 
                    "/update_position", 
                    [player_id, *position]  # *position unpacks the (x, y, angle) tuple
                )
        
        # Wait for 1/60th of a second before the next update
        # This maintains a steady 60 FPS game loop
        await asyncio.sleep(1/60)

def create_player(address, *args):
    """
    Handle a new player connection request.
    
    This function is called when a client sends a "/connect" OSC message.
    It creates a new physics body for the player and sets up communication.
    
    Args:
        address (str): The OSC address (always "/connect" for this handler)
        *args: Variable arguments from the OSC message:
               args[0] = player_id (unique identifier for the player)
               args[1] = client_ip (IP address of the connecting client)
               args[2] = client_port (port number the client is listening on)
    """
    player_id = args[0]
    
    # Create a physics body for the new player
    # A Body represents an object that can move and respond to forces
    body = pymunk.Body()
    
    # Set the initial position of the player
    body.position = 50, 100
    
    # Calculate the moment of inertia for a box-shaped object
    # This affects how the object rotates when forces are applied
    body.moment = pymunk.moment_for_box(10, (50, 50))  # mass=10, size=(50x50)
    
    # Create a polygon shape (box) attached to the body
    poly = pymunk.Poly.create_box(body)
    poly.mass = 10          # How heavy the object is
    poly.elasticity = 0.95  # How bouncy it is (0=no bounce, 1=perfect bounce)
    poly.friction = 0.8     # How much friction with other objects (0=slippery, 1=sticky)
    
    # Add the body and shape to the physics space
    space.add(body, poly)
    
    # Store the player's physics body for future reference
    players[player_id] = body

    print(f"Player {player_id} connected")

    # Create a UDP client to send updates back to this specific player
    client_ip = args[1]    # The IP address where the client is listening
    client_port = args[2]  # The port where the client is listening
    client = SimpleUDPClient(client_ip, client_port)
    
    # Add this client to our set of clients to send updates to
    clients.add(client)

def update_player_velocity(address, *args):
    """
    Handle player movement input from clients.
    
    This function is called when a client sends a "/update_velocity" OSC message.
    It applies forces to the player's physics body based on input.
    
    Args:
        address (str): The OSC address (always "/update_velocity" for this handler)
        *args: Variable arguments from the OSC message:
               args[0] = player_id (which player is moving)
               args[1] = x (horizontal movement: -1=left, 0=none, 1=right)
               args[2] = y (vertical movement: -1=up, 0=none, 1=down)
    """
    player_id = args[0]
    x, y = args[1], args[2]  # Movement direction (-1, 0, or 1 for each axis)
    
    # Only apply forces if this player exists in our game
    if player_id in players:
        # Only apply force if there's actually movement input
        if abs(x) > 0 or abs(y) > 0:
            # Apply force to the player's physics body
            # force=(x*speed_factor, y*speed_factor) - scale the input by our speed factor
            # point=player's current position - where to apply the force
            players[player_id].apply_force_at_world_point(
                force=(x * speed_factor, y * speed_factor),
                point=(players[player_id].position.x, players[player_id].position.y)
            )

def create_space():
    """
    Initialize the physics world and create boundaries.
    
    This function:
    1. Creates a new physics space (the world where physics happens)
    2. Sets gravity (downward force applied to all objects)
    3. Creates walls around the game area to contain players
    
    The physics space is where all physics calculations happen.
    """
    global space
    
    # Create a new physics space - this is the "world" where physics happens
    space = pymunk.Space()
    
    # Set gravity - (0, 98) means no horizontal gravity, 98 downward
    # 98 pixels/second² is roughly equivalent to Earth's gravity for our scale
    space.gravity = 0, 98

    # Create walls to contain the game area
    # Walls are static objects that don't move but can be collided with
    walls = []
    
    # Left wall: from (0,0) to (0,400) - vertical line on the left edge
    walls.append(pymunk.Segment(space.static_body, (0, 0), (0, 400), 0.0))
    
    # Right wall: from (700,0) to (700,400) - vertical line on the right edge  
    walls.append(pymunk.Segment(space.static_body, (700, 0), (700, 400), 0.0))
    
    # Top wall: from (0,0) to (700,0) - horizontal line at the top
    walls.append(pymunk.Segment(space.static_body, (0, 0), (700, 0), 0.0))
    
    # Bottom wall: from (0,400) to (700,400) - horizontal line at the bottom
    walls.append(pymunk.Segment(space.static_body, (0, 400), (700, 400), 0.0))
    
    # Set properties for all walls
    for wall in walls:
        wall.elasticity = 0.95  # How bouncy the walls are
        wall.friction = 0.8     # How much friction the walls have
        space.add(wall)         # Add each wall to the physics space

async def init_main():
    """
    Initialize and start the game server.
    
    This function:
    1. Sets up OSC message handling (network communication)
    2. Registers the service for automatic discovery
    3. Starts the network server
    4. Begins the game loop
    
    This is the main entry point for the server.
    """
    # Create an OSC dispatcher to handle incoming messages
    # The dispatcher routes different message types to different functions
    dispatcher = Dispatcher()    
    
    # Map OSC addresses to handler functions
    # When a "/update_velocity" message arrives, call update_player_velocity
    dispatcher.map("/update_velocity", update_player_velocity)
    
    # When a "/connect" message arrives, call create_player
    dispatcher.map("/connect", create_player)
    
    # Create service information for network discovery
    # This allows clients to automatically find our server
    service_info = make_service_info()
    
    # Start the service registration in the background
    # ensure_future schedules the coroutine to run concurrently
    asyncio.ensure_future(register_service(service_info))
    
    # Convert the IP address from bytes to string format
    ip_string = socket.inet_ntoa(service_info.addresses[0])
    
    # Create the OSC server that will listen for incoming messages
    server = AsyncIOOSCUDPServer(
        (ip_string, service_info.port),  # Listen on our IP and port
        dispatcher,                       # Use our message dispatcher
        asyncio.get_event_loop()         # Use the current event loop
    )
    
    # Start the server and get transport/protocol objects
    transport, protocol = await server.create_serve_endpoint()
    
    print(f"Game server started on {ip_string}:{service_info.port}")
    print("Waiting for players to connect...")
    
    # Start the main game loop (this runs forever)
    await game_loop()
    
    # Clean up (this line is never reached in normal operation)
    transport.close()

def initialize():
    """
    Initialize global variables and game state.
    
    This function sets up:
    1. Data structures to track clients and players
    2. Game configuration parameters
    3. The physics world
    
    This is called before starting the server.
    """
    # Global variables to track game state
    global clients, players
    
    # Set to store UDP clients for sending updates
    # We use a set to avoid duplicate clients
    clients = set()
    
    # Dictionary to map player IDs to their physics bodies
    # Key: player_id (string), Value: pymunk.Body object
    players = {}

    # Game configuration parameters
    global max_velocity, speed_factor
    
    # Maximum speed a player can move (pixels per second)
    max_velocity = 200
    
    # How much force to apply when a player presses movement keys
    # Higher values = more responsive movement
    speed_factor = 1000

    # Create the physics world
    create_space()


if __name__ == "__main__":
    """
    Entry point when running this file directly.
    
    This code only runs when you execute this file with:
    python -m multibox.game_server
    
    It initializes the game state and starts the async server.
    """
    print("Starting multiplayer game server...")
    print("This server demonstrates:")
    print("- Asyncio for concurrent programming")
    print("- OSC for network communication")
    print("- PyMunk for physics simulation")
    print("- Zeroconf for service discovery")
    print()
    
    # Initialize game state and configuration
    initialize()
    
    # Start the async server (this runs until interrupted)
    asyncio.run(init_main())