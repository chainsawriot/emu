#!/usr/bin/env python
import os
import re
import sys
libretroPath = {
"nes": {"path": "/home/pi/RetroPie/emulatorcores/fceu-next/fceumm-code/fceumm_libretro.so", "regex": r'\.nes$' }, 
"snes": {"path": "/home/pi/RetroPie/emulatorcores/pocketsnes-libretro/libretro.so", "regex": r'\.smc$'}, 
"mame": {"path": "/home/pi/RetroPie/emulatorcores/imame4all-libretro/libretro.so", "regex": r'\.zip$'},
"gb": {"path": "/home/pi/RetroPie/emulatorcores/gambatte-libretro/libgambatte/libretro.so", "regex": r'\.gbc?$'},
"pce": {"path": "/home/pi/RetroPie/emulatorcores/mednafen-pce-libretro/libretro.so", "regex": r'\.pce$'},
"gba": {"path": "/home/pi/RetroPie/emulatorcores/vba-next/libretro.so", "regex": r'\.gba$'}
}

if len(sys.argv) < 2:
    print "Usage: emu.py [romfile]"
    sys.exit()

romfile = sys.argv[1]


### detect rom type
def detectRom(romfile, libretroPath = libretroPath):
    for key in libretroPath:
        if re.search(libretroPath[key]['regex'], romfile.lower()):
            return key
    sys.exit()

### check for existance of romfile
if not os.path.isfile(romfile):
    print "non-exist rom"
    sys.exit()

#print romfile
#print detectRom(romfile)
os.system("retroarch -L "+libretroPath[detectRom(romfile, libretroPath)]['path']+" '"+str(romfile)+"'")
