#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      MTJacobson
#
# Created:     07/04/2014
# Copyright:   (c) MTJacobson 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#STILL CAN'T READ MULTI LETTER TILES
#vertical line test
#negative image better?
#smaller image?
#individual threshholds
import sys
sys.path.append('D:\Coding\Python Codes\General')
import pyimage
import pymouse
import os
import grid
import trie
import time

OCR_PATH = "D:\Coding\Python Codes\Wordament\OCR\\"
OCR_FILES = os.listdir(OCR_PATH)
DICT_LOC = "D:\Coding\Python Codes\Wordament\dictionary.txt"
OCR_ALPHABET = ['e','t','a','o','i','n','s','h','r','d','l','c','u','m','w','f','g','y','p','b','v','k','j','x','z']# missing q atm

def testWhiteCount(): #possibly use white pixel count to identify singular tiles... ugly but fast
    import Image
    import ImageOps
    res = {}
    for fileName in OCR_FILES:
        letter = fileName[0]
        img = Image.open(OCR_PATH+fileName)
        colors = img.getcolors()
        cnt = [x[0] for x in colors if x[1] == (255,255,255)]
        res[cnt[0]] = letter
    return res

def test():
    a = findGrid()
    #return verticalLineTest(a[1])
    return analyzeGrid(a[1])
    #return getBest(a[1][0],2)
    #return createGrid(a[1])

def verticalLineTest(tileBoxes): # returns number of characters in each tile
    #numbers end on pixel 22, definitely by 23, so vertical line starts on 24 and down
    chars = []
    for box in tileBoxes:
        img = pyimage.grabColor(box)
        bbox = img.getbbox()
        yLine = range(24,bbox[3])
        boolChar = False
        chars.append(0)
        for x in range(0,bbox[2]):
            boolWhite = False
            for y in yLine:
                color = getColor(img.getpixel((x,y)))
                if color == 'white':
                    boolChar = True
                    boolWhite = True
            if boolChar and not boolWhite:
                chars[-1] += 1
                boolChar = False

    return chars



def _analyzeTile(tileBox,threshhold=True):
    res = {}
    for fileName in [x +'.png' for x  in OCR_ALPHABET]:
        letter = fileName.split('.')[0]
        res[letter] = pyimage.compareBox(tileBox,OCR_PATH+fileName)
        if threshhold and res[letter][0] > 0.95: return res #return early on threshhold value

    return res

def analyzeGrid(tileBoxes,threshhold=False):
    grid = []
    for box in tileBoxes:
        grid.append(_analyzeTile(box,threshhold))
    return grid

def getBest(box,amt=1):
    threshhold = True
    if amt > 1: threshhold = False
    res = _analyzeTile(box,threshhold)
    best = []
    for i in range(amt):
        a = max(res.iterkeys(), key=(lambda key: res[key]))
        best.append((a,res.pop(a,None)[0])) #PROBABLY GOING TO HAVE TO SORT THESE BY [1][0] ONCE I GET OCR ON MULTIPLE LETTERS WORKING

    return best

def getColor(rgb): #orange (9,150,240)
    if rgb[0] > 200 and rgb[1] > 200 and rgb[2] > 200: return 'white'
    if rgb[2] > rgb[0] and rgb[2] > rgb[1]: return 'blue'
    if rgb[0] > rgb[1] and rgb[0] > rgb[2]: return 'red' #~orange
    if rgb[1] > rgb[0] and rgb[1] > rgb[2]: return 'green'
    return None

def createGrid(tileBoxes):
    grid = ''
    chars = verticalLineTest(tileBoxes)
    for i, box in enumerate(tileBoxes):
        res = getBest(box,chars[i])
        if min([x[1] for x in res]) < 0.7: # if no result has value > 0.7
            grid = grid +'(qxqxq)' #nullifies any chance of using this tile
            continue
        if chars[i] > 1: grid = grid + '('
        for best in res:
            grid = grid + best[0]
        if chars[i] > 1: grid = grid + ')'

    return grid

def checkTile(pos):
    hWnd = pymouse.getWindowHandle()
    res = findGrid(hWnd)
    tileGrid = [[res[1][r*4+c] for c in range(4)] for r in range(4)]
    return _analyzeTile(tileGrid[pos[0]][pos[1]])


def ai():
    hWnd = pymouse.getWindowHandle()
    print 'finding grid...'
    res = findGrid(hWnd)
    print 'reading grid...'
    gridtiles = createGrid(res[1])
    print 'creating grid isntance...'
    newgrid = grid.Grid(gridtiles)
    print 'creating trie instance...'
    t = trie.Trie()
    t.loadFile(DICT_LOC)
    print 'find words...'
    newgrid.findDictionaryWords(t,3)
    print 'entering words...'
    print newgrid.grid
    centerGrid = [[res[0][r*4+c] for c in range(4)] for r in range(4)]
    for word in newgrid.sortedWords:
        dragCords = [centerGrid[x[0]][x[1]] for x in newgrid.words[word]]
        pymouse.drag(dragCords)
        time.sleep(0.2)
    return newgrid


def findGrid(hWnd=None):
    if not hWnd: hWnd = pymouse.getWindowHandle()
    windowBox = pymouse.getWindowBox(hWnd)
##    pyimage.saveBox(windowBox,'android_snap')
    img = pyimage.grabColor(windowBox)
    bbox = img.getbbox()
    boolTile = False
    startPixel = None
    endx = 0
    endy = 0
    x,y = (0,0)

    #find top left of first tile
    for x in xrange(bbox[3]):
        if startPixel is not None: break
        for y in xrange(bbox[2]):
            color = getColor(img.getpixel((x,y)))
            if  color == 'red':
                startPixel = (x,y)
                break
    #find center of tile horizontally and next tile right
    x,y = startPixel
    boolTile = True
    while True:
        x+=1
        color = getColor(img.getpixel((x,y)))
        if boolTile and color != 'red':
            endx = x-1
            boolTile = False
        elif not boolTile and color =='red': #found next tile right
            xdist = x-startPixel[0]
            break

    #find center of tile vertically and next tile down
    x,y = startPixel
    boolTile = True
    while True:
        y+=1
        color = getColor(img.getpixel((x,y)))
        if boolTile and color != 'red':
            endy = y-1
            boolTile = False
        elif not boolTile and color =='red': #found next tile down
            ydist = y-startPixel[1]
            break

    tileBoxes = []
    centers = []

    #convert all coordinates to screen frame
    (endx,endy) = pymouse.clientToScreen(hWnd,(endx,endy))
    startPixel = pymouse.clientToScreen(hWnd,startPixel)

    center = ((endx + startPixel[0])/2,(endy + startPixel[1])/2)
    box = startPixel+(endx,endy)
    for y in range(4):
        for x in range(4):
            centers.append(center)
            tileBoxes.append(box)
            center = (center[0]+xdist,center[1])
            box = (box[0]+xdist,box[1],box[2]+xdist,box[3])
        center = ((endx + startPixel[0])/2,center[1]+ydist)
        box = (startPixel[0],box[1]+ydist,endx,box[3]+ydist)

    i = 0
    for box in tileBoxes:
        pyimage.saveBox(box,'tile'+ str(i))
        i+=1

    return centers, tileBoxes




















