"""
Tests for the multiplayer game server.

These tests demonstrate:
1. How to test async code with pytest-asyncio
2. How to test long-running services
3. Proper cleanup of async tasks
4. Testing network services without actual network calls

For students: This shows how to write tests for async code.
Testing async code requires special considerations since normal
test functions are synchronous but async code is... asynchronous!
"""

import asyncio
import pytest
from multibox.game_server import initialize, init_main
from multibox.player import Player


@pytest.mark.asyncio
async def test_server_initialization():
    """
    Test that the server initializes properly.
    
    This test:
    1. Calls the initialize function
    2. Checks that global variables are set up correctly
    3. Verifies the physics space is created
    
    This is a unit test - it tests individual components.
    """
    # Initialize the server (this sets up global variables)
    initialize()
    
    # Import the global variables to check them
    # Note: This is not ideal practice, but works for educational purposes
    from multibox.game_server import clients, players, space, max_velocity, speed_factor
    
    # Check that data structures are initialized
    assert isinstance(clients, set), "clients should be a set"
    assert isinstance(players, dict), "players should be a dictionary"
    assert len(clients) == 0, "should start with no clients"
    assert len(players) == 0, "should start with no players"
    
    # Check that configuration is set
    assert max_velocity == 200, "max_velocity should be 200"
    assert speed_factor == 1000, "speed_factor should be 1000"
    
    # Check that physics space exists
    assert space is not None, "physics space should be created"


@pytest.mark.asyncio 
async def test_server_runs():
    """
    Test that the server starts and runs without crashing.
    
    This test:
    1. Starts the server in a background task
    2. Lets it run for a short time
    3. Verifies it's still running (hasn't crashed)
    4. Cleanly shuts it down
    
    This is an integration test - it tests the whole system working together.
    """
    # Initialize the server first
    initialize()
    
    # Start the server in a background task
    # create_task() schedules the coroutine to run concurrently
    server_task = asyncio.create_task(init_main())

    # Let the server run for 1 second
    # This gives it time to start up and begin running
    await asyncio.sleep(1)

    # Verify the server task is still running (hasn't crashed or completed)
    assert not server_task.done(), "Server should still be running after 1 second"

    # Clean shutdown: cancel the server task
    server_task.cancel()
    
    # Wait for the task to finish cancelling
    # This prevents asyncio warnings about unawaited tasks
    try:
        await server_task
    except asyncio.CancelledError:
        # This exception is expected when cancelling a task
        pass


def test_player_creation():
    """
    Test the Player class works correctly.
    
    This is a simple unit test that doesn't involve async code.
    It tests the Player class in isolation.
    """
    # Create a new player
    player = Player(100, 200)
    
    # Check initial position
    assert player.x == 100, "Player x position should be 100"
    assert player.y == 200, "Player y position should be 200"
    
    # Check that a unique ID was generated
    assert player.id is not None, "Player should have an ID"
    assert len(player.id) > 0, "Player ID should not be empty"
    
    # Test position updates
    player.set_position(150, 250)
    assert player.x == 150, "Player x should update to 150"  
    assert player.y == 250, "Player y should update to 250"
    
    # Test that each player gets a unique ID
    player2 = Player(0, 0)
    assert player.id != player2.id, "Each player should have a unique ID"


@pytest.mark.asyncio
async def test_server_handles_no_clients():
    """
    Test that the server runs properly even with no connected clients.
    
    This test verifies the server doesn't crash when:
    - No clients are connected
    - The game loop runs with empty player list
    - Network operations are attempted with no clients
    
    Note: This test is simplified to avoid port conflicts during testing.
    In a real test suite, you'd use mock objects or test-specific ports.
    """
    initialize()
    
    # For this educational example, we'll just test the initialization
    # In a real application, you'd test the full server with mock networking
    from multibox.game_server import clients, players, space
    
    # Verify the server state is correct for handling no clients
    assert len(clients) == 0, "Should start with no clients"
    assert len(players) == 0, "Should start with no players"
    assert space is not None, "Physics space should exist"
    
    # Test that the space can run a physics step without crashing
    space.step(1/60)  # This should work fine with no objects
    
    # Server initialization handles no clients correctly


# Example of how you might test the network components
# (This test is commented out because it would require more setup)
"""
@pytest.mark.asyncio
async def test_osc_message_handling():
    '''
    Test that OSC message handlers work correctly.
    
    In a real test suite, you might:
    1. Create mock OSC messages
    2. Call the handler functions directly  
    3. Verify the correct state changes occurred
    '''
    initialize()
    
    from multibox.game_server import create_player, players
    
    # Simulate a "/connect" message
    # In reality, this would come from the OSC server
    create_player("/connect", "test_player_123", "127.0.0.1", 5000)
    
    # Verify the player was created
    assert "test_player_123" in players
    assert players["test_player_123"] is not None
"""