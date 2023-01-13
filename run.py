import logging
import os
from app import server

logging.basicConfig(level = logging.DEBUG)
if __name__ == '__main__':
    server.app.run(host = 'localhost', port = int(os.environ.get('PORT', '9000')))