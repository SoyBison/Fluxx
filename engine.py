import sys

from objects import *

board = None


def start_screen():
    global board

    print('Starting Game...')
    playnum = input('How Many Players?')
    board = Board(int(playnum))
    if isinstance(board, Board):
        play_game(board)
    else:
        return False



def print_info():
    global board
    info = board.info
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
    print(f"Your options are: {info['options']}")


def interact(entry):
    global board
    try:
        if len(entry) == 1:
            board.action(entry[0])
        else:
            board.action(entry)
        print_info()
    except (Board.IllegalMove, IndexError) as e:
        if isinstance(e, IndexError):
            print("That isn't an available option.")
        if isinstance(e, Board.IllegalMove):
            print(e)


def play_game(_):
    global board
    print_info()
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
            else:
                entry = entry.replace(' ', '').split(',')
                entry = list(filter(lambda a: a != '', entry))
                entry = [int(x) - 1 for x in entry]
                interact(entry)
        except Board.Win:
            print('Congratulations')
            sys.exit()


def main():
    print(logo)
    print('\n\n\n')
    start_screen()


if __name__ == '__main__':
    main()
