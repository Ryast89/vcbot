from typing import Literal
import os
import random
from dotenv import load_dotenv, find_dotenv

import discord
from discord import app_commands
from discord.ext import tasks

import database
from custom_types import Vote, Post, Phase

import aerosync_commands

async def updateStatus(status):
  game = discord.Game(status)
  await client.change_presence(status=discord.Status.online, activity=game)
  return

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

test_guild = discord.Object(id="951678432494911528")

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)
tree.add_command(aerosync_commands.god())
tree.add_command(aerosync_commands.game())
tree.add_command(aerosync_commands.update())
tree.add_command(aerosync_commands.game_phase())
tree.add_command(aerosync_commands.rank_activity())
tree.add_command(aerosync_commands.alias())
tree.add_command(aerosync_commands.special())
tree.add_command(aerosync_commands.votecount())
tree.add_command(aerosync_commands.queue())


@client.event
async def tree_eh(interaction, error):
  if isinstance(error, discord.app_commands.CheckFailure):
    error = "Error. To use this command, you must have role `God`, `Puppeteer (Host)`, or `Mafia`."
  try:
    await interaction.response.send_message(
        embed=discord.Embed(color=discord.Color.red(), description=error))
  except:
    await interaction.channel.send(
        embed=discord.Embed(color=discord.Color.red(), description=error))

tree.on_error = tree_eh


@tasks.loop(minutes = 10)
async def myLoop():
  status_options = ["Hypixel Mafia", "Mind games", "Threadcamping", "on MafiaUniverse", "Town of Salem", "Among Us",
                        "Forum Ghosting", "Bandwagoning", "as the Deepwolf", "in LYLO", "Desperado", "Role Cop", "Bus Driver"
                        "Jailkeeper", "Godfather", "Neutral Killing", "Executioner", "Pwincess", "Cult Leader", 
                        "Survivor", "Mafia Goon", "Vigilante", "Jester", "Town Leader", "Celeste"
                        ]
  await updateStatus(random.choice(status_options))


@client.event
async def on_ready():
    #start task loop
    myLoop.start()
    await updateStatus("Threadcamping")


#message event - check if a message is equal to #sync
@client.event
async def on_message(message):
    if message.content == "$sync":
        #global sync discord command tree
        await tree.sync()
        await message.channel.send("Global synced command tree.")

    if message.content == "$sync local":
        #local sync discord command tree
        tree.clear_commands(guild=test_guild)
        tree.copy_global_to(guild=test_guild)
        await tree.sync(guild=test_guild)
        await message.channel.send("Local synced command tree. Note that this doesn't globally sync the command tree.")

load_dotenv()
#get env variable called AEROSYNC_DISCORD_TOKEN
token = os.getenv("AEROSYNC_DISCORD_TOKEN")

client.run(token)

