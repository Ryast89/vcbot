from flask import Flask, render_template
from flask_apscheduler import APScheduler
from iso import get_iso
from ctypes import Post

app = Flask(__name__)
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()
app.config["TEMPLATES_AUTO_RELOAD"] = True

# interval example
@scheduler.task('interval', id='do_job_1', seconds=300, misfire_grace_time=900)
def job1():
    print('Posts updated (NOT IMPLEMENTED)')



# https://github.com/HyperbolicStudios/YYJ-Bus-Speed-Tracker/blob/main/app.py
# Use above as an example

# set up scheduler for votecount updates
#@scheduler.task('interval', id='do_job_1', seconds=10, misfire_grace_time=900)
# REQUIRED FUNCTION: Must be able to update votecounts for all games

# Set up endpoint for votecount
#@app.route('/<game>/votecount')
# REQUIRED FUNCTION: Must be able to create a retrospective votecount for any post


# Set up endpoint for retrospective votecount
#@app.route('/<game>/votecount/<postnum>')
# REQUIRED FUNCTION: Must be able to create a retrospective votecount for any post


# Set up endpoint for vote history
#@app.route('/<game>/votes')
# REQUIRED FUNCTION: Must be able to collect all votes placed this game


# Set up endpoint for targeted ISO
@app.route('/<game>/iso/<target>')
def iso(game, target):
    # take target, append it to a list of targets containing only that target
    targets = [target]
    posts = get_iso(targets, game)
    articles = []
    for post in posts:
        articles.append(post.HTML)

    return render_template('iso.html', posts=articles)

# Above this line: All outlined functions have stubs
# --------------------------------------------------------------------------------------------

# Set up endpoint for login
#@app.route('/login')
# Allow for a login session to be created
# Login session should be able to be removed by site admin remotely


# Set up endpoint for logout
#@app.route('/logout')
# Allow for a login session to be removed


# Set up endpoint for game management
#@app.route('/<game>/manage')
    # This endpoint needs to be able to do the following:
    # Set the game URL
    # wipe the game's data
    # create a new phase in the game
    # Toggle EOD mode?


# set up endpoint for game playerlist management
#@app.route('/<game>/players')
    # This endpoint needs to be able to do the following:
    # Add a player
    # Remove a player
    # Replace a player
    # Set a player's living/dead status
    # List all players


# Set up endpoint for alias management
#@app.route('/aliases')
    # This endpoint needs to be able to do the following:
    # Add an alias
    # Remove an alias
    # List all aliases
    # Shift aliases to a new username


