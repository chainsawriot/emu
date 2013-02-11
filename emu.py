#!/usr/bin/env python
import curses
import os
import sys
import re

basedir="/home/pi/RetroPie/roms/nes"

libretroPath = {
"nes": {"path": "/home/pi/RetroPie/emulatorcores/fceu-next/fceumm-code/fceumm_libretro.so", "regex": r'\.nes$' }, 
"snes": {"path": "/home/pi/RetroPie/emulatorcores/pocketsnes-libretro/libretro.so", "regex": r'\.smc$'}, 
"mame": {"path": "/home/pi/RetroPie/emulatorcores/imame4all-libretro/libretro.so", "regex": r'\.zip$'},
"gb": {"path": "/home/pi/RetroPie/emulatorcores/gambatte-libretro/libgambatte/libretro.so", "regex": r'\.gbc?$'},
"pce": {"path": "/home/pi/RetroPie/emulatorcores/mednafen-pce-libretro/libretro.so", "regex": r'\.pce$'},
"gba": {"path": "/home/pi/RetroPie/emulatorcores/vba-next/libretro.so", "regex": r'\.gba$'}
}

def combiningRegex(libretroPath):
    final = ""
    for key in libretroPath:
        final = final+libretroPath[key]["regex"]+"|"
    return final[:-1] # quick and dirty

###get all files from basedir and filter rubbish
rawallfiles = os.listdir(basedir)
romsExtn = re.compile(combiningRegex(libretroPath))
allfiles = filter(lambda i: romsExtn.search(i.lower()), rawallfiles)

myscreen = curses.initscr()
curses.noecho()
curses.cbreak()
#curses.curs_set(2)
myscreen.keypad(1)

def menuProcess(myscreen, allfiles):
    ###TODO: paging if too many files
    myscreen.border(0)
    pos = 0
    keyinput = None
    x = None
    while x != ord('\n'):
        myscreen.addstr(1, 5, "Curses EMU STATION by Chainsaw Riot", curses.A_BOLD)
        myscreen.addstr(2, 5, "https://github.com/chainsawriot/emu")
        myscreen.addstr(3, 5, "- - - - - - - - - - - - - - - - - -")
        for ind in range(len(allfiles)):
            if ind == pos:
                myscreen.addstr(ind+4,5, allfiles[ind], curses.A_REVERSE)
            else:
                myscreen.addstr(ind+4,5, allfiles[ind])
        myscreen.addstr(len(allfiles)+5,5, "Arrow Key / Enter, q to quit")
        myscreen.refresh()
        x = myscreen.getch()
        if x == 258:
            if pos < len(allfiles):
                pos += 1
            else:
                pos = 0
        elif x == 259:
            if pos > 0:
                pos -= 1
            else:
                pos = len(allfiles)
        elif x == ord("q"):
            curses.endwin()
            sys.exit()
        elif x != ord('\n'):
            curses.flash()
    return allfiles[pos]
romfile = menuProcess(myscreen, allfiles)

curses.endwin()


### detect rom type
def detectRom(romfile, libretroPath = libretroPath):
    for key in libretroPath:
        if re.search(libretroPath[key]['regex'], romfile.lower()):
            return key
    sys.exit()

os.system("retroarch -L "+libretroPath[detectRom(romfile, libretroPath)]['path']+" "+basedir+"/'"+str(romfile)+"'")
