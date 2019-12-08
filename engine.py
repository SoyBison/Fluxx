from pynput.keyboard import Key, Listener, KeyCode
import webbrowser

from objects import *


def start_screen(key):
    if isinstance(key, KeyCode) and (key.char == 'r' or key.char == '\x12'):
        print('Redirecting to Rule Book...')
        webbrowser.open('https://www.looneylabs.com/sites/default/files/literature/Fluxx5.0_Rules.pdf')
    if key == Key.enter:
        print('Starting Game...')
        begin_game()


def end_listen(key):
    if key == Key.esc:
        return False


def begin_game():
    pass


def main():
    print(logo)
    print('\n\n\n')
    print('Welcome to Fluxx, Press Enter to Start, or Press "r" to view the rules.')
    with Listener(on_press=start_screen, on_release=end_listen) as listener:
        listener.join()
    print('Thanks for Playing!')


if __name__ == '__main__':
    main()
