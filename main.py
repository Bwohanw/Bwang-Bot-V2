# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord
import requests
import random
from discord.ext import commands
import time

# Import the os module.
import os
# Import load_dotenv function from dotenv module.
from dotenv import load_dotenv
# Loads the .env file that resides on the same level as the script.
load_dotenv()
# Grab the API token from the .env file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="$")

mckey = {'a':0, 'b':1, 'c':2, 'd':3}

@bot.command()
async def ping(ctx):
	await ctx.channel.send("pong")

@bot.command(brief = "fuck you")
async def hello(ctx, *name):
	s = ""
	for x in name:
		s += x + " "
	s = s[:len(s) - 1]
	await ctx.send("fuck you " + s)

@bot.command(help = "enter a number for a surprise.")
async def omdeh(ctx, arg):
	arg = int(arg)
	s = ":skull:" * arg
	await ctx.send(s)


def get_kanji_info():
	kanji_index = random.randint(0, 1234)
	url = "https://kanjialive-api.p.rapidapi.com/api/public/kanji/all"
	headers = {
	"X-RapidAPI-Key": os.getenv("KANJI_KEY"),
	"X-RapidAPI-Host": "kanjialive-api.p.rapidapi.com"
	}
	response = requests.request("GET", url, headers=headers)
	example_list = response.json()[kanji_index]["examples"]
	index = random.randint(0, len(example_list)-1)
	return example_list[index]

def get_reading(info):
	reading = info["japanese"]
	furigana = reading.split('（')
	return furigana[1][:len(furigana[1])-1]

def get_kanji(info):
	reading = info["japanese"]
	furigana = reading.split('（')
	return furigana[0]

def shuffle(list):
	for i in range(len(list)):
		k = random.randint(0, len(list) - i - 1)
		index = i + k
		swap(list, i, index)

def swap(list, index1, index2):
	temp = list[index1]
	list[index1] = list[index2]
	list[index2] = temp

def check(list):
	def inner_check(message):
		return message.author.name not in list
	return inner_check

@bot.command()
async def kanjiquiz(ctx):
	points = {}
	for x in range(2):
		guessed = []
		correct = []
		kanji_info = get_kanji_info()
		meaning = kanji_info["meaning"]["english"]
		kanji = get_kanji(kanji_info)
		reading = get_reading(kanji_info)
		choicelist = [reading]
		while len(choicelist) < 4:
			k_info = get_kanji_info()
			read = get_reading(k_info)
			if read in choicelist:
				continue
			choicelist.append(read)
		shuffle(choicelist)
		await ctx.send('```What is the reading of {}? \nA: {} \nB: {} \nC: {} \nD: {}```'.format(kanji, choicelist[0],choicelist[1],choicelist[2],choicelist[3]))
		now = time.time()
		future = now + 10
		while time.time() < future:
			try:
				guess = await bot.wait_for('message', check=check(guessed), timeout=10)
			except:
				break
			if guess.content.lower() in mckey.keys():
				guessed.append(guess.author.name)
				if choicelist[mckey[guess.content.lower()]] == reading:
					correct.append(guess.author.name)
					await ctx.send("Correct! Good job " + guess.author.name + "!!")
					points[guess.author.name] = points[guess.author.name] + 1 if guess.author.name in points.keys() else 1
				else:
					await ctx.send("Sorry " + guess.author.name + ", that is not correct")
					if (guess.author.name not in points.keys()):
						points[guess.author.name] = 0
			else:
				await ctx.send("Fuck are you doing stupid bitch guess a real guess next time")
				if guess.author.name not in points.keys():
					points[guess.author.name] = 0
		await ctx.send("The round is over. The correct answer was " + reading + "which means " + meaning + ".")
		await ctx.send(points)
	await ctx.send(points)

# GETS THE CLIENT OBJECT FROM DISCORD.PY. CLIENT IS SYNONYMOUS WITH BOT.

# EVENT LISTENER FOR WHEN THE BOT HAS SWITCHED FROM OFFLINE TO ONLINE.
@bot.event
async def on_ready():
	# CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO.
	guild_count = 0

	# LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH.
	for guild in bot.guilds:
		# PRINT THE SERVER'S ID AND NAME.
		print(f"- {guild.id} (name: {guild.name})")

		# INCREMENTS THE GUILD COUNTER.
		guild_count = guild_count + 1

	# PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN.
	print("SampleDiscordBot is in " + str(guild_count) + " guilds.")

# EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL.
@bot.event
async def on_message(message):
	# CHECKS IF THE MESSAGE THAT WAS SENT IS EQUAL TO "HELLO".
	if message.content == "ま":
		# SENDS BACK A MESSAGE TO THE CHANNEL.
		await message.channel.send("hey dirtbag")
	await bot.process_commands(message)

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run(DISCORD_TOKEN)
