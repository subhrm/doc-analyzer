
from flask import Flask, request, make_response, send_from_directory
from flask_cors import CORS, cross_origin
from gevent.pywsgi import WSGIServer, LoggingLogAdapter
import os
from datetime import datetime

from image_processor.__version__ import name, version
print("%s - Version : %s" % (name, version))

# Create Flask APP Instance
app = Flask(name)

'''
    Define common logger.
'''
import logging
from .config import Config
config = Config()

log_dir = config.LOG_DIR
time_now_str = str(datetime.now()).replace(":", "-").replace(" ", "-")[:10]

log_file_name = os.path.join(log_dir, "{}.log".format(time_now_str))

if not os.path.exists(log_dir):
    os.mkdir(log_dir)

print("Logging to : ", log_file_name)
logging.basicConfig(format=config.LOG_FORMAT,
                    datefmt=config.LOG_DATE_FORMAT,
                    level=config.LOG_LEVEL,
                    filename=log_file_name)
logger = logging.getLogger(name)

logger.info("=" * 80)
logger.info("%s %s - Version : %s %s", "=" * 15, name, version, "=" * 15)
logger.info("=" * 80)

'''
    Enable CORS 
'''
if config.ENABLE_CORS:
    logger.info("Enabling CORS")
    logging.getLogger('flask_cors').level = logging.INFO
    CORS(app)


'''
    Import all the API endpoints
'''
logger.info("Initializing all API endpoints. ")

import image_processor.endpoints.__root__
import image_processor.endpoints.align_b64
import image_processor.endpoints.pdf_to_images

# Serve Static Files
@app.route('/static/<path:path>')
def serve_static_file(path):
    return send_from_directory(config.STATIC_DIR, path)

logger.info("All API endpoints initialized. ")

server_logger = LoggingLogAdapter(logger)


def start_http_server():
    '''
        Start the API server over HTTP
    '''
    logger.info("Starting HTTP Server")
    http_server = WSGIServer((config.HOST, int(config.PORT)),
                             app,
                             log=server_logger,
                             error_log=server_logger)
    http_server.serve_forever()
