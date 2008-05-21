###############################################################################
# Name: sudoku_cmn.py                                                         #
# Purpose: Common Code                                                        #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Common Objects

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__revision__ = "$Revision$"
__scid__ = "$Id$"

#-----------------------------------------------------------------------------#
# Imports
import os
import cPickle
import wx

# Local Imports
import puzzle

#-----------------------------------------------------------------------------#
# Values
DEBUG = False

ID_EASY = wx.NewId()
ID_NORMAL = wx.NewId()
ID_HARD = wx.NewId()
ID_EVIL = wx.NewId()

DIFF_MAP = { ID_EASY : puzzle.DIFFICULTY_EASY,
             ID_NORMAL : puzzle.DIFFICULTY_NORMAL,
             ID_HARD : puzzle.DIFFICULTY_HARD,
             ID_EVIL : puzzle.DIFFICULTY_EVIL }

VALID_DIFFICULTIES = (puzzle.DIFFICULTY_EASY, puzzle.DIFFICULTY_NORMAL,
                      puzzle.DIFFICULTY_HARD, puzzle.DIFFICULTY_EVIL)

DIFFICULTY_STRINGS = ("Easy", "Normal", "Hard", "Evil")

# Other Menu Id's
ID_FEEDBACK = wx.NewId()

#-----------------------------------------------------------------------------#
# Debugging Functions

def DebugP(msg):
    """Print debug messages
    @param msg: string

    """
    if DEBUG:
        print msg

#-----------------------------------------------------------------------------#
# File Functions

def ReadPuzzleFile(path):
    """Read the puzzle state from the given puzzle file
    @param path: Path to puzzle file
    @return: dict('initial':'', 'current':'', 'moves':0, 'hints':0, 'time':0)

    """
    if os.path.exists(path):
        try:
            fhandle = open(path, 'rb')
            val = cPickle.load(fhandle)
            fhandle.close()
        except (IOError, SystemError, OSError,
                cPickle.UnpicklingError, EOFError), msg:
            sudoku_cmn.DebugP("[sudoku][err] %s" % msg)
        else:
            return val

    # Load failed
    return dict(initial='', current='', moves=0, hints=0, time=0)

def WritePuzzleFile(path, state):
    """Write out the given game file
    @param path: Path to write to
    @param state: Puzzle state (dict)
    @return: bool

    """
    try:
        fhandle = open(path, 'wb')
        cPickle.dump(state, fhandle, cPickle.HIGHEST_PROTOCOL)
        fhandle.close()
    except (IOError, cPickle.PickleError), msg:
        sudoku_cmn.DebugP("[sudoku][err] %s" % msg)
        return False
    else:
        return True
