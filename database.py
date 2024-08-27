import pymongo
from functools import wraps

from ctypes import Vote, Post, Phase


# Define a decorator to validate 'game' entries
def validate_game(func):
    @wraps(func)
    def wrapper(game, *args, **kwargs):
        allowed_games = {'A', 'B', 'C'}
        if game not in allowed_games:
            raise ValueError(f"Invalid game: {game}. Must be one of {allowed_games}")
        return func(game, *args, **kwargs)
    return wrapper


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mafia"]


@validate_game
def add_vote_to_db(game, vote):
    col = db["votes"]
    myquery = { "postnum": vote.postnum, "game": game }
    newvalues = { "$set": { "voter": vote.voter, "target": vote.target, "url": vote.url, "postnum": vote.postnum, "game": game } }
    col.update_one(myquery, newvalues, upsert=True)
    return


@validate_game
def get_votes_by_range(game, start, end):
    col = db["votes"]
    res = col.find({ "game": game, "postnum": { "$gte": start, "$lte": end } })
    res = sorted(res, key=lambda x: x["postnum"])
    return list(res)


@validate_game
def get_all_votes(game):
    col = db["votes"]
    res = col.find({ "game": game })
    return list(res)

  
@validate_game
def get_votes_by_voter(game, player):
    col = db["votes"]
    res = col.find({ "game": game, "voter": player })
    return list(res)


@validate_game
def get_votes_by_target(game, player):
    col = db["votes"]
    res = col.find({ "game": game, "target": player })
    return list(res)


@validate_game
def add_post_to_db(game, post):
    col = db["posts"]
    myquery = { "post_id": post.id }
    newvalues = { "$set": { "post_id": post.id, "author": post.author, "content": post.HTML, "postnum": post.postnum, "date":post.date, "game": game } }
    col.update_one(myquery, newvalues, upsert=True)
    return


@validate_game
def get_posts_by_authors(game, authors):
    col = db["posts"]    
    res = col.find({ "game": game, "author": { "$in": authors } }).sort("postnum", 1)
    return list(res)


@validate_game
def get_all_posts(game):
    col = db["posts"]
    res = col.find({ "game": game })
    return list(res)

  
@validate_game
def add_phase_to_db(game, phase):
    
    col = db["phases"]
    myquery = { "postnum": phase.postnum, "game": game }
    newvalues = { "$set": { "postnum": phase.postnum, "phase": phase.phase_name, "game": game } }
    col.update_one(myquery, newvalues, upsert=True)
    return

  
@validate_game
def get_phases(game):
    col = db["phases"]
    res = col.find({ "game": game })
    # sort phases by postnum
    res = sorted(res, key=lambda x: x["postnum"])
    return list(res)

  
def add_alias_to_db(name, alias):
    alias = alias.lower()  # for searchability
    col = db["aliases"]
    myquery = { "alias": alias }
    newvalues = { "$set": { "alias": alias, "name": name } }
    col.update_one(myquery, newvalues, upsert=True)
    return


def get_aliases():
    col = db["aliases"]
    res = col.find()
    return {x["alias"]: x["name"] for x in res} # returns a dict for searchability

 
@validate_game
def set_game_attr(game, key, value):
    # game is the column, key is the row, value is the value to update
    col = db["game_attr"]
    myquery = { "game": game, "key": key }
    newvalues = { "$set": { "game": game, "key": key, "value": value } }
    col.update_one(myquery, newvalues, upsert=True)
    return

  
@validate_game
def get_game_attr(game, key):
    col = db["game_attr"]
    q = { "game": game, "key": key }
    res = col.find_one(q)
    if res is None:
        return None
    return res["value"]


@validate_game
def wipe_game_db(game):
    # wipe all posts for a certain game
    col = db["posts"]
    q = { "game": game }
    col.delete_many(q)
    # wipe all votes for a certain game
    col = db["votes"]
    q = { "game": game }
    col.delete_many(q)
    return
