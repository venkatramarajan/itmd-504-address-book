import multiprocessing
import os
import sys

# Server socket
bind = "127.0.0.1:5000"  # Changed to localhost only
backlog = 2048

# Worker processes
workers = 2  # Reduced number of workers for debugging
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = '/var/log/addressbook/access.log'
errorlog = '/var/log/addressbook/error.log'
loglevel = 'debug'  # Changed to debug for troubleshooting
capture_output = True
enable_stdio_inheritance = True

# Process naming
proc_name = 'addressbook'

# SSL (uncomment and configure if using HTTPS)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Server mechanics
daemon = False
pidfile = '/var/run/addressbook.pid'
umask = 0o022
user = 'www-data'
group = 'www-data'
tmp_upload_dir = None

def check_environment():
    """
    Check if all required environment variables and directories exist
    """
    required_dirs = [
        '/var/www/addressbook',
        '/var/log/addressbook',
        '/var/www/addressbook/venv',
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"Error: Required directory {directory} does not exist")
            return False
    
    # Check if .env file exists and is readable
    env_file = '/var/www/addressbook/.env'
    if not os.path.exists(env_file):
        print(f"Error: .env file not found at {env_file}")
        return False
    
    try:
        with open(env_file, 'r') as f:
            f.read()
    except PermissionError:
        print(f"Error: Cannot read .env file at {env_file}")
        return False
    
    return True

def on_starting(server):
    """
    Log when the server starts and check environment
    """
    print("Starting Address Book application server")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Environment variables: {dict(os.environ)}")
    
    if not check_environment():
        print("Environment check failed")
        sys.exit(1)
    
    # Ensure log directory exists and has correct permissions
    log_dir = '/var/log/addressbook'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, mode=0o755)
    os.chmod(log_dir, 0o755)
    
    print("Environment check passed")

def on_exit(server):
    """
    Log when the server exits
    """
    print("Stopping Address Book application server")

def worker_int(worker):
    """
    Log when a worker receives SIGINT or SIGQUIT
    """
    worker.log.info("Worker received SIGINT or SIGQUIT")

def worker_abort(worker):
    """
    Log when a worker receives SIGABRT
    """
    worker.log.info("Worker received SIGABRT")

def post_fork(server, worker):
    """
    Log after a worker has been forked
    """
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """
    Log before a worker is forked
    """
    pass

def pre_exec(server):
    """
    Log before a new master process is forked
    """
    server.log.info("Forked master process") 