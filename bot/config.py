import os
import dotenv


class Config:
    def __init__(self, ignore_users: list = [], ignore_channels: list = []) -> None:
        self.ignore_channels: list = ignore_users
        self.ignore_users: list = ignore_channels


    def load_token(self) -> str:
        dotenv.load_dotenv()
        return os.getenv("DISCORD_TOKEN")

