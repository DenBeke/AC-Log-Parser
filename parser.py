"""
Script for parsing logs generated by the Assault Cube server
"""

__author__ = "Mathias Beke"


import sys
import re
import json
import jsonpickle
import collections

class Player:
    """
    Data structure for a player
    """
    
    def __init__(self):
        
        self.name             = ""
        self.ip                = ""
        self.visits            = 0
        self.time            = 0
        
        self.killactions     = {}
        self.flagactions    = {}
                
        self.kills            = 0
        self.killed            = 0
        self.teamkills      = 0
        self.teamkilled     = 0
        self.flagteamkills    = 0
        self.flagteamkilled    = 0
        self.suicides        = 0
        
        
    def incrementKillAction(self, action):
        
        if action in self.killactions:
            self.killactions[action] += 1
        else:
            self.killactions[action] = 1
            
    def incrementFlagAction(self, action):
        
        if action in self.flagactions:
            self.flagactions[action] += 1
        else:
            self.flagactions[action] = 1
            
    def decrementFlagAction(self, action):
        
        if action in self.flagactions:
            self.flagactions[action] -= 1
        else:
            self.flagactions[action] = 0


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
            "stole",
            "dropped",
            "hunted",
            "forced to pickup",
            "carrying"
        ]
        
        self.flagbearer = None
                
        self.teamkillMessage = "their teammate"
        self.suicideMessage = "suicided"
        
        self.playerConnected = "logged in"
        self.playerDisconnected = "disconnected client"
        
        self.patternLine = re.compile("\[[0-9\.]*\]") # regex matching all lines that are interesting
        self.patternGameStart = re.compile("Game start: .+ on .+, [0-9]+ players")
        
        self.total = {
            "kills" :     0, # all kills + teamkills + suicides
            "teamkills" : 0,
            "suicides" :  0,
            "games" :     0,
        }
        
        self.numberOfPlayers = 0
        self.modes = {}
        self.maps  = {}
        
        # Some tmp data structures
        self.modesTmp = []
        self.mapsTmp  = []
        
    
    def reset(self):
        self.players =     {}
        self.total = {
            "kills" :      0, # all kills + teamkills + suicides
            "teamkills" :  0,
            "suicides" :   0,
            "games" :      0,
        }
        
        self.modes         = {}
        self.maps          = {}
        
        self.modesTmp      = []
        self.mapsTmp       = []

        
        
    def getPlayer(self, name):
        
        if name in self.players:
            return self.players[name]
        else:
            player = Player()
            player.name = name
            self.players[name] = player
            return self.players[name]
        
        
    def parseline(self, line):
        
        if self.patternGameStart.match(line):
            if line.startswith("Game start:"):
               line = line[len("Game start:"):]
            
            # Game start: ctf on poolparty, 7 players, 15 minutes, mastermode 0, (map rev 1/1801, temporary, 'getmap' prepared)
            self.total["games"] += 1
            info = line.split(",")
            
            while "on " not in info[0]:
                # Special case where mode name has comma in it
                info[:2] = [''.join(info[:2])]
            
            while "players" not in info[1]:
                # Special case where map name has comma in it
                info[:2] = [''.join(info[:2])]
                
            self.modesTmp.append(info[0].split()[0])
            self.mapsTmp.append(info[0].split()[-1])
            self.modes = collections.Counter(self.modesTmp)
            self.maps = collections.Counter(self.mapsTmp)
            
            self.numberOfPlayers = int(info[1].split()[0])
        
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

            
            # Player connects
            if line.find(self.playerConnected) >= 0:
                self.getPlayer(actor).ip = items[0][1:-1]
                self.numberOfPlayers += 1
                return
            
            # Player disconnects
            elif line.find(self.playerDisconnected) >= 0:
                actor = items[3]
                
                if actor == "cn":
                    #special case for empty player name
                    return
                
                time = int(items[6])
                
                self.getPlayer(actor).visits += 1
                self.getPlayer(actor).time += time
                self.numberOfPlayers -= 1
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
                            
                            if self.flagbearer == target:
                                self.getPlayer(actor).flagteamkills += 1
                                self.getPlayer(target).flagteamkilled += 1
                                self.flagbearer = None
                    
                    if self.getPlayer(actor).ip == "":
                        # set ip if ip not yet set
                        # this is needed for when players change name
                        self.getPlayer(actor).ip = items[0][1:-1]
                            
            
            # Loop through all the flag actions
            for a in self.flagActions:
                if line.find(a) >= 0:
                    self.getPlayer(actor).incrementFlagAction(a)
                    
                    if a in ["carrying"]:
                        # [85.196.30.159] MathiasB scored, carrying for 15 seconds, new score 1
                        # displays 'scored' and 'carrying', but we want to count it only once
                        self.getPlayer(actor).decrementFlagAction("scored")
                    
                    if a in ["stole","forced to pickup"]:
                        self.flagbearer = actor
                    
                    else:
                        self.flagbearer = None
                        
                    if self.getPlayer(actor).ip == "":
                        # set ip if ip not yet set
                        # this is needed for when players change name
                        self.getPlayer(actor).ip = items[0][1:-1]



    def __getstate__(self):
        
        return {"total": self.total, "players": self.players}



if __name__ == "__main__":
    
    p = LogParser()
    
    for line in sys.stdin:
        p.parseline(line)
        
    json = json.dumps(json.loads(jsonpickle.encode(p, unpicklable=False)), indent=4)
    
    print(json)
    
