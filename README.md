jrpg
====

JRPG is a kanji learning game styled after the classic SNES RPG games (like Final Fantasy 6, or Legend of Zelda: Link to the Past). The game tries to help you learn how to read and understand kanji in context, and in doing that it also helps you improve your Japanese vocabulary. You can also use it to refresh your kana.

There is also a playable demo of how JRPG would look like if it was styled after PlayStation 1 RPG games.

To learn more visit JRPG's website: http://taw.github.io/jrpg/

Code
====

The code is pretty messy, and is was not originally intended for public consumption.

Cleanup pull requests welcome.

The game was originally designed for Python 2.7 and pygame 1.
It now runs on Python 3.13 and pygame 2.

Running it
==========

Dependencies are pinned in `pyproject.toml` and locked in `uv.lock`, so
[uv](https://docs.astral.sh/uv/) will fetch the right Python and libraries for you:

    cd jrpg
    uv run python jrpg.py

The game reads its data with relative paths, so it has to be run from the `jrpg`
directory. The level editor needs wxPython, which is not installed by default:

    uv run --extra editor python level_editor.py

What to run?
============

* `jrpg.py` - the game itself
* `level_editor.py` - level editor for the game
* `jrpg2demo.py` - demo for jrpg in PS1 style, not meant for serious use

`sciripts` and `extra_scripts` directories, and `Rakefile` contain a lot of
completely undocumented data preprocessing and other such tasks.
