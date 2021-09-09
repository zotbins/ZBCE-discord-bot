"""
A python discord bot, for the ZBCE discord server.

Documentation for Github API requests referenced here: https://docs.github.com/en/rest/reference/issues

Documentation for Discord.py referenced here: https://discordpy.readthedocs.io/en/latest/index.html

Ideas:
- Integrate with a project board (task list). React when done/finished/you_want_the_task
"""

# ALl imports
import requests
from datetime import datetime
import os
from pathlib import Path
from discord.ext import tasks
import discord
from dotenv import load_dotenv

DIRNAME = os.path.dirname(__file__)


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # hard-coded repos of interests (ROI)
        # These are repos that we are interested in for following
        # when a new issue is posted.
        self.ROIs = ["waste_watcher", "zbceblog", "zbce_api"]

        # start the task to run in the background
        self.check_issues.start()

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("------")

    @tasks.loop(seconds=3600 * 24)  # task runs every 60 seconds
    async def check_issues(self):
        channel = self.get_channel(773326709797027850)  # channel ID goes here
        for repo in self.ROIs:
            s = self.git_open_issues(repo)
            if s:
                await channel.send(s)
                await channel.send(
                    "⠀"
                )  # There is a magical special blank character here. Please be aware!

    @check_issues.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

    def git_open_issues(self, repo):
        header = {"Accept": "application/vnd.github.v3+json"}
        payload = {"state": "open", "since": datetime.now().strftime("%Y-%m-%dT")}
        # payload = {"state":"open","since":"2021-02-21T"} # uncomment for testing

        # make the get request
        r = requests.get(
            "https://api.github.com/repos/zotbins/{}/issues".format(repo),
            params=payload,
            headers=header,
        )

        # keep track of all the issue information to return in a list
        mark_list = []
        for i in range(len(r.json())):
            with open(os.path.join(DIRNAME, "templates/issue.txt")) as f:
                mark_str = f.read().format(r.json()[i]["title"], r.json()[i]["url"])
                mark_list.append(mark_str)

        if len(mark_list) > 0:
            heading = "__📚 **{}** Github Issues__\n".format(repo)
            return heading + "".join(mark_list)
        else:
            return None

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.startswith("/help"):
            with open(os.path.join(DIRNAME, "templates/help.txt")) as f:
                await message.channel.send(f.read())

        elif message.content.startswith("/hello"):
            await message.channel.send("👋 Hello!")

        elif message.content.startswith("/new_issues"):
            for repo in self.ROIs:
                s = self.git_open_issues(repo)
                if s:
                    await message.channel.send(s)
                    await message.channel.send(
                        "⠀"
                    )  # There is a magical special blank character here. Please be aware!
                else:
                    await message.channel.send(
                        "No new issues for **{}** today 🌱".format(repo)
                    )


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")

    client = MyClient()
    client.run(TOKEN)
