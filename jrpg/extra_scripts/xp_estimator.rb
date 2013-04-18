#!/usr/bin/env ruby

# This script explores behavious of old jrpg XP system:
# How quickly does XP grow with fights.
#
# Old rules (tested here) were:
# * Players got +1XP on 3rd win,
# * demon probablity was uniform within a set.

sz  = 500
apf =  50
fs  = 100

xp = 0
dxp = 0
u = (0...sz).map{ 0 }
(apf * fs).times {|round_nr|
    i = rand(sz)
    u[i] += 1
    if u[i] >= 2 and u[i] <= 4
	xp += 1
	dxp += 1
    end
    if (round_nr+1) % apf == 0
	print "XP: #{xp} | #{dxp}\n" 
	dxp = 0
    end
}
