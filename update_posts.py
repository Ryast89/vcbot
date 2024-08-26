import cloudscraper
from bs4 import BeautifulSoup
import pytz
import datetime
import re
import gspread
import time
import random

import database

gc = gspread.service_account(filename="Credentials/google_secret.json")

sh = gc.open("Aerosync")

from object_types.post import post
from object_types.vote import vote

#read_from_last reads all posts from the last read page to the current page and returns the posts as a list.
def read_from_last(url, last_page_number):

    scrapedPosts = []  #list of post objects
    prev_post_number = -1

    for i in range(last_page_number, 1000):
        time.sleep(random.randint(500,1500)/1000.0)
        #cloudscraper is a library that bypasses cloudflare protection - similar to requests
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url + str(i))
        soup = BeautifulSoup(response.content, 'html.parser')

        firstpostnumber = int(
        soup.find("article", class_='message').find(
            "ul", {
                "class":
                "message-attribution-opposite message-attribution-opposite--list"
            }).text.replace(",", "").replace("\n", "").replace(
                "#", ""))  #first post number of the page

        if firstpostnumber == prev_post_number:
            break

        prev_post_number = firstpostnumber

        #Extract relevant info to create a post object
        for message in soup.find_all("article", class_='message'):

            username = message.find(class_='username').get_text().replace(
                "\n", "").replace(" ", "").lower()
            postnumber = int(
                message.find(
                    "ul", {
                        "class":
                        "message-attribution-opposite message-attribution-opposite--list"
                    }).text.replace("\n", "").replace(",", "").replace("#", ""))
            timestamp = int(message.find("time").get("data-time"))

            # Get a timezone object for the desired timezone
            tz = pytz.timezone('US/Eastern')

            # Convert the timestamp to a datetime object
            dt = datetime.datetime.fromtimestamp(timestamp, tz)
            postdate = dt.strftime('%Y-%m-%d %H:%M %Z')

            postid = message.find("a", rel='nofollow')["href"]
            postid = int(postid[postid.find("post-") + 5:])

            #add post to list
            scrapedPosts.append(
                post(username, postnumber, postid, postdate, str(message)))
          
    return scrapedPosts

#update_game updates the posts and votes in the database for a game.
def update_game(game):

    # Call read_from_last to get all posts from the last read page to the current page
    # For each post in the list:
        # Check if the post is already in the database
        # If not, add the post to the database
        # If yes, update the post in the database
        # Check if the post has votes
        # If yes, update the votes in the database
    stored_posts = database.get_all_posts(game)

    #sort posts by post number
    stored_posts.sort(key=lambda x: x["postnum"])

    #get the last post number
    if stored_posts != []:
        last_post_number = stored_posts[-1]["postnum"]
        last_page_number = last_post_number//20 + 1 #20 posts per page
    else:
        last_post_number = 0
        last_page_number = 1
    
    #need to update this to get the actual thread url from database
    url = database.get_game_attr(game, "url")
    new_posts = read_from_last(url, last_page_number)

    for post in new_posts:
        if post.postnum > last_post_number:
            database.add_post_to_db(game, post)

            #check for votes
            message = post.HTML
            message = BeautifulSoup(message, 'html.parser')

            text = (message.find(class_='bbWrapper')).get_text()
         
            for quote in (message.find_all("blockquote")):
                #delete quote from text
                text = text.replace(quote.get_text(), "")

            #check if there's a vote within valid tags
            #Use a regex to find what the LAST text string starting with <vote> and ending with </vote> is
            #Not case sensitive. Stripped. Returns name of target
            matches = re.findall(r'\[vote\](.*?)\[/vote\]', text, re.IGNORECASE | re.DOTALL)
            target = matches[-1].strip() if matches else None

            if target != None:
                target = target.replace("@", "").lower()
                v = vote(post.author, target, "google.ca", post.postnum, game)
                database.add_vote_to_db(game, v)
    

    return

def scrape_playerlist(game):
    playerlist = []

    scraper = cloudscraper.create_scraper()
    response = scraper.get(database.get_game_attr(game, "url")+"1").text
    soup = BeautifulSoup(response, 'html.parser')

    message = soup.find_all("article", class_='message')[0]
    text = (message.find(class_='bbWrapper')).get_text()
    text = text[text.lower().find("spoiler: living players"):text.lower().
                find("spoiler: dead players")]

    while (text.find("@") != -1):
        text = text[text.find("@"):]
        player = text[text.find("@") + 1:text.find('\n')].replace(" ", "").replace(
            "\u200b", "")
        playerlist.append(player)
        text = text[text.find('\n'):]

    #in sh, open tab "Game {}"
    ws = sh.worksheet("Game {}".format(game))

    ws.batch_clear(["A2:C1000"])  #clear all cells

    for i in range(0, len(playerlist)):
        ws.update_acell("A{}".format(i + 2), playerlist[i])
  
    #clear "Forum Username", "When did they join?", "When did they die?" columns - columns 1, 2, 3 
    return

def get_original_playerlist(game):
    ws = sh.worksheet("Game {}".format(game))    
    #get col A, B, and C in a pandas dataframe
    df = ws.get_all_records(expected_headers=["Forum Username", "When did they join?", "When did they die?"], head=1)
    return(df)