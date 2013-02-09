#!/usr/bin/env python
import os
import re
import sys
libretroPath = {"nes": "/home/pi/RetroPie/emulatorcores/fceu-next/fceumm-code/fceumm_libretro.so", "snes": "/home/pi/RetroPie/emulatorcores/pocketsnes-libretro/libretro.so"}

if len(sys.argv) < 2:
    print "Usage: emu.py [romfile]"
    sys.exit()
romfile = sys.argv[1]


### detect rom type
def detectRom(romfile):
    if re.search(r'\.nes$', romfile):
        return "nes"
    elif re.search(r'\.smc$', romfile):
        return "snes"
    else:
        sys.exit()

### check for existance of romfile
if not os.path.isfile(romfile):
    print "non-exist rom"
    sys.exit()

#print romfile
#print detectRom(romfile)
os.system("retroarch -L "+libretroPath[detectRom(romfile)]+" '"+str(romfile)+"'")
