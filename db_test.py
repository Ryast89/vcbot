# test adding everything
from database import add_alias_to_db, add_phase_to_db, add_post_to_db, add_vote_to_db, \
                     set_game_attr, get_game_attr, get_votes_by_range, get_votes_by_voter
import time
from ctypes import Vote, Post, Phase

# test adding a vote
v = Vote("voter", "target", "url", 1)
add_vote_to_db("A", v)

# test adding a post
p = Post("author", 1, 1, "date", "HTML")
add_post_to_db("A", p)

# test adding a phase
ph = Phase(1, "phase")
add_phase_to_db("A", ph)

# test adding an alias
add_alias_to_db("name", "alias")

# test updating a key
set_game_attr("A", "test_key", "test_value")

# sleep for a while
time.sleep(15)

# test getting data
print(get_game_attr("A", "test_key"))

# test getting data that doesn't exist
print(get_game_attr("A", "nonexistent_key"))

# test getting votes from a range
# First, add 10 votes, with postnum 1-10
for i in range(1, 11):
    v = Vote("voter", "target", "url", i)
    add_vote_to_db("A", v)

# Then, get votes from 5-7
print(get_votes_by_range("A", 5, 7))

# test getting votes by player
# First, add votes from 1-10, with voter "voter", and from 11-20, with voter "voter2"
for i in range(1, 11):
    v = Vote("voter", "target", "url", i)
    add_vote_to_db("A", v)
for i in range(11, 21):
    v = Vote("voter2", "target", "url", i)
    add_vote_to_db("A", v)

# Then, get votes from "voter"
print(get_votes_by_voter("A", "voter"))
