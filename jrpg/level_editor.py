#!/usr/bin/python

# Some code based on various wx hello-worlds (mostly the superdoodle)

from __future__ import print_function
import wx
from wx.lib import buttons

from terrain import corner_shader

idNEW    = wx.NewId()
idOPEN   = wx.NewId()
idSAVE   = wx.NewId()
idSAVEAS = wx.NewId()
idRESIZE = wx.NewId()
idEXIT   = wx.NewId()

terrain_image_file = "images/angband.png"

mtctl_terrain = {
# Movable terrain
  ' ' : (  9, 23, False), # grass
  's' : ( 12, 23, False), # sand
  'h' : ( 93, 23, False), # hilly land
  '.' : ( 30, 23, False), # (stone) road
  ',' : ( 27, 23, False), # dungeon floor
  'D' : ( 67, 25, False), # Door (brick)
  'd' : ( 81, 25, False), # Door (blue)
  'V' : ( 96, 24, False), # Door (wooden)
  'k' : ( 32, 26, False), # gate, open
  '_' : ( 84, 23, False), # Snowy land
  'H' : ( 96, 23, False), # Icy hilly land
  '0' : (123, 24, True),  # Door (red)
  '>' : ( 28, 26, False), # stairs up
  '<' : ( 29, 26, False), # stairs down
# Blocking terrain
# FIXME: this is silly
  ':' : ( 30, 23, True),  # (stone) road - special version that can block you ;-)
  't' : ( 54, 23, True),  # tree
  'T' : ( 60, 23, True),  # pine tree
  'm' : (117, 23, True),  # mountain
  'r' : ( 96, 21, True),  # rocks
  '&' : ( 15, 23, True),  # water
  '~' : ( 18, 23, True),  # water
  'P' : ( 69, 23, True),  # palm tree
  'C' : ( 99, 22, True),  # cactus
  'i' : (105, 22, True),  # dead desert tree
  'j' : (123, 23, True),  # desert mountain
  'b' : ( 99, 24, True),  # brick wall
  'S' : (105, 24, True),  # stone wall
  'W' : (111, 24, True),  # wooden wall
  'B' : ( 78, 25, True),  # Blue brick wall
  'K' : ( 30, 26, True),  # gate, closed
  'z' : ( 72, 24, True),  # Window in a brick wall
  'Z' : ( 75, 24, True),  # Window in a stone wall
  'M' : ( 87, 23, True),  # Icy mountain
  'Q' : ( 90, 23, True),  # Icy tree
  'E' : (120, 24, True),  # Red brick wall
}

# Ordering in the control panel
terrain_types = [
    " ", "s", "h", ".", ",", "D", "d", "V", "k", "_",
    "H", ">", "<", "0", ":", "t", "T", "m", "r", "&", "~", "P",
    "C", "i", "j", "b", "S", "W", "B", "K", "z", "Z",
    "M", "Q", "E"]

class Map_model:
    def __init__(self):
        # FIXME: make it actually work
        self.needs_a_save = False
        self.open("maps/new_world.map")

    def new(self, file_name):
        print("new")

    def recompute_corners(self, xmin, xmax, ymin, ymax):
        if xmin < 0: xmin = 0
        if xmax >= self.size_x: xmax = self.size_x-1
        if ymin < 0: ymin = 0
        if ymax >= self.size_y: ymax = self.size_y-1
        if xmin > xmax or ymin > ymax: return
        # At this point:
        # 0 <= xmin <= xmax < self.size_x
        # 0 <= ymin <= ymax < self.size_y

        for y in range(ymin, ymax+1):
            for x in range(xmin, xmax+1):
                this = self.gett(x,y)
                ul = None
                ur = None
                dl = None
                dr = None
                if this in corner_shader:
                    r = self.gett(x+1,y  )
                    d = self.gett(x,  y+1)
                    l = self.gett(x-1,y)
                    u = self.gett(x,  y-1)
                    for (horz, vert, diag, shade_to) in corner_shader[this]:
                        if( r in horz and
                            d in vert and
                            ((not diag) or (self.gett(x+1,y+1) in diag))):
                            dr = shade_to
                            break
                    for (horz, vert, diag, shade_to) in corner_shader[this]:
                        if( r in horz and
                            u in vert and
                            ((not diag) or (self.gett(x+1,y-1) in diag))):
                            ur = shade_to
                            break
                    for (horz, vert, diag, shade_to) in corner_shader[this]:
                        if( l in horz and
                            d in vert and
                            ((not diag) or (self.gett(x-1,y+1) in diag))):
                            dl = shade_to
                            break
                    for (horz, vert, diag, shade_to) in corner_shader[this]:
                        if( l in horz and
                            u in vert and
                            ((not diag) or (self.gett(x-1,y-1) in diag))):
                            ul = shade_to
                            break
                self.data[y][x][1] = ul
                self.data[y][x][2] = ur
                self.data[y][x][3] = dl
                self.data[y][x][4] = dr

    def open(self, file_name):
        self.file_name = file_name
        f = open(file_name)
        data = [line.rstrip('\n') for line in f.readlines()]
        f.close()

        self.size_y = len(data)
        self.size_x = 0
        for y in range(self.size_y):
            self.size_x = max(self.size_x, len(data[y]))
        self.data = []
        for y in range(self.size_y):
            line = [[tile,None,None,None,None] for tile in data[y]]
            while len(line) < self.size_x:
                line.append([None,None,None,None,None]) # Fill with something if the map is not a rectangle
            self.data.append(line)
        self.recompute_corners(0, self.size_x-1, 0, self.size_y-1)

        # FIXME: Force repaint
        # FIXME: notify map_view that the model changed
    def save(self):
        # Serialize ...
        data = []
        for line in self.data:
            line = [(tile and tile[0]) for tile in line]
            while len(line) > 0 and line[-1] == None:
                line.pop()
            data.append(line)
        contents = "".join(["".join(line) + "\n" for line in data])
        print("saving...")
        f = open(self.file_name, "w")
        f.write(contents)
        f.close()
        print("saved.")
    def save_as(self, file_name):
        pass
    # Get [tile, ul, ur, dl, dr]
    def get(self,x,y):
        if x < 0 or y < 0 or x >= self.size_x or y >= self.size_y: return None
        return self.data[y][x]
    # Get tile
    def gett(self,x,y):
        if x < 0 or y < 0 or x >= self.size_x or y >= self.size_y: return None
        tile = self.data[y][x]
        if tile: return tile[0]
        else: return None
    def set(self,x,y,v):
        if self.data[y][x][0] != v:
            self.data[y][x][0] = v
            self.needs_a_save = True
        self.recompute_corners(x-1,x+1,y-1,y+1)

class Control_panel_model:
    def __init__(self):
        self.selected_terrain = terrain_types[0]

class Control_panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.RAISED_BORDER)

        global control_panel_model
        control_panel_model = Control_panel_model()

        button_size = wx.Size(32+2*3, 32+2*3)

        c_grid = wx.GridSizer(cols=3, hgap=2, vgap=2)
        self.terrain_buttons={}

        for i in range(len(terrain_types)):
            tile = terrain_types[i]
            bmp = wx.EmptyBitmap(32, 32)
            bmp_dc = wx.MemoryDC()
            bmp_dc.SelectObject(bmp)

            xsrc = mtctl_terrain[tile][0] * 32
            ysrc = mtctl_terrain[tile][1] * 32
            bmp_dc.Blit(0, 0, 32, 32, terrain_dc, xsrc, ysrc)

            b = buttons.GenBitmapToggleButton(self, i, bmp, size=button_size)
            b.SetBezelWidth(1)
            b.SetUseFocusIndicator(False)
            self.Bind(wx.EVT_BUTTON, self.OnSetTerrain, b)
            c_grid.Add(b, 0)
            self.terrain_buttons[terrain_types[i]] = b

        self.terrain_buttons[control_panel_model.selected_terrain].SetToggle(True)

        # Make a box sizer and put the two grids and the indicator
        # window in it.
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(c_grid, 0, wx.ALL, 4)
        self.SetSizer(box)
        self.SetAutoLayout(True)

        # Resize this window so it is just large enough for the
        # minimum requirements of the sizer.
        box.Fit(self)

    def OnSetTerrain(self, event):
        self.terrain_buttons[control_panel_model.selected_terrain].SetToggle(False)

        id = event.GetId()
        control_panel_model.selected_terrain = terrain_types[id]

# TODO: Add scroolbars
class Map_view(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, -1, style=wx.HSCROLL|wx.VSCROLL)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)

        # REFACTORME: It's rather silly to have it here
        self.left_down = False

        self.SetScrollRate(32, 32)
        self.SetVirtualSize((32 * map_model.size_x, 32 * map_model.size_y))
    def paint_tile_range(self, x_range, y_range):
        # sx,sy in virtual units, one unit = one tile
        dcout = wx.PaintDC(self)
        (sx,sy) = self.GetViewStart()
        for y in y_range:
            for x in x_range:
                tile = map_model.get(x,y)
                if not tile: continue # Out-of-map
                tile, ul, ur, dl, dr = tile
                if not tile: continue # In-map gap
                xsrc = mtctl_terrain[tile][0] * 32
                ysrc = mtctl_terrain[tile][1] * 32
                dcout.Blit(x*32-sx*32, y*32-sy*32, 32, 32, terrain_dc, xsrc, ysrc)

                if ul:
                    xsrc = mtctl_terrain[ul][0] * 32
                    ysrc = mtctl_terrain[ul][1] * 32
                    dcout.Blit(x*32-sx*32, y*32-sy*32, 16, 16, terrain_dc, xsrc, ysrc, useMask=True, xsrcMask=0, ysrcMask=0)

                if ur:
                    xsrc = mtctl_terrain[ur][0] * 32+16
                    ysrc = mtctl_terrain[ur][1] * 32
                    dcout.Blit(x*32-sx*32+16, y*32-sy*32, 16, 16, terrain_dc, xsrc, ysrc, useMask=True, xsrcMask=16, ysrcMask=0)

                if dl:
                    xsrc = mtctl_terrain[dl][0] * 32
                    ysrc = mtctl_terrain[dl][1] * 32+16
                    dcout.Blit(x*32-sx*32, y*32-sy*32+16, 16, 16, terrain_dc, xsrc, ysrc, useMask=True, xsrcMask=0, ysrcMask=16)

                if dr:
                    xsrc = mtctl_terrain[dr][0] * 32+16
                    ysrc = mtctl_terrain[dr][1] * 32+16
                    dcout.Blit(x*32-sx*32+16, y*32-sy*32+16, 16, 16, terrain_dc, xsrc, ysrc, useMask=True, xsrcMask=16, ysrcMask=16)
    def OnPaint(self, event):
        # TODO: Limit paint to the visible portion of the screen
        self.paint_tile_range(range(map_model.size_x), range(map_model.size_y))
    def OnLeftDown(self, event):
        self.mouse_terrain_set_event(event.GetPosition())
        self.left_down = True
    def mouse_terrain_set_event(self, pos):
        x = pos[0] / 32
        y = pos[1] / 32
        (sx,sy) = self.GetViewStart()
        x += sx
        y += sy

        if x >= 0 and x < map_model.size_x and y >= 0 and y < map_model.size_y:
            map_model.set(x, y, control_panel_model.selected_terrain)
            self.paint_tile_range(range(x-1,x+2), range(y-1,y+2))
    def OnLeftUp(self, event):
        self.left_down = False
    def OnMotion(self, event):
        if self.left_down:
            self.mouse_terrain_set_event(event.GetPosition())

class Main_window(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "jrpg level editor", size=(640, 480))

        menuBar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(idNEW,    "&New ...\tAlt-N", "New map")
        menu.Append(idOPEN,   "&Open\tAlt-O", "Open a map")
        menu.Append(idSAVE,   "&Save\tAlt-S", "Save current map")
        menu.Append(idSAVEAS, "Save &as ...\tAlt-A", "Save current map as ...")
        menu.Append(idRESIZE, "&Resize ...\tAlt-R", "Resize current map")
        menu.Append(idEXIT, "E&xit\tAlt-X", "Exit")

        self.Bind(wx.EVT_MENU, self.menu_event)

        menuBar.Append(menu, "&Editor")
        self.SetMenuBar(menuBar)
        self.CreateStatusBar()

        self.control_panel = Control_panel(self)
        self.map_view      = Map_view(self)

        global map_view
        map_view = self.map_view

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.control_panel, 0, wx.EXPAND)
        box.Add(self.map_view,      1, wx.EXPAND)
        # Tell the frame that it should layout itself in response to size events.
        self.SetAutoLayout(True)
        self.SetSizer(box)

    def menu_event(self, event):
        id = event.GetId()
        if id == idNEW:
            print("cmd new")
        elif id == idOPEN:
            open_dialog = wx.FileDialog(None, style=wx.OPEN)
            if open_dialog.ShowModal() == wx.ID_OK:
                file_name = open_dialog.GetPath()
                map_model.open(file_name)
                open_dialog.Destroy()
        elif id == idSAVE:
            map_model.save()
        elif id == idSAVEAS:
            save_as_dialog = wx.FileDialog(None, style=wx.SAVE|wx.OVERWRITE_PROMPT)
            if save_as_dialog.ShowModal() == wx.ID_OK:
                file_name = save_as_dialog.GetPath()
                map_model.save_as(file_name)
                save_as_dialog.Destroy()
        elif id == idRESIZE:
            pass
        elif id == idEXIT:
            self.Close()
        else:
            print("Unknown command id:", id)

class Level_editor(wx.App):
    def OnInit(self):
        global terrain_dc

        terrain_bitmap = wx.Bitmap(terrain_image_file)

        # rounded_corners_mask = wx.Mask(bitmap=wx.Bitmap("mask.png"))
        # terrain_bitmap.SetMask(rounded_corners_mask)
        #
        terrain_dc = wx.MemoryDC()
        terrain_dc.SelectObject(terrain_bitmap)

        main_window = Main_window()
        main_window.Show(True)
        return True

map_model = Map_model()
app = Level_editor()
app.MainLoop()
