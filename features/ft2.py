"""
# FT-2 Proposition d’activités en groupe

Le bot doit organiser et planifier des activités qu’il proposera à intervalle régulier dans le serveur
Discord.

Le bot doit prendre en compte les agendas des membres pour identifier les disponibilités. Si
l’activité est en extérieur, il doit aussi prendre en compte la météo
"""
import csv
import random
import discord
from datetime import datetime
from typing import Dict, List

from features.feature import Feature
from bot.command import Command
from bot.client import Client

from api_clients import calendar_api, weather_api

LOCATION: str = "Aix-en-Provence"
MIN_USER: int = 2
CALENDAR_DIR: str = 'data/calendars'
ACTIVITIES_FILE: str = 'data/activities_dset.csv'

class Ft2(Feature):
    def __init__(self, client: Client) -> None:
        super().__init__(client)
        client.register_command(Command(
            name="ft2-propose-activities", 
            description="Propose activities depending of users availabilities", 
            callback=self._activities, 
            options=None
        ))

        self.activities_list = self.read_activities_from_csv(ACTIVITIES_FILE)


    def read_activities_from_csv(self, file_path: str) -> List[str]:
        activities = []
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                activities.append(row['activity'])
        return activities


    def schedule_activities(self, availability: Dict[datetime, List[str]]) -> List[Dict[str, str]]:
        proposed_dates = set() # double check
        activities = []

        for date, members in availability.items():
            if date in proposed_dates or len(members) < MIN_USER:
                continue

            weather = weather_api.fetch_weather(LOCATION, date)
            if not weather['forecast']['forecastday']:
                continue

            if weather['forecast']['forecastday'][0]['day']['condition']['text'] == 'Sunny':
                proposed_dates.add(date)
                selected_events = random.sample(self.activities_list, 3)
                activity = {
                    "date": date,
                    "time_of_day": "morning" if date.hour < 11 else "afternoon",
                    "members": members,
                    "events": selected_events
                }
                activities.append(activity)
        return activities


    async def check_and_propose_activities(self) -> None:
        availability: Dict[datetime, List[str]] = calendar_api.parse_ics_files(CALENDAR_DIR)
        activities: List[Dict[str, str]] = self.schedule_activities(availability)
        activities.sort(key=lambda x: (x["date"].date(), x["time_of_day"]))

        for activity in activities:
            date = activity["date"]
            time_of_day = activity["time_of_day"]
            members = activity["members"]
            events = activity["events"]
        
            activity_message = f"### Proposed activity on `{date.strftime('%Y-%m-%d')} {time_of_day}`\n"
            
            activity_message += "### Available members:\n"
            for m in members:
                activity_message += f"- {m}\n"

            activity_message += "### Activities:\n"
            for e in events:
                activity_message += f"- {e}\n"
            
            await self.client.get_channel().send(activity_message)
    
    
    async def _activities(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond("[DEBUG] Looking for fun activities ...")
        await self.check_and_propose_activities()
        await ctx.respond("[DEBUG] Activities found !")
