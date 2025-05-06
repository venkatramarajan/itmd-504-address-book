import multiprocessing
import os
import sys

# Server socket
bind = "127.0.0.1:5000"  # Changed to localhost only
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
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

# Server hooks
def on_starting(server):
    """
    Log when the server starts
    """
    server.log.info("Starting Address Book application server")
    # Ensure log directory exists and has correct permissions
    log_dir = '/var/log/addressbook'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, mode=0o755)
    os.chmod(log_dir, 0o755)

def on_exit(server):
    """
    Log when the server exits
    """
    server.log.info("Stopping Address Book application server")

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