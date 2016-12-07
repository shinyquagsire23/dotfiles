#! /bin/sh

position(){
pos=$(mpc | awk 'NR==2' | awk '{print $4}' | sed 's/(//' | sed 's/%)//')
bar=$(echo $pos | gdbar -w 190 -h 1 -fg "#8e40c2" -bg "#403745")
echo -n "$bar"
return
}

font="lemon-10"
icon="/home/maxamillion/.config/bspwm/panel/images"

while :; do
echo "   $(mpc current -f %artist%)
   $(mpc current -f %title%) 
   $(mpc current -f %album%)

^p(55)^ca(1,mpc prev)^i($icon/prev.xbm)^ca()   ^ca(1,mpc toggle)^i($icon/playpause.xbm)^ca()   ^ca(1,mpc stop)^i($icon/stop.xbm)^ca()   ^ca(1,mpc next)^i($icon/next.xbm)^ca()
$(position)" 
done | dzen2 -p -y 18 -x 1296 -l 5 -u -w 190 -ta l -bg "#403745" -h 10 -fn "$font" -e 'onstart=uncollapse,grabkeys,grabmouse;key_Escape=ungrabkeys,ungrabmouse,exit'
