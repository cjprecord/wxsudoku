#!/usr/bin/env python
###############################################################################
# Name: setup.py                                                              #
# Purpose: Setup/build script for wxSudoku                                    #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""
 wxSudoku Setup Script

 USAGE:

   1) Windows:
      - python setup.py py2exe

   2) MacOSX:
      - python setup.py py2app

   3) Boil an Egg
      - python setup.py bdist_egg

   4) Install as a python package
      - python setup.py install

"""
__author__ = "Cody Precord <cprecord@editra.org>"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#---- Imports ----#
import os
import sys
import glob
import sudoku.proj_info as info

#---- System Platform ----#
__platform__ = os.sys.platform

#---- Global Settings ----#
APP = ['sudoku/Sudoku.py']
AUTHOR = "Cody Precord"
AUTHOR_EMAIL = "cprecord@editra.org"
YEAR = 2008
DESCRIPTION = "Developer's Text Editor"
LONG_DESCRIPT = \
r"""
========
Overview
========
wxSudoku is a simple sudoku game

============
Dependancies
============
  * Python 2.4+
  * wxPython 2.8+ (Unicode build suggested)

"""

ICON = { 'Win' : "pixmaps/app/Sudoku.ico",
         'Mac' : "pixmaps/app/Sudoku.icns"
}
LICENSE = "wxWindows"
NAME = "wxSudoku"
URL = "http://wxsudoku.googlecode.com"
VERSION = info.VERSION
CLASSIFIERS = [
            'Development Status :: 3 - Alpha',
            'Environment :: MacOS X',
            'Environment :: Win32 (MS Windows)',
            'Environment :: X11 Applications :: GTK',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved',
            'Natural Language :: English',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            ]

# Py2App/Py2exe Data Files
DATA_FILES = [("pixmaps", ["pixmaps/app/Sudoku.png", "pixmaps/app/Sudoku.ico",
                           "pixmaps/app/Sudoku.icns"]),
              "puzzles.dat", "INSTALL", "README", "CHANGELOG",
              "COPYING"
             ]

# Py2Exe manifest
MANIFEST_TEMPLATE = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24
#---- End Global Settings ----#

#---- Setup Windows EXE ----#
if __platform__ == "win32" and 'py2exe' in sys.argv:
    from distutils.core import setup
    try:
        import py2exe
    except ImportError:
        print "\n!! You dont have py2exe installed. !!\n"
        exit()

    # put package on path for py2exe
    sys.path.append(os.path.abspath('sudoku/'))

    setup(
        name = NAME,
        version = VERSION,
        options = {"py2exe" : {"compressed" : 1,
                               "optimize" : 2,
                               "bundle_files" : 2}},
        windows = [{"script": "sudoku/Sudoku.py",
                    "icon_resources": [(0, ICON['Win'])],
                    "other_resources" : [(RT_MANIFEST, 1,
                                          MANIFEST_TEMPLATE % dict(prog=NAME))],
                  }],
        description=DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=AUTHOR,
        maintainer_email=AUTHOR_EMAIL,
        license=LICENSE,
        url=URL,
        data_files=DATA_FILES,
        )

#---- Setup MacOSX APP ----#
elif __platform__ == "darwin" and 'py2app' in sys.argv:
    # Check for setuptools and ask to download if it is not available
    from setuptools import setup

    PLIST = dict(CFBundleName=info.PROG_NAME,
             CFBundleIconFile='Sudoku.icns',
             CFBundleShortVersionString=info.VERSION,
             CFBundleGetInfoString=info.PROG_NAME + " " + info.VERSION,
             CFBundleExecutable=info.PROG_NAME,
             CFBundleIdentifier="org.editra.wxsudoku.%s" % info.PROG_NAME.title(),
             NSHumanReadableCopyright=u"Copyright %s %d" % (AUTHOR, YEAR)
             )

    PY2APP_OPTS = dict(iconfile=ICON['Mac'],
                       argv_emulation=True,
                       optimize=True,
                       plist=PLIST)

    setup(
        app=APP,
        version=VERSION,
        options=dict(py2app=PY2APP_OPTS),
        description=DESCRIPTION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=AUTHOR,
        maintainer_email=AUTHOR_EMAIL,
        license=LICENSE,
        url=URL,
        data_files=DATA_FILES,
        setup_requires=['py2app']
        )

#---- Other Platform(s)/Source module install ----#
else:
    # Force optimization
    if 'install' in sys.argv and ('O1' not in sys.argv or '02' not in sys.argv):
        sys.argv.append('-O2')

    if 'bdist_egg' in sys.argv:
        try:
            from setuptools import setup
        except ImportError:
            print "To build an egg setuptools must be installed"
    else:
        from distutils.core import setup

    setup(
        name=NAME,
        scripts=['Sudoku.py', 'Sudoku.pyw'],
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPT,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=AUTHOR,
        maintainer_email=AUTHOR_EMAIL,
        url=URL,
        download_url="http://wxsudoku.googlecode.com/downloads/list",
        license=LICENSE,
        platforms=[ "Many" ],
        packages=[ NAME ],
        package_dir={ NAME : '.' },
        classifiers=CLASSIFIERS
        )
