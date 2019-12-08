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
    'Play': {'Play 2': 2, 'Play 3': 3, 'Play 4': 4, 'Play All But 1': -1, 'Play All': 0},
    'Limit': {'Hand Limit 2': (2, 'Hand'), 'Hand Limit 1': (1, 'Hand'), 'Hand Limit 0': (0, 'Hand'),
              'Keeper Limit 4': (4, 'Keep'), 'Keeper Limit 3': (3, 'Keep'), 'Keeper Limit 2': (2, 'Keep')},
    'Effect': {'Party Bonus': 'e_partybonus', 'Rich Bonus': 'e_richbonus', 'Poor Bonus': 'e_poorbonus',
               'Inflation': 'e_inflation', 'Double Agenda': 'e_doubleagenda'},
    'Start': {'First Play Random': 's_firstplayrandom', 'No-Hand Bonus': 's_nohandbonus'},
    'Free Action': {'Swap Plays For Draws': 'fa_swapplaysfordraws', 'Mystery Play': 'fa_mysteryplay',
                    'Goal Mill': 'fa_goalmill', 'Get On With It!': 'fa_getonwithit', 'Recycling': 'fa_recycling'}
}

actions = {'Share the Wealth': 'a_sharethewealth', 'Discard and Draw': 'a_discardanddraw',
           'Draw 3, Play 2 of Them': 'a_draw3play2', 'Everybody Gets 1': 'a_everybody1', 'Zap a Card': 'a_zap',
           'Jackpot!': 'a_jackpot', 'Take Another Turn': 'a_anotherturn',
           'Rotate Hands': 'a_rotatehands', "Let's Do That Again!": 'a_dothatagain', 'Steal a Keeper': 'a_steal',
           "Let's Simplify": 'a_simplify', 'Trash a Keeper': 'a_trash', 'Exchange Keepers': 'a_exchange',
           'Trade Hands': 'a_trade', 'Rules Reset': 'a_rulesreset', "Draw 2 and Use 'Em": 'a_draw2use2',
           'Random Tax': 'a_tax', 'Use What You Take': 'a_usetake', 'No Limits': 'a_nolimits',
           'Empty the Trash': 'a_emptytrash'}

optionalactions = {'Rock-Paper-Scissors Showdown': 'a_rps', "Today's Special!": 'a_todaysspecial'}

with open('banner.txt', 'r') as file:
    logo = file.read()
