import logging
import sys

def setup_logging(logger_name):
    logging.basicConfig(stream=sys.stdout, format='%(filename)s: %(message)s')
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    return logger