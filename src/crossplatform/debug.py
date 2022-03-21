import logging
import time
import traceback
import sys

LOG_PATH = "tmp/log.txt"
LOG_FILENAME = '/tmp/logging_example.out'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)

exc_type, exc_value, exc_traceback = sys.exc_info()

def debug_print(msg: str, origin:str = ""):
    with open(LOG_PATH, mode="a") as f:
        tback = traceback.format_exc()

        print(msg, tback)
        logging.exception(msg)
        f.write(f"{time.asctime()}, {origin}: {msg}; traceback: {tback} \n")