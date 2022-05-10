import fastf1
import os

def init():
    if not os.path.exists('.f1-cache'):
        os.makedirs(".f1-cache")
    fastf1.Cache.enable_cache('.f1-cache')
