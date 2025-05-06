import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
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
loglevel = 'info'

# Process naming
proc_name = 'addressbook'

# SSL (uncomment and configure if using HTTPS)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Server mechanics
daemon = False
pidfile = '/var/run/addressbook.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# Server hooks
def on_starting(server):
    """
    Log when the server starts
    """
    server.log.info("Starting Address Book application server")

def on_exit(server):
    """
    Log when the server exits
    """
    server.log.info("Stopping Address Book application server") 