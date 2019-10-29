import re
import time
from collections import deque
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(filename="bot.log", level=logging.INFO, filemode="w")
my_log = logging.getLogger()
handler = RotatingFileHandler("maxsize", maxBytes=2048, backupCount=1)
my_log.addHandler(handler)

from property import ALLOWED_TIME_PASSED, REJECTION, REJECTION_TIME


def log(*args):
    list(map(logging.info, args))


REGEX_HTML_CLEANER = re.compile('<.*?>')


def clean_html(raw_html):
    return re.sub(REGEX_HTML_CLEANER, '', raw_html)


class PollStat:

    def __str__(self):
        return f"PollStat[{self.likes}, {self.dislikes}, {self.rejects}] Stiker = {self.stiker_id}"

    def __repr__(self):
        return str(self)

    def __init__(self, stiker_id):
        self.likes = set()
        self.dislikes = set()
        self.rejects = set()
        self.stiker_id = stiker_id

    def remove_vote(self, user_id):
        self.likes.discard(user_id)
        self.dislikes.discard(user_id)
        self.rejects.discard(user_id)

    def add_like(self, user_id):
        self.likes.add(user_id)

    def add_dislike(self, user_id):
        self.dislikes.add(user_id)

    def add_reject(self, user_id):
        self.rejects.add(user_id)

    def __iter__(self):
        yield self.likes
        yield self.dislikes
        yield self.rejects


class TimeProtector:

    def __init__(self):
        self.last_time = time.time()

    def refresh_time(self):
        self.last_time = time.time()

    def can_post(self):
        return time.time() - self.last_time >= ALLOWED_TIME_PASSED


class RejectProtector:

    def __init__(self):
        self.rejections = deque(maxlen=REJECTION)

    def add_rejection(self, times):
        for i in range(times):
            self.rejections.append(time.time())

    def can_post(self):
        if len(self.rejections) == REJECTION:
            return time.time() - self.rejections[0] >= REJECTION_TIME
        return True
