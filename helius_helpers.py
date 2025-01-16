import asyncio
import websockets
import json
import random
from datetime import datetime

async def mock_generate_event():
    event_types = ['SWAP', 'TRANSFER']
    mock_addresses = [
        'GWvnVMKwPuaHfsJUr92QNDjCLkwW7AdW1Y3dt1Vc5Jzt',
        'BXKFxNfNt6xyYcCsk5Jdv3XVqFNmXc6vXNBmpcvNhDkY',
        'FZLVHh9HqEZoYw7GtZxmRKBbfSzrZkTVEJiub2oTFYAZ'
    ]
    
    event = {
        'type': random.choice(event_types),
        'accountAddress': random.choice(mock_addresses),
        'signature': ''.join(random.choices('0123456789abcdef', k=64)),
        'timestamp': datetime.now().isoformat()
    }
    return json.dumps(event)

# Set Interval Timing Below
async def mock_websocket_server(websocket, path):
    while True:
        event = await mock_generate_event()
        await websocket.send(event)
        await asyncio.sleep(random.uniform(5, 15))

async def mock_start_server():
    server = await websockets.serve(mock_websocket_server, "localhost", 8765)
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(mock_start_server())