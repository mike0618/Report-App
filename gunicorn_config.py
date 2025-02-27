import eventlet

bind = "unix:mikedrun.sock"
workers = 1
worker_class = "eventlet"
timeout = 60
daemon = False
max_requests = 1000
keepalive = 2
preload_app = True
errorlog = "/home/miked/mikedrun/logs/gunicorn.error.log"
accesslog = "/home/miked/mikedrun/logs/gunicorn.access.log"


def post_fork(server, worker):
    eventlet.monkey_patch()
