def log(*messages):
    # TODO Real logging
    print(*messages)


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
