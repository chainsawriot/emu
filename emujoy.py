#!/usr/bin/env python
import curses
import os
import sys
import re
import pygame
import StringIO
import ConfigParser

class frontend():
    basedir="/home/pi/RetroPie/roms/nes"
    libretroPath = {
        "nes": {"path": "/home/pi/RetroPie/emulatorcores/fceu-next/fceumm-code/fceumm_libretro.so", "regex": r'\.nes$' }, 
        "snes": {"path": "/home/pi/RetroPie/emulatorcores/pocketsnes-libretro/libretro.so", "regex": r'\.smc$'}, 
        "mame": {"path": "/home/pi/RetroPie/emulatorcores/imame4all-libretro/libretro.so", "regex": r'\.zip$'},
        "gb": {"path": "/home/pi/RetroPie/emulatorcores/gambatte-libretro/libgambatte/libretro.so", "regex": r'\.gbc?$'},
        "pce": {"path": "/home/pi/RetroPie/emulatorcores/mednafen-pce-libretro/libretro.so", "regex": r'\.pce$'},
        "gba": {"path": "/home/pi/RetroPie/emulatorcores/vba-next/libretro.so", "regex": r'\.gba$'},
        "sms": {"path": "/home/pi/code/emu/libretro/genesis_plus_gx_libretro.so", "regex": r'\.sms$'}
        }
    retroarchcfg = "/home/pi/.retroarch.cfg"
    maxdisplay = 19
    joy = []
    filterby = None
    joyKeysHash = dict()
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
        pygame.joystick.init()
        pygame.display.init()
        if not pygame.joystick.get_count():
            print "nPlease connect a joystick and run again.n"
            quit()
#        print "n%d joystick(s) detected." % pygame.joystick.get_count()

#            print "Joystick %d: " % (i) + self.joy[i].get_name()
        try:
            self.joyKeysHash = self.joyHashGen()
        except:
            print "Cannot open or parse: "+retroarchcfg
            quit()
        while 1:
            for i in range(pygame.joystick.get_count()):
                myjoy = pygame.joystick.Joystick(i)
                myjoy.init()
                self.joy.append(myjoy)
            myscreen = curses.initscr()
            curses.noecho()
            curses.cbreak()
            #myscreen.keypad(1)
            myscreen.clear()
            rawallfiles = self.getAllRoms(self.basedir, self.libretroPath)
            if self.filterby is not None:
                displayExtKey = self.libretroPath.keys()[self.filterby]
                romsExtn = re.compile(self.libretroPath[displayExtKey]["regex"])
                allfiles = list(filter(lambda i: romsExtn.search(i.lower()), rawallfiles))
                if len(allfiles) == 0:
                    allfiles = rawallfiles
            else:
                allfiles = rawallfiles
            romfile = self.menuProcess(myscreen, allfiles)
            if romfile == "refresh":
                curses.endwin()
                self.filterby = None
                print "reload rom files\n"
            elif romfile == "filter":
                curses.endwin()
                if self.filterby is None:
                    self.filterby = 0
                else:
                    self.filterby += 1
                    if self.filterby == len(self.libretroPath):
                        self.filterby = None
            else:
                for myjoy in self.joy:
                    myjoy.quit()
                curses.endwin()
                os.system("retroarch -L "+self.libretroPath[self.detectRom(romfile, self.libretroPath)]['path']+" "+self.basedir+"/'"+str(romfile)+"'")


    #joyKeysHash = {0: "up", 1: "down", 3: "right", 2: "left", 4: "confirm", 13: "confirm", 14: "quit", 5: "refresh", 6:"filter"}
    def joyHashGen(self):
        c = StringIO.StringIO()
        c.write("[retroarch]\n")
        c.write(open(self.retroarchcfg, 'r').read())
        c.seek(0, os.SEEK_SET)
        cp = ConfigParser.ConfigParser()
        cp.readfp(c)
        a = ['input_player1_left_btn', 'input_player1_right_btn', 'input_player1_up_btn' ,'input_player1_down_btn', 'input_player1_b_btn', 'input_player1_y_btn', 'input_player1_a_btn', 'input_player1_select_btn']
        jKHValue = ['left', 'right', 'up', 'down', 'confirm', 'filter', 'refresh', 'quit']
        print a
        keypairnum = len(a)
        joyKeysHash = dict()
        for i in range(0, keypairnum):
            keycode = int(re.sub(r'"', r'', cp.get('retroarch', a[i])))
            joyKeysHash[keycode] = jKHValue[i]
        if cp.has_option('retroarch', 'input_exit_emulator_btn'):
            joyKeysHash[int(re.sub(r'"', r'', cp.get('retroarch', 'input_exit_emulator_btn')))] = 'quit'
        c.close()
        return joyKeysHash

    def joystickListener(self):
        while True:
            e = pygame.event.wait()
            if e.type == pygame.JOYBUTTONDOWN:
                keypressed = e.dict['button']
                if keypressed in self.joyKeysHash:
                    return self.joyKeysHash[keypressed]

    def menuProcess(self, myscreen, allfiles):
        pos = 0
        maxdisplay = self.maxdisplay
        bigindex = 0
        maxindex = len(allfiles) / maxdisplay
        keyinput = None
        x = None
        while x != "confirm":
            myscreen.border(0)
            myscreen.addstr(1, 5, "emu.py by Chainsaw Riot", curses.A_BOLD)
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
            myscreen.addstr(maxdisplay+4, 5, "- - - - - - - - - - - - - - - - - -")
            myscreen.addstr(maxdisplay+5,5, "page "+str(bigindex)+" / "+str(maxindex))
            if self.filterby is not None:
                myscreen.addstr(maxdisplay+5,20, "Display only:"+self.libretroPath.keys()[self.filterby])
            myscreen.refresh()
            x = self.joystickListener()
            if x == "down":
                if pos < (maxdisplay-1):
                    pos += 1
                else:
                    pos = 0
            elif x == "up":
                if pos > 0:
                    pos -= 1
                else:
                    pos = (rangeend-1)
            elif x == "quit":
                curses.endwin()
                sys.exit()
            elif x == "right":
                if bigindex != maxindex:
                    bigindex += 1
                else:
                    bigindex = 0
                myscreen.clear()
            elif x == "left":
                if bigindex > 0:
                    bigindex -= 1
                else:
                    bigindex = maxindex
                myscreen.clear()
            elif x == "refresh":
                return "refresh"
            elif x == "filter":
                return "filter"
            elif x != "confirm":
                curses.flash()
        return allfiles[(bigindex * maxdisplay)+pos]
    def detectRom(self, romfile, libretroPath):
        for key in libretroPath:
            if re.search(libretroPath[key]['regex'], romfile.lower()):
                return key
        sys.exit()

if __name__=="__main__":
    frontend = frontend()
