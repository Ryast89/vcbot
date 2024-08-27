# ctypes.py
# Custom Types centralized


# Phases are moderator-defined stages of a game. Usually, this is used for day 1, day 2, etc
# Phases are used by the retrospective votecounts to determine which votes are in the current phase
# Phases have a user-defined name and a post number that marks the beginning of the phase.

class Phase:
    def __init__(self, postnum, phase_name):
        self.postnum = postnum
        self.phase_name = phase_name


# Posts are used by the ISO endpoint to collect all posts by a player.
# User is the player who made the vote
# Number is the post number within the thread
# id is the hypixel forums post id
# Date is the date the post was made
# HTML is the content of the post

class Post:
    def __init__(self, author, postnum, id, date, html):
        self.author = author
        self.postnum = postnum
        self.id = id
        self.date = date
        self.HTML = html


# Votes are placed by players, and are read in by the bot update.
# Votes have a voter, a target, a link to the post, and a post number.

class Vote:
    def __init__(self, voter, target, url, postnum, game):
        self.voter = voter
        self.target = target
        self.url = url
        self.postnum = postnum
        self.game = game
