"""Production process boundary for the Expedition verification service."""

import os


bind = os.environ.get("PORT_BIND", "0.0.0.0:8080")
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
threads = int(os.environ.get("WEB_THREADS", "4"))
worker_class = "gthread"
timeout = 15
graceful_timeout = 15
keepalive = 5
limit_request_line = 1024
limit_request_fields = 32
limit_request_field_size = 2048
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(t)s "%(m)s %(U)s" %(s)s %(b)s %(L)s'
capture_output = False
preload_app = False
