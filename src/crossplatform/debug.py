import time

LOG_PATH = "log.txt"

def debug_print(msg: str, origin:str = ""):
    with open(LOG_PATH, mode="a") as f:
        print(msg)
        f.write(f"{time.asctime()}, {origin}: {msg} \n")