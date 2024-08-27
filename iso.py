# This file contains functions for working with ISOs.

from database import get_posts_by_authors
from ctypes import Post


# get_iso takes a list of players (at least one), and returns a list of all posts by those players.
# The list is sorted by post number, with the earliest post first.
# Currently, we only support one player, but having a list of players allows for multi-iso in the future.
def get_iso(players, game):
    iso_db_obj = get_posts_by_authors(game, players)  # get a list of database objects pertaining to "players"
    iso_list = []  # storage
    for mapping in iso_db_obj:
        cur_post = Post(mapping["author"], mapping["postnum"], mapping["post_id"],
                        mapping["date"], mapping["content"])  # initiate a post obj
        iso_list.append(cur_post)
    return iso_list


# rank_activity returns a formatted list of strings, where each string is a player's name and the number of posts
# they have made.
# The list is sorted by the number of posts, with the player who has made the most posts first.
def rank_activity(game):
    return NotImplemented
