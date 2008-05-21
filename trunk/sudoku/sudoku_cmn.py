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
    """Read the puzzle text from the given puzzle file
    The file should be ordered as follows
    line 1: original puzzle
    line 2: current state
    @param path: Path to puzzle file
    @return: string

    """
    txt = ''
    try:
        file_h = open(path, "rb")
        txt = [line.strip() for line in file_h.readlines()]
        file_h.close()
    except (IOError, OSError, AttributeError):
        return txt
    return txt

def WritePuzzleFile(path, txt1, txt2):
    """Write out the given game file
    @param path: Path to write to
    @param txt1: Original Puzzle Text
    @param txt2: Current Puzzle Text
    @return: bool

    """
    try:
        file_h = open(path, "wb")
        txt = file_h.write(os.linesep.join((txt1, txt2)))
        file_h.close()
    except (IOError, OSError, AttributeError):
        return False
    return True
