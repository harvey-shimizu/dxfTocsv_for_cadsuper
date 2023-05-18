#!/bin/python/
# cording:cp932

#
#                                                               2022.05.19
#   DXF class
#
#                                                 Author by Hideaki Shimizu
#

import os
import sys
import re
from operator import attrgetter
import dxf

#Default layer configuration of DXF
xTargetLayerCode = 8
# Layer Name for Table Lines
xLayerNameForTableLines = 'Table_Lines'
# Parts Name for Table Lines
xLayerNameForPartsLists = 'Parts_Lists'

#csv data
xDictFromCsv = {}
xDictFromCsv2 = {}

# Morio Matrix Format
xLengthMatrixHorizonal = 178.5
xLengthMatrixVertical  = 7

xSheetLimit_X = 841.0
xSheetLimit_Y = 594.0

xMatrixHeader=\
{'b0':'No', 'b1':'Description', 'b2':'DRG.No', 'b3':'Material', 'b4':'G1', 'b5':'G2', 'b6':'G3', 'b7':'G4', 'b8':'Weight', 'b9':'Remarks'}
xSheetSize=\
{'B6M':{'v':594.0, 'h':841.0}, 'C7M':{'v':420.0, 'h':594.0}, 'D8M':{'v':297.0, 'h':420.0}, 'E9M':{'v':210.0, 'h':297.0}}

# Internal Buffer
xAllData = []

# Error Counts
xErrorCounts = 0

# LIST INDEXES
sHEADER  = 0
sCLASSES = 1
sTABLES  = 2
sLAYER   = 3
sBLOCKS  = 4
sENTITIES= 5
sOBJECTS = 6
sLenTopLAYERS = range(sHEADER,sOBJECTS+1)

sHANDSEED= 0
sCLAYER  = 1
sLenHeadLAYERS = range(sHANDSEED, sCLAYER+1)

sTblOffset  = 3
sVPORT   = 0+sTblOffset
sLTYPE   = 1+sTblOffset
sLAYER   = 2+sTblOffset
sSTYLE   = 3+sTblOffset
sVIEW    = 4+sTblOffset
sUCS     = 5+sTblOffset
sAPPID   = 6+sTblOffset
sDIMSTYLE= 7+sTblOffset
sBLOCKRED= 8+sTblOffset
sLenTableLAYERS = range(sVPORT, sBLOCKRED+1)

sNumHeaderLayer = 6
sNumLayersInHeader = 6
idxNumLayers= sNumLayersInHeader-1

#GROUP CODE
sGC_LYNAME_ENTITY=8

# CONDITIONS
tSECTION =    [(0, "SECTION")]
tENDSEC =     [(0, "ENDSEC")]
tENDTAB =     [(0, "ENDTAB")]
tHEADER =     [(2, "HEADER")]
tCLASSES =    [(2, "CLASSES")]
tTABLES =     [(2, "TABLES")]
tBLOCKS =     [(2, "BLOCKS")]
tBLOCK =      [(0, "BLOCK")]
tENDBLK =     [(0, "ENDBLK")]
tENTITIES =   [(2, "ENTITIES")]
tOBJECTS =    [(2, "OBJECTS")]
tEOF =        [(0, "EOF")]
tLAYERS =     [(2, "LAYER")]
tLAYER =      [(0, "LAYER")]
tTABLE =      [(0, "TABLE")]
tTEXT =       [(0,"TEXT")]

tPRINT_FLAG = [(290, "0")]

# ENTITIE SECTIONS
t3DFACE=             (0,"3DFACE")
t3DSOLID=            (0,"3DSOLID")
tACAD_PROXY_ENTITY=  (0,"ACAD_PROXY_ENTITY")
tARC=                (0,"ARC")
tARCALIGNEDTEXT=     (0,"ARCALIGNEDTEXT")
tATTDEF=             (0,"ATTDEF")
tATTRIB=             (0,"ATTRIB")
tBODY=               (0,"BODY")
tCIRCLE=             (0,"CIRCLE")
tDIMENSION=          (0,"DIMENSION")
tELLIPSE=            (0,"ELLIPSE")
tHATCH=              (0,"HATCH")
tIMAGE=              (0,"IMAGE")
tINSERT=             (0,"INSERT")
tLEADER=             (0,"LEADER")
tLINE=               (0,"LINE")
tLWPOLYLINE=         (0,"LWPOLYLINE")
tMLINE=              (0,"MLINE")
tMTEXT=              (0,"MTEXT")
tOLEFRAME=           (0,"OLEFRAME")
tOLE2FRAME=          (0,"OLE2FRAME")
tPOINT=              (0,"POINT")
tPOLYLINE=           (0,"POLYLINE")
tRAY=                (0,"RAY")
tREGION=             (0,"REGION")
tRTEXT=              (0,"RTEXT")
tSEQEND=             (0,"SEQEND")
tSHAPE=              (0,"SHAPE")
tSOLID=              (0,"SOLID")
tSPLINE=             (0,"SPLINE")
tTOLERANCE=          (0,"TOLERANCE")
tTRACE=              (0,"TRACE")
tVERTEX=             (0,"VERTEX")
tVIEWPORT=           (0,"VIEWPORT")
tWIPEOUT=            (0,"WIPEOUT")
tXLINE=              (0,"XLINE")

tENTITIE_SECTIONS=[\
t3DFACE, t3DSOLID, tACAD_PROXY_ENTITY, tARC, tARCALIGNEDTEXT, tATTDEF, tATTRIB,\
tBODY, tCIRCLE, tDIMENSION, tELLIPSE, tHATCH, tIMAGE, tINSERT, tLEADER, tLINE,\
tLWPOLYLINE, tMLINE, tMTEXT, tOLEFRAME, tOLE2FRAME, tPOINT, tPOLYLINE, tRAY, \
tREGION, tRTEXT, tSEQEND, tSHAPE, tSOLID, tSPLINE, tTEXT, tTOLERANCE, tTRACE,\
tVERTEX, tVIEWPORT, tWIPEOUT, tXLINE]

class cDrawing:

    def __init__(self, fname):
        #self.filename = fname.replace('/', os.sep)
        self.filename = fname
        self.LIMMAX_x = 0
        self.LIMMAX_y = 0
        #self.fbase, self.fcode, self.frev = self.get_head_sfx_and_num(self.filename)
        self.fabrr, self.fbase, self.fcode, self.frev = self.get_head_sfx_and_num(self.filename)
        self.matrix = self.dxf_analysis(self.readfile(self.filename))
        #self.numOfParts = self.matrix.numOfBlocks

    @classmethod
    def get_head_sfx_and_num(cls, filename=""):
        #print(filename)
        #char = re.match(r".*-(?P<base>B6M|C7M|D8M|E9M|MR[DCZ])(?P<code>[0-9]{5})(?P<rev>[A-Z]?[A-Z]?).DXF", filename)
        # Return the basename(group(1 and 2), and alphabet revision(group(3)) of input file.
        char = re.match(r"(\d{2,3}_\d{2,3})_?(?P<abrr>.*)_.*-(?P<base>B6M|C7M|D8M|E9M|MR[DCZ])(?P<code>\d{5})(?P<rev>[A-Z]?[A-Z]?).DXF", os.path.basename(filename))
        if char.group('abrr'):
            return char.group('abrr'), char.group('base'), char.group('code'), char.group('rev')
        else:
            baseCode = char.group('base') + char.group('code')
            if not (baseCode in xDictFromCsv):
                return xDictFromCsv2[baseCode], char.group('base'), char.group('code'), char.group('rev')
            return xDictFromCsv[baseCode], char.group('base'), char.group('code'), char.group('rev')

    def dxf_analysis(self, raw):

        data = xAllData
        self.makeList_xData(data)

        for num, (code, value) in enumerate(zip(raw[::2], raw[1::2]), 1):
            code, value = int(code), value.strip()
            num = num*2-1

            if (code, value) in tSECTION:
                pass
            elif code == 9 and value == '$LIMMAX':
                #print(raw[num], raw[num+2], raw[num+4])
                #$LIMMAX
                self.LIMMAX_x = float(raw[num+2])
                self.LIMMAX_y = float(raw[num+4])
            elif (code, value) in tHEADER:
                LAYER_NAME = sHEADER
                data[LAYER_NAME] = [num-2]
                data[LAYER_NAME].append((0, "SECTION"))
                data[LAYER_NAME].append((code, value))
            elif (code, value) in tCLASSES:
                LAYER_NAME = sCLASSES
                data[LAYER_NAME] = [num-2]
                data[LAYER_NAME].append((0, "SECTION"))
                data[LAYER_NAME].append((code, value))
            elif (code, value) in tTABLES:
                LAYER_NAME = sTABLES
                data[LAYER_NAME] = [num-2]
                data[LAYER_NAME].append((0, "SECTION"))
                data[LAYER_NAME].append((code, value))
            elif (code, value) in tBLOCKS:
                LAYER_NAME = sBLOCKS
                data[LAYER_NAME] = [num-2]
                data[LAYER_NAME].append((0, "SECTION"))
                data[LAYER_NAME].append((code, value))
            elif (code, value) in tENTITIES:
                LAYER_NAME = sENTITIES
                data[LAYER_NAME] = [num-2]
                data[LAYER_NAME].append((0, "SECTION"))
                data[LAYER_NAME].append((code, value))
            elif (code, value) in tOBJECTS:
                LAYER_NAME = sOBJECTS
                data[LAYER_NAME] = [num-2]
                data[LAYER_NAME].append((0, "SECTION"))
                data[LAYER_NAME].append((code, value))
            elif (code, value) in tENDSEC:
                data[LAYER_NAME].append((code, value))
            elif (code, value) in tEOF:
                pass
            else:
                self.input_data(LAYER_NAME, data, code, value)

        if self.LIMMAX_x == 0.0:
            xSheetLimit_X = xSheetSize.get(self.fbase, xSheetSize['B6M']['h'])
        else:
            xSheetLimit_X = self.LIMMAX_x

        if self.LIMMAX_y == 0.0:
            xSheetLimit_Y = xSheetSize.get(self.fbase, xSheetSize['B6M']['v'])
        else:
            xSheetLimit_Y = self.LIMMAX_y

        #print(data)
        self.dxf_tables_analysis(data[sTABLES])
        self.dxf_layers_analysis(data[sTABLES][sLAYER])
        iblk = self.dxf_blocks_analysis(data[sBLOCKS])
        if iblk:
            itxt = self.dxf_entities_analysis(data[sENTITIES])
            iblk.matching_text_with_box(itxt)
        else:
            global xErrorCounts
            xErrorCounts += 1
            print("Tt dosen't have any data or have invalid values.")

        return iblk

    def dxf_tables_analysis(self, tbldata):

        tmpdata = []
        srtTblofst = 0
        endTblofst = 0

        for num, (code, value) in enumerate(tbldata[1::], 0):
            if (code, value) in tTABLE:
                srtTblofst = num
            elif (code, value) in tLAYERS: pass
            elif (code, value) in tLAYER:  pass
            elif (code, value) in tENDTAB:
                endTblofst = num
                tmpdata.append((srtTblofst+1, endTblofst+2))
                tmpdata.append(tbldata[srtTblofst+1:endTblofst+2])
            else: pass

        del tbldata[3:len(tbldata)+1]
        for i, d in zip(tmpdata[::2], tmpdata[1::2]):
            tbldata.append(d)

        tbldata.append(tENDSEC)

    def dxf_layers_analysis(self, lyrdata):

        tmpdata = []
        srtLyrofst = 0
        endLyrofst = 0

        fstLoop = 1
        for num, (code, value) in enumerate(lyrdata[0::],0):
            if (code, value) in tTABLE: pass
            elif (code, value) in tLAYERS: pass
            elif (code, value) in tLAYER:
                if fstLoop == 0:
                    endLyrofst = num-1
                    tmpdata.append((srtLyrofst, endLyrofst+1))
                    tmpdata.append(lyrdata[srtLyrofst:endLyrofst+1])
                    srtLyrofst = num
                else:
                    srtLyrofst = num
                    fstLoop = 0
            elif (code, value) in tENDTAB:
                endLyrofst = num
                tmpdata.append((srtLyrofst, endLyrofst))
                tmpdata.append(lyrdata[srtLyrofst:endLyrofst])
                tmpdata.append((len(lyrdata), len(lyrdata)))
                tmpdata.append(lyrdata[len(lyrdata)-1])
            else: pass

        del lyrdata[sNumHeaderLayer:len(lyrdata)+1]
        for i, d in zip(tmpdata[::2], tmpdata[1::2]):
            lyrdata.append(d)

    def dxf_entities_analysis(self, data):

        target_layer = 0
        target_entitiy = 0
        tmpdata = []
        result = []
        itexts = cTexts()

        # Header is skkipping for data[2::]
        for num, (code, value) in enumerate(data[2::],2):
            if code == 0:
                if target_layer == 1 and target_entitiy == 1:
                    result.append(tmpdata)
                target_layer = target_entitiy = 0
                tmpdata = []
                if value == 'TEXT':
                    target_entitiy = 1
            elif (code, value) in [(xTargetLayerCode, xLayerNameForPartsLists)]:
                target_layer = 1
            tmpdata.append((code, value))

        for text in result:
            #print(text)
            itexts.set_texts(self.initializing_text_param(text))

        return itexts

    def initializing_text_param(self, texts):

        itext = cText()
        for (code, value) in texts:
            if code == 10 or code == 20 or code == 30: #Start position
                itext.set_txt_coordination(code, value)
            elif code == 11 or code == 21:
                itext.set_txt_coordination(code, value)
            elif code == 40:
                itext.set_txt_coordination(code, value)
            elif code == 1:
                itext.set_txt_coordination(code, value)
            else:
                pass
        return itext


    def dxf_blocks_analysis(self, data):

        target_layer = 0
        result = []
        tmpdata = []
        iblocks = cBlocks()

        # Header is skkipping for data[1::]
        for num, (code, value) in enumerate(data[1::], 0):
            if (code, value) in tBLOCK:
                tmpdata = []
                target_layer = 0
                tmpdata.append((code, value))
            elif (code, value) in tENDBLK:
                if target_layer == 1:
                    result.append(tmpdata)
                    tmpdata.append((code, value))
            else:
                if code == xTargetLayerCode and value == xLayerNameForTableLines:
                    target_layer = 1
                tmpdata.append((code, value))

        for block in result:
            # Walus expression supported from Python3.8
            if not (b := self.initializing_block_param(block)) == None:
                #print(block)
                iblocks.set_blocks(b)
            else:
                #print('Invalid format')
                pass

        return iblocks

    def initializing_block_param(self, block):

        iblock = cBlock()
        line_flag = 0
        for (code, value) in block:
            if (code, value) in tBLOCK:
                pass
            elif code == 2: # Block name
                iblock.set_name(value)
            elif code == 0 and value == "LINE":
                iline = cLine()
                line_flag = 1 # Line part is startting
            elif line_flag == 1:
                if code == 10 or code == 20 or code == 30: #Start position
                    iline.set_line_coordination(code, value)
                elif code == 11 or code == 21: #End position
                    iline.set_line_coordination(code, value)
                elif code == 31: #End position
                    iline.set_line_coordination(code, value)
                    if not iblock.set_lines(iline):
                        return None
            elif (code, value) in tENDBLK:
                pass
            else:
                pass

        return iblock

    def makeList_xData(self, xAllData):

        for i in sLenTopLAYERS:
            xAllData.append([])

    def input_data(self, LAYER_NAME, data, code, value):

        if LAYER_NAME == sHEADER:
            data[LAYER_NAME].append((code, value))
        elif LAYER_NAME == sCLASSES:
            data[LAYER_NAME].append((code, value))
        elif LAYER_NAME == sTABLES:
            data[LAYER_NAME].append((code, value))
        elif LAYER_NAME == sBLOCKS:
            data[LAYER_NAME].append((code, value))
        elif LAYER_NAME == sENTITIES:
            data[LAYER_NAME].append((code, value))
        elif LAYER_NAME == sOBJECTS:
            data[LAYER_NAME].append((code, value))
        elif (code, value) in tENDSEC:
            LAYER_NAME = ""
        else:
            pass

    def readfile(self, ifile):
        with open(ifile, "r", encoding="cp932") as f:
            line = f.readlines()
        return line

class cTexts:

    def __init__(self):
        self.texts = []
        self.num = 0

    def set_texts(self, text):
        self.texts.append(text)

class cText:

    def __init__(self):
        #Line Name
        self.name = None
        #Contents
        self.content = None
        #Position of Line
        self.start_x = 0
        self.start_y = 0
        self.center_x = 0
        self.center_y = 0
        self.hight = 0

    def set_txt_coordination(self, code, value):
        if code != 40 and code != 1:
            value = round(float(value), 2)
        if code == 10 and value <= xSheetLimit_X:
            self.start_x = value
        elif code == 20 and value <= xSheetLimit_Y:
            self.start_y = value
        elif code == 30:
            pass
        elif code == 40:
            self.hight = value
        elif code == 1:
            self.content = str(value)
        elif code == 11 and value <= xSheetLimit_X:
            self.center_x = value
        elif code == 21 and value <= xSheetLimit_Y:
            self.center_y = value
        elif code == 31:
            pass
        else:
            pass

class cLine:

    def __init__(self):
        #Line Name
        self.name = None
        #Length of Line
        self.length_x = 0
        self.length_y = 0
        #Position of Line
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

    def __lt__(self, other):
        self.start_x < other.start_x

    def set_line_coordination(self, code, value):
        value = round(float(value), 2)
        if code == 10 and value <= xSheetLimit_X:
            self.start_x = value
        elif code == 20 and value <= xSheetLimit_Y:
            self.start_y = value
        elif code == 30:
            pass
        elif code == 11 and value <= xSheetLimit_X:
            self.end_x = value
        elif code == 21 and value <= xSheetLimit_Y:
            self.end_y = value
        elif code == 31:
            pass
        else:
            pass

class cBox:

    def __init__(self, name, x, y, x2, y2):
        self.name = name
        self.leftLimit  = {'x':x, 'y':y}
        self.rightLimit = {'x':x2, 'y':y2}
        self.contents = []

    def set_contents_for_box(self, contents):
        self.contents.append(contents)

class cBlock:

    def __init__(self):
        self.hLines = []
        self.vLines = []
        self.name = None
        self.leftUpper  = {'x':0, 'y':0}
        self.rightLower = {'x':0, 'y':0}
        self.boxies = []

    def set_name(self, name):
        self.name = name

    def set_lines(self, line):
        if (self.configure_line(line)):
            if line.name == 'h':
                self.hLines.append(line)
            elif line.name == 'v':
                self.vLines.append(line)
            else:
                # never run under the code.
                return 0
        else:
            #print("Invalid format:", self.name)
            return 0
        return 1

    def configure_line(self, line):
        line.length_x = line.end_x - line.start_x
        if line.length_x < 0:
            #Swapping if value is negative
            tmp = line.end_x; line.end_x = line.start_x; line.start_x = tmp
            line.length_x = line.end_x - line.start_x
        line.length_y = line.end_y - line.start_y
        if line.length_y < 0:
            #Swapping if value is negative
            tmp = line.end_y; line.end_y = line.start_y; line.start_y = tmp
            line.length_y = line.end_y - line.start_y
        # Setting Line name
        if line.length_x == xLengthMatrixHorizonal:
            # Horizontal
            line.name = 'h'
            return 1
        elif line.length_y == xLengthMatrixVertical:
            # Vertical
            line.name = 'v'
            return 1
        else:
            # Unknown for an invalid format
            line.name = 'u'
            return 0

class cBlocks:

    def __init__(self):
        # List of instance for Block class
        self.iblk = []
        self.numObBlocks = 0
        self.name = None

    def set_blocks(self, block):
        self.configure_block(block)
        self.iblk.append(block)
        self.numOfBlocks = len(self.iblk)

    def configure_block(self, block):
        if block.vLines:
            # Sorting vertical Lines
            block.vLines.sort(key=attrgetter('start_x'))
            #print(block.vLines)

            # Registration of range of Block
            block.leftUpper['x']  = block.vLines[0].end_x
            block.leftUpper['y']  = block.vLines[0].end_y
            block.rightLower['x'] = block.vLines[-1].start_x
            block.rightLower['y'] = block.vLines[-1].start_y

            # Sorting horizontal Lines
            block.hLines.sort(key=attrgetter('start_y'))

            for l, n in zip(block.vLines, range(len(block.vLines)-1)):
                b = cBox('b'+str(n), l.end_x, l.end_y, block.vLines[n+1].start_x, block.vLines[n+1].start_y)
                block.boxies.append(b)

    def matching_text_with_box(self, itext):
        for b in self.iblk:
            for b2 in b.boxies:
                for txt in itext.texts:
                    if     b2.leftLimit['x']  < txt.center_x and b2.leftLimit['y']  > txt.center_y \
                       and b2.rightLimit['x'] > txt.center_x and b2.rightLimit['y'] < txt.center_y:
                           b2.set_contents_for_box(txt.content)
                # Sorted by strings in the list of Descriptions.
                b2.contents.sort()
        try:
            # Deleted data in the iblk list if the contents is None.
            self.iblk = [ b for b in self.iblk if len(b.boxies[0].contents) != 0]
        except IndexError:
            global xErrorCounts
            xErrorCounts =+ 1
            print("Tt dosen't have any data or have invalid values.")
        else:
            # Sorted by No(int) in the list of No.
            self.iblk.sort(key=lambda x:int(x.boxies[0].contents[0]))

def flatten(lis):
    """Given a list, possibly nested to any level, return it flattened."""
    new_lis = []
    for item in lis:
        if type(item) == type([]):
            new_lis.extend(flatten(item))
        else:
            new_lis.append(item)
    return new_lis


def writefile(ofile):
    return open(ofile, "w", encoding="cp932")

def chkGroupID (line, pattern):
    if re.search(pattern, line):
        return True
    return False

if __name__ == "__main__":

    args = sys.argv
    filename = args.pop(0)
    raw = readfile(args[0])
    d = cDrawing(filename, dxf_analysis(raw))

    print(d.numOfLine)
    for n, b in enumerate(d.matrix.iblk, 1):
        print(n, b.boxies[0].contents[0])
