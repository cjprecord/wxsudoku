###############################################################################
# Name: puzzledlg.py                                                          #
# Purpose: UI for Loading/Saving and Managing saved puzzles                   #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
Puzzle Dialog

@summary: Dialog for Loading/Saving/Managing puzzle files
"""

__author__ = "Cody Precord <cprecord@editra.org>"
__revision__ = "$Revision$"
__scid__ = "$Id$"

#-----------------------------------------------------------------------------#
# Imports
import os
import wx

# Local Imports
import sudoku_cmn
import puzzle
from Icons import getMinusBitmap

#-----------------------------------------------------------------------------#
# Globals

PD_OPEN = 0     # Open dialog style flag
PD_SAVE = 1     # Save dialog style flag

# Id's
ID_SAVE_ENTRY = wx.NewId()

# Aliases
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#

class PuzzleDialog(wx.Dialog):
    """Dialog for opening, saving, and managing puzzles"""
    def __init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString,
                 path=None, diff=puzzle.DIFFICULTY_NORMAL,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=PD_OPEN, name="PuzzleDialog"):
        """Create the dialog
        @keyword path: Path to list files from / save to
        @keyword diff: Default difficulty to open/save to

        """
        wx.Dialog.__init__(self, parent, id, title, pos, size, 
                           wx.DEFAULT_DIALOG_STYLE, name)

        # Attributes
        self._path = path       # Path to saved files
        self._diff = diff       # Selected difficulty
        self._games = dict()    # Saved Games mapping
        self._file = ''         # Hold the selected file
        self._style = style     # Type of dialog
        for folder in sudoku_cmn.DIFFICULTY_STRINGS:
            pth = os.path.join(self._path, folder) + os.sep
            if os.path.exists(pth):
                self._games[folder] = sorted(os.listdir(pth))
            else:
                self._games[folder] = list()

        idx = sudoku_cmn.DIFFICULTY_STRINGS[self._diff]
        self._list = wx.ListBox(self, choices=self._games[idx],
                                style=wx.LB_SINGLE|wx.NO_BORDER)
        self._list.SetMinSize((350, 200))

        # Setup
        self.__DoLayout()
        self.SetInitialSize()
        self.CenterOnParent()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        if self._style == PD_OPEN:
            self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_OPEN)
            self.Bind(wx.EVT_CHOICE, self.OnChoice)
        else:
            self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_SAVE)
            self.Bind(wx.EVT_LISTBOX,
                      lambda evt: self.FindWindowById(ID_SAVE_ENTRY).\
                                       SetValue(evt.GetString()))
        self.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI, id=wx.ID_DELETE)

    def __DoLayout(self):
        """Layout the dialog"""
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add((5, 5), 0)

        # Setup the top section
        tsizer = wx.BoxSizer(wx.HORIZONTAL)
        if self._style == PD_OPEN:
            folder = wx.Choice(self, wx.ID_ANY, choices=[_("Easy"), _("Normal"),
                                                         _("Hard"), _("Evil")])
            folder.SetSelection(self._diff)
            tsizer.AddMany([((10, 10), 0),
                            (wx.StaticText(self, label=_("Difficulty") + u":"),
                             0, wx.ALIGN_CENTER), ((5, 5), 0),
                            (folder, 1, wx.EXPAND), ((10, 10), 0)])
        else:
            name = wx.TextCtrl(self, ID_SAVE_ENTRY, style=wx.TE_LEFT)
            tsizer.AddMany([((10, 10), 0),
                            (wx.StaticText(self, label=_("Save As") + u":"),
                             0, wx.ALIGN_CENTER), ((5, 5), 0),
                            (name, 1, wx.EXPAND), ((10, 10), 0)])

        # Setup the bottom section
        if self._style == PD_OPEN:
            btn2 = wx.Button(self, wx.ID_OPEN, _("Open"))
        else:
            btn2 = wx.Button(self, wx.ID_SAVE, _("Save"))
        btn2.SetDefault()

        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        delete_b = wx.BitmapButton(self, wx.ID_DELETE, getMinusBitmap())
        delete_b.SetToolTipString(_("Delete selected game file"))
        bsizer.AddMany([((8, 8), 0), (delete_b, 0, wx.ALIGN_LEFT)])
        bsizer.AddStretchSpacer()
        bsizer.AddMany([(wx.Button(self, wx.ID_CANCEL, _("Cancel")),
                         0, wx.ALIGN_RIGHT), ((8, 8), 0),
                        (btn2, 0, wx.ALIGN_RIGHT), ((8, 8), 0)])

        vsizer.AddMany([(tsizer, 0, wx.EXPAND), ((5, 5), 0),
                        (self._list, 1, wx.EXPAND), ((5, 5), 0),
                        (bsizer, 0, wx.EXPAND|wx.ALIGN_RIGHT), ((10, 10), 0)])

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddMany([((5, 5), 0), (vsizer, 0, wx.EXPAND), ((5, 5), 0)])
        self.SetSizer(sizer)

    def OnButton(self, evt):
        """Handle button clicks"""
        e_id = evt.GetId()
        if e_id == wx.ID_OPEN:
            fname = self._list.GetStringSelection()
            self._file = os.path.join(self._path,
                                      sudoku_cmn.DIFFICULTY_STRINGS[self._diff],
                                      fname)
        elif e_id == wx.ID_SAVE:
            fname = self.FindWindowById(ID_SAVE_ENTRY).GetValue()
            self._file = os.path.join(self._path,
                                      sudoku_cmn.DIFFICULTY_STRINGS[self._diff],
                                      fname)
            
        elif e_id == wx.ID_CANCEL:
            self._file = ''
        elif e_id == wx.ID_DELETE:
            fname = self._list.GetStringSelection()
            if fname:
                path = os.path.join(self._path,
                                    sudoku_cmn.DIFFICULTY_STRINGS[self._diff],
                                    fname)
                if os.path.exists(path):
                    try:
                        os.remove(path)
                        self._list.Delete(self._list.GetSelection())
                    except Exception, msg:
                        sudoku_cmn.DebugP("[sudoku][err] %s" % msg)
        else:
            evt.Skip()

        if e_id != wx.ID_DELETE:
            self.EndModal(e_id)

    def OnChoice(self, evt):
        """Update the listbox with the files in the selected difficulty
        @param evt: wx.CommandEvent

        """
        self._diff = evt.GetSelection()
        idx = sudoku_cmn.DIFFICULTY_STRINGS[self._diff]
        self._list.SetItems(self._games[idx])

    def OnUpdateUI(self, evt):
        """Handle UpdateUI events for the open/save buttons
        @param evt: UpdateUIEvent

        """
        e_id = evt.GetId()
        if e_id in (wx.ID_OPEN, wx.ID_DELETE):
            evt.Enable(len(self._list.GetStringSelection()))
        elif e_id == wx.ID_SAVE:
            evt.Enable(len(self.FindWindowById(ID_SAVE_ENTRY).GetValue()))
        else:
            evt.Skip()

    def GetPuzzleDifficulty(self):
        """Get the difficulty of the selected puzzle
        @return: int

        """
        return self._diff

    def GetPuzzleFile(self):
        """Get the selected puzzle file
        @return: string (may be empty)

        """
        return self._file
