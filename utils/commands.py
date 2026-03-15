import os
import subprocess
import psutil

class CommandUtils:
    @staticmethod
    def execute_command(command):
        """Execute a shell command and return the output and error."""
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()
        return output.decode('utf-8'), error.decode('utf-8')

    @staticmethod
    def list_files(directory):
        """List all files in a given directory."""
        return os.listdir(directory)

    @staticmethod
    def get_process_info(pid):
        """Get information about a process by its PID."""
        try:
            process = psutil.Process(pid)
            return process.info
        except psutil.NoSuchProcess:
            return None

    @staticmethod
    def get_system_info():
        """Retrieve system information such as CPU, Memory, etc."""
        return {
            'CPU Info': psutil.cpu_percent(interval=1),
            'Memory Info': psutil.virtual_memory()._asdict(),
        }

    @staticmethod
    def monitor_process(pid):
        """Monitor a running process and return its status."""
        try:
            process = psutil.Process(pid)
            return process.status(), process.cpu_percent(), process.memory_info()
        except psutil.NoSuchProcess:
            return None
