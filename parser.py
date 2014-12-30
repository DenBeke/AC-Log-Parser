"""
Simple script for parsing logs generated by the Assault Cube server
"""

__author__ = "Mathias Beke"


import sys
import re
import json
import jsonpickle

class Player:
	"""
	Data structure for a player
	"""
	
	def __init__(self):
		
		self.name 		= ""
		
		self.killactions = {}
		self.flagactions	= {}
				
		self.kills		= 0
		self.killed		= 0
		self.teamkills  	= 0
		self.teamkilled 	= 0
		self.suicides	= 0
		
		
	def incrementKillAction(self, action):
		
		if self.killactions.has_key(action):
			self.killactions[action] += 1
		else:
			self.killactions[action] = 1
			
	def incrementFlagAction(self, action):
		
		if self.flagactions.has_key(action):
			self.flagactions[action] += 1
		else:
			self.flagactions[action] = 1


class LogParser:
	"""
	Class for parsing logfiles generated by the Assault Cube server
	"""
	
	def __init__(self):
		
		self.players = {}
		
		self.killActions = [
			"busted",
			"picked off",
			"peppered",
			"sprayed",
			"punctured",
			"shredded",
			"slashed",
			"splattered",
			"headshot",
			"gibbed",
			"suicided"
		]
		
		self.flagActions = [
			"scored",
			"returned",
			"lost",
			"stole"
		]
		
		self.teamkillMessage = "their teammate"
		self.suicideMessage = "suicided"
		
		self.patternLine = re.compile("\[[0-9\.]*\]") # regex matching all lines that are interesting
		
		self.total = {
			"kills" : 0, # all kills + teamkills + suicides
			"teamkills" : 0,
			"suicides" : 0
		}
		
		
	def getPlayer(self, name):
		
		if name in self.players:
			return self.players[name]
		else:
			player = Player()
			player.name = name
			self.players[name] = player
			return self.players[name]
		
		
	def parseline(self, line):
		if self.patternLine.match(line):
			
			# Look for the names of the actor / target
			items = line.split()	
			actor = ""
			target = ""
			teamkill = False
			
			# Line too short, we're not interested
			if len(items) > 2:
				actor = items[1]
				target = items[-1]				
			else:
				return

			
			# Loop through all the kill actions
			for a in self.killActions:
				if line.find(a) >= 0:
					
					self.total["kills"] += 1
					
					# suicided
					if a == self.suicideMessage:
						self.getPlayer(actor).suicides += 1
						self.total["suicides"] += 1
					
					# regular kill
					else:
						self.getPlayer(actor).incrementKillAction(a)
						self.getPlayer(actor).kills += 1
						
						self.getPlayer(target).killed += 1
						
						## check for teamkill
						if line.find(self.teamkillMessage) >= 0:
							self.getPlayer(actor).teamkills += 1
							self.getPlayer(target).teamkilled += 1
							self.total["teamkills"] += 1
							
			
			# Loop through all the flag actions
			for a in self.flagActions:
				if line.find(a) >= 0:
					self.getPlayer(actor).incrementFlagAction(a)



if __name__ == "__main__":
	
	p = LogParser()
	
	for line in sys.stdin:
		p.parseline(line)
		
	print json.dumps(json.loads(jsonpickle.encode(p, unpicklable=False)), indent=4) 
