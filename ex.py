#!/bin/python/
# cording:cp932

#
#                                                               2022.05.19
#   Program for extracting parts list from DXF file.
#
#                                                 Written by Harvey Shimizu
#

import os
import sys
import re
import datetime

import tqdm as t
from collections import OrderedDict

sys.path.append(os.path.join(os.path.dirname(__file__), './mylib'))
import dxf

import pandas as pd
pd.set_option('display.unicode.east_asian_width', True)
import numpy as np

# Setting Dxf layers for PartsList and TableLines.
dxf.xLayerNameForTableLines = '表題、部品表_02'
dxf.xLayerNameForPartsLists = '表題、部品表_03'

if __name__ == "__main__":

    args = sys.argv
    ltmpdf = []
    #for a in args:
    #    print(a)

    #exit()

    countUp = 0
    for n, f in enumerate(t.tqdm(args[1:], 0, ncols=100)):
        #print(str(n) + "\t: " + f) //For debug
        d = dxf.cDrawing(f)
        d2 = []
        for m, b in enumerate(d.matrix.iblk, 0):
            d1 = {'file':d.fbase+d.fcode+d.frev}
            for box in b.boxies:
                #print(box.contents)
                d1[dxf.xMatrixHeader[box.name]] = ','.join(box.contents)
            d2.append(d1)

        ltmpdf.append(pd.DataFrame.from_dict(d2))
        countUp += 1

    # Joined all dataframes.
    df = pd.concat(ltmpdf)

    #pd.set_option('display.max_columns', 100)
    #pd.set_option('display.max_rows', 5000)

    # Formatting Time Info
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    t = now.strftime('%Y%m%d%H%M%S')

    outputFileName = t + "_" + 'partsList.xlsx'
    print(os.getcwd() + "\\" + outputFileName)

    with pd.ExcelWriter(outputFileName) as writer:
        df.to_excel(writer, sheet_name='Parts Lists', index=None)

    if (countUp - dxf.xErrorCounts) == len(args[1:]):
        print(str(countUp) + " files have been processed.")
    else:
        print("Errors have happened in some files.(" + str(dxf.xErrorCounts) + ")")

