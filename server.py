import asyncio
import websockets
import json

connected_devices = {}

def register_device(device_id):
    connected_devices[device_id] = {"status": "online"}
    print(f"Device {device_id} registered.")

def unregister_device(device_id):
    if device_id in connected_devices:
        del connected_devices[device_id]
        print(f"Device {device_id} unregistered.")

async def handle_device_commands(websocket, path):
    async for message in websocket:
        data = json.loads(message)
        device_id = data.get("device_id")

        if data["action"] == "register":
            await register_device(device_id)
        elif data["action"] == "unregister":
            await unregister_device(device_id)
        elif data["action"] == "execute_command":
            command = data.get("command")
            # Execute command logic here
            response = {"status": "executed", "command": command}
            await websocket.send(json.dumps(response))

async def monitor_devices():
    while True:
        # Update the status of connected devices (for example, every minute)
        await asyncio.sleep(60)

async def main():
    async with websockets.serve(handle_device_commands, "localhost", 6789):
        await monitor_devices()

if __name__ == "__main__":
    asyncio.run(main())
