# This file contains a function to calculate the votecount for a given postnum in a given game.
import math

import database
import update_posts


def get_playerlist(postnum, og_playerlist):
    playerlist = []
    for row in og_playerlist:
        if row["When did they join?"] == "":
            row["When did they join?"] = -1
        if row["When did they die?"] == "":
            row["When did they die?"] = float("inf")

        if row["When did they join?"] < postnum < row["When did they die?"]:
            playerlist.append(row["Forum Username"].lower())
        
    return playerlist


def get_votecount(game, postnum):
    current_phase = None

    # identify what phase the post is in
    phases = database.get_phases(game)
    for phase in reversed(phases):
        if postnum >= phase['postnum']:
            current_phase = phase
            break

    og_playerlist = update_posts.get_original_playerlist(game)
    aliases = database.get_aliases()            
   
    votes = database.get_votes_by_range(game, current_phase['postnum'], postnum)
    
    # temp dict. Format is {voter: target}
    working_votes = {}

    # Loop through all votes. Each time a vote is added to working_votes, calculate the votecount, check for hammer, etc
    for vote in votes:
        playerlist = get_playerlist(vote['postnum'], og_playerlist)
        if vote['voter'] not in playerlist:
            continue

        working_votes[vote['voter']] = vote

        for p in playerlist:
            if p not in working_votes.keys():
                working_votes[p] = {'voter': p, 'target': 'Not voting', 'postnum': 1, 'url': 'google.ca'}

        # end result is a dictionary representing the most recent votes
        
        for voter in working_votes.keys():
            target = working_votes[voter]['target']
            if target.lower() in aliases.keys():
                working_votes[voter]['target'] = aliases[target.lower()]
        
        # dictionary representing the final votecount. Format: {target: [vote, vote, vote]}
        votecount = {}
        for voter in working_votes.keys():
            target = working_votes[voter]['target']
            if target not in votecount.keys():
                votecount[target] = [working_votes[voter]]
            else:
                votecount[target].append(working_votes[voter])
        
        # check hammer
        for target in votecount.keys():
            if len(votecount[target]) > (len(playerlist)/2) and target != "Not voting":
                hammer = (target, vote['postnum'])
                break
            else:
                hammer = None

        if hammer is not None:
            break

    # format votecount
    
    output = "{} Votecount:\n".format(current_phase['phase'])
    # sort the votecount by number of votes, high to low
    votecount = dict(sorted(votecount.items(), key=lambda item: len(item[1]), reverse=True))
    for target in votecount.keys():
        output += "({}) {}: ".format(len(votecount[target]), target)
        for vote in votecount[target]:
            output += "{}, ".format(vote['voter'].title())
        output = output[:-2] + "\n"

    if hammer is not None:
        output += "\n{} was hammered at post {}.".format(hammer[0], hammer[1])
    else:
        output += "\nWith {} players alive, it takes {} votes to hammer.".format(len(playerlist), math.ceil(len(playerlist) / 2))
    return output
