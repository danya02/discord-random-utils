from flask import Flask
from flask_discord_interactions import DiscordInteractions
import os

app = Flask(__name__)
discord = DiscordInteractions(app)

app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]

@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"


discord.set_route("/interactions")

if os.getenv("TESTING_MODE") == 1:
    discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])
else:
    discord.update_slash_commands()


