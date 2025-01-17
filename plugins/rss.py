import os
import sys
import pyrogram
import feedparser
import bot
from sql import db
from time import sleep, time
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config

api_id = Config.API_ID
api_hash = Config.API_HASH
feed_urls = Config.FEED_URLS
bot_token = Config.BOT_TOKEN
log_channel = Config.LOG_CHANNEL
check_interval = Config.INTERVAL
max_instances = Config.MAX_INSTANCES

for feed_url in feed_urls:
    if db.get_link(feed_url) == None:
        db.update_link(feed_url, "*")

app = pyrogram.Client("RSSBOT", bot_token=Config.BOT_TOKEN, api_id=Config.API_ID, api_hash=Config.API_HASH,)

def create_feed_checker(feed_url):
    def check_feed():
        FEED = feedparser.parse(feed_url)
        entry = FEED.entries[0]
        enid = entry.id
        if entry.id != db.get_link(feed_url).link:
                       # ↓ Edit this message as your needs.
            if "eztv.re" in enid:   
                message = f"{entry.torrent_magneturi}"
            elif "yts.mx" in enid:
                message = f"{entry.links[1]['href']}"
            else:
                message = f"{entry.link}"
            try:
                msg = app.send_message(log_channel, message)
                msg.reply_text("/leech@jarvisleechbot")
                db.update_link(feed_url, entry.id)
                
            except FloodWait as e:
                print(f"FloodWait: {e.x} seconds")
                sleep(e.x)
            except Exception as e:
                print(e)
        else:
            print(f"Checked RSS FEED: {entry.id}")
    return check_feed


scheduler = BackgroundScheduler()
for feed_url in feed_urls:
    feed_checker = create_feed_checker(feed_url)
    scheduler.add_job(feed_checker, "interval", seconds=check_interval, max_instances=max_instances)
scheduler.start()
