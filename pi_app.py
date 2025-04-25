# Pi code for updating the database

from flask import Flask, render_template
from flask_apscheduler import APScheduler

import database
import update_posts
import time
from datetime import datetime

app = Flask(__name__)
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Stores when the last update was. Doesn't need to be persistent.
update_time_log_A = 0
update_time_log_B = 0
update_time_log_C = 0


# Global variables for the EoD toggle method
eod_toggle_until_A = None
is_A_in_eod = False
eod_toggle_until_B = None
is_B_in_eod = False
eod_toggle_until_C = None
is_C_in_eod = False

def try_update(game):
    database.set_game_attr(game, "update_now_requested", "Updating now")
    try:
        update_posts.update_game(game)
    except Exception as e:
        print(e)
    database.set_game_attr(game, "update_now_requested", False)
    
    return

# Scheduler job for checking if updates are desired. Pulled every 10 seconds.
@scheduler.task('interval', id='do_job_A', seconds=10, misfire_grace_time=900)
def job_A():
    global update_time_log_A
    global update_time_log_B
    global update_time_log_C
    for game in ['A', 'B', 'C']:
        current_time = datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")

        if game == 'A':
            current_game_log = update_time_log_A
        elif game == 'B':
            current_game_log = update_time_log_B
        else:
            current_game_log = update_time_log_C

        if database.get_game_attr(game, "update_toggle"):

            # get current time since epoch
            if int(time.time()) > current_game_log + database.get_game_attr(game, "update_interval"):
                print("updating game at " + str(time_string))
                current_game_log = int(time.time())
                try_update(game)

        if database.get_game_attr(game, "update_now_requested"):
            print("manually updating game at " + str(time_string))
            current_game_log = int(time.time())  # reset automatic update timer
            try_update(game)

        # save value
        if game == 'A':
            update_time_log_A = current_game_log
        elif game == 'B':
            update_time_log_B = current_game_log
        else:
            update_time_log_C = current_game_log


# Scheduler job for EoD toggle (temp vc auto update delay change)
@scheduler.task('interval', id='check_toggle_and_run', seconds=10, misfire_grace_time=900)
def job_eod():
    global eod_toggle_until_A, is_A_in_eod
    global eod_toggle_until_B, is_B_in_eod
    global eod_toggle_until_C, is_C_in_eod

    eod_toggle_length = (30 * 60)  # Currently, EoD toggle lasts for 30mins
    default_autoupdate_length = (5 * 60)  # default waiting period before auto scrape
    if_eod_autoupdate_length = 20  # 20 second autoupdate pause

    for game in ['A', 'B', 'C']:
        current_time = datetime.now()
        now_epoch = time.time()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")

        if game == 'A':
            current_game_toggle = eod_toggle_until_A
            is_currently_eod = is_A_in_eod
        elif game == 'B':
            current_game_toggle = eod_toggle_until_B
            is_currently_eod = is_B_in_eod
        else:
            current_game_toggle = eod_toggle_until_C
            is_currently_eod = is_C_in_eod

        database_response = database.get_game_attr(game, "eod_toggle")

        # Check for the flag being set by the discord command
        if database_response:
            if not is_currently_eod:  # if eod toggle needs startup
                current_game_toggle = now_epoch + eod_toggle_length  # add 30 mins
                is_currently_eod = True
                print(f"[@ {time_string}]: EoD toggle flag for game {game} detected, 30 minute timer begun.")

                database.set_game_attr(game, "update_interval", if_eod_autoupdate_length)  # update the interval
                database.set_game_attr(game, "eod_toggle", False)

            else:  # If EoD is already toggled
                current_game_toggle = now_epoch + eod_toggle_length

                print(f"[@ {time_string}]: EoD toggle flag for game {game} extended.")

        elif database_response is None:  # eod_toggle needs to be created
            database.set_game_attr(game, "eod_toggle", False)

        # Check if the current EoD toggle has been active for >30min
        if is_currently_eod and now_epoch > current_game_toggle:
            database.set_game_attr(game, "update_interval", default_autoupdate_length)  # resume default
            print(f"[@ {time_string}]: 30 mins passed for game {game}. Update interval reset.")

        # remembering the game's values
        if game == 'A':
            eod_toggle_until_A = current_game_toggle
            is_A_in_eod = is_currently_eod
        elif game == 'B':
            eod_toggle_until_B = current_game_toggle
            is_B_in_eod = is_currently_eod
        else:
            eod_toggle_until_C = current_game_toggle
            is_C_in_eod = is_currently_eod


@app.route("/")
def home():
    return "Hello world!"


if __name__ == '__main__':
    app.run()
