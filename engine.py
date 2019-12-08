import sys

from objects import *

board = None


def start_screen():
    global board

    print('Starting Game...')
    print('The game rules are available at: '
          'https://www.looneylabs.com/sites/default/files/literature/Fluxx5.0_Rules.pdf')
    playnum = input('How Many Players? ')
    board = Board(int(playnum))
    if isinstance(board, Board):
        play_game(board)
    else:
        return False


def print_info():
    global board
    info = board.info
    options = list(enumerate(info['options']))
    split_options = [options[i * 5:(i + 1) * 5] for i in range((len(options) + 5 - 1) // 5)]
    print('\n')
    print(f"It is player {info['player']}'s turn.")
    print(f'Rules state {info["draws"]} draws and {info["plays"]} plays')
    keeps = info['keeps']
    for keep in keeps:
        print(f'Player {keep.player_num} has {[card.name for card in keep]} in their keep.')
    if board.mysteryplay:
        print(f'The last mystery play was {info["mystery"].name}')
    print(f'The goals are {[card.name for card in info["goals"]]}')
    print(f"The Rules are {[card.name for card in info['rules']]}")
    print(f"This is a {info['actiontype']} action.")
    print(f"You have {info['remaining']} plays remaining.")
    print(f"Your options are:")
    for options in split_options:
        print('    '.join([f'{i}: {name}' for i, name in options]))
    print(f"You have drawn {info['drawn']} cards.")


def card_text_info(card_name):
    if card_name in card_text['Action']:
        card_type = 'Action'
    elif card_name in card_text['Goal']:
        card_type = 'Goal'
    else:
        card_type = 'Rule'
    type_d = card_text[card_type]

    return f'{card_type}: {type_d[card_name]}'


def get_card_text():
    global board
    info = board.cards_seen
    print("Enter the target card as a number, or type in the card's name as it appears in game. "
          "Enter 'q' to return to game.")
    options = list(enumerate(info))
    split_options = [options[i * 5:(i + 1) * 5] for i in range((len(options) + 5 - 1) // 5)]
    print(f"Your options are:")
    for options in split_options:
        print('    '.join([f'{i}: {name}' for i, name in options]))

    while True:
        entry = input('Which card would you like to read? ')
        print('\n')
        if entry == 'q':
            break
        try:
            selection = int(entry)
        except ValueError:
            selection = entry

        if isinstance(selection, int):
            try:
                print(card_text_info(info[selection].name))
            except KeyError:
                print('That card is a Keeper, and has no card text.')
        else:
            try:
                print(card_text_info(selection))
            except KeyError:
                print(f'Could not find card: {selection}, please try again.')
        print('\n')


def interact(entry):
    global board
    try:
        if len(entry) == 1:
            board.action(entry[0])
        else:
            board.action(entry)
        print_info()
    except (Board.IllegalMove, IndexError, TypeError) as e:
        if isinstance(e, IndexError):
            print("That isn't an available option.", e)
        if isinstance(e, Board.IllegalMove):
            print(e)
        elif isinstance(e, TypeError):
            print("That isn't an available option.", e)


def play_game(_):
    global board
    print_info()
    print('You may enter "d" to view the discard, "h" to view your hand, \n'
          '"i" to print the information display again, or "t" to view card text.')
    prompt = 'Enter your selection as a number, or a list of numbers seperated by a comma: '
    while True:
        try:
            entry = input(prompt)
            if entry == 'd':
                print(f'The discard is: {[card.name for card in board.info["discard"]]}')
            elif entry == 'h':
                print(f'Your hand is: {[card.name for card in board.info["hand"]]}')
            elif entry == 'i':
                print_info()
            elif entry == 't':
                get_card_text()
            else:
                try:
                    entry = entry.replace(' ', '').split(',')
                    entry = list(filter(lambda a: a != '', entry))
                    entry = [int(x) for x in entry]
                except ValueError:
                    print("That isn't an option, try again.")
                interact(entry)
        except Board.Win as e:
            print(f'Congratulations player {e}')
            sys.exit()


def main():
    print(logo)
    print('\n\n\n')
    start_screen()


if __name__ == '__main__':
    main()
