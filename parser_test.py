import unittest
from parser import *

class TestParser(unittest.TestCase):
	
	def __init__(self, *args, **kwargs):
		super(TestParser, self).__init__(*args, **kwargs)
		self.p = LogParser()
		self.parse()
	
	def parse(self):
		f = open('server_test.log','r')
		while True:
			line = f.readline()
			if not line:
				break
			
			self.p.parseline(line)
	
	def test_players(self):
		self.assertEqual(len(self.p.players), 7)
		
	def test_players_score(self):
		player = self.p.players["MathiasB"]
		self.assertEqual(player.name, "MathiasB")
		self.assertEqual(player.ip, "62.205.75.76")
		self.assertEqual(player.kills, 3)
		self.assertEqual(player.killed, 1)
	
	def test_player_killactions(self):
		player = self.p.players["MathiasB"]
		self.assertEqual(player.killactions["headshot"], 1)
		self.assertEqual(player.killactions["punctured"], 1)
	
	def test_player_flagactions(self):
		player = self.p.players["MathiasB"]
		self.assertEqual(player.flagactions["scored"], 1)
		self.assertEqual(player.flagactions["returned"], 1)
		self.assertEqual(player.flagactions["stole"], 1)
	
	def test_total_games_played(self):
		self.assertEqual(self.p.total["games"], 1)
	
	def test_modes(self):
		self.assertEqual(self.p.modes["ctf"], 1)
	
	def test_maps(self):
		self.assertEqual(self.p.maps["poolparty"], 1)
	
	def test_num_players(self):
		self.assertEqual(self.p.numberOfPlayers, 6)
		

if __name__ == '__main__':
	
	suite = unittest.TestLoader().loadTestsFromTestCase(TestParser)
	unittest.TextTestRunner(verbosity=2).run(suite)