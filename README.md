# Fluxx

### Introduction:

Fluxx is a mildly popular card game. All things considered, it's
actually fairly contentious. It has a score of 5.7 on Board Game Geek,
but it has a serious cult following. This is a python implementation of
version 5.0 of the Vanilla Fluxx card game. The full rules are available
[here](https://www.looneylabs.com/sites/default/files/literature/Fluxx5.0_Rules.pdf).
The core idea is that the players can play cards which change the rules
of the game. Each turn, each player draws a certain number of cards and
plays a certain number of cards. There are four types of cards. There
are Keepers, which are laid on the table in front of the player, Goals
which determine how the game is won, New Rules which change the rules of
the game, and finally Actions, which are played to the discard pile and
perform the action printed on the card. 

This particular implementation of the game was built from the ground-up,
using no third-party libraries or assets. Card text has been abridged
slightly, but retains all of the original's gameplay meaning.

Fluxx is a registered trademark of Looney Labs -- College Park, MD 20741-0763

The goal of this project is to create a playground for advanced AI
experiments with a complicated, not-analytically-solvable traditional
game. Looney Labs has developed a polished and well-made digital version
of Fluxx available
[here](https://www.looneylabs.com/news/digital-fluxx-back-now-android-too).
Which is actually optimized for play by humans, and I suggest that
anyone who found this project with the intention of playing the game for
fun pay them the $0.99 and get the digital edition. That being said,
there is a human-interface portion to this project which can be played
by running `engine.py`. 
 



### Installation and Use:

To play the game, all you need to do is run `engine.py`. The
construction is fully portable and relies on no third party packages.

For actually interesting uses of this project, a user needs to do the
following.

1. `from fluxx.objects import Board`
1. Create an instance of `Board`, which I will call `board`. 
1. Use `board.info` to get a dictionary which contains all of the
  player-knowable information about the game.
4. `board.info['options']` will show a list of the choices that the
   player has at the given stage of the game.
5. Run `board.action(option)` where `option` is the index of the desired
   option in `board.info['options']`. 
6. Repeat 4 and 5 until a winner becomes apparent. The `board.action()`
   will throw a `Board.Win` exception which contains the number of the
   player who won.
   
