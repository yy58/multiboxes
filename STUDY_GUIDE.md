# Study Guide: Multiboxes Multiplayer Game

This study guide helps students understand the key concepts demonstrated in this project.

## 1. Asyncio (Asynchronous Programming)

### Key Concepts
- **Coroutines**: Functions defined with `async def`
- **Awaiting**: Using `await` to pause execution until something completes
- **Event Loop**: The core that runs all async operations
- **Tasks**: Units of concurrent work

### Where to Look in the Code
- `game_server.py`: Lines 35-72 (`game_loop` function)
- `game_client.py`: Lines 140-170 (`main` function)

### Study Questions
1. Why does the game loop use `await asyncio.sleep(1/60)`?
2. How many things are happening "at the same time" in the client?
3. What would happen if we didn't use `await` in the game loop?

## 2. Network Programming with OSC

### Key Concepts
- **UDP**: Connectionless protocol (faster but less reliable than TCP)
- **OSC**: Open Sound Control message format
- **Dispatcher**: Routes incoming messages to handler functions
- **Client/Server**: Architecture where server coordinates, clients display

### Where to Look in the Code
- `game_server.py`: Lines 74-112 (message handlers)
- `game_client.py`: Lines 74-105 (message handlers)

### Study Questions
1. What OSC messages are sent from client to server?
2. What OSC messages are sent from server to client?
3. Why use UDP instead of TCP for games?

## 3. Physics Simulation

### Key Concepts
- **Physics Space**: The world where physics calculations happen
- **Body**: An object that can move and have forces applied to it
- **Shape**: The collision boundary of an object
- **Forces**: What causes objects to move or change direction

### Where to Look in the Code
- `game_server.py`: Lines 144-175 (`create_space` function)
- `game_server.py`: Lines 114-142 (`create_player` function)

### Study Questions
1. What properties affect how bouncy a collision is?
2. How does gravity work in this physics world?
3. What happens when a player reaches maximum velocity?

## 4. Service Discovery with Zeroconf

### Key Concepts
- **Service Discovery**: Automatically finding services on the network
- **Zeroconf/Avahi**: Protocol for automatic network configuration
- **Service Info**: Describes what service is available and where

### Where to Look in the Code
- `avahi_utils.py`: All functions, especially `register_service`
- `game_client.py`: Lines 42-73 (`connect_to_server` function)

### Study Questions
1. Why use service discovery instead of hardcoded IP addresses?
2. What information is included in a ServiceInfo object?
3. How does the client find the server automatically?

## 5. Game Architecture Patterns

### Client-Server Model
- **Server**: Authoritative (makes all the decisions)
- **Client**: Display only (shows what server tells it)
- **Input**: Clients send input, server processes it

### Where to Look in the Code
- Server authority: `game_server.py` lines 35-72 (physics runs on server)
- Client display: `game_client.py` lines 107-124 (just draws what server says)

### Study Questions
1. Why does physics run on the server instead of each client?
2. What happens if there's network lag?
3. How could you make movement feel more responsive?

## 6. Python Packaging

### Key Concepts
- **Modules**: Python files that can be imported
- **Packages**: Directories containing modules with `__init__.py`
- **pyproject.toml**: Modern Python project configuration
- **Development Install**: Installing a package you're still working on

### Where to Look in the Code
- `pyproject.toml`: Project configuration
- `src/multibox/__init__.py`: Package definition
- Directory structure: How modules are organized

### Study Questions
1. Why put source code in a `src/` directory?
2. What's the difference between `pip install .` and `pip install -e .`?
3. How do relative imports work (the `.` in `from .player import Player`)?

## Practical Exercises

### Beginner
1. **Change colors**: Modify `player.py` to make players different colors
2. **Adjust physics**: Change gravity or friction values in `create_space`
3. **Add debug output**: Print player positions in the game loop

### Intermediate
1. **Add player names**: Extend the Player class to have names
2. **Score system**: Count collisions or time alive
3. **Different player sizes**: Make some players bigger/smaller

### Advanced
1. **Smooth movement**: Add interpolation between position updates
2. **Predict movement**: Make clients predict where they'll move
3. **Multiple rooms**: Allow different game instances

## Common Debugging Tips

### "Import could not be resolved"
- Make sure you activated the virtual environment
- Run `uv pip install -e .` to install in development mode

### "No server found"
- Start the server first with `python launcher.py server`
- Check that both client and server are on the same network

### Game runs slowly
- Physics simulation is CPU intensive
- Try connecting fewer clients
- Reduce the FPS if needed

### Port already in use
- Stop other instances of the server
- The error happens when running multiple servers

## Next Steps

After understanding this project, you can:

1. **Learn more asyncio**: Try `aiohttp` for web servers
2. **Study game networking**: Look into lag compensation techniques  
3. **Explore physics**: Try more complex PyMunk features
4. **Build something new**: Create your own multiplayer game!

## Additional Resources

- [Python Asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [PyMunk Physics Documentation](http://www.pymunk.org/en/latest/)
- [Pygame Tutorial](https://www.pygame.org/wiki/tutorials)
- [OSC Specification](http://opensoundcontrol.org/spec-1_0)

Remember: The best way to learn is to experiment! Try changing things and see what happens.