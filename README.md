Assault Cube Log Parser
=======================

*Simple Python class that parses lines from an [Assault Cube](http://assault.cubers.net) server log and saves the stats for each player*

Requirements
------------

**Python 2.7** *(I have only tested it on Python 2.7)*

**jsonpickle**

> The easiest way to get [jsonpickle](http://jsonpickle.github.io) is via PyPi with pip:  
> `$ pip install -U jsonpickle`


Usage
-----

You can use the `LogParser` class to create your own parser, but I have included a main function that reads from `stdin`, which can be easily used on the Unix command line: just pipe the AC server log file into the Python script.

    $ python parser.py < server.log


This will output stats for each player, and some global stats. Everything is outputted in JSON, so it can be easily imported in other applications.  
Stats for a given player look like this:
   
    "MathiasB": {
        "name": "MathiasB", 
        "teamkilled": 9, 
        "teamkills": 2, 
        "flagactions": {
            "scored": 4, 
            "stole": 7, 
            "returned": 8, 
            "lost": 5
        }, 
        "kills": 75, 
        "killactions": {
            "slashed": 17, 
            "gibbed": 13, 
            "busted": 3, 
            "headshot": 27, 
            "punctured": 12, 
            "picked off": 2
        }, 
        "suicides": 3, 
        "killed": 44
    }


Storing the output in a file can be done using pipes:

    $ python parser.py < server.log > stats.json

Author
------

Mathias Beke - [denbeke.be](http://denbeke.be)