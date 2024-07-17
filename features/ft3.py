"""
# FT-3 Censure et avertissements

## Détection et censure de contenu inapproprié

Le bot doit détecter et censurer les messages contenant des propos haineux, sexuels,
explicites, vulgaires, etc. À défaut de pouvoir supprimer ou modifier le message de l’utilisateur
concerné, le bot doit au moins émettre un message dans le même salon avertissant l’utilisateur.

## Compteur d’avertissements

Le bot doit maintenir un compteur d’avertissements par utilisateur. Le bot doit être capable
d’afficher sur demande un résumé des avertissements pour chaque utilisateur
"""
import discord
from transformers import pipeline

from features.feature import Feature
from bot.client import Client
from bot.command import Command


class Ft3(Feature):
    def __init__(self, client: Client) -> None:
        super().__init__(client)
        self.leaderboard: dict = {}

        client.register_command(Command(
            name="ft3-leaderboard", 
            description="Display leaderboard", 
            callback=self._print_leaderboard, 
            options=None
        ))

        self.classifier = pipeline("text-classification", model="unitary/toxic-bert")


    def _score_up(self, user: str) -> None:
        if not user in self.leaderboard.keys():
            self.leaderboard[user] = 1
            return
        
        self.leaderboard[user] += 1


    async def _print_leaderboard(self, ctx: discord.ApplicationContext) -> None:
        response: str = "===== LEADERBOARD =====\n"
        sorted_scores = sorted(self.leaderboard.items(), key=lambda item: item[1], reverse=True)
        
        for user, score in sorted_scores:
            response += f"- {user} : {score}\n"

        await ctx.respond(response)

    
    async def on_message(self, message: discord.Message) -> None:
        result = self.classifier(message.content)[0]

        if result["label"] == "toxic" and result["score"] > 0.7:
                self._score_up(message.author)

                await message.channel.send(f"{message.author} stop saying curse words you bitch")
                await message.delete()
                return
