# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
from http import client
import discord
import requests
import random
from discord.ext import commands
import time
import objecthelper

# Import the os module.
import os
# Import load_dotenv function from dotenv module.
from dotenv import load_dotenv
# Loads the .env file that resides on the same level as the script.
load_dotenv()
# Grab the API token from the .env file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="$")


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

@bot.command(help = "begin a kanji quiz, default 2 questions")
async def kanjiquiz(ctx, arg=2):
	points = {}
	ungotten = []
	mckey = {'a':0, 'b':1, 'c':2, 'd':3}
	try:
		arg = int(arg)
	except:
		await ctx.send("Enter a valid argument stupidhead")
	for x in range(arg):
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
					#await ctx.send("Correct! Good job " + guess.author.name + "!!")
					points[guess.author.name] = points[guess.author.name] + 1 if guess.author.name in points.keys() else 1
				else:
					#await ctx.send("Sorry " + guess.author.name + ", that is not correct")
					if (guess.author.name not in points.keys()):
						points[guess.author.name] = 0
			else:
				await ctx.send("Fuck are you doing stupid bitch " + guess.author.name + " guess a real guess next time")
				if guess.author.name not in points.keys():
					points[guess.author.name] = 0
		if (len(correct) == 0):
			ungotten.append(reading + ", which means " + meaning + ".")
		await ctx.send("The round is over. The correct answer was " + reading + "which means " + meaning + ".")
		await ctx.send("The current points are:\n" + objecthelper.points_to_string(points))
	await ctx.send("Final results:\n" + objecthelper.points_to_string(points))
	if len(ungotten) == 0:
		await ctx.send("All the words were gotten. Congratulations!")
	else:
		await ctx.send("The ungotten words were:\n" + objecthelper.list_to_string(ungotten))

#yes no poll for one topic

yesnopoll = None
ynpollreacts = {}
ynpollname = ""
@bot.command(help = "Make a yes/no question poll")
async def makeynpoll(ctx, *, name):
	global yesnopoll
	global ynpollreacts
	global ynpollname
	ynpollname = name
	ynpollreacts["\N{THUMBS UP SIGN}"] = 1
	ynpollreacts["\N{THUMBS DOWN SIGN}"] = 1
	ynpollstring = 'Poll: {} \nYes votes: {} \nNo votes: {}'.format(name, ynpollreacts["\N{THUMBS UP SIGN}"]-1, ynpollreacts["\N{THUMBS DOWN SIGN}"]-1)
	yesnopoll = await ctx.send(ynpollstring)
	await yesnopoll.add_reaction("\N{THUMBS UP SIGN}")
	await yesnopoll.add_reaction("\N{THUMBS DOWN SIGN}")

alphabetcaps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
pollmessage = None
availablereactions = ["\N{REGIONAL INDICATOR SYMBOL LETTER A}","\N{REGIONAL INDICATOR SYMBOL LETTER B}","\N{REGIONAL INDICATOR SYMBOL LETTER C}","\N{REGIONAL INDICATOR SYMBOL LETTER D}","\N{REGIONAL INDICATOR SYMBOL LETTER E}","\N{REGIONAL INDICATOR SYMBOL LETTER F}","\N{REGIONAL INDICATOR SYMBOL LETTER G}","\N{REGIONAL INDICATOR SYMBOL LETTER H}","\N{REGIONAL INDICATOR SYMBOL LETTER I}","\N{REGIONAL INDICATOR SYMBOL LETTER J}","\N{REGIONAL INDICATOR SYMBOL LETTER K}","\N{REGIONAL INDICATOR SYMBOL LETTER L}","\N{REGIONAL INDICATOR SYMBOL LETTER M}","\N{REGIONAL INDICATOR SYMBOL LETTER N}","\N{REGIONAL INDICATOR SYMBOL LETTER O}","\N{REGIONAL INDICATOR SYMBOL LETTER P}","\N{REGIONAL INDICATOR SYMBOL LETTER Q}","\N{REGIONAL INDICATOR SYMBOL LETTER R}","\N{REGIONAL INDICATOR SYMBOL LETTER S}","\N{REGIONAL INDICATOR SYMBOL LETTER T}"]
pollchoices = []
pollreacts = {}
# letterindexing = {}
# for x in range(26):
# 	letterindexing[x] = availablereactions[x]

def create_string(list, dict):
	s = ""
	for x in range(len(list)):
		s += '{}. {}: {} vote(s)\n'.format(alphabetcaps[x], list[x], dict[availablereactions[x]]-1)
	return s.strip()

@bot.command(help = "Separate the poll choices with commas, up to twenty")
async def makepoll(ctx, *, name):
	global pollchoices
	pollchoices = []
	global pollmessage
	global pollreacts
	pollreacts = {}
	name = name.strip()
	pollchoices = name.split(",")
	pollchoices = [x.strip() for x in pollchoices if len(x.strip()) != 0]
	for x in range(len(pollchoices)):
		pollreacts[availablereactions[x]] = 1
	pollmessage = await ctx.send(create_string(pollchoices, pollreacts))
	for x in pollreacts.keys():
		await pollmessage.add_reaction(x)

@bot.command()
async def addpollchoice(ctx,*,name):
	if pollmessage is None:
		await ctx.send("There's no poll active right now")
		return
	if len(pollchoices) >= 20:
		await ctx.send("Sorry, you can't add any more options to this poll")
	name = name.strip()
	pollchoices.append(name)
	pollreacts[availablereactions[len(pollchoices)-1]] = 1
	await pollmessage.add_reaction(availablereactions[len(pollchoices) - 1])
	await pollmessage.edit(content = create_string(pollchoices, pollreacts))

@bot.event
async def on_reaction_add(reaction, user):
	if user.bot:
		return
	if reaction.message == yesnopoll:
		if reaction.emoji in ynpollreacts.keys():
			ynpollreacts[reaction.emoji] += 1
			ynpollstring = 'Poll: {} \nYes votes: {} \nNo votes: {}'.format(ynpollname, ynpollreacts["\N{THUMBS UP SIGN}"]-1, ynpollreacts["\N{THUMBS DOWN SIGN}"]-1)
			await yesnopoll.edit(content= ynpollstring)
		return
	if reaction.message == pollmessage:
		if reaction.emoji in pollreacts.keys():
			pollreacts[reaction.emoji] += 1
			await pollmessage.edit(content = create_string(pollchoices, pollreacts))
		return

@bot.event
async def on_raw_reaction_remove(payload):
	if yesnopoll is not None:
		if payload.message_id == yesnopoll.id:
			if payload.emoji.name in ynpollreacts.keys():
				ynpollreacts[payload.emoji.name] -= 1
				ynpollstring = 'Poll: {} \nYes votes: {} \nNo votes: {}'.format(ynpollname, ynpollreacts["\N{THUMBS UP SIGN}"]-1, ynpollreacts["\N{THUMBS DOWN SIGN}"]-1)
				await yesnopoll.edit(content = ynpollstring)
				return
	if pollmessage is not None:
		if payload.message_id == pollmessage.id:
			if payload.emoji.name in pollreacts.keys():
				pollreacts[payload.emoji.name] -= 1
				await pollmessage.edit(content = create_string(pollchoices, pollreacts))
				return


reminders = {} #dictionary of (member_id, guild_id): [list of reminders]
@bot.command(help = "input a prompt to remind you of something to say 'next time in call'")
async def remindcall(ctx, *args):
	global reminders
	if (len(args) == 0):
		return
	pair = (ctx.author.id, ctx.guild.id)
	if (pair not in reminders):
		reminders[pair] = []
	reminders[pair].append(' '.join(args))
	#print(reminders)
	await ctx.send("Reminder set. You'll be reminded next time you join a voice channel")

@bot.event
async def on_voice_state_update(member, before, after):
	if not before.channel and after.channel:
		pair = (member.id, member.guild.id)
		if pair in reminders:
			#print(member.guild.id)
			channels = member.guild.text_channels
			#print(channels)
			if (len(channels) == 0):
				return
			channel = channels[0]
			toret = f"{member.mention} reminding you of the following:\n{objecthelper.list_to_string(reminders[pair])}"
			reminders.pop(pair)
			await channel.send(toret)

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
	if message.content == "hello":
		# SENDS BACK A MESSAGE TO THE CHANNEL.
		await message.channel.send("hey dirtbag")
	await bot.process_commands(message)

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run(DISCORD_TOKEN)
