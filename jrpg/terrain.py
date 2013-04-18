# This file describes the corner rounder
# It is used by both jrpg and the level editor

# Corner rounding format - (this, hor, vert, diag, shade)
# None in diagonal if doesn't matter
grs = [' ', 'r', 't', 'T', 'h']
stn = ['S', 'Z']
dst = ['s', 'P', 'C', 'i', 'j']
blu = ['B', 'd']
ice = ['_', 'M', 'Q']
# There isn't much system behind those rules
# They're just added when I feel something doesn't look right
# Do not add self-shading rules (corner of 'S' in context foo is 'S' etc.),
# they're just wasting cycles.
corner_shader = {}
corner_shader[' '] = [
    (['.'],['.'],None , '.'),
    ([','],[','],None , ','),
    (['h'],['h'],['h'], 'h'),
    (['~'],['~'],None , '~'),
    ( dst , dst , dst , 's'),
    ( ice,  ice,  ice , '_'),
]
corner_shader['.'] = [
    ( grs , grs , grs , ' '),
    ( stn , stn , stn , 'S'),
    (['W'],['W'],['W'], 'W'),
    (['B'],['B'],['B'], 'B'),
    ( dst , dst , dst , 's'),
    (['E'],['E'],['E'], 'E'),
]
corner_shader[','] = [
    (['S'],['S'],['S'], 'S'),
    ( grs,  grs,  grs,  ' '),
]
corner_shader['h'] = [
    ([' '],[' '],[' '], ' '),
]
corner_shader['~'] = [
    (grs , grs , grs ,  ' '),
    (dst , dst , dst ,  's'),
# Shallow water shader, kinda silly
    (['&'],grs, grs,  '&'),
    (grs, ['&'],grs,  '&'),
]
corner_shader['b'] = [
    (grs , grs , grs ,  ' '),
]
corner_shader['S'] = [
    (['.'],['.'],['.'], '.'),
    ([','],[','],None , ','),
]
corner_shader['s'] = [
    (['.'],['.'],None,  '.'),
    ( grs,  grs,  grs,  ' '),
]
corner_shader['E'] = [
    (['.'],['.'],None,  '.'),
    ([','],[','],None,  ','),
    ( grs,  grs, None,  ' '),
]
corner_shader['_'] = [
    ( grs,  grs,  None, ' '),
]
corner_shader['W'] = [
    (['.'],['.'],['.'], '.'),
    ( grs,  grs,  None, ' '),
    ( blu , blu , blu , 'B'),
]
corner_shader['B'] = [
    (['.'],['.'],['.'], '.'),
    ( grs , grs , grs , ' '),
    (['.'],['.'],None, '.'),
]
