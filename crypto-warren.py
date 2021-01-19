import os
from os import environ
import time


if __name__ == "__main__":
    key = environ['test-key']
    while True:
        print('hello world')
        print(key)
        print('----------')
        time.sleep(120)
