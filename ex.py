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
import csv

# Setting Dxf layers for PartsList and TableLines.
dxf.xLayerNameForTableLines = '表題、部品表_02'
dxf.xLayerNameForPartsLists = '表題、部品表_03'


if __name__ == "__main__":

    args = sys.argv
    ltmpdf = []
    #for a in args:
    #    print(a)

    # Make the dictionary from CSV file in mylib/r211_e.csv
    f = open('./mylib/r211_e.csv', 'r',encoding="utf-8_sig")
    for rows in csv.reader(f):
        dxf.xDictFromCsv.update({rows[0]:rows[1]})
        dxf.xDictFromCsv2.update({rows[2]:rows[1]})

    #print(dxf.xDictFromCsv)
    #print(dxf.xDictFromCsv2)

    #exit()

    countUp = 0
    # An array to keep a filename that doesn't have any parts.
    notAnyParts = [];
    for n, f in enumerate(t.tqdm(args[1:], 0, ncols=100)):
        #print(str(n) + "\t: " + f) //For debug
        d = dxf.cDrawing(f)
        d2 = []
        for m, b in enumerate(d.matrix.iblk, 0):
            d1 = {'Abrr':d.fabrr, 'File':d.fbase+d.fcode+d.frev}
            for box in b.boxies:
                if '' in box.contents:
                    box.contents = [c for c in box.contents if ''!=c]
                #for debug
                #print(box.name, box.contents)
                d1[dxf.xMatrixHeader[box.name]] = ','.join(box.contents)
            d2.append(d1)
        if not d2:
            notAnyParts.append(f)
            #print("It doesn't have any parts!: ", f)

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

    # Making output file in the current directory
    outputFileName = t + "_" + 'partsList.xlsx'
    print(os.getcwd() + "\\" + outputFileName)

    # Making a file with the name above, formatting it to Excel.
    with pd.ExcelWriter(outputFileName) as writer:
        df.to_excel(writer, sheet_name='Parts Lists', index=None)

    if (countUp - dxf.xErrorCounts) == len(args[1:]):
        print(str(countUp) + " files have been processed.")
    else:
        print("Errors have happened in some files.(" + str(dxf.xErrorCounts) + ")")

    print("Here are files that don't have any parts.")
    for f in notAnyParts:
        print(f)
    print("**** Please check if they are correct! ****")
