#!/usr/bin/env python
###############################################################################
# Name: Sudoku.py                                                             #
# Purpose: App Implementation                                                 #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Sudoku application object and main

"""

__author__ = "Cody Precord <cprecord@editra.org>"
__revision__ = "$Revision$"
__scid__ = "$Id$"

#-----------------------------------------------------------------------------#
# Imports
import locale
import wx

# Local imports
import proj_info
import sudoku_cfg
import sudoku_gui

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class Sudoku(wx.App, sudoku_cfg.SudokuConfig):
    """The Sudoku games application object"""
    def __init__(self, *args, **kargs):
        wx.App.__init__(self, *args, **kargs)
        sudoku_cfg.SudokuConfig.__init__(self)

        # Attributes

        # Setup Localizations
        locale.setlocale(locale.LC_ALL, '')

    def OnInit(self):
        """Setup"""
        self.SetAppName(proj_info.PROG_NAME)
        return True

#-----------------------------------------------------------------------------#

def Main():
    """Run the applications MainLoop"""
    app = Sudoku(False)
    frame = sudoku_gui.SudokuFrame(None, title=_("wxSudoku"),
                                   pos=app.Get('WINPOS', wx.DefaultPosition))
    frame.Show()
    app.MainLoop()

#-----------------------------------------------------------------------------#

if __name__ == '__main__':
    Main()
