###############################################################################
# Name: puzzle.py                                                             #
# Purpose: Puzzle Management and Representation Objects                       #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Classes for representing and managing Sudoku game puzzles

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__revision__ = "$Revision$"
__scid__ = "$Id$"

#-----------------------------------------------------------------------------#
# Imports
import os
import random

# Local Imports
from puzzledb import PUZZLES

#-----------------------------------------------------------------------------#
# Globals

DIFFICULTY_EASY   = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD   = 2
DIFFICULTY_EVIL   = 3
DIFFICULTIES = { 'Easy' : DIFFICULTY_EASY,
                 'Normal' : DIFFICULTY_NORMAL,
                 'Hard' : DIFFICULTY_HARD,
                 'Evil' : DIFFICULTY_EVIL }

#-----------------------------------------------------------------------------#

def DebugP(msg):
    """Print debug messages
    @param msg: string

    """
    print msg

#-----------------------------------------------------------------------------#

class CellData(object):
    """Data object to hold information about a given cell"""
    def __init__(self, pos, size, readonly=False, val='', active=False):
        """Create a cell data object
        @param pos: Cell position
        @param size: Size of cell
        @keyword readonly: Value is read only
        @keyword val: Value of cell
        @keyword active: Is the cell active

        """
        object.__init__(self)

        # Attributes
        self.pos = pos              # Postion
        self.size = size            # Cell Size
        self.val = val              # Current Value
        self.active = active        # Is active
        self.readonly = readonly    # Is a fixed cell
        self.pmarks = list()        # Pencil Marks

    @property
    def x(self):
        """Cells X cordinate"""
        return self.pos[0]

    @property
    def y(self):
        """Cells Y cordinate"""
        return self.pos[1]

    @property
    def w(self):
        """Width of the cell"""
        return self.size[0]
    width = w

    @property
    def h(self):
        """Height of the cell"""
        return self.size[1]
    height = h

    def CanEdit(self):
        """Can this cell be editted
        @return: bool

        """
        return not self.readonly

    def GetRect(self):
        """Get the rect of the cell
        @return: tuple

        """
        return (self.x, self.y, self.w, self.h)

    def SetValue(self, val):
        """Set the cells value
        @param val: string

        """
        if not self.CanEdit():
            return

        if val.isdigit():
            self.val = val
        else:
            self.val = ''

#-----------------------------------------------------------------------------#

class PuzzleBoard(list):
    """Data storage and representation of the puzzles state
    @todo: add undo/redo support

    """
    CORNERS = [0, 3, 6, 27, 30, 33, 54, 57, 60]

    def __init__(self):
        list.__init__(self)

    def __str__(self):
        """Convert the board to a string in compact puzzle format"""
        rstr = ''
        for cell in self:
            if cell.val.isdigit():
                rstr += cell.val
            else:
                rstr += '.'
        return rstr

    def append(self, cell):
        """Add a cell to the board
        @param cell: L{CellData}
        @note: overrides list.append

        """
        if isinstance(cell, CellData):
            list.append(self, cell)
        else:
            raise TypeError, "A PuzzleBoard can only accept CellData"

    def ActivateCell(self, cell):
        """Set the active cell
        @param cell: cell to activate
        @postcondition: All cells but the specified are deactivated

        """
        for idx, cell_data in enumerate(self):
            if idx != cell:
                cell_data.active = False
            else:
                cell_data.active = True

    def GetBlockValues(self, block):
        """Get the list of values for the given block (0-8)
        @param block: int
        @return: list

        """
        cell = PuzzleBoard.CORNERS[block]
        return self.GetValueList(self.GetCellsSameBlock(cell))

    def GetCellsSameBlock(self, cell):
        """Get all the cells that are in the same 3x3 block as the given cell
        @param cell: int
        @return: list

        """
        row, column = self.GetPosition(cell)
        block = (3 * (row / 3) + (column / 3))
        idx = (9 * (block / 3) + (block % 3)) * 3
        return self[idx:idx+3] + self[idx+9:idx+12] + self[idx+18:idx+21]

    def GetCellsSameColumn(self, cell):
        """Get a list of the cells that are in the same column as the given
        cell.
        @param cell: int

        """
        return [ self[idx] for idx in range(cell % 9, 81, 9) ]

    def GetCellsSameRow(self, cell):
        """Get a list of the cells that are in the same row as the given cell.
        @param cell: int

        """
        start = (cell / 9) * 9
        return self[start:start+9]

    def GetColumnValues(self, column):
        """Get the list of values for the given column
        @param column: column to get values from
        @type column: int
        @return: list
        @note: 0 represents an empty cell

        """
        return self.GetValueList(self.GetCellsSameColumn(column))

    @staticmethod
    def GetPosition(cell):
        """Get the (row, column) position of a given cell
        @param cell: int
        @return: tuple

        """
        return (cell / 9, cell % 9)

    def GetRowValues(self, row):
        """Get the list of values for the given row
        @param row: row to get values from
        @type row: int
        @return: list

        """
        return self.GetValueList(self.GetCellsSameRow(row * 9))

    @staticmethod
    def GetValueList(cells):
        """Get a list of values from the given list of cells
        @param cells: list of L{CellData}
        @return: list of cell values

        """
        vals = list()
        for val in [ cell.val for cell in cells ]:
            if len(val):
                vals.append(val)
            else:
                vals.append('0')
        return vals

    def IsComplete(self):
        """Check if the puzzle has been completely solved or not
        @return: bool

        """
        for i in range(9):
            rstr = ''.join(sorted(self.GetRowValues(i)))
            cstr = ''.join(sorted(self.GetColumnValues(i)))
            bstr = ''.join(sorted(self.GetBlockValues(i)))
            for val in (rstr, cstr, bstr):
                if val != "123456789":
                    return False
        return True

#-----------------------------------------------------------------------------#

class PuzzleManager(object):
    """Object for loading and serving the games puzzle boards. The puzzle
    manager excepts puzzles that are in the standard compact form.

    """
    def __init__(self):
        object.__init__(self)

        # Attributes
        self._boards = dict()

        # Setup
        self.LoadPuzzles()

    def GetNewPuzzle(self, diff=DIFFICULTY_NORMAL):
        """Get a new random game board
        @keyword diff: Puzzle difficulty rating
        @return: (puzzle id, puzzle string)

        """
        puzzleid = 0
        board = ''
        puzzles = self._boards.get(diff, None)
        if puzzles is not None:
            npuzzles = len(puzzles) - 1
            if npuzzles >= 0:
                puzzleid = random.randint(0, npuzzles)
                board = puzzles[puzzleid]
        return (puzzleid, board)

    def GetPuzzleData(self):
        """Get the dictionary of all loaded puzzles
        @return: dict

        """
        return self._boards

    def GetPuzzles(self, difficulty):
        """Get the list of puzzles for the given difficulty
        @param difficulty: int
        @return: list

        """
        return self._boards.get(difficulty, [])

    def LoadPuzzles(self, fname=None):
        """Load the game boards from a puzzle data file. The data file must
        contain puzzles that are in the standard compact form, with one puzzle
        per line. Puzzle difficultys can be specified by a line starting with
        '#' then followed by the difficutly i.e '# Normal'.
        
        The valid difficulties are (Easy, Normal, Hard, Evil)

        @keyword fname: path to file to load, or None for default
        @return: boolean

        """
        puzzles = dict()
        current = None
        if fname is None:
            puzzles = PUZZLES
        else:
            try:
                f_handle = open(fname, 'r')
                for line in f_handle:
                    line = line.strip()
                    if line.startswith("#"):
                        current = line.lstrip("#").strip().title()
                        current = DIFFICULTIES.get(current, None)
                        if current is not None and not puzzles.has_key(current):
                            puzzles[current] = list()
                    elif current is not None and len(line) == 81:
                        puzzles[current].append(line)
                    else:
                        pass
                f_handle.close()
            except Exception, msg:
                puzzles = None

        if puzzles is None:
            puzzles = PUZZLES

        self._boards = puzzles
        return True

# Create a PuzzleManager instance to use as a singleton
ThePuzzleManager = PuzzleManager()
