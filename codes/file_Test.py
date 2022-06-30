import pickle
import urllib.request
import urllib.parse
import json
import time
import numpy as np

if __name__ == '__main__':
    try:
        with open('last_update_id.txt', 'r') as file:
            next_update_id = int(file.read())
    except (FileNotFoundError, ValueError):
        next_update_id = 0