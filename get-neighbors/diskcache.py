import psutil
import os

def available_memory():
    """
    Return the available memory in MB
    """
    
    return psutil.virtual_memory().available / float(2 ** 20)


class DiskCache(object):
    
    def __init__(self):
        self.file_handler = open('')
