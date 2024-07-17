"""
# FT-1 Système de recommandation de contenu

## Recommandation de contenu

Le bot doit analyser les sujets de discussion récents toutes les X heures (paramétrable) et
recommander des articles, vidéos, ou ressources pertinentes.

## Notifications de streamers en ligne

Le bot doit notifier les membres du serveur Discord (en envoyant un message dans un salon)
lorsqu’un streamer devient online sur Twitch. Les streamers à surveiller ne sont pas
paramétrables par les utilisateurs du serveur Discord, mais seulement par l’administrateur du
bot.
"""
import os
import discord
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import requests

from features.feature import Feature
from bot.client import Client
from bot.command import Command

from api_clients import twitch_api


# number of recommendations <= MAX_TOPICS_EXTRACTED * MAX_ARTICLES_PER_TOPIC * N discussions
MAX_TOPICS_EXTRACTED: int = 3
MAX_ARTICLES_PER_TOPIC: int = 2
HISTORY_LIMIT: int = 300


class Ft1(Feature):
    def __init__(self, client: Client) -> None:
        super().__init__(client)
        client.register_feature(self)

        client.register_command(Command(
            name="ft1-ask-recommendations", 
            description="Analyze last discussions and propose recommendations", 
            callback=self._recommendations, 
            options=None
        ))

        client.register_command(Command(
            name="ft1-notify-twitch", 
            description="Verify if registered twitch users are connected", 
            callback=self._twitch, 
            options=None
        ))


    def extract_topics(self, messages):
        stop_words = set(stopwords.words('french'))
        words = []

        for message in messages:
            tokens = word_tokenize(message.lower())
            filtered_tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
            words.extend(filtered_tokens)

        most_common_words = [word for word, count in Counter(words).most_common(MAX_TOPICS_EXTRACTED)]
        return most_common_words
    

    def fetch_recommendations(self, topics):
        recommendations = []

        for topic in topics:
            response = requests.get(
                f'https://newsapi.org/v2/everything?q={topic}&apiKey={os.getenv("NEWS_TOKEN")}'
            )

            i: int = 0
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                for article in articles:
                    recommendations.append({
                        'title': article['title'],
                        'url': article['url']
                    })
                    i += 1
                    if i == MAX_ARTICLES_PER_TOPIC: break

        return recommendations


    async def analyze_discussions(self) -> None:
        channel = self.client.get_channel()
        
        # Fetch message history
        messages: list = []
        async for message in channel.history(limit=HISTORY_LIMIT):
            messages.append((message.created_at, message.author.name, message.content))
        
        if not messages:
            return
        
        # Sort messages by timestamp
        messages.sort(key=lambda x: x[0])


        # Group messages by time interval
        discussions: list = self.client.group_messages_into_discussions(messages)

        # Store discussions
        self.client.store_discussions(discussions)

        # Analyze and recommend for each discussion
        for i, messages in enumerate(discussions):
            message_texts = [msg for _, _, msg in messages]
            topics = self.extract_topics(message_texts)
            recommendations = self.fetch_recommendations(topics)

            # Send recommendations to a specific channel
            channel = self.client.get_channel()
            print(f"Discussion {i} :")
            if recommendations:
                await channel.send(f"Here are some recommendations based on discussion {i} :")
                for rec in recommendations:
                    print(f" - {rec['title']}")
                    if rec['title'] == "[Removed]": # lol
                        continue

                    await channel.send(f"{rec['title']} : {rec['url']}")

    
    async def notify_online_streamers(self):
        newly_online_streamers = twitch_api.check_streamers_online()
        if newly_online_streamers:
            channel = self.client.get_channel()
            for streamer in newly_online_streamers:
                await channel.send(f'{streamer} is now live on Twitch! Check out the stream at https://twitch.tv/{streamer}')


    async def _recommendations(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond("[DEBUG] Manually running discussions analysis and recommendations ...")
        await self.analyze_discussions()
        await ctx.respond("[DEBUG] Analysis done !")


    async def _twitch(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond("[DEBUG] Mannualy checking twitch user connection ...")
        await self.notify_online_streamers()
        await ctx.respond("[DEBUG] Twitch verification done !")