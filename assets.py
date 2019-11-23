"""
The point of defining the Assets folder as seperate from the objects folder is to make it easy to add new assets to the
game, especially those which have their own behavior. You'll notice I didn't include CREEPERs in the game, because they
are considered an auxiliary mechanic by most players. Every card-code in this file which has an underscore before it
refers to a card which has special behavior within its class. This behavior is recorded in subclasses for their type.
The foodlist is stored here, too.
"""


keepers = {'Sleep', 'Money', 'Time', 'Music', 'Sun', 'Toaster', 'Eye', 'Brain', 'Moon',
           'Love', 'Peace', 'Rocket', 'Television', 'Milk', 'Cookies', 'Chocolate', 'Dreams', 'Party', 'Bread'}

foods = {'Milk', 'Cookies', 'Chocolate', 'Bread'}

goals = {
        'Milk & Cookies': ('Milk', 'Cookies'),
        'Party Snacks': ('Party', '_anyfood'),
        'Night & Day': ('Sun', 'Moon'),
        'Turn Up Volume': ('Music', 'Party'),
        'Great Theme Song': ('Music', 'Television'),
        'Winning Lottery': ('Dreams', 'Money'),
        'Toast': ('Bread', 'Toaster'),
        'Eye of Beholder': ('Eye', 'Love'),
        'Dreamland': ('Sleep', 'Dreams'),
        'Squishy Chocolate': ('Sun', 'Chocolate'),
        'Chocolate Cookies': ('Chocolate', 'Cookies'),
        'Rocket to Moon': ('Rocket', 'Moon'),
        'World Peace': ('Dreams', 'Peace'),
        'Chocolate Milk': ('Chocolate', 'Milk'),
        'Rocket Science': ('Rocket', 'Brain'),
        'Time is Money': ('Time', 'Money'),
        'Bread & Chocolate': ('Bread', 'Chocolate'),
        'Party Time': ('Party', 'Time'),
        'Five Keepers': ('_fivekeepers',),
        'The Brain (No TV)': ('Brain', '_notv'),
        'Ten Cards in Hand': ('_tencards',),
        'Bed Time': ('Sleep', 'Time'),
        'Cant Buy Me Love': ('Money', 'Love'),
        'Hearts & Minds': ('Love', 'Brain'),
        'Baked Goods': ('Bread', 'Cookies'),
        'The Minds Eye': ('Eye', 'Brain'),
        'The Appliances': ('Toaster', 'Television'),
        'Day Dreams': ('Dreams', 'Sun'),
        'Hippyism': ('Peace', 'Love'),
        'Lullaby': ('Sleep', 'Music')
        }

# We use _ to denote exotic goals because there's only conventional meaning for it in python,
# so I can call a function _func in objects.py.

rules = {
        'Draw': {'Draw 2': 2, 'Draw 3': 3, 'Draw 4': 4, 'Draw 5': 5},
        'Play': {'Play 2': 2, 'Play 3': 3, 'Play 4': 4, 'Play All But 1': -1, 'Play All': 0}
        }
