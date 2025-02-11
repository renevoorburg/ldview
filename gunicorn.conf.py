# Gunicorn configuration file

# Server socket
bind = '127.0.0.1:8000'
backlog = 2048

# Worker processes
workers = 3  # Regel van duim: 2 * aantal CPU cores + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = 'ldview'

# Logging
accesslog = 'access.log'
errorlog = 'error.log'
loglevel = 'info'

# SSL (uncomment if using HTTPS)
# keyfile = 'path/to/keyfile'
# certfile = 'path/to/certfile'

# Server mechanics
daemon = False
pidfile = 'ldview.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment if using HTTPS)
# ssl_version = 'TLS'
# cert_reqs = 'CERT_NONE'
# ca_certs = 'path/to/ca.crt'
# suppress_ragged_eofs = True
