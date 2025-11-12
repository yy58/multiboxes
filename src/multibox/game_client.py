"""
Multiplayer Game Client

This is the game client that handles:
1. Pygame for graphics and input
2. OSC communication with the server
3. Service discovery to find the game server
4. Real-time display of multiplayer game state

The client runs multiple async tasks concurrently:
- Pygame event handling (keyboard input)
- Network communication (receiving updates)
- Graphics rendering (drawing the game)

Key concepts demonstrated:
- Asyncio with Pygame integration
- OSC network communication
- Service discovery
- Real-time multiplayer client architecture
"""

import pygame
import asyncio
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from .player import Player
import time
import random
from .avahi_utils import get_ip, service_type, service_name
from zeroconf import Zeroconf
import socket

# Game window configuration
width, height = 700, 400  # Match the server's physics world boundaries
spawn_margin = 50         # Keep players away from edges when spawning

def connect_to_server():
    """
    Discover and connect to the game server.
    
    This function:
    1. Sets up the local client configuration
    2. Uses Zeroconf to automatically discover the game server
    3. Creates a UDP client to communicate with the server
    4. Sends a connection request to join the game
    
    This demonstrates automatic service discovery - no need to manually
    configure IP addresses!
    """
    global client
    global local_ip, local_port, local_player
    
    # Set up local network configuration
    local_ip = get_ip()  # Get the actual local IP address for network communication
    local_port = random.randint(5000, 10000)  # Random port to avoid conflicts
    
    # Create our local player at a random spawn position
    local_player = Player(
        random.randint(spawn_margin, width - spawn_margin), 
        random.randint(spawn_margin, height - spawn_margin)
    )

    print(f"Looking for game server...")
    
    # Use Zeroconf to automatically discover the game server
    zeroconf = Zeroconf()
    resp = zeroconf.get_service_info(service_type, service_name)
    
    if resp is None:
        print("No game server found! Make sure the server is running.")
        return False
        
    print(f"Found game server: {resp}")
    
    # Extract server IP and port from the service info
    server_ip = socket.inet_ntoa(resp.addresses[0])
    
    # Create UDP client to send messages to the server
    client = SimpleUDPClient(server_ip, resp.port)

    print(f"Connecting to server at {server_ip}:{resp.port}")
    print(f"Local player ID: {local_player.id}")
    
    # Send connection request to the server
    # Format: [player_id, client_ip, client_port]
    client.send_message("/connect", [local_player.id, local_ip, local_port])
    
    return True

async def pygame_event_loop(event_queue):
    """
    Continuously collect Pygame events and put them in a queue.
    
    This function runs in its own async task and bridges the gap between
    Pygame's synchronous event system and our async architecture.
    
    Args:
        event_queue (asyncio.Queue): Queue to store pygame events
    """
    while True:
        # Get all pending pygame events (keyboard, mouse, window close, etc.)
        events = pygame.event.get()
        
        # Put each event in the queue for the event handler to process
        if events:
            await event_queue.put(events)
            
        # Small delay to prevent busy-waiting and allow other tasks to run
        await asyncio.sleep(0.002)

# OSC Message Handlers
# These functions are called when the client receives messages from the server

def update_position(address, *args):
    """
    Handle position updates from the server.
    
    This function is called when the server sends a "/update_position" message
    with updated player coordinates and rotation.
    
    Args:
        address (str): The OSC address (always "/update_position")
        *args: Variable arguments:
               args[0] = player_id (which player to update)
               args[1] = x coordinate
               args[2] = y coordinate  
               args[3] = rotation angle
    """
    player_id = args[0]
    x, y = args[1], args[2]
    
    # Update existing player or create new one if we haven't seen them before
    if player_id in moving_objects:
        # Update position and rotation for existing player
        moving_objects[player_id].set_position(x, y)
        moving_objects[player_id].set_rotation(args[3])
    else:
        # Create new player object for unknown player
        moving_objects[player_id] = Player(x, y)
        print(f"New player appeared: {player_id}")

def new_player(address, *args):
    """
    Handle new player notifications from the server.
    
    This function would be called when the server notifies us about
    a new player joining the game.
    
    Args:
        address (str): The OSC address (always "/new_player")
        *args: Variable arguments:
               args[0] = player_id (the new player's ID)
    """
    player_id = args[0]
    if player_id not in moving_objects:
        # Create a new player object at a default position
        moving_objects[player_id] = Player(50, 100)
        print(f"Player {player_id} joined the game")

async def draw(screen):
    """
    Main rendering loop that draws the game at 60 FPS.
    
    This function runs continuously and:
    1. Clears the screen
    2. Draws all players
    3. Updates the display
    4. Waits for the next frame
    
    Args:
        screen (pygame.Surface): The main game window surface
    """
    black = (0, 0, 0)  # Background color (black)
    
    while True:
        # Cap the framerate at 60 FPS
        await asyncio.sleep(1/60)
        
        # Clear the screen with black background
        screen.fill(black)
        
        # Draw all players (including remote players and our local player)
        for player_id in moving_objects:
            moving_objects[player_id].draw(screen)
        
        # Update the display to show our changes
        # flip() is more efficient than update() for full-screen updates
        pygame.display.flip()

async def handle_events(event_queue):
    """
    Process keyboard input and send movement commands to the server.
    
    This function:
    1. Processes pygame events from the event queue
    2. Tracks current movement state based on key presses/releases
    3. Sends movement updates to the server
    4. Handles the quit event to close the game
    
    Controls:
    - Arrow keys: Move player (up/down/left/right)
    - Q/E: Rotate player (not fully implemented in physics)
    - Window close or ESC: Exit game
    
    Args:
        event_queue (asyncio.Queue): Queue containing pygame events
    """
    # Current movement state
    velocity = [0, 0]    # [x_movement, y_movement] where -1, 0, 1 are the values
    angular_velocity = 0  # Rotation (not fully implemented)

    while True:        
        # Check if there are events to process
        if event_queue.empty():
            # No events, but still send current velocity to server
            await asyncio.sleep(0.01)  # Small delay to prevent busy-waiting
            client.send_message("/update_velocity", [local_player.id, velocity[0], velocity[1], angular_velocity])
            continue
        
        # Get events from the queue
        events = await event_queue.get()
        
        # Check for quit events (window close button, ESC key, etc.)
        quit_events = [event for event in events if event.type == pygame.QUIT]
        if quit_events:
            print("Quitting game...")
            break
            
        # Process each event
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Key pressed - start movement in that direction
                if event.key == pygame.K_LEFT:
                    velocity[0] = -1  # Move left
                elif event.key == pygame.K_RIGHT:
                    velocity[0] = 1   # Move right
                elif event.key == pygame.K_UP:
                    velocity[1] = -1  # Move up (negative Y in pygame coordinates)
                elif event.key == pygame.K_DOWN:
                    velocity[1] = 1   # Move down
                elif event.key == pygame.K_q:
                    angular_velocity = -1  # Rotate counterclockwise
                elif event.key == pygame.K_e:
                    angular_velocity = 1   # Rotate clockwise
                elif event.key == pygame.K_ESCAPE:
                    print("ESC pressed, quitting...")
                    asyncio.get_event_loop().stop()
                    return
                    
            elif event.type == pygame.KEYUP:
                # Key released - stop movement in that direction
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    velocity[0] = 0  # Stop horizontal movement
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    velocity[1] = 0  # Stop vertical movement
                elif event.key == pygame.K_q or event.key == pygame.K_e:
                    angular_velocity = 0  # Stop rotation
        
        # Send the current movement state to the server
        client.send_message("/update_velocity", [local_player.id, velocity[0], velocity[1], angular_velocity])

    # If we get here, the user wants to quit
    print("Shutting down client...")
    asyncio.get_event_loop().stop()


def main():
    """
    Main function that sets up and runs the game client.
    
    This function:
    1. Sets up pygame and the game window
    2. Creates OSC message handlers for server communication
    3. Starts multiple concurrent tasks (async coroutines)
    4. Runs the main event loop
    5. Handles cleanup when the game exits
    
    The client runs four concurrent tasks:
    - OSC server: Receives messages from the game server
    - Pygame events: Collects keyboard/mouse input
    - Drawing: Renders the game at 60 FPS  
    - Event handling: Processes input and sends to server
    """
    print("Starting game client...")
    print("Controls:")
    print("- Arrow keys: Move your player")
    print("- Q/E: Rotate (not fully implemented)")
    print("- ESC or close window: Quit")
    print()

    # Get the asyncio event loop
    loop = asyncio.get_event_loop()
    
    # Create a queue for passing pygame events between tasks
    event_queue = asyncio.Queue()

    # Set up OSC message dispatcher for receiving server messages
    dispatcher = Dispatcher()
    dispatcher.map("/update_position", update_position)  # Handle position updates
    dispatcher.map("/new_player", new_player)            # Handle new player notifications

    # Initialize the dictionary of all game objects
    # Start with just our local player
    global moving_objects
    moving_objects = {local_player.id: local_player}

    # Initialize pygame
    pygame.init()

    # Set up the game window
    pygame.display.set_caption("Multiplayer Physics Game - Client")
    screen = pygame.display.set_mode((width, height))

    print(f"Listening for server messages on {local_ip}:{local_port}")

    # Create OSC server to receive messages from the game server
    server = AsyncIOOSCUDPServer((local_ip, local_port), dispatcher, asyncio.get_event_loop())
    
    # Create and start all concurrent tasks
    # These all run at the same time using asyncio
    osc_receive_task = asyncio.ensure_future(server.create_serve_endpoint())  # Listen for server messages
    pygame_task = asyncio.ensure_future(pygame_event_loop(event_queue))       # Collect pygame events
    drawing_task = asyncio.ensure_future(draw(screen))                        # Render the game
    event_task = asyncio.ensure_future(handle_events(event_queue))           # Process input
    
    print("Game client is running!")
    
    # Run the main event loop
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal")
    finally:
        # Clean up all tasks when the game exits
        print("Cleaning up tasks...")
        pygame_task.cancel()
        drawing_task.cancel()
        osc_receive_task.cancel()
        event_task.cancel()
        
        # Wait for tasks to finish cancelling
        try:
            loop.run_until_complete(pygame_task)
            loop.run_until_complete(drawing_task) 
            loop.run_until_complete(osc_receive_task)
            loop.run_until_complete(event_task)
        except asyncio.CancelledError:
            pass
            
    # Shut down pygame
    pygame.quit()
    print("Game client stopped.")

if __name__ == "__main__":
    """
    Entry point when running this file directly.
    
    This code only runs when you execute this file with:
    python -m multibox.game_client
    
    It connects to the server and starts the client.
    """
    print("=== Multiplayer Physics Game Client ===")
    print("This client demonstrates:")
    print("- Pygame integration with asyncio")
    print("- OSC network communication")
    print("- Automatic server discovery with Zeroconf")
    print("- Real-time multiplayer gameplay")
    print()
    
    # Try to connect to the server
    if connect_to_server():
        # If connection successful, start the game
        main()
    else:
        print("Failed to connect to server. Make sure the server is running!")
        print("Start the server with: python -m multibox.game_server")