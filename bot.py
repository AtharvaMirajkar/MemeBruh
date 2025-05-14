import discord
import requests
import json
import os
import asyncio


TOKEN = os.getenv("DISCORD_TOKEN")

def get_meme():
    response = requests.get('https://meme-api.com/gimme')
    json_data = json.loads(response.text)
    return json_data['url']

class MyClient(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_activity_time = None
        self.activity_timer = None     

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await self.set_status_online()

    async def on_message(self, message):
        if message.author == self.user:
            return
        
        self.last_activity_time = asyncio.get_event_loop().time()

        if message.content.startswith('$meme'):
            await message.channel.send(get_meme())
        
        if self.user.mentioned_in(message):
            await self.set_status_online()
        
    async def set_status_online(self):
        """Set the bot status to online."""
        if self.activity_timer is not None:
            self.activity_timer.cancel()
        await self.change_presence(status=discord.Status.online)
        self.activity_timer = asyncio.create_task(self.inactivity_timer())

    async def inactivity_timer(self):
        """Wait for 30 minutes of inactivity and then set the bot offline."""
        await asyncio.sleep(1800) 
        if self.last_activity_time and (asyncio.get_event_loop().time() - self.last_activity_time >= 1800):
            await self.change_presence(status=discord.Status.offline)
            print("Bot is now offline due to inactivity.")

    async def on_disconnect(self):
        """Clean up the timer when the bot disconnects."""
        if self.activity_timer:
            self.activity_timer.cancel()
        print("Bot has disconnected.")        

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)


