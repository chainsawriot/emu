#!/usr/bin/env python
import curses
import os
import sys
import re


class frontend():
    basedir="/home/pi/RetroPie/roms/nes"
    libretroPath = {
        "nes": {"path": "/home/pi/RetroPie/emulatorcores/fceu-next/fceumm-code/fceumm_libretro.so", "regex": r'\.nes$' }, 
        "snes": {"path": "/home/pi/RetroPie/emulatorcores/pocketsnes-libretro/libretro.so", "regex": r'\.smc$'}, 
        "mame": {"path": "/home/pi/RetroPie/emulatorcores/imame4all-libretro/libretro.so", "regex": r'\.zip$'},
        "gb": {"path": "/home/pi/RetroPie/emulatorcores/gambatte-libretro/libgambatte/libretro.so", "regex": r'\.gbc?$'},
        "pce": {"path": "/home/pi/RetroPie/emulatorcores/mednafen-pce-libretro/libretro.so", "regex": r'\.pce$'},
        "gba": {"path": "/home/pi/RetroPie/emulatorcores/vba-next/libretro.so", "regex": r'\.gba$'}
        }
    maxdisplay = 10

    def combiningRegex(self, libretroPath):
        final = ""
        for key in libretroPath:
            final = final+libretroPath[key]["regex"]+"|"
        return final[:-1] # quick and dirty

    def getAllRoms(self, basedir, libretroPath):
        rawallfiles = os.listdir(basedir)
        romsExtn = re.compile(self.combiningRegex(libretroPath))
        allfiles = list(filter(lambda i: romsExtn.search(i.lower()), rawallfiles)) ## so ugly! Hate you Python3!
        return allfiles

    def __init__(self):
        myscreen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        myscreen.keypad(1)
        allfiles = self.getAllRoms(self.basedir, self.libretroPath)
        romfile = self.menuProcess(myscreen, allfiles)
        curses.endwin()
        os.system("retroarch -L "+self.libretroPath[self.detectRom(romfile, self.libretroPath)]['path']+" "+self.basedir+"/'"+str(romfile)+"'")


    def menuProcess(self, myscreen, allfiles):
        pos = 0
        maxdisplay = self.maxdisplay
        bigindex = 0
        maxindex = len(allfiles) / maxdisplay
        keyinput = None
        x = None
        while x != ord('\n'):
            myscreen.border(0)
            myscreen.addstr(1, 5, "Curses EMU STATION by Chainsaw Riot", curses.A_BOLD)
            myscreen.addstr(2, 5, "https://github.com/chainsawriot/emu")
            myscreen.addstr(3, 5, "- - - - - - - - - - - - - - - - - -")
            if bigindex == maxindex:
                rangeend = len(allfiles) % maxdisplay
                if pos >= rangeend:
                    pos = 0
            else:
                rangeend = maxdisplay
            for ind in range(0, rangeend):
                if ind == pos:
                    myscreen.addstr(ind+4,5, allfiles[(bigindex*maxdisplay)+ind], curses.A_REVERSE)
                else:
                    myscreen.addstr(ind+4,5, allfiles[(bigindex*maxdisplay)+ind])
            myscreen.addstr(maxdisplay+7,5, "page "+str(bigindex)+" / "+str(maxindex))
            myscreen.addstr(maxdisplay+8,5, "Arrow Key / Enter, q to quit")
            myscreen.refresh()
            x = myscreen.getch()
            if x == 258:
                if pos < (maxdisplay-1):
                    pos += 1
                else:
                    pos = 0
            elif x == 259:
                if pos > 0:
                    pos -= 1
                else:
                    pos = (maxdisplay-1)
            elif x == ord("q"):
                curses.endwin()
                sys.exit()
            elif x == 261:
                if bigindex != maxindex:
                    bigindex += 1
                else:
                    bigindex = 0
                myscreen.clear()
            elif x == 260:
                if bigindex > 0:
                    bigindex -= 1
                else:
                    bigindex = maxindex
                myscreen.clear()
            elif x != ord('\n'):
                curses.flash()
        return allfiles[(bigindex * maxdisplay)+pos]
    def detectRom(self, romfile, libretroPath):
        for key in libretroPath:
            if re.search(libretroPath[key]['regex'], romfile.lower()):
                return key
        sys.exit()

if __name__=="__main__":
    frontend = frontend()
