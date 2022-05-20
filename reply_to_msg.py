import discord

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # an attribute we can access from our task
        self.counter = 0

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message):\
        # Ignore own messages
        if message.author == self.user:
            return

        await message.reply("potato")


client = MyClient()
client.run("token")  # TODO Replace token with with client secret