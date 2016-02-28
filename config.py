# Configuration details for the push.py script
# take a look in README.md for more info

key         = "fe54d7841adceb62fcb8738a723bf8af"                     # API key for access
url         = "http://127.0.0.1:8888/ac-ladder/push/" + str(key)     # URL of the ladder server
timestamp   = False
interval    = 20 # Interval (in minutes) between pushes to ladder back-end
logdir      = "./"