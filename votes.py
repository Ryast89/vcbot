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

        if row["When did they join?"] <= postnum <= row["When did they die?"]:
            playerlist.append(row["Forum Username"].lower())
        
    return playerlist

def create_vc_dict(working_votes, aliases):
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
    
    return votecount

def get_phase(game, postnum, phases):
    for phase in reversed(phases):
        if postnum >= phase['postnum']:
            return phase
    return None

def get_vote_history(game):
    votes = database.get_all_votes(game)
    i = 0
    output = ""
    phases = database.get_phases(game)
    for vote in votes:
        i += 1
        phase = get_phase(game, vote['postnum'], phases)
        output += "<tr class=''><td class='position'>" + str(i) + "</td><td class='data'>" + vote['voter'] + "</td><td class='data'>" + vote['target'] + "</td><td class='data'><a href=" + vote['url'] + ">" + str(vote['postnum']) + "</a></td>" + "<td class='data'>" + phase['phase'] + "</td>" + "<td class='retro-vc'> <a href='#' class='retrospective-vc-link' data-postnum='" + str(vote['postnum']) + "'>Link</a></td></tr>"
    return output

def get_votecount(game, postnum):

    # identify what phase the post is in
    phases = database.get_phases(game)
    current_phase = get_phase(game, postnum, phases)

    og_playerlist = update_posts.get_original_playerlist(game)
    playerlist = get_playerlist(postnum, og_playerlist)
 
    aliases = database.get_aliases()            
    votes = database.get_votes_by_range(game, current_phase['postnum'], postnum)
    
    # temp dict. Format is {voter: target}
    working_votes = {}

    #Assign everyone "Not Voting" to begin with
    for p in playerlist:
        working_votes[p] = {'voter': p, 'target': 'Not voting', 'postnum': 1, 'url': None}

    if votes == []:
        votecount = create_vc_dict(working_votes, aliases)
        hammer = None
    
    else:
        # Loop through all votes. Each time a vote is added to working_votes, calculate the votecount, check for hammer, etc
        for vote in votes:
            if vote['voter'] not in playerlist:
                continue

            working_votes[vote['voter']] = vote
            # end result is a dictionary representing the most recent votes

            votecount = create_vc_dict(working_votes, aliases)
            
            # check hammer
            for target in votecount.keys():
                if len(votecount[target]) > (len(playerlist)/2.0) and target != "Not voting" and database.get_game_attr(game, "hammer_toggle"):
                    hammer = (target, vote['postnum'])
                    break
                else:
                    hammer = None

            if hammer is not None:
                break
    
    # format votecount
    if postnum == float('inf'):
        postnum = database.get_latest_post(game)['postnum']
    output = "**{} Votecount** (as of post **{}**):\n\n".format(current_phase['phase'], postnum)
    # sort the votecount by number of votes, high to low
    votecount = dict(sorted(votecount.items(), key=lambda item: len(item[1]), reverse=True))
    #put Not Voting at the end, if it exists
    if "Not voting" in votecount.keys():
        not_voting = votecount.pop("Not voting")
        votecount["Not voting"] = not_voting

    for target in votecount.keys():
        if target == "Not voting":
            output += "\n({}) {}: ".format(len(votecount[target]), target)
            for vote in votecount[target]:
                output += "{}, ".format(vote['voter'].title())
        else:
            output += "({}) {}: ".format(len(votecount[target]), target)
            for vote in votecount[target]:
                output += "[{}]({}), ".format(vote['voter'].title(), vote['url'])
        output = output[:-2] + "\n"

    output = output.replace('\n\n\n', '\n\n')

    if hammer is not None:
        output += "\n{} was hammered at post {}.".format(hammer[0], hammer[1])
    else:
        if database.get_game_attr(game, "hammer_toggle"):
            output += "\nWith {} players alive, it takes {} votes to hammer.".format(len(playerlist), math.floor(len(playerlist) / 2.0 + 1))
        else:
            output += "\nHammering is not currently enabled."
    return output
