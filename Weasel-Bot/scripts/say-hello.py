#!/usr/bin/env python

def OnPaint(frame):
    import wx
    def OnPaintInner(event):
        hello_world = 'Hello from the botmaster!'
        extents = frame.GetTextExtent(hello_world)
        position_x = (frame.GetSize()[0] - extents[0])/2
        position_y = (frame.GetSize()[1] - extents[1])/2
        dc = wx.ClientDC(frame)
        dc.DrawText(hello_world, position_x, position_y)
    return OnPaintInner 


def show_frame():
    import wx
    app = wx.App()
    frame = wx.Frame(None, -1, 'Botnet Window', 
                            wx.DefaultPosition, 
                            wx.Size(400,400))
    wx.EVT_PAINT(frame, OnPaint(frame))
    frame.Show()
    frame.Fit()
    app.MainLoop()

show_frame()
