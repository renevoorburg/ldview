# Gunicorn configuration file

# Server socket
bind = '0.0.0.0:8000'  # Listen on all interfaces
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
accesslog = '/var/log/ldview/access.log'
errorlog = '/var/log/ldview/error.log'
loglevel = 'warning'  # Changed from 'info' to 'warning'

# Process management
pidfile = '/var/run/ldview/gunicorn.pid'
worker_tmp_dir = '/var/run/ldview'

# SSL (uncomment if using HTTPS)
# keyfile = 'path/to/keyfile'
# certfile = 'path/to/certfile'

# Server mechanics
daemon = False
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (uncomment if using HTTPS)
# ssl_version = 'TLS'
# cert_reqs = 'CERT_NONE'
# ca_certs = 'path/to/ca.crt'
# suppress_ragged_eofs = True
