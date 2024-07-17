import asyncio
import nltk
import schedule
import threading
import time

from bot.config import Config
from bot.client import Client

from features.ft1 import Ft1
from features.ft2 import Ft2
from features.ft3 import Ft3
from features.ft4 import Ft4
from features.ft5 import Ft5


def scheduler_thread():
    # please dont fucked up <3
    while True: 
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    # Downloading models
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('vader_lexicon')

    # Create discord bot
    client = Client(Config())
    
    # Initialize features
    f1 = Ft1(client)
    f2 = Ft2(client)
    f3 = Ft3(client)
    f4 = Ft4(client)
    f5 = Ft5(client)

    # Schedule repetitive tasks
    schedule.every().hour.do(lambda: asyncio.run_coroutine_threadsafe(f1.analyze_discussions(), client.bot.loop))
    schedule.every(5).minutes.do(lambda: asyncio.run_coroutine_threadsafe(f1.notify_online_streamers(), client.bot.loop))
    schedule.every().monday.do(lambda: asyncio.run_coroutine_threadsafe(f2.check_and_propose_activities(), client.bot.loop))
    schedule.every().saturday.do(lambda: asyncio.run_coroutine_threadsafe(f2.check_and_propose_activities(), client.bot.loop))
    schedule.every().day.do(lambda: asyncio.run_coroutine_threadsafe(f5.generate_report(1), client.bot.loop))
    schedule.every().monday.do(lambda: asyncio.run_coroutine_threadsafe(f5.generate_report(7), client.bot.loop))
    
    # Start the scheduler in a separate thread
    threading.Thread(target=scheduler_thread).start()

    # Run discord bot
    client.run()