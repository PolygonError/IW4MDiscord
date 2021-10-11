#TODO - OUTLINE
#	.register as a bot
#	get server info every ## (30 secs?) period
#		including map, player count
#       player count:
#           command= !list (commands need ! in front)
#test = requests.post('http://localhost:1624/api/server/1270014976/execute', json={'serverId': 1270014976, 'Command': '!list'}, headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
#need to use /api/status for map and player count :)
# use len() on ['output']
# we need to provide ids in here, have them hard coded in a dict like 'ffa': '124124' etc.
#server to test: Black Ops 2 FFA (Plutonium) 203.123.120.184:4976 

import discord
from discord.enums import ActivityType, Status
from discord.ext import commands

import requests

import os

with open(os.path.dirname(os.path.realpath(__file__)) + r"\creds.file") as creds:
    BOT_TOKEN = creds.read()

class IW4MDiscordClient(commands.Bot):
    lastMapName = ""
    serverInfo = {  'map': '',
                    'players': '',
                    'maxplayers': ''  }

    async def on_ready(self):
        print('Logged in as {0}'.format(self.user))
        self.getInfo()
        self.updateInfo(self.serverInfo['map'], self.serverInfo['players'], self.serverInfo['maxplayers'])

    async def updateInfo(self, mapName, playerCount, maxPlayerCount):
        infoString = "{} {}/{}".format(mapName, playerCount, maxPlayerCount)
        print('Updating info: \'{}\''.format(infoString))

        #set the presence
        #if no players, change status to idle
        self.change_presence(discord.Activity(name=infoString, type=ActivityType.playing, status=(Status.idle if playerCount == 0 else Status.online)))

        #check if we have to update profile picture
        if (mapName != self.lastMapName):
            print('Map changed, changing profile picture to current map')
            self.lastMapName = self.serverInfo['map']

            try:
                mapImage = open(os.path.dirname(os.path.realpath(__file__)) + r"\assets\map_thumb\{}.png".format(mapName))
            except OSError as e:
                print("Failed to open map thumbnail \'{}.png\', using default".format(mapName))
                print(e)
                #lets hope we dont fail this
                mapImage = open(os.path.dirname(os.path.realpath(__file__)) + r"\assets\map_thumb\default.png")

            await client.user.edit(avatar=mapImage.read())

    def getInfo(self):
        serverStatus = requests.get('http://localhost:1624/api/status')
        server = next((server for server in serverStatus.json() if server['id'] == 1270014976), None)
        if (server is not None):
            self.serverInfo['map']          = server['map']['name']
            self.serverInfo['players']      = server['currentPlayers']
            self.serverInfo['maxplayers']   = server['maxPlayers']
            return True
        return False

client = IW4MDiscordClient(command_prefix="$")

#@client.command()
#async def test(ctx):
#        with open('E:/Projects/Python/IW4MDiscord/assets/map_thumb/nuketown_2020.jpg', 'rb') as image:
#            await client.user.edit(avatar=image.read())

client.run(BOT_TOKEN)