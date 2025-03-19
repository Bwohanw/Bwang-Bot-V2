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


@bot.command(help="pong, motherfucker")
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
async def kanjiquiz(ctx, rounds=2):
	points = {}
	ungotten = []
	mckey = {'a':0, 'b':1, 'c':2, 'd':3}
	try:
		rounds = int(rounds)
	except:
		await ctx.send("Enter a valid argument stupidhead")
	for x in range(rounds):
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


alphabetcaps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
availablereactions = ["\N{REGIONAL INDICATOR SYMBOL LETTER A}","\N{REGIONAL INDICATOR SYMBOL LETTER B}","\N{REGIONAL INDICATOR SYMBOL LETTER C}","\N{REGIONAL INDICATOR SYMBOL LETTER D}","\N{REGIONAL INDICATOR SYMBOL LETTER E}","\N{REGIONAL INDICATOR SYMBOL LETTER F}","\N{REGIONAL INDICATOR SYMBOL LETTER G}","\N{REGIONAL INDICATOR SYMBOL LETTER H}","\N{REGIONAL INDICATOR SYMBOL LETTER I}","\N{REGIONAL INDICATOR SYMBOL LETTER J}","\N{REGIONAL INDICATOR SYMBOL LETTER K}","\N{REGIONAL INDICATOR SYMBOL LETTER L}","\N{REGIONAL INDICATOR SYMBOL LETTER M}","\N{REGIONAL INDICATOR SYMBOL LETTER N}","\N{REGIONAL INDICATOR SYMBOL LETTER O}","\N{REGIONAL INDICATOR SYMBOL LETTER P}","\N{REGIONAL INDICATOR SYMBOL LETTER Q}","\N{REGIONAL INDICATOR SYMBOL LETTER R}","\N{REGIONAL INDICATOR SYMBOL LETTER S}","\N{REGIONAL INDICATOR SYMBOL LETTER T}"]
ynreactions = ["\N{THUMBS UP SIGN}", "\N{THUMBS DOWN SIGN}"]
polls = {} #map of poll id to message
polltoid = {}#map of message to id
ynpolls = {} #map of ynpoll ids to the poll name
options = {} #map of poll id to list of selection options
reactions = {} #map of poll id to list of reaction counts

def create_string(id):
	s = ""
	for x in range(len(options[id])):
		if (id in ynpolls):
			s += '{}: {} vote(s)\n'.format(options[id][x], reactions[id][x])
		else:
			s += '{}. {}: {} vote(s)\n'.format(alphabetcaps[x], options[id][x], reactions[id][x])
	return s + "This poll id is {}. Use this number to interact with the poll".format(id)

@bot.command(help="Make a yes/no question poll")
async def makeynpoll(ctx, *, name):
	global polls
	global ynpolls
	global reactions
	global options
	global polltoid
	id = random.randint(0,100000)
	while id in polls:
		id = random.randint(0,100000)
	ynpolls[id] = name
	options[id] = ["Yes", "No"]
	reactions[id] = [0] * 2
	pollstring = 'Poll: {}\n'.format(name) + create_string(id)
	poll = await ctx.send(pollstring)
	polls[id] = poll
	polltoid[poll] = id
	for reaction in ynreactions:
		await poll.add_reaction(reaction)

@bot.command(help = "Makes a poll with up to 20 options.\nFormat: $makepoll <option 1>, ..., <option n>")
async def makepoll(ctx, *, name):
	global polls
	global reactions
	global options
	name = name.strip().split(",")
	name = [x.strip() for x in name if len(x.strip()) != 0]
	numoptions = len(name)
	if (numoptions > 20):
		await ctx.send("Only 20 options allowed")
		return
	id = random.randint(0,100000)
	while id in polls:
		id = random.randint(0,100000)
	options[id] = name
	reactions[id] = [0] * numoptions
	pollstring = 'Poll:\n' + create_string(id)
	poll = await ctx.send(pollstring)
	polls[id] = poll
	polltoid[poll] = id
	for reaction in availablereactions[:numoptions]:
		await poll.add_reaction(reaction)
	
@bot.command(help = "add an option to a poll using its id.\nformat: $addpolloption <poll_id> <option>")
async def addpolloption(ctx,*,name):
	global polls
	global options
	global reactions
	name = name.strip()
	id = int(name[:name.find(' ')]) #parse poll id
	name = name[name.find(' ') + 1:]
	if id in ynpolls:
		await ctx.send("Unable to add options to yes/no polls")
		return
	if id not in polls or polls[id].guild != ctx.guild:
		await ctx.send("No poll available")
		return
	if (len(options[id]) == 20):
		await ctx.send("You can't add more options to this poll")
		return
	options[id].append(name)
	reactions[id].append(0)
	pollstring = 'Poll:\n' + create_string(id)
	await polls[id].add_reaction(availablereactions[len(options[id])-1])
	await polls[id].edit(content = pollstring)

@bot.event
async def on_reaction_add(reaction, user):
	global reactions
	global options
	if user.bot:
		return
	if reaction.message not in polltoid:
		return
	id = polltoid[reaction.message]
	if id in ynpolls:
		if reaction.emoji not in ynreactions:
			return
		reactions[id][ynreactions.index(reaction.emoji)] += 1
		pollstring = 'Poll: {}\n'.format(ynpolls[id]) + create_string(id)
		await polls[id].edit(content = pollstring)
	else:
		if reaction.emoji not in availablereactions:
			return
		numoptions = len(options[id])
		idx = availablereactions.index(reaction.emoji)
		if (idx >= numoptions):
			return
		reactions[id][idx] += 1
		pollstring = 'Poll:\n' + create_string(id)
		await polls[id].edit(content = pollstring)

async def fetch_message(payload):
    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    return message

@bot.event
async def on_raw_reaction_remove(payload):
	global reactions
	global options
	message = await fetch_message(payload)
	if message not in polltoid:
		return
	id = polltoid[message]
	reaction = payload.emoji.name
	if id in ynpolls:
		if reaction not in ynreactions:
			return
		reactions[id][ynreactions.index(reaction)] -= 1
		pollstring = 'Poll: {}\n'.format(ynpolls[id]) + create_string(id)
		await polls[id].edit(content = pollstring)
	else:
		if reaction not in availablereactions:
			return
		numoptions = len(options[id])
		idx = availablereactions.index(reaction)
		if (idx >= numoptions):
			return
		reactions[id][idx] -= 1
		pollstring = 'Poll:\n' + create_string(id)
		await polls[id].edit(content = pollstring)

async def _removepoll(id):
	global polls
	global ynpolls
	global polltoid
	global options
	global reactions
	poll = polls[id]
	polls.pop(id)
	if id in ynpolls:
		ynpolls.pop(id)
	polltoid.pop(poll)
	options.pop(id)
	reactions.pop(id)

@bot.command(help = "removes the poll with specified id.")
async def removepoll(ctx,*,name):
	id = int(name)
	if id not in polls or polls[id].guild != ctx.guild:
		await ctx.send("Specified poll doesn't exist")
		return
	await _removepoll(id)
	await ctx.send("Sucessfully removed poll {}".format(id))


@bot.command(help = "deletes all polls in this server after confirmation.\nformat: $flushpolls CONFIRM")
async def flushpolls(ctx,*args):
	if (len(args) != 1):
		await ctx.send("Please confirm deletion of all polls with argument CONFIRM")
		return
	args = ''.join(args)
	if (args != "CONFIRM"):
		await ctx.send("Please confirm deletion of all polls with argument CONFIRM")
		return
	guild = ctx.guild
	todelete = []
	for id in polls:
		if (polls[id].guild == guild):
			todelete.append(id)
	for id in todelete:
		await _removepoll(id)
		await ctx.send("Successfully removed poll {}".format(id))
	await ctx.send("Deleted all active polls in this server")


reminders = {} #dictionary of (member_id, guild_id): [list of reminders]
@bot.command(help = "set a prompt reminder activating on call join.\nformat: $remindcall <prompt>")
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
