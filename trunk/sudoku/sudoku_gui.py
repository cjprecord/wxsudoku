###############################################################################
# Name: sudoku_gui.py                                                         #
# Purpose: The main gui objects used by the game                              #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

""""
Creates the graphical user interface for the Sukoku game

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__revision__ = "$Revision$"
__scid__ = "$Id$"

#-----------------------------------------------------------------------------#
# Imports
import os
import sys
import time
import webbrowser
import wx

# Local Imports
import proj_info
import puzzle
import sudoku_cmn
import puzzledlg
import Icons
from solver import SudokuSolver

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class SudokuGameEvent(wx.PyCommandEvent):
    """Class for events generated during game play"""
    def __init__(self, eventType, id):
        wx.PyCommandEvent.__init__(self, eventType, id)

# Event Types
suEVT_NEW_BOARD = wx.NewEventType()
EVT_NEW_BOARD = wx.PyEventBinder(suEVT_NEW_BOARD, 1)

suEVT_MOVE_MADE = wx.NewEventType()
EVT_MOVE_MADE = wx.PyEventBinder(suEVT_MOVE_MADE, 1)

suEVT_GAME_COMPLETE = wx.NewEventType()
EVT_GAME_COMPLETE = wx.PyEventBinder(suEVT_GAME_COMPLETE, 1)

#-----------------------------------------------------------------------------#

class SudokuFrame(wx.Frame):
    """The games main window"""
    def __init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE, name="SudokuFrame"):
        """Create the frame"""
        style &= ~wx.RESIZE_BORDER 
        wx.Frame.__init__(self, parent, id, title, pos, size, style, name)

        # Attributes
        self.canvas = SudokuCanvas(self)
        self._timer = wx.Timer(self)
        self._time = 0      # Elapsed game time in seconds
        self._difficulty = puzzle.DIFFICULTY_NORMAL
        self._hints = 0     # Number of hints given
        self._gamefile = None

        # Layout
        self.__DoLayout()
        puzzles = puzzle.ThePuzzleManager.GetPuzzleData()
        sudoku_cmn.DebugP("[sudoku][info] Loaded %d Puzzles" % \
                          sum(len(val) for val in puzzles.values()))

        # Setup
        self.SetIcon(wx.IconFromBitmap(Icons.getSudokuBitmap()))
        self.NewGame()

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_MENU, lambda evt: self.NewGame(), id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, lambda evt: self.ClearGame(), id=wx.ID_CLEAR)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnSave, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, lambda evt: self.GiveHint(), id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU,
                  lambda evt: webbrowser.open("mailto:%s" % proj_info.CONTACT_MAIL),
                  id=sudoku_cmn.ID_FEEDBACK)
        self.Bind(wx.EVT_MENU,
                  lambda evt: webbrowser.open(proj_info.HOME_PAGE), id=wx.ID_HOME)
        self.Bind(wx.EVT_MENU, lambda evt: AboutBox(), id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU,
                  lambda evt: self.SetDifficulty(sudoku_cmn.DIFF_MAP[sudoku_cmn.ID_EASY]),
                  id=sudoku_cmn.ID_EASY)
        self.Bind(wx.EVT_MENU,
                  lambda evt: self.SetDifficulty(sudoku_cmn.DIFF_MAP[sudoku_cmn.ID_NORMAL]),
                  id=sudoku_cmn.ID_NORMAL)
        self.Bind(wx.EVT_MENU,
                  lambda evt: self.SetDifficulty(sudoku_cmn.DIFF_MAP[sudoku_cmn.ID_HARD]),
                  id=sudoku_cmn.ID_HARD)
        self.Bind(wx.EVT_MENU,
                  lambda evt: self.SetDifficulty(sudoku_cmn.DIFF_MAP[sudoku_cmn.ID_EVIL]),
                  id=sudoku_cmn.ID_EVIL)

        for menu_id in (sudoku_cmn.ID_EASY, sudoku_cmn.ID_NORMAL,
                        sudoku_cmn.ID_HARD, sudoku_cmn.ID_EVIL, wx.ID_HELP):
            self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateDiffUI, id=menu_id)

        # Game Event Handlers
        self.Bind(EVT_NEW_BOARD, lambda evt: self.UpdateMoves())
        self.Bind(EVT_MOVE_MADE, self.OnMove)
        self.Bind(EVT_GAME_COMPLETE, self.OnPuzzleSoved)

    def __del__(self):
        if self._timer.IsRunning():
            self._timer.Stop()

    def __DoLayout(self):
        """Layout the window"""
        # Setup Menus
        self.__SetupMenuBar()

        # Setup Toolbar
        toolbar = wx.ToolBar(self)
        toolbar.SetToolBitmapSize((32, 32))
        toolbar.AddSimpleTool(wx.ID_NEW, Icons.getNewBitmap(),
                              _("New Puzzle"), _("Start a new puzzle"))
        toolbar.AddSimpleTool(wx.ID_OPEN, Icons.getOpenBitmap(),
                              _("Open Puzzle"), _("Open a saved puzzle"))
        toolbar.AddSimpleTool(wx.ID_SAVE, Icons.getSaveBitmap(),
                              _("Save Puzzle"), _("Save the puzzle"))
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(wx.ID_CLEAR, Icons.getClearBitmap(),
                              _("Clear Puzzle"),
                              _("Restart the current puzzle"))
        toolbar.AddSeparator()
        toolbar.AddSimpleTool(wx.ID_HELP, Icons.getHelpBitmap(),
                              _("Hints"), _("Get a hint"))
        toolbar.Realize()
        self.SetToolBar(toolbar)

        # Setup Status Bar
        self.CreateStatusBar(2)
        twidth = self.GetStatusBar().GetTextExtent("0000:00:00")[0] + 15
        self.SetStatusWidths([-1, twidth])

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetInitialSize()

    def __SetupMenuBar(self):
        """Setup the menus"""
        menub = wx.MenuBar()

        # Puzzle Menu
        gamem = wx.Menu()
        gamem.Append(wx.ID_NEW, _("&New Puzzle") + "\tCtrl+N",
                     _("Start a new puzzle"))
        gamem.Append(wx.ID_CLEAR, _("&Clear Puzzle") + "\tCtrl+R",
                     _("Restart the current puzzle"))
        gamem.AppendSeparator()
        gamem.Append(wx.ID_OPEN, _("&Open Puzzle") + u"...\tCtrl+O",
                     _("Load a saved puzzle"))
        gamem.AppendSeparator()
        gamem.Append(wx.ID_SAVE, _("&Save") + "\tCtrl+S",
                     _("Save the current puzzle"))
        gamem.Append(wx.ID_SAVEAS, _("Save &As") + u"...\tCtrl+Shift+S",
                     _("Save As"))
        gamem.AppendSeparator()
        gamem.Append(wx.ID_EXIT, _("&Quit") + "\tCtrl+Q",
                     _("Quit %s") % proj_info.PROG_NAME)
        menub.Append(gamem, _("&Puzzle"))

        # Difficulty Menu
        diffm = wx.Menu()
        diffm.Append(sudoku_cmn.ID_EASY, _("Easy"),
                     _("Change to easy puzzles"),
                     wx.ITEM_CHECK)
        diffm.Append(sudoku_cmn.ID_NORMAL, _("Normal"),
                     _("Change to normal puzzles"),
                     wx.ITEM_CHECK)
        diffm.Append(sudoku_cmn.ID_HARD, _("Hard"),
                     _("Change to hard puzzles"),
                     wx.ITEM_CHECK)
        diffm.Append(sudoku_cmn.ID_EVIL, _("Evil"),
                     _("Change to evil puzzles"),
                     wx.ITEM_CHECK)
        menub.Append(diffm, _("Difficulty"))

        # Help Menu
        helpm = wx.Menu()
        helpm.Append(wx.ID_ABOUT, _("&About") + u"...", _("About") + u"...")
        helpm.Append(wx.ID_HELP, _("&Get Hint") + u"\tCtrl+G",
                     _("Get hint for selected square"))
        helpm.AppendSeparator()
        helpm.Append(wx.ID_HOME, _("Visit Project Homepage"),
                     _("Open webrowser to %s") % proj_info.HOME_PAGE)
        helpm.Append(sudoku_cmn.ID_FEEDBACK, _("Feedback"),
                     _("Send an email to the author"))
        menub.Append(helpm, _("&Help"))

        if wx.Platform == '__WXMAC__':
            wx.GetApp().SetMacHelpMenuTitleName(_("&Help"))

        self.SetMenuBar(menub)

    #---- End Private Methods ----#

    #---- Public Methods ----#

    def ClearGame(self):
        """Clear the current board back to its starting state"""
        self.StopGameTimer()
        self.canvas.ResetBoard()

    def GetTimeString(self):
        """Get the formated time string for the current puzzle"""
        secs = self._time
        hours = 0
        mins = 0
        if secs > 3600:
            hours = secs / 3600
            secs = secs - (hours * 3600)

        if secs > 60:
            mins = secs / 60
            secs = secs - (mins * 60)

        hours = str(hours).zfill(2)
        mins = str(mins).zfill(2)
        secs = str(secs).zfill(2)

        return "%s:%s:%s" % (hours, mins, secs)

    def GiveHint(self):
        """Try to solve the current puzzle and give a hint"""
        selection = self.canvas.GetSelection()
        if selection is None:
            return

        # Search for a hint
        board = self.canvas.GetPuzzleBoard()
        solver = SudokuSolver(str(board))
        solution = solver.GetValue(selection)
        if solution is not None:
            if solution != self.canvas.GetCellValue(selection):
                self._hints += 1
                self.canvas.MakeMove( selection, solution)
        else:
            wx.Bell()
            # TODO Show why no hints can be given

    def LoadPuzzle(self, board):
        """Load the given game board
        @param board: string

        """
        self.StopGameTimer()
        self._hints = 0
        self.canvas.InitializeBoard(board)
        if self._gamefile:
            name = os.path.split(self._gamefile)[-1]
            self.SetTitle(proj_info.PROG_NAME + " - " + name)

    def NewGame(self):
        """Load a new random game board"""
        self.StopGameTimer()
        pid, pstr = puzzle.ThePuzzleManager.GetNewPuzzle(self._difficulty)
        self.canvas.InitializeBoard(pstr)
        self._hints = 0
        self._gamefile = None
        self.SetTitle(proj_info.PROG_NAME + " - " + _("Puzzle #%d") % pid)

    def OnClose(self, evt):
        """Handle when the dialog is closing"""
        wx.GetApp().Set('WINPOS', self.GetPositionTuple())
        wx.GetApp().Save()
        evt.Skip()

    def OnMove(self, evt):
        """Handle when a move is made in the canvas"""
        if not self._timer.IsRunning():
            self._timer.Start(1000)
        self.UpdateMoves()

    def OnOpen(self, evt):
        """Open a saved puzzle"""
        dlg = puzzledlg.PuzzleDialog(self, title=_("Open Puzzle"),
                                     path=wx.GetApp().GetSaveDir(),
                                     diff=self._difficulty,
                                     style=puzzledlg.PD_OPEN)
        if dlg.ShowModal() == wx.ID_OPEN:
            fname = dlg.GetPuzzleFile()
            difficulty = dlg.GetPuzzleDifficulty()
            board = sudoku_cmn.ReadPuzzleFile(fname)
            self._difficulty = difficulty
            self._gamefile = fname
            self.LoadPuzzle(board.get('initial', ''))
            for idx, val in enumerate(board.get('current', '')):
                if val != '.':
                    self.canvas.SetValue(idx, val)
            self.canvas.SetMoves(board.get('moves', 0))
            self._hints = board.get('hints', 0)
            self._time = board.get('time', 0)
        dlg.Destroy()

    def OnPuzzleSoved(self, evt):
        """Handle when the puzzle has been completed"""
        msgmap = dict(moves=self.canvas.GetMoves(),
                      time=self.GetTimeString(),
                      hints=self._hints)
        self.StopGameTimer()
        wx.MessageBox((_("You solved the puzzle!\n") + \
                      _("Moves: %(moves)d\n") + 
                      _("Total Time: %(time)s\n") + \
                      _("Hints Used: %(hints)d")) % \
                      msgmap, _("Congradulations!"))

    def OnSave(self, evt):
        """Save a game"""
        e_id = evt.GetId()
        if self._gamefile is None or e_id == wx.ID_SAVEAS:
            dlg = puzzledlg.PuzzleDialog(self, title=_("Save Puzzle"),
                                         path=wx.GetApp().GetSaveDir(),
                                         diff=self._difficulty,
                                         style=puzzledlg.PD_SAVE)

            if dlg.ShowModal() == wx.ID_SAVE:
                self._gamefile = dlg.GetPuzzleFile()
                state = dict(initial=self.canvas.GetInitialState(),
                             current=str(self.canvas.GetPuzzleBoard()),
                             moves=self.canvas.GetMoves(),
                             hints=self._hints,
                             time=self._time)
                             
                if not sudoku_cmn.WritePuzzleFile(self._gamefile, state):
                    wx.MessageBox(_("Failed to save %s") % self._gamefile,
                                  _("Save Error"))
            dlg.Destroy()
        elif e_id == wx.ID_SAVE:
            state = dict(initial=self.canvas.GetInitialState(),
                         current=str(self.canvas.GetPuzzleBoard()),
                         moves=self.canvas.GetMoves(),
                         hints=self._hints,
                         time=self._time)

            sudoku_cmn.WritePuzzleFile(self._gamefile, state)
        else:
            evt.Skip()

    def OnTimer(self, evt):
        """Update the game clock"""
        self._time += 1
        self.SetStatusText(self.GetTimeString(), 1)

    def OnUpdateDiffUI(self, evt):
        """Update the difficulty menu"""
        if not self.IsActive():
            return

        e_id = evt.GetId()
        # Slow the update interval to reduce overhead
        #evt.SetUpdateInterval(120)
        if e_id in (sudoku_cmn.ID_EASY, sudoku_cmn.ID_NORMAL,
                    sudoku_cmn.ID_HARD, sudoku_cmn.ID_EVIL):
            evt.Check(sudoku_cmn.DIFF_MAP[e_id] == self._difficulty)
            evt.Enable(len(puzzle.ThePuzzleManager.GetPuzzles(sudoku_cmn.DIFF_MAP[e_id])))
        elif e_id == wx.ID_HELP:
            evt.Enable(self.canvas.GetSelection() is not None and \
                       self._difficulty < puzzle.DIFFICULTY_HARD)
        else:
            evt.Skip()

    def SetDifficulty(self, difficulty):
        """Set the difficulty of the current puzzle
        @param difficulty: int

        """
        if difficulty in sudoku_cmn.VALID_DIFFICULTIES:
            self._difficulty = difficulty
            self.NewGame()
        else:
            pass

    def StartGame(self):
        """Start the game clock"""
        self.StopGameTimer()
        self._timer.Start(1000)

    def StopGameTimer(self):
        """Stop the game timer and reset the stats"""
        if self._timer.IsRunning():
            self._timer.Stop()
            self._time = 0
        self.SetStatusText(self.GetTimeString(), 1)
        self.UpdateMoves()

    def UpdateMoves(self):
        """Update the moves status field"""
        self.SetStatusText(_("Moves: %d") % self.canvas.GetMoves())

#-----------------------------------------------------------------------------#

class SudokuCanvas(wx.PyControl):
    """The canvas that the game board is drawn on"""
    NUM_KEYS = [ wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3,
                 wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, wx.WXK_NUMPAD6,
                 wx.WXK_NUMPAD7, wx.WXK_NUMPAD8, wx.WXK_NUMPAD9,
                 ord('1'), ord('2'), ord('3'), ord('4'), ord('5'),
                 ord('6'), ord('7'), ord('8'), ord('9') ]

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.TAB_TRAVERSAL|wx.NO_BORDER, name="GameCanvas"):
        """Initialize the canvas
        @keyword board: Dimension of the game board (rows, columns)

        """
        wx.PyControl.__init__(self, parent, id, pos, size,
                              style, wx.DefaultValidator, name)

        # Attributes
        self._cellSize = 50      # Default Cell Size
        self._board = None       # Current Game Board
        self._cells = None       # Board cells
        self._active = None      # Currently active cell
        self._moves = 0          # Number of moves made

        # Setup
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

        # Event Handlers
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt: evt)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseClick)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda evt: wx.SetCursor(wx.NullCursor))

    #---- Private Methods ----#

    def __CalculateCords(self):
        """Calculate the coordinates of the grids cells"""
        csize = self._cellSize
        rec_list = list()
        for row in xrange(9):
            for column in xrange(9):
                rec_list.append((column * csize, row * csize, csize, csize))
        return rec_list

    @staticmethod
    def __DrawOneCell(gc, cell):
        """Draw one cell
        @param gc: GCDC to draw in
        @param cell: L{puzzle.CellData} object

        """
        # Store Current Pen/Brush
        brush = gc.GetBrush()
        pen = gc.GetPen()

        # Draw the Cell
        if not cell.CanEdit():
            color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
        elif cell.active:
            color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        else:
            color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE)

        if cell.CanEdit():
            ngc = gc.GetGraphicsContext()
            rgb = ngc.CreateRadialGradientBrush(cell.x + (cell.w/2.0),
                                                cell.y + (cell.h/2.0),
                                                cell.x + (cell.w/2.0),
                                                cell.y + (cell.h/2.0),
                                                cell.w, wx.WHITE, color)
            ngc.SetBrush(rgb)
        else:
            gc.SetBrush(wx.Brush(color))

        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(cell.x, cell.y, cell.w, cell.h)

        # Draw Cell Value
        gc.DrawLabel(cell.val, cell.GetRect(), wx.ALIGN_CENTER)

        # Restore the pen and brush
        gc.SetBrush(brush)
        gc.SetPen(pen)

    #---- End Private Methods ----#

    #---- Public Methods ----#

    def CheckComplete(self):
        """Check if the board is completed or not. If the board has been
        solved this method will post a EVT_GAME_COMPLETE event, if it is
        incomplete it will do nothing.

        """
        if self._cells.IsComplete():
            self._cells.ActivateCell(None)
            self.Refresh()
            wx.PostEvent(self.GetParent(),
                         SudokuGameEvent(suEVT_GAME_COMPLETE, self.GetId()))
            self.Disable()

    def DoGetBestSize(self):
        """Get the best size of the canvas
        @return: size
        @note: overridden from PyControl

        """
        return wx.Size(self._cellSize * 9, self._cellSize * 9)

    def GetCellFromPosition(self, pos):
        """Get the cell that the given position is found in or None
        if the pos is out of range.
        @param pos: (x, y)
        @return: Cell index or None

        """
        for idx, cell in enumerate(self._cells):
            if pos[0] >= cell.x and pos[0] <= cell.x + cell.w and \
               pos[1] >= cell.y and pos[1] <= cell.y + cell.h:
                return idx
        return None

    def GetCellValue(self, cell):
        """Get the value of the given cell
        @param cell: cell index (int)

        """
        return self._cells[cell].GetValue()

    def GetInitialState(self):
        """Get the string that represents the intial state of the game board
        when it was first loaded.

        """
        return self._board

    def GetPuzzleBoard(self):
        """Get the L{puzzle.PuzzleBoard} of L{puzzle.CellData} which represents
        the current state of the puzzle.

        """
        return self._cells

    def GetMoves(self):
        """Get how many moves have been made in the current game
        @return: int

        """
        return self._moves

    def GetNextDown(self):
        """Get the next editable cell below the current active cell
        @return: int

        """
        if self._active is not None:
            column = self._active - ((self._active / 9) * 9)
            column = max(0, column)
            if column > 8:
                column = max(0, (column / 9) - 1)

            for cell in range(self._active + 9, 81, 9):
                if self._cells[cell].CanEdit():
                    return cell
            for cell in range(column, self._active, 9):
                if self._cells[cell].CanEdit():
                    return cell
        return None

    def GetNextLeft(self):
        """Get the next editable cell to the left of the current
        @return: int

        """
        if self._active is not None:
            for cell in range(self._active - 1, -1, -1):
                if self._cells[cell].CanEdit():
                    return cell
            for cell in range(80, self._active, -1):
                if self._cells[cell].CanEdit():
                    return cell
        return None

    def GetNextRight(self):
        """Get the next editable cell to the right of the current
        @return: int

        """
        if self._active is not None:
            for cell in range(self._active+1, 81):
                if self._cells[cell].CanEdit():
                    return cell
            for cell in range(0, self._active):
                if self._cells[cell].CanEdit():
                    return cell
        return None

    def GetNextUp(self):
        """Get the next editable cell above the current active cell
        @return: int

        """
        if self._active is not None:
            column = self._active - ((self._active / 9) * 9)
            column = max(0, column)
            for cell in range(self._active - 9, -1, -9):
                if self._cells[cell].CanEdit():
                    return cell
            for cell in range(range(column, 81, 9)[-1], self._active, -9):
                if self._cells[cell].CanEdit():
                    return cell
        return None

    def GetSelection(self):
        """Get the index of the currently selected cell
        @return: int or None

        """
        return self._active

    def InitializeBoard(self, state):
        """Initialize the game board with the initial values. The board
        is initialized with a string that specifies the state of each cell
        on the board. The string is formatted with '.' to specify an empty
        cell and with a number to specify a cell that has a value.
        @param state: string

        """
        self.Enable()
        cords = self.__CalculateCords()
        cell_list = puzzle.PuzzleBoard()

        self._board = state
        for cell, val in enumerate(state):
            cord = cords[cell]
            if not val.isdigit():
                val = ''
            readonly = len(val) > 0
            cell_list.append(puzzle.CellData(cord[:2], cord[2:], readonly, val))

        self._cells = cell_list
        self._moves = 0
        wx.PostEvent(self.GetParent(),
                     SudokuGameEvent(suEVT_NEW_BOARD, self.GetId()))
        self.Refresh()

    def MakeMove(self, cell, val):
        """Make a move
        @param cell: cell index
        @param val: (str) value

        """
        if self.GetCellValue(cell) != val:
            self._cells[cell].SetValue(val)
            self._moves += 1
            self.Refresh()
            wx.PostEvent(self.GetParent(),
                         SudokuGameEvent(suEVT_MOVE_MADE, self.GetId()))
            self.CheckComplete()

    #---- Event Handlers ----#

    def OnKeyUp(self, evt):
        """Handle the key up events for entering numbers
        @param evt: wx.KeyEvent

        """
        key_code =  evt.GetKeyCode()
        if self._active is not None and \
           not evt.HasModifiers() and \
           key_code in SudokuCanvas.NUM_KEYS:
            self.MakeMove(self._active, unichr(evt.GetUniChar()))
        elif self._active is not None and \
             key_code in (wx.WXK_DELETE, wx.WXK_BACK):
            self._cells[self._active].SetValue('')
            self.Refresh()
        elif self._active is not None and \
             key_code in [wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN]:

            if key_code == wx.WXK_LEFT:
                self._active = self.GetNextLeft()
            elif key_code == wx.WXK_RIGHT:
                self._active = self.GetNextRight()
            elif key_code == wx.WXK_UP:
                self._active = self.GetNextUp()
            elif key_code == wx.WXK_DOWN:
                self._active = self.GetNextDown()
            else:
                return

            self._cells.ActivateCell(self._active)
            self.Refresh(False)
        else:
            evt.Skip()

    def OnMouseClick(self, evt):
        """Activate/DeActivate the cell that is clicked on
        @param evt: wx.EVT_LEFT_UP

        """
        pos = evt.GetPositionTuple()
        cell = self.GetCellFromPosition(pos)
        self._active = cell
        if cell is not None and not self._cells[cell].CanEdit():
            self._active = None
        self._cells.ActivateCell(cell)
        self.Refresh()
        evt.Skip()

    def OnPaint(self, evt):
        """Draw the game board"""
        dc = wx.BufferedPaintDC(self)
        gc = wx.GCDC(dc)

        # Draw the Cells
        for cell in self._cells:
            self.__DrawOneCell(gc, cell)

        # Draw the Borders
        # Solid around the edges and between the subfields
        # Dashed inbetween
        blockpen = wx.Pen(wx.BLACK, 2, wx.SOLID)
        cellpen = wx.Pen(wx.BLACK, 1, wx.SOLID)
        lines = list()
        pens = list()

        # Calculate the Horizontal Borders
        for hline in range(10):
            if hline != 0:
                y = hline * self._cellSize
            else:
                y = hline
            lines.append((0, y, self._cellSize * 9, y))
            if not hline % 3:
                pens.append(blockpen)
            else:
                pens.append(cellpen)

        # Calculate the Vertical Borders
        for vline in range(10):
            if vline != 0:
                x = vline * self._cellSize
            else:
                x = vline
            lines.append((x, 0, x, self._cellSize * 9))
            if not vline % 3:
                pens.append(blockpen)
            else:
                pens.append(cellpen)

        gc.DrawLineList(lines, pens)

    #---- End Event Handlers ----#

    def ResetBoard(self):
        """Reset the current game board"""
        self.InitializeBoard(self._board)

    def SetCellSize(self, pixels):
        """Set the size of the individual game cells in pixels
        @param pixels: int

        """
        self._cellSize = pixels 

    def SetMoves(self, moves):
        """Set the amount of moves that have been made
        @param moves: int

        """
        self._moves = max(0, moves)

    def SetValue(self, cell, value):
        """Set the value of the given cell
        @param cell: int (0 >= cell <= 80)
        @param value: string digit or empty string

        """
        self._cells[cell].SetValue(value)
        self.Refresh(False, self._cells[cell].GetRect())

#-----------------------------------------------------------------------------#
# Helper Functions

def AboutBox():
    """Show the programs information"""
    info = wx.AboutDialogInfo()
    year = time.localtime()
    desc = [_("wxSudoku"),
            _("Written in 100%% Python."),
            _("Homepage") + ": " + proj_info.HOME_PAGE + "\n",
            _("Platform Info") + ": (%s,%s)",
            _("License: wxWindows (see COPYING.txt for full license)")]
    desc = "\n".join(desc)
    py_version = sys.platform + ", python " + sys.version.split()[0]
    platform = list(wx.PlatformInfo[1:])
    platform[0] += (" " + wx.VERSION_STRING)
    wx_info = ", ".join(platform)
    info.SetCopyright(_("Copyright") + "(C) %d Cody Precord" % year[0])
    info.SetName(proj_info.PROG_NAME)
    info.SetDescription(desc % (py_version, wx_info))
    info.SetVersion(proj_info.VERSION)
    wx.AboutBox(info)
