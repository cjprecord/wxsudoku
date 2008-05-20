###############################################################################
# Name: sudoku_cfg.py                                                         #
# Purpose: Configuration Class                                                #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

""""
Configuration and Persistance helper classes

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
import sudoku_cmn

#-----------------------------------------------------------------------------#

class SudokuConfig(dict):
    """Configuration managment and data storage class"""
    def __init__(self):
        """Initialize the SudokuConfig instance"""
        dict.__init__(self)

        # Attributes
        self.cfgdir = wx.StandardPaths_Get().GetUserDataDir()
        self.instdir = wx.StandardPaths_Get().GetExecutablePath()
        self.imgdir = os.path.join(self.instdir, 'pixmaps')
        self.savedir = os.path.join(self.cfgdir, 'SavedPuzzles') + os.sep

        # Setup Config Directories
        if not os.path.exists(self.cfgdir):
            os.mkdir(self.cfgdir)

        if not os.path.exists(self.savedir):
            os.mkdir(self.savedir)

        for sdir in [os.path.join(self.savedir, ddir)
                     for ddir in sudoku_cmn.DIFFICULTY_STRINGS]:
            if not os.path.exists(sdir):
                os.mkdir(sdir)

        # Load any saved preferences
        self.Load()

    def Get(self, key, default=None):
        """Get a setting value
        @param key: string
        @keyword default: 

        """
        return self.get(key, default)

    def GetIconDir(self):
        """Get the icon resource directory"""
        return self.imgdir

    def GetInstallDir(self):
        """Get the installation directory"""
        return self.instdir

    def GetSaveDir(self):
        """Get the path of where the saved games are"""
        return self.savedir

    def Load(self):
        """Load the on disk configuration pickle"""
        path = os.path.join(self.cfgdir, 'sudoku.cfg')
        if os.path.exists(path):
            try:
                fhandle = open(path, 'rb')
                val = cPickle.load(fhandle)
                fhandle.close()
            except (IOError, SystemError, OSError,
                    cPickle.UnpicklingError, EOFError), msg:
                sudoku_cmn.DebugP("[sudoku][err] %s" % msg)
            else:
                self.update(val)

    def Save(self):
        """Save the prereferences out to disk
        @return: bool

        """
        try:
            fhandle = open(os.path.join(self.cfgdir, 'sudoku.cfg'), 'wb')
            cPickle.dump(self.copy(), fhandle, cPickle.HIGHEST_PROTOCOL)
            fhandle.close()
        except (IOError, cPickle.PickleError), msg:
            sudoku_cmn.DebugP("[sudoku][err] %s" % msg)
            return False
        else:
            return True

    def Set(self, key, value):
        """Set a preference value
        @param key: Preference identifier
        @param value: The value to save

        """
        self[key] = value
