import asyncio
import websockets
import json
import logging
import platform
import psutil
from datetime import datetime
from utils.commands import CommandUtils
import config

logging.basicConfig(level=config.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeviceAgent:
    def __init__(self, server_url: str, device_id: str, device_name: str = None):
        self.server_url = server_url
        self.device_id = device_id
        self.device_name = device_name or platform.node()
        self.websocket = None
        self.connected = False
        self.reconnect_attempts = 0
    
    async def connect(self):
        """Establish connection to the server"""
        while self.reconnect_attempts < config.MAX_RECONNECT_ATTEMPTS:
            try:
                logger.info(f"Connecting to server at {self.server_url}...")
                async with websockets.connect(self.server_url) as websocket:
                    self.websocket = websocket
                    self.connected = True
                    self.reconnect_attempts = 0
                    logger.info(f"Connected to server as {self.device_id}")
                    
                    await self.register()
                    await self.run()
            
            except Exception as e:
                self.reconnect_attempts += 1
                logger.error(f"Connection failed: {str(e)}. Retrying in {config.RECONNECT_INTERVAL}s...")
                await asyncio.sleep(config.RECONNECT_INTERVAL)
    
    async def register(self):
        """Register device with the server"""
        register_msg = {
            'action': 'register',
            'device_id': self.device_id,
            'device_name': self.device_name,
            'system': platform.system(),
            'platform': platform.platform()
        }
        await self.websocket.send(json.dumps(register_msg))
        logger.info(f"Device registered: {self.device_id}")
    
    async def send_heartbeat(self):
        """Send periodic heartbeat to server"""
        while self.connected:
            try:
                heartbeat_msg = {
                    'action': 'heartbeat',
                    'device_id': self.device_id,
                    'timestamp': datetime.now().isoformat()
                }
                await self.websocket.send(json.dumps(heartbeat_msg))
                await asyncio.sleep(config.HEARTBEAT_INTERVAL)
            except Exception as e:
                logger.error(f"Heartbeat error: {str(e)}")
                break
    
    async def send_metrics(self):
        """Send system metrics to server"""
        while self.connected:
            try:
                metrics = {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory': psutil.virtual_memory()._asdict(),
                    'disk': psutil.disk_usage('/')._asdict()
                }
                msg = {
                    'action': 'metrics',
                    'device_id': self.device_id,
                    'data': metrics,
                    'timestamp': datetime.now().isoformat()
                }
                await self.websocket.send(json.dumps(msg))
                await asyncio.sleep(config.HEARTBEAT_INTERVAL)
            except Exception as e:
                logger.error(f"Metrics error: {str(e)}")
                break
    
    async def execute_command(self, command_data):
        """Execute command and send response"""
        action = command_data.get('action')
        try:
            if action == 'shell':
                output, error = CommandUtils.execute_command(command_data.get('command'))
                result = {'output': output, 'error': error}
            
            elif action == 'system_info':
                result = CommandUtils.get_system_info()
            
            elif action == 'file_list':
                result = CommandUtils.list_files(command_data.get('path', '.'))
            
            else:
                result = {'error': f'Unknown action: {action}'}
        
        except Exception as e:
            result = {'error': str(e)}
        
        response = {
            'action': 'response',
            'device_id': self.device_id,
            'command_id': command_data.get('id'),
            'data': result,
            'timestamp': datetime.now().isoformat()
        }
        await self.websocket.send(json.dumps(response))
        logger.info(f"Command executed: {action}")
    
    async def run(self):
        """Main agent loop - listen for commands"""
        heartbeat_task = asyncio.create_task(self.send_heartbeat())
        metrics_task = asyncio.create_task(self.send_metrics())
        
        try:
            async for message in self.websocket:
                data = json.loads(message)
                command_action = data.get('action')
                
                if command_action in ['shell', 'system_info', 'file_list']:
                    await self.execute_command(data)
        
        except Exception as e:
            logger.error(f"Error in agent loop: {str(e)}")
        finally:
            self.connected = False
            heartbeat_task.cancel()
            metrics_task.cancel()

async def main():
    import argparse
    parser = argparse.ArgumentParser(description='CyForteAI Device Agent')
    parser.add_argument('--server-url', default=config.SERVER_URL, help='Server URL')
    parser.add_argument('--agent-id', default=config.AGENT_ID, help='Device Agent ID')
    parser.add_argument('--agent-name', help='Device Agent Name')
    args = parser.parse_args()
    
    agent = DeviceAgent(args.server_url, args.agent_id, args.agent_name)
    await agent.connect()

if __name__ == "__main__":
    asyncio.run(main())