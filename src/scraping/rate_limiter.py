
"""
Rate limiting utilities for Thesis-Webscraper.

Control the frequency of requests to external websites.
"""

import random
import threading
import time
from collections import deque
from typing import Deque


class RateLimiter:
    """
    Rate limiter using minimum delays and a sliding window.
    
