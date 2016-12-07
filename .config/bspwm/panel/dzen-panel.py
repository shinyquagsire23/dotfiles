#!/bin/python2

#python2 dzen-test.py | dzen2 -fn "lemon-10" -ta l -bg '#3c3540'

from __future__ import print_function
from subprocess import Popen, PIPE
import re
import time
import sys
import os

import mpd

count = 0
panel_str = ""
FONT_WIDTH = 7

client = mpd.MPDClient(use_unicode=True)
client.connect("localhost", 6600)

def get_volume_percent_string():
    vol = Popen(['pactl', 'list', 'sinks'], stdout=PIPE)
    for i in vol.stdout:
        if "Volume:" in i:
            percent = i[i.find("/ ")+2:i.find("/ ")+6]
            if percent[0] == ' ':
                percent = percent[1:] + " "
            return percent

# from http://stackoverflow.com/questions/3983946/get-active-window-title-in-x
def get_active_window_title():
    root_check = ''
    root = Popen(['xprop', '-root'],  stdout=PIPE)

    if root.stdout != root_check:
        root_check = root.stdout

        for i in root.stdout:
            if '_NET_ACTIVE_WINDOW(WINDOW):' in i:
                id_ = i.split()[4]
                
                if(id_ == "0x0"):
                    return ""
                    
                id_w = Popen(['xprop', '-id', id_], stdout=PIPE)
        id_w.wait()
        buff = []
        for j in id_w.stdout:
            buff.append(j)

        for line in buff:
            match = re.match("WM_NAME\((?P<type>.+)\) = (?P<name>.+)", line)
            if match != None:
                type = match.group("type")
                if type == "STRING" or type == "COMPOUND_TEXT":
                    return match.group("name")[1:-1]
        return ""

def clickable_start(btn, command):
    global panel_str
    panel_str += "^ca(" + btn + ", " + command + ")"
    
def clickable_end():
    global panel_str
    panel_str += "^ca()"

def clear_panel():
    global panel_str
    panel_str = ""
    
def set_foreground(color):
    global panel_str
    panel_str += "^fg(" + ("#%X" % color if type(color) is int else color) + ")"

def set_background(color):
    global panel_str
    panel_str += "^bg(" + ("#%X" % color if type(color) is int else color) + ")"

def add_str(string):
    global panel_str
    panel_str += string
    panel_str = unicode(panel_str, errors='ignore') if isinstance(panel_str, str) else panel_str

def pad_pixels_right(pixels):
    global panel_str
    panel_str += "^p(" + str(pixels) + ")"

def pad_space_right(num_spaces):
    global panel_str
    panel_str += "^p(" + str(num_spaces * -FONT_WIDTH) + ")"
    
def lock_x():
    global panel_str
    panel_str += "^p(_LOCK_X)"
    
def unlock_x():
    global panel_str
    panel_str += "^p(_UNLOCK_X)"
    
def add_icon_right(icon, padding):
    global panel_str
    
    path = os.path.expanduser("~") + "/.config/bspwm/panel/images/" + icon + ".xbm"
    contents = open(path, "r").read()
    width = int(contents[contents.find("_width")+len("_width"):contents.find("\n")])
    contents = contents[contents.find("\n")+1:]
    height = int(contents[contents.find("_height")+len("_height"):contents.find("\n")])
    
    pad_pixels_right((width * -1) + (padding * -1))
    lock_x()
    panel_str += "^i(" + path + ")"
    unlock_x()
    pad_pixels_right(padding * -1)
    
def add_str_right(string):
    try:
        global panel_str
        pad_space_right(len(string))
        lock_x()
        panel_str += string
        unlock_x()
    except:
        unlock_x()
        pass
    
def move_right():
    global panel_str
    panel_str += "^p(_RIGHT)"
    pad_space_right(1)
    
def update_panel():
    global panel_str
    print(unicode(panel_str, errors='ignore').encode('utf-8') if isinstance(panel_str, str) else panel_str.encode('utf-8'))
    
    #Flush and update at 60fps
    sys.stdout.flush()
    time.sleep(1.0/60.0)

music_marquee_wait = 0;
music_marquee = 0
music_marquee_width = 40
fg_color = 0xf5e2fb
bg_color = 0x3c3540

while(1):
    clear_panel()
    set_foreground(fg_color)
    set_background(bg_color)
    add_str(get_active_window_title())
    
    #All of our right side, from right to left
    move_right()
    add_str_right(time.strftime("%A, %b %d %H:%M:%S", time.localtime()))
    set_foreground(0xAC73BF)
    add_icon_right("clock", 12)
    
    #Battery
    set_foreground(fg_color)
    bat_fraction = int(open("/sys/class/power_supply/BAT0/charge_now", "r").read());
    bat_total = int(open("/sys/class/power_supply/BAT0/charge_full", "r").read());
    percent_string = str(int(float(bat_fraction) / float(bat_total) * 100.0)) + "%"
    add_str_right(percent_string.rjust(4))
    set_foreground(0xC07495)
    add_icon_right("battery90", 6)
    
    #Volume
    set_foreground(fg_color)
    add_str_right(get_volume_percent_string())
    set_foreground(0xD4766B)
    add_icon_right("spkr", 12)
    
    #clickable_start("1", "bash " + os.path.expanduser("~") + "/.config/bspwm/panel/dzenmpd.sh &")
    
    #Music Marquee
    set_foreground(fg_color)
    music_marquee_wait += 1;
    if music_marquee_wait > 3:
        music_marquee += 1;
        music_marquee_wait = 0;
    current_song_title = ""
    
    if 'album' in client.currentsong():
        current_song_title += client.currentsong()['album'] + " - "
    
    if 'title' in client.currentsong():
        current_song_title += client.currentsong()['title']
        
    if 'artist' in client.currentsong():
        current_song_title += " - " + client.currentsong()['artist']
        
    if client.status()['state'] == 'pause':
        current_song_title += " (paused)"
        
    if client.status()['state'] == 'stop':
        #music_marquee = 0
        current_song_title = "Music Stopped"
        
    current_song_title += "   "
    
    if(len(current_song_title) < music_marquee_width):
        current_song_title = current_song_title.ljust(music_marquee_width+3)
    
    current_song_title = unicode(current_song_title, errors='ignore') if isinstance(current_song_title, str) else current_song_title
    
    if(music_marquee >= len(current_song_title)):
        music_marquee = 0;
        
    if len(current_song_title)-music_marquee < music_marquee_width:
        add_str_right(current_song_title[:music_marquee_width-len(current_song_title[music_marquee:music_marquee+music_marquee_width])])
    else:
        add_str_right("")
    add_str_right(current_song_title[music_marquee:music_marquee+music_marquee_width])
    
    set_foreground(0xE97841)
    add_icon_right("phones", 12)
    #lock_x()
    add_str("^ib(1)^ca(1, bash " + os.path.expanduser("~") + "/.config/bspwm/panel/dzenmpd.sh" + ")    " + "".ljust(music_marquee_width) + "^ca()^ib(0)")
    #unlock_x()
    #add_str_right("test")
    #clickable_end()
    
    #Something
    
    update_panel()
    
