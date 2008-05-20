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
    """Read the puzzle text from the given file
    @param path: Path to puzzle file
    @return: string

    """
    txt = ''
    try:
        file_h = open(path, "rb")
        txt = file_h.readline()
        file_h.close()
    except (IOError, OSError, AttributeError):
        return txt
    return txt.strip()

def WritePuzzleFile(path, txt):
    """Write out the given game file
    @param path: Path to write to
    @param txt: Puzzle Text
    @return: bool

    """
    try:
        file_h = open(path, "wb")
        txt = file_h.write(txt)
        file_h.close()
    except (IOError, OSError, AttributeError):
        return False
    return True
