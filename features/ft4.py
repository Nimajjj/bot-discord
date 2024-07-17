"""
# FT-4 Proposition de GIF en temps réel

Le bot doit proposer des GIFs en fonction de l’analyse de sentiment de la discussion en cours.
Ces GIFs peuvent par exemple être un simple montage d’un GIF existant et d’un texte choc
extrait de la conversation en cours.
"""
import discord
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from features.feature import Feature
from bot.client import Client

from api_clients import giphy_api

SENTIMENT_THRESHOLD: float = 0.45

class Ft4(Feature):
    def __init__(self, client: Client) -> None:
        super().__init__(client)

        self.sid = SentimentIntensityAnalyzer()


    def analyze_sentiment(self, text) -> float:
        sentiment_scores = self.sid.polarity_scores(text)
        return sentiment_scores['compound']


    async def on_message(self, message: discord.Message) -> None:
        sentiment: float = self.analyze_sentiment(message.content)
        if sentiment < SENTIMENT_THRESHOLD and sentiment > -SENTIMENT_THRESHOLD:
            return
        
        gif: str = giphy_api.fetch_gif(message.content)
        if gif:
            user_message_excerpt = message.content[:15] + ('...' if len(message.content) > 15 else '')
            print(f"[DEBUG] sentiment={sentiment}; message='{user_message_excerpt}'; gif='{gif}'")
            
            await message.channel.send(gif)
