# Pi code for updating the database

from flask import Flask, render_template
from flask_apscheduler import APScheduler

import database
import update_posts
import time

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


# Scheduler job for checking if updates are desired. Pulled every 10 seconds.
@scheduler.task('interval', id='do_job_A', seconds=10, misfire_grace_time=900)
def job_A():
    global update_time_log_A
    global update_time_log_B
    global update_time_log_C
    for game in ['A', 'B', 'C']:
        if database.get_game_attr(game, "update_toggle"):
            # get current time since epoch
            if int(time.time()) > update_time_log_A + database.get_game_attr(game, "update_interval"):
                update_time_log_A = int(time.time())
                update_posts.update_game(game)
        if database.get_game_attr(game, "update_now_requested"):
            database.set_game_attr(game, "update_now_requested", False)
            update_posts.update_game(game)


@app.route("/")
def home():
    return "Hello world!"


if __name__ == '__main__':
    app.run()
