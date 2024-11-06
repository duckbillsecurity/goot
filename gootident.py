
#!/usr/bin/env python

import argparse
import re

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('jsFilePath', help='Path to the GOOTLOADER JS file.')
args = parser.parse_args()

def getGootVersion(topFileData):
    goot3linesRegex = """GOOT3"""
    goot3linesPattern = re.compile(goot3linesRegex, re.MULTILINE)
    
    gloader3sample = False
    gloader21sample = False
    
    if re.search(r'jQuery JavaScript Library v\d{1,}\.\d{1,}\.\d{1,}$', topFileData):
        print('GootLoader Obfuscation Variant 2.0 detected')
        gloader21sample = False
    elif goot3linesPattern.match(topFileData):
        print('GootLoader Obfuscation Variant 3.0 detected')
        gloader3sample = True
        gloader21sample = True
    else:
        print('GootLoader Obfuscation Variant 2.1 or higher detected')
        gloader21sample = True
    
    return gloader21sample, gloader3sample

def gootDecode(path):
    # Open file and read first few lines to detect obfuscation variant
    with open(path, mode="r", encoding="utf-8") as file:
        fileTopLines = ''.join(file.readlines(5))
        getGootVersion(fileTopLines)

# Run detection
gootDecode(args.jsFilePath)
