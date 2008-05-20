###############################################################################
# Name: solver.py                                                             #
# Purpose: Sudoku Puzzle Solver and hint provider                             #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

# Main Reference:
# http://norvig.com/sudoku.html
#
# Other References used:
# http://www.scanraid.com/BasicStrategies.htm
# http://www.krazydad.com/blog/2005/09/29/an-index-of-sudoku-strategies/
# http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/sudoku/
#

"""
Sudoku Puzzle Solver for checking puzzle solution and providing hints

"""

__revision__ = "$Revision$"
__scid__ = "$Id$"

#-----------------------------------------------------------------------------#
# Globals 

def Cross(seq1, seq2):
    return [a + b for a in seq1 for b in seq2]

ROWS = 'ABCDEFGHI'
COLS = '123456789'

# List of all squares
SQUARES  = Cross(ROWS, COLS)

# List of all Rows, Columns, Boxes
UNITLIST = ([Cross(ROWS, column) for column in COLS] + \
            [Cross(row, COLS) for row in ROWS] + \
            [Cross(rs, cs)
             for rs in ('ABC','DEF','GHI')
             for cs in ('123','456','789')])

# Map of Square => [all units it belongs to]
UNITS = dict((square, [unit for unit in UNITLIST if square in unit])
             for square in SQUARES)

# Map of Square => [all squares that are in same unit]
PEERS = dict((s, set(s2 for u in UNITS[s] for s2 in u if s2 != s))
             for s in SQUARES)

#-----------------------------------------------------------------------------#

class SudokuSolver:
    """Sudoku puzzle solver"""
    def __init__(self, puzzle):
        """Create the solver object"""

        # Attributes
        self._puzzle = puzzle

    def __ParsePuzzle(self):
        """Given a string of 81 digits, return a dict of {cell:values}"""
        values = dict((square, '123456789') for square in SQUARES)
        for square, digit in zip(SQUARES, self._puzzle):
            if digit in '123456789' and not Assign(values, square, digit):
                return False
        return values

    def __Search(self, vmap):
        """Using depth-first search and propagation, try all possible values."""
        # Check if failed earlier
        if vmap is False:
            return False

        # Check if its been solved
        if All(len(vmap[s]) == 1 for s in SQUARES):
            return vmap

        # Choose the unfilled square s with the fewest possibilities
        _, square = min((len(vmap[square]), square)
                        for square in SQUARES
                        if len(vmap[square]) > 1)
        return Some(self.__Search(Assign(vmap.copy(), square, digit))
                    for digit in vmap[square])

    def GetValue(self, idx):
        """Get the value for a given index in the puzzle if it exists
        @param idx: int
        @return: string or None

        """
        sol = self.GetSolution()
        if sol:
            return sol[idx]
        return sol

    def GetSolution(self):
        """Get the ordered list of the puzzles solution
        @return: list or None

        """
        result = self.__Search(self.__ParsePuzzle())
        if result:
            return [result[key] for key in sorted(result.keys())]
        else:
            return None

    def SetPuzzle(self, puzzle):
        """Set the puzzle that this solver owns
        @param puzzle: string

        """
        self._puzzle = puzzle

#-----------------------------------------------------------------------------#

def Assign(values, square, digit):
    """Eliminate all the other values (except d) from values[s] and propagate.
    @param values: dict ('A1' => '12345')
    @param square: square to check
    @param digit: digit t

    """
    if All(Eliminate(values, square, digit2)
           for digit2 in values[square]
           if digit2 != digit):
        return values
    else:
        return False

def Eliminate(values, square, digit):
    """Eliminate d from values[s]; propagate when values or places <= 2"""
    # Check if already eliminated
    if digit not in values[square]:
        return values

    values[square] = values[square].replace(digit, '')
    if len(values[square]) == 0:
        # Contradiction: removed last value
        return False
    elif len(values[square]) == 1:
        # If there is only one value (digit2) left in a square
        # then remove it from its peers
        digit2 = values[square]
        if not All(Eliminate(values, square2, digit2)
                   for square2 in PEERS[square]):
            return False

    # Check the places where the digit appears in the units of the square
    for unit in UNITS[square]:
        dplaces = [square for square in unit if digit in values[square]]
        if len(dplaces) == 0:
            return False
        elif len(dplaces) == 1:
            # A digit can only be in one place in a unit so assign it there
            if not Assign(values, dplaces[0], digit):
                return False
    return values

def All(seq):
    """Are all the values in the sequence are true
    @note: for python < 2.5 compatibility

    """
    for val in seq:
        if not val:
            return False
    return True

def Some(seq):
    """Return whether some of the values are true or not"""
    for val in seq:
        if val:
            return val
    return False
