"""
The point of defining the Assets folder as seperate from the objects folder is to make it easy to add new assets to the
game, especially those which have their own behavior. You'll notice I didn't include CREEPERs in the game, because they
are considered an auxiliary mechanic by most players. Every card-code in this file which has an underscore before it
refers to a card which has special behavior within its class. This behavior is recorded in subclasses for their type.
The foodlist is stored here, too.

"""
import os

keepers = {'Sleep', 'Money', 'Time', 'Music', 'Sun', 'Toaster', 'Eye', 'Brain', 'Moon',
           'Love', 'Peace', 'Rocket', 'Television', 'Milk', 'Cookies', 'Chocolate', 'Dreams', 'Party', 'Bread'}

foods = {'Milk', 'Cookies', 'Chocolate', 'Bread'}

goals = {
    'Milk & Cookies': ('Milk', 'Cookies'),
    'Party Snacks': ('Party', '_anyfood'),
    'Night & Day': ('Sun', 'Moon'),
    'Turn Up the Volume!': ('Music', 'Party'),
    'Great Theme Song': ('Music', 'Television'),
    'Winning the Lottery': ('Dreams', 'Money'),
    'Toast': ('Bread', 'Toaster'),
    'The Eye of the Beholder': ('Eye', 'Love'),
    'Dreamland': ('Sleep', 'Dreams'),
    'Squishy Chocolate': ('Sun', 'Chocolate'),
    'Chocolate Cookies': ('Chocolate', 'Cookies'),
    'Rocket to the Moon': ('Rocket', 'Moon'),
    'World Peace': ('Dreams', 'Peace'),
    'Chocolate Milk': ('Chocolate', 'Milk'),
    'Rocket Science': ('Rocket', 'Brain'),
    'Time is Money': ('Time', 'Money'),
    'Bread & Chocolate': ('Bread', 'Chocolate'),
    'Party Time': ('Party', 'Time'),
    '5 Keepers': ('_fivekeepers',),
    'The Brain (No TV)': ('Brain', '_notv'),
    '10 Cards in Hand': ('_tencards',),
    'Bed Time': ('Sleep', 'Time'),
    "Can't Buy Me Love": ('Money', 'Love'),
    'Hearts & Minds': ('Love', 'Brain'),
    'Baked Goods': ('Bread', 'Cookies'),
    "The Mind's Eye": ('Eye', 'Brain'),
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
    'Free Action': {'Swap Plays for Draws': 'fa_swapplaysfordraws', 'Mystery Play': 'fa_mysteryplay',
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

with open(os.path.dirname(os.path.abspath(__file__)) + '/banner.txt', 'r') as file:
    logo = file.read()

card_text = {'Goal': {'Hippyism': 'Peace + Love',
                      'Day Dreams': 'Sun + Dreams',
                      'The Appliances': 'Toaster + Television',
                      'Party Time': 'Party + Time',
                      '5 Keepers': 'If someone has 5 or more Keepers on the table, \n '
                                   'then the player with the most Keepers in play wins.\n'
                                   ' In the event of a tie, continue playing until a clear winner emerges',
                      "The Mind's Eye": 'Brain + Eye',
                      "Baked Goods": 'Bread + Cookies',
                      "Hearts & Minds": 'Love + Brain',
                      "Can't Buy Me Love": 'Money + Love',
                      "Bed Time": 'Sleep + Time',
                      "10 Cards in Hand": "If someone has 10 or more cards in his or her hand, \n"
                                          "then the player with the most cards in hand wins. \n"
                                          "In the event of a tie, continue playing until a clear winner emerges.",
                      "The Brain (No TV)": 'If no one has Television on the table, '
                                           'the player with The Brain on the table wins.',
                      "Lullaby": 'Sleep + Music',
                      'Time is Money': 'Time + Money',
                      'Rocket Science': 'Rocket + Brain',
                      'Chocolate Milk': 'Chocolate + Milk',
                      'World Peace': 'Dreams + Peace',
                      'Rocket to the Moon': 'Rocket + Moon',
                      'Chocolate Cookies': 'Chocolate + Cookies',
                      'Squishy Chocolate': 'Chocolate + Sun',
                      'Dreamland': 'Sleep + Dreams',
                      'The Eye of the Beholder': 'Eye + Love',
                      'Toast': 'Bread + The Toaster',
                      'Winning the Lottery': 'Dreams + Money',
                      'Great Theme Song': 'Music + Television',
                      'Turn Up the Volume!': 'Music + Party',
                      'Night & Day': 'Sun + Moon',
                      'Milk & Cookies': 'Milk + Cookies',
                      'Party Snacks': 'The Party + At Least 1 Food Keeper',
                      'Bread & Chocolate': 'Bread + Chocolate'
                      },
             'Rule': {'Goal Mill': 'Once during your turn, discard as many of your goal \n'
                                   'cards as you choose, then draw that many cards.',
                      'Recycling': 'Once during your turn, you many discard one of your \n'
                                   ' Keepers from the table and draw 3 extra cards',
                      'Get On With It!': 'Before your final play, if you are not empty handed, \n'
                                         'you may discard your entire hand and draw 3 cards.\n'
                                         ' Your turn then ends immediately.',
                      'Mystery Play': 'Once during your turn, \n'
                                      'you may take the top card from the draw pile and play it immediately.',
                      'Swap Plays for Draws': 'During your turn, you may decide to play no more cards and instead \n'
                                              'draw as many cards as you have plays remaining.\n'
                                              ' If Play All, draw as many cards as you hold.\n',
                      'No-Hand Bonus': 'If empty handed, draw 3 cards before observing the current draw rule.',
                      'First Play Random': 'The first card you play must be chosen at random. \n'
                                           'Ignore this rule if you can only play one card per turn.',
                      'Rich Bonus': 'If one player has more Keepers than any other player, \n'
                                    'that person may play 1 extra card. \n'
                                    'In the event of a tie, no player receives the bonus.\n',
                      'Poor Bonus': 'If one player has fewer Keepers on the table than any other player,\n'
                                    ' that player draws 1 additional card. In the event of a tie, \n'
                                    'no player receives the bonus.',
                      'Party Bonus': 'If someone has the Party on the table, \n'
                                     'all players Draw 1 extra card and Play 1 extra card during their turns.',
                      'Double Agenda': 'A second Goal can now be played.\n'
                                       ' After this, whoever plays a new Goal must \n'
                                       'choose which of the ccurrent Goals to discard. \n'
                                       'You win if you satisfy either Goal.',
                      'Inflation': 'Any time a numeral is seen on another card, add one to that numeral.\n'
                                   ' For example, 1 becomes 2 while one remains one.\n'
                                   ' Yes, this affects the Basic Rules.',
                      'Draw 2': 'If you just played this card, draw extra cards as needed to reach 2 cards drawn.',
                      'Draw 3': 'If you just played this card, draw extra cards as needed to reach 3 cards drawn.',
                      'Draw 4': 'If you just played this card, draw extra cards as needed to reach 4 cards drawn.',
                      'Draw 5': 'If you just played this card, draw extra cards as needed to reach 5 cards drawn.',
                      'Hand Limit 2': "If it isn't your turn, you can only have 2 cards in your hand.\n"
                                      " Discard extras immediately. \n"
                                      "During your turn, this rule does not apply to you;\n"
                                      "after your turn ends, discard down to 2 cards.",
                      'Hand Limit 1': "If it isn't your turn, you can only have 1 cards in your hand.\n"
                                      " Discard extras immediately. \n"
                                      "During your turn, this rule does not apply to you;\n"
                                      "after your turn ends, discard down to 1 cards.",
                      'Hand Limit 0': "If it isn't your turn, you can only have 0 cards in your hand.\n"
                                      " Discard extras immediately. \n"
                                      "During your turn, this rule does not apply to you;\n"
                                      "after your turn ends, discard down to 0 cards.",
                      'Keeper Limit 4': "If it isn't your turn, you can only have 4 Keepers in play.\n"
                                        " Discard extras immediately. \n"
                                        "You may acquire new Keepers during your turn as long as \n"
                                        "you discard down to 4 when your turn ends.",
                      'Keeper Limit 3': "If it isn't your turn, you can only have 3 Keepers in play.\n"
                                        " Discard extras immediately. \n"
                                        "You may acquire new Keepers during your turn as long as \n"
                                        "you discard down to 3 when your turn ends.",
                      'Keeper Limit 2': "If it isn't your turn, you can only have 2 Keepers in play.\n"
                                        " Discard extras immediately. \n"
                                        "You may acquire new Keepers during your turn as long as \n"
                                        "you discard down to 2 when your turn ends.",
                      'Play 2': 'Play 2 cards per turn. If you have fewer than that, play all your cards.',
                      'Play 3': 'Play 3 cards per turn. If you have fewer than that, play all your cards.',
                      'Play 4': 'Play 4 cards per turn. If you have fewer than that, play all your cards.',
                      'Play All But 1': 'Play all but 1 of your cards per turn. \n'
                                        'If you started with no cards in hand and only drew one, draw an extra card.',
                      'Play All': 'Play all your cards per turn.'},
             'Action': {'Empty the Trash': 'Start a new discard pile with this card and \n'
                                           'shuffle the rest of the discard pile back into the draw pile.',
                        'No Limits': 'Discard all Hand and Keeper limits currently in play.',
                        'Use What You Take': 'Take a card at random from another players hand, and play it.',
                        'Rules Reset': "Reset to the Basic Rules.\n"
                                       " Discard all New Rule cards, and leave only the Basic Rules in play. \n"
                                       "Do not discard the current goal.",
                        'Trade Hands': 'Trade your hand for the hand of one of your opponents.',
                        'Exchange Keepers': 'Pick any Keeper another player has on the table and \n'
                                            'exchange it for one you have on the table.\n'
                                            'You may choose to do nothing.',
                        'Trash a Keeper': 'Take a keeper from in front of any player and put it on the discard pile.\n'
                                          ' You may choose no keepers.',
                        "Let's Simplify": 'Discard your choice of up to half (rounded up) \n'
                                          'of the New Rule cards in play.',
                        'Steal a Keeper': 'Steal a Keeper from in front of another player, \n'
                                          'and add it to your collection of Keepers.',
                        'Take Another Turn': 'Take another turn as soon as you finish this one.\n'
                                             'The maximum numer of turns you can take in a row with this card is two.',
                        'Everybody Gets 1': 'Set your hand aside. Draw enough cards to give every player 1 card. \n'
                                            'Give every player 1 card. You decide who gets what',
                        'Random Tax': 'Take 1 card at random from the hand of each other \n'
                                      'player and add these cards to your own hand.',
                        'Jackpot!': 'Draw 3 extra cards!',
                        "Draw 2 and Use 'Em": 'Set your hand aside. \n'
                                              'Draw 2 cards, play them in any order you choose, \n'
                                              'then pick up your hand and continue with your turn.\n'
                                              ' This card, and all cards played because of it, \n'
                                              'are counted as a single play.',
                        "Let's Do That Again!": 'Search through the discard pile. \n'
                                                'Take any Action or New Rule card you wish and immediately play it.',
                        'Rotate Hands': 'All players pass their hands to the player next to them. \n'
                                        'You decide which direction.',
                        'Zap a Card': 'Choose any card in play, anywhere on the table and add it to your hand.',
                        'Draw 3, Play 2 of Them': 'Set your hand aside\n'
                                                  'Draw 3 cards and play 2 of them. Discard the last card, \n'
                                                  'then pick up your hand and coninue with your turn.\n'
                                                  'This card, and all cards played because of it,\n'
                                                  'are counted as a single play',
                        'Share the Wealth': 'Gather up all the Keepers on the table. Shuffle them together, \n'
                                            'then deal them out, giving the first card to yourself.\n',
                        'Discard and Draw': 'Discard your entire hand, then draw as many cards as your discarded. \n'
                                            'Do not count this card.'
                        }

             }


def nametest():
    for y in card_text['Goal']:
        if y not in goals:
            print(y)
    for y in card_text['Action']:
        if y not in actions:
            print(y)
    for y in card_text['Rule']:
        if all(y not in d for n, d in rules.items()):
            print(y)


if __name__ == '__main__':
    nametest()
