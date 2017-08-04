# Places torches into a ROM in one command. The command can be executed multiple times from anywhere in the world,
# each execution will place and remove torches where needed to match the program.
#
# PROGRAM ARGUMENTS:
#  1. settings
#  2. the program
#
# SETTINGS:
# Settings are provided in a one line property format: "key=val;key=val;..."
# Settings required to run:
# - x, y, z: the position of the most significant bit of the first data element
# - dir: the direction the torches should face. Torches of following lines will be placed behind, torches from the same line to the right.
# - height: Split output into multiple commands setting at most 'height' blocks at once. 
# PROGRAM:
# - Each line in the argument equals one data line (address) in the ROM
# - Each char equals to one bit
# - Chars that are "1" are interpreted as "place torch", all other as "place air". Spaces are ignored.
#
# LIMITATIONS:
# This is slow. Each bit will generate a command block, and they will get stacked on top of each other. If blocks can't be placed (no air, or world limit),
# the program fails and won't execute. Make sure the height parameter is set low enough to fit your ceiling. Also note that the command block pillars will be 3 blocks taller than height during execution


# direction handling
class Direction:
	dir = None
	name = None
	index = None
	metadata = None
	def __init__(self, index, name, metadata, dirx, dirz):
		self.dir = [dirx, dirz]
		self.name = name
		self.index = index
		self.metadata = metadata
	def __str__(self):
		return str(self.index) + ":" + self.name + ", " + str(self.dir)

DIRECTIONS = {
				'north': Direction(0, 'north', 4, 0, -2),
				'east': Direction(1, 'east', 1, 2, 0),
				'south': Direction(2, 'south', 3, 0, 2),
				'west': Direction(3, 'west', 2, -2, 0)
			}
DIRLIST = [DIRECTIONS['north'], DIRECTIONS['east'], DIRECTIONS['south'], DIRECTIONS['west']]

def setblock(x, y, z, block):
	return "/setblock " + str(x) + " " + str(y) + " " + str(z) + " " + block;
def rotateDir(dir, amount):
	return DIRLIST[(dir.index + amount) % 4]
def oneCommand(commands):
	# prepare command
	out = "/summon falling_block ~ ~2 ~ {Time:1,Block:chain_command_block,Data:0,TileEntityData:{CustomName:Weltbereiniger,Command:\"/fill ~ ~ ~ ~ ~" + str(len(commands)) + " ~ air\",auto:1b}"
	footer = "}"
	for command in commands[:-1]:
		out += ",Passengers:[{id:falling_block,Time:1,Block:chain_command_block,Data:0,TileEntityData:{Command:\"" + command + "\",auto:1b}"
		footer = "}]" + footer
	out += ",Passengers:[{id:falling_block,Time:1,Block:command_block,Data:0,TileEntityData:{CustomName:Weltbereiniger,Command:\"" + commands[-1] + "\",auto:1b}}]"
	return out + footer
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

settings = {}
# parse settings
for line in sys.argv[1].split(";"):
	if "=" in line:
		name, value = line.split("=", 1)
		settings[name.strip()] = value.strip()

# add commands
commands = []
torchDir = DIRECTIONS[settings['dir']]
mainDir = rotateDir(torchDir, 2)
innerDir = rotateDir(torchDir, 1)
pos = [int(settings['x']), int(settings['y']), int(settings['z'])]
for line in sys.argv[2].split('\n'):
	pos2 = [pos[0], pos[1], pos[2]]
	for char in line:
		block = "air"
		if char == " ":
			continue
		if char == "1":
			block = "redstone_torch " + str(torchDir.metadata)
		commands.append(setblock(pos2[0], pos2[1], pos2[2], block))
		pos2[0] += innerDir.dir[0]
		pos2[2] += innerDir.dir[1]
	pos[0] += mainDir.dir[0]
	pos[2] += mainDir.dir[1]

commands = chunks(commands, int(settings['height']))
for command in commands:
	print(oneCommand(command))