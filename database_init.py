import database


def init_clean_database():
    # set urls, phase1, update_interval, update_toggle, update_now_requested for each game
    for game in ['A', 'B', 'C']:
        database.set_game_attr(game, "url", "https://hypixel.net/threads/hypixel-mini-mafia-iii-logical-fallacies-edition-game-over-town-wins.1857318/page-")
        database.set_game_attr(game, "D1", 1)
        database.set_game_attr(game, "update_interval", 300)
        database.set_game_attr(game, "update_toggle", False)
        database.set_game_attr(game, "update_now_requested", False)


init_clean_database()
