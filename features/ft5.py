"""
# FT-5 Rapports et tendances sur les discussions

## Analyse du sentiment global des membres

Le bot doit pouvoir générer un rapport quotidien et hebdomadaire avec des statistiques globales
des membres du serveur sur une période donnée. Le rapport doit inclure des informations de ce
type :
    · Les moments forts (discussions ou messages avec une forte charge émotionnelle, avec des prises de positions, etc.) ;
    · Le sentiment global (triste, neutre, joyeux) ;
    · La liste des discussions trouvées (membres participants, durée, sujet) ;
    · Le classement des membres les plus vulgaires/haineux/explicites (en référence à la fonctionnalité de censure).

Le rapport doit être synthétique et doit utiliser des représentations visuelles (schémas, graphiques, etc.).

Le rapport doit être également rendu accessible sous forme de fichier Excel.
"""
import discord
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

from features.feature import Feature
from bot.command import Command
from bot.client import Client

REPORT_DIR = 'data/reports'


class Ft5(Feature):
    def __init__(self, client: Client) -> None:
        super().__init__(client)

        client.register_command(Command(
            name="ft5-generate-report", 
            description="Generate report", 
            callback=self._report, 
            options=[
                discord.Option(name="days", description="Generate report based on N days", type=int, required=True)
            ]
        ))

        self.sid = SentimentIntensityAnalyzer()


    async def generate_report(self, days: int):
        channel = self.client.get_channel()
        await channel.send(f'Generating report for the last {days} days...')
        messages = await self.collect_messages(days)
        df = pd.DataFrame(messages)
        
        if df.empty:
            await channel.send("No messages found for the given period.")
            return

        # Remove timezone information (Excel does not support datetimes with timezones.)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)

        # Perform sentiment analysis
        df['sentiment'] = df['content'].apply(self.analyze_sentiment)
        df['sentiment_score'] = df['sentiment'].apply(lambda x: x['compound'])
        
        # Ensure sentiment_score is numeric
        df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce')
        
        # Drop rows where sentiment_score could not be converted to numeric
        df.dropna(subset=['sentiment_score'], inplace=True)
        df['sentiment_score'] = df['sentiment_score'].astype(float) # RAAAAAAAAAAAAAAAAAAAAAAAAA

        # Calculate global sentiment
        global_sentiment = df['sentiment_score'].mean()
        sentiment_label = 'neutral'
        if global_sentiment > 0.05:
            sentiment_label = 'joyful'
        elif global_sentiment < -0.05:
            sentiment_label = 'sad'

        # Identify key moments
        key_moments = df[df['sentiment_score'].abs() > 0.5]

        # Generate statistics
        member_activity = df['author'].value_counts()
        top_negative_members = df[df['sentiment_score'] < -0.5]['author'].value_counts()
        top_positive_members = df[df['sentiment_score'] > 0.5]['author'].value_counts()

        # Create visual reports
        # 1. Sentiment Score Distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(df['sentiment_score'], kde=True)
        plt.title('Sentiment Score Distribution')
        sentiment_distribution_image_filename = f'{REPORT_DIR}/sentiment_distribution_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
        plt.savefig(sentiment_distribution_image_filename)
        plt.close()
        
        # 2. Member Activity
        plt.figure(figsize=(10, 6))
        sns.barplot(x=member_activity.values, y=member_activity.index)
        plt.title('Member Activity')
        plt.xlabel('Number of Messages')
        member_activity_image_filename = f'{REPORT_DIR}/member_activity_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
        plt.savefig(member_activity_image_filename)
        plt.close()

        # 3. Top Negative Members
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_negative_members.values, y=top_negative_members.index)
        plt.title('Top Negative Members')
        plt.xlabel('Number of Negative Messages')
        top_negative_members_image_filename = f'{REPORT_DIR}/top_negative_members_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
        plt.savefig(top_negative_members_image_filename)
        plt.close()

        # 4. Top Positive Members
        plt.figure(figsize=(10, 6))
        sns.barplot(x=top_positive_members.values, y=top_positive_members.index)
        plt.title('Top Positive Members')
        plt.xlabel('Number of Positive Messages')
        top_positive_members_image_filename = f'{REPORT_DIR}/top_positive_members_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
        plt.savefig(top_positive_members_image_filename)
        plt.close()

        # 5. Overall Sentiment Over Time
        try:
            plt.figure(figsize=(10, 6))
            df.set_index('timestamp', inplace=True)
            df_daily = df[['sentiment_score']].resample('D').mean()

            # Check for empty resampled data
            if df_daily.empty:
                await channel.send("No data available after resampling.")
                return

            df_daily['sentiment_score'].plot()
            plt.title('Overall Sentiment Over Time')
            plt.ylabel('Average Sentiment Score')
            overall_sentiment_image_filename = f'{REPORT_DIR}/overall_sentiment_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
            plt.savefig(overall_sentiment_image_filename)
            plt.close()
        except Exception as e:
            print(f"[ERROR] `Overall Sentiment Over Time` is broken AGAIN : {e}")

        # 6. Key Moments Visualization
        if not key_moments.empty:
            plt.figure(figsize=(10, 6))
            key_moments_counts = key_moments['channel'].value_counts()
            sns.barplot(x=key_moments_counts.values, y=key_moments_counts.index)
            plt.title('Key Moments by Channel')
            plt.xlabel('Number of Key Moments')
            key_moments_image_filename = f'{REPORT_DIR}/key_moments_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'
            plt.savefig(key_moments_image_filename)
            plt.close()
            
        # Generate Excel report
        report_filename = f'{REPORT_DIR}/report_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xlsx'
        with pd.ExcelWriter(report_filename) as writer:
            df.to_excel(writer, sheet_name='Messages')
            member_activity.to_excel(writer, sheet_name='Member Activity')
            top_negative_members.to_excel(writer, sheet_name='Top Negative Members')
            top_positive_members.to_excel(writer, sheet_name='Top Positive Members')
            
            # Add key moments
            if not key_moments.empty:
                key_moments.to_excel(writer, sheet_name='Key Moments')

            # Add summary
            summary = pd.DataFrame({
                'Global Sentiment': [sentiment_label],
                'Average Sentiment Score': [global_sentiment],
                'Number of Messages': [len(df)]
            })
            summary.to_excel(writer, sheet_name='Summary')


        await channel.send(f'Report generated :')
        await channel.send(file=discord.File(report_filename))
        await channel.send(file=discord.File(sentiment_distribution_image_filename))
        await channel.send(file=discord.File(member_activity_image_filename))
        await channel.send(file=discord.File(top_negative_members_image_filename))
        await channel.send(file=discord.File(top_positive_members_image_filename))
        try:
            await channel.send(file=discord.File(overall_sentiment_image_filename))
        except:
            pass # fuck you
        await channel.send(file=discord.File(key_moments_image_filename))


    async def collect_messages(self, days: int):
        messages = []
        time_limit = datetime.now() - timedelta(days=days)
        
        for guild in self.client.bot.guilds:
            for channel in guild.text_channels:
                try:
                    async for message in channel.history(limit=None, after=time_limit):
                        if message.author == self.client.bot.user:
                            continue
                        messages.append({
                            'content': message.content,
                            'author': message.author.name,
                            'timestamp': message.created_at,
                            'channel': message.channel.name,
                        })
                except discord.Forbidden:
                    print(f"[ERROR] Missing access to channel `{channel}`")
                except Exception as e:
                    print(f"[ERROR] Fail to retrieve message in channel `{channel}` : {e}")
        return messages


    def analyze_sentiment(self, text) -> float:
        scores = self.sid.polarity_scores(text)
        return scores


    async def _report(self, ctx: discord.ApplicationContext, days: int) -> None:
        await self.generate_report(int(days))
