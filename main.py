#TODO - OUTLINE
# we need to provide ids in here, have them hard coded in a dict like 'ffa': '124124' etc.
# need to support multiple bots soon, turn creds.file into json for each thing, like 'ffa'?
#server to test: Black Ops 2 FFA (Plutonium) 203.123.120.184:4976 

import discord
from discord.enums import ActivityType, Status
from discord.ext import commands, tasks
from discord.ext.tasks import loop
from asyncio import sleep

import requests

import os

try:
    with open(os.path.dirname(os.path.realpath(__file__)) + r"\creds.file") as creds:
        BOT_TOKEN = creds.read()
except OSError:
    print("Add a creds.file with your Discord Bot's token")
    os._exit()

class IW4MDiscordClient(commands.Bot):
    lastMapName = ""
    serverInfo = {  'map': '', #the maps file name, eg. nuketown_2020, for thumbnails
                    'mapname': '', #the Alias, eg. Nuketown 2025
                    'players': '',
                    'maxplayers': ''  }

    async def on_ready(self):
        print('Logged in as {0}'.format(self.user))
        #self.getInfo()
        #await self.updateInfo(self.serverInfo['mapname'], self.serverInfo['players'], self.serverInfo['maxplayers'])

    async def updateInfo(self, mapName, playerCount, maxPlayerCount):
        infoString = "{} {}/{}".format(mapName, playerCount, maxPlayerCount)
        print('Updating info: \'{}\''.format(infoString))

        #set the presence
        #if no players, change status to idle
        await self.change_presence(activity=discord.Activity(name=infoString, type=ActivityType.playing), status=(Status.idle if playerCount == 0 else Status.online))

        #check if we have to update profile picture
        if (mapName != self.lastMapName):
            print('Map changed, changing profile picture to current map')
            self.lastMapName = self.serverInfo['map']

            try:
                mapImage = open(os.path.dirname(os.path.realpath(__file__)) + r"\assets\map_thumb\{}.png".format(mapName), 'rb')
            except OSError as e:
                print("Failed to open map thumbnail \'{}.png\', using default".format(mapName))
                #lets hope we dont fail this
                mapImage = open(os.path.dirname(os.path.realpath(__file__)) + r"\assets\map_thumb\default.png", 'rb')

            await client.user.edit(avatar=mapImage.read())

    async def getInfo(self):
        serverStatus = requests.get('http://localhost:1624/api/status')
        server = next((server for server in serverStatus.json() if server['id'] == 1270014976), None)
        if (server is not None):
            self.serverInfo['map']          = server['map']['name']
            self.serverInfo['mapname']      = server['map']['alias']
            self.serverInfo['players']      = server['currentPlayers']
            self.serverInfo['maxplayers']   = server['maxPlayers']
            return True
        return False

client = IW4MDiscordClient(command_prefix="$")

@loop(seconds=30)
async def infoTimer(self):
    print("Updating bot info")
    await self.getinfo()
    await self.updateInfo(self.serverInfo['mapname'], self.serverInfo['players'], self.serverInfo['maxplayers'])
infoTimer.before_loop(client.wait_until_ready())
infoTimer.start()

client.run(BOT_TOKEN)