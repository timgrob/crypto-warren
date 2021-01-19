import os
from os import environ


if __name__ == "__main__":
    key = environ['test-key']
    print('hello world')
    print(key)
    print('----------')