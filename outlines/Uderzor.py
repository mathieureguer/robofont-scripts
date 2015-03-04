# Mathieu Reguer
__version__ = 0.2

"""
Draw asterisks.
Uses an anchor named 'origin' or the bottom center of the glyph bbox as the center of the transformation.
"""

##########
# settings
##########
anchorDefault = "origin"
colorRGBA = (1, 0, 0.5, 0.5)


##########
# imports
##########

import math
from mojo.events import addObserver, removeObserver
from fontTools.misc.transform import Identity
from mojo.drawingTools import *
from mojo.UI import UpdateCurrentGlyphView
#from mojo.UI import CurrentFontWindow
from vanilla import *
from AppKit import NSColor

##########
# objects
##########

class uderzor():
    def __init__(self):
        self.increments = 5
        self.anchorName = None

    def offsetToOriginPoint(self, pt):
        t = Identity
        t = t.translate(pt[0], pt[1])
        return t.inverse()
        
    def anchorSearch(self, glyph, anchorName):
        for a in glyph.anchors:
            if a.name == anchorName:
                return a
         
    def getDefaultOrigin(self, glyph):
        return ((glyph.box[0]+glyph.box[2])/2, glyph.box[1])
                
    def getOrigin(self, glyph, anchorName):
        anchor = self.anchorSearch(glyph, anchorName)
        if anchor:
            return (anchor.x, anchor.y)
        else:
            return self.getDefaultOrigin(glyph)
        
    def radialDuplicate(self, glyph):
        origin = self.getOrigin(glyph, self.anchorName)
        t = self.offsetToOriginPoint(origin)
        angle = 360.0/self.increments
        glyph.transform(t)

        gBis = glyph.copy()
        a = self.anchorSearch(gBis, self.anchorName)
        if a:
            gBis.removeAnchor(a)
        
        for x in range(self.increments-1):
            gBis.rotate(angle)
            glyph.appendGlyph(gBis)
        
        glyph.transform(t.inverse())
        
        
class uderzorPanel():
    
    def __init__(self, colorDefault=(.4, .8, .3, .8), anchorDefault="origin"):
        self.panel()
        self.uderzor = uderzor()
        self.uderzor.anchorName = anchorDefault
        
        self.color = NSColor.colorWithCalibratedRed_green_blue_alpha_(colorDefault[0], colorDefault[1], colorDefault[2], colorDefault[3])
        
        self.drawAsterisk()
        
        addObserver(self, "updateView", "drawBackground")

        
    def panel(self):
        
        xMargin = 15
        yMargin = 15
        itemHeight = 50
        windowsWidth = xMargin*2 + itemHeight*2
        
        self.w = FloatingWindow((windowsWidth, 0), "Uderzor")
        self.w.bind("close", self.windowCloseCallback)
        
        currentHeight = yMargin
        
        self.w.minus = SquareButton((xMargin, currentHeight, itemHeight, itemHeight),
                                     "-",
                                     callback = self.decreaseIncrements)

                                     
        self.w.plus = SquareButton((itemHeight+xMargin, currentHeight, itemHeight, itemHeight),
                                     "+",
                                     callback = self.increaseIncrements)
         
                                     
         
        currentHeight += itemHeight + yMargin/2
        
        self.w.origin = Button((xMargin, currentHeight, -xMargin, 22),
                             "Add Origin",
                             callback = self.addOriginCallback)
                             
        currentHeight += 22 + yMargin/2

         
        self.w.outline = Button((xMargin, currentHeight, -xMargin, 22),
                             "outline",
                             callback = self.outlineCallback)
                             
         
        currentHeight += 22 + yMargin
                           
        self.w.setPosSize((200, 100, windowsWidth, currentHeight))
        
        self.w.open()
        self.w.makeKey()
        
        self.w.setDefaultButton(self.w.outline)
        
    # callbacks
    def updateView(self, info):
        self.drawAsterisk()
        self.showPreview()
    
    def drawAsterisk(self):
        if CurrentGlyph():
            self.output = CurrentGlyph().copy()
            self.uderzor.radialDuplicate(self.output)
        
    def showPreview(self):
        if self.output :
            self.color.set()
            self.previewPath = self.output.naked().getRepresentation("defconAppKit.NSBezierPath")
            self.previewPath.fill()
            UpdateCurrentGlyphView()
    
    def windowCloseCallback(self, sender):
        removeObserver(self, "drawBackground")
                
    def increaseIncrements(self, sender):
        self.uderzor.increments += 1
        self.updateView("dummmyInfo")
        
    def decreaseIncrements(self, sender):
        if self.uderzor.increments <= 2:
            self.uderzor.increments = 2
        else:
            self.uderzor.increments -= 1 
        self.updateView("dummmyInfo")

    def outlineCallback(self, sender):
        g = CurrentGlyph()
        g.prepareUndo("Uderzor")
        g.clear()
        CurrentGlyph().appendGlyph(self.output)
        g.performUndo()
        
    def addOriginCallback(self, sender):
        g = CurrentGlyph()
        if self.uderzor.anchorSearch(g, anchorDefault) == None:
            g.appendAnchor(anchorDefault, self.uderzor.getDefaultOrigin(g))
        

uderzorPanel(colorDefault=colorRGBA, anchorDefault=anchorDefault)
