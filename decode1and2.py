#!/usr/bin/env python

import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('jsFilePath', help='Path to the GOOTLOADER JS file.')
args = parser.parse_args()

def ConvertVarsToDict(var_matches):
    var_dict = {}
    for var_name, value in var_matches:
        var_dict[var_name] = value
    return var_dict

def convertConcatToString(concat_matches, var_dict):
    concatenated_result = ''
    for match in concat_matches:
        if '=' not in match:
            continue
        try:
            var_name, expression = match.split('=')
            var_name, expression = var_name.strip(), expression.strip()
            current_concat = ''.join(var_dict.get(item.strip(), '') for item in expression.split('+'))
            var_dict[var_name] = current_concat
            concatenated_result = current_concat
        except ValueError:
            continue
    return concatenated_result

def decodeString(encoded_text):
    decoded_result = ''
    for i, char in enumerate(encoded_text):
        decoded_result = char + decoded_result if i % 2 == 0 else decoded_result + char
    return decoded_result

def getGootVersion(topFileData):
    goot3pattern = re.compile(r'GOOT3', re.MULTILINE)
    if re.search(r'jQuery JavaScript Library v\d{1,}\.\d{1,}\.\d{1,}$', topFileData):
        return False, False
    elif goot3pattern.match(topFileData):
        return True, True
    else:
        return True, False

def parseRound2Data(round2InputStr, round1InputStr, variablesDict, isGootloader3sample):
    if round2InputStr.startswith('function'):
        global goot3detected
        goot3detected = True
        return 'GOOT3\n' + invokeStage2Decode(round2InputStr, variablesDict), 'GootLoader3Stage2.js_'
    else:
        if isGootloader3sample:
            outputCode = round2InputStr.replace("'+'",'').replace("')+('",'').replace("+()+",'').replace("?+?",'')
            if 'sptth' in outputCode:
                outputCode = outputCode[::-1]
            return outputCode, 'DecodedJsPayload.js_'
        else:
            return round2InputStr, 'DecodedJsPayload.js_'

def getDataToDecode(isGloader21Sample, inputData):
    if isGloader21Sample:
        return inputData
    findObfuscatedPattern = re.compile(r'((?<=\t)|(?<=\;))(.{800,})(\n.*\=.*\+.*)*')
    return findObfuscatedPattern.search(inputData)[0].replace("\n", " ").replace("\r", " ")

def gootDecode(path):
    with open(path, mode="r", encoding="utf-8") as file:
        fileTopLines = ''.join(file.readlines(5))
        gootloader21sample, gootloader3sample = getGootVersion(fileTopLines)
        file.seek(0)
        fileData = file.read()

    dataToDecode = getDataToDecode(gootloader21sample, fileData)
    var_pattern = re.compile(r"""^([a-zA-Z0-9_]+)\s*=\s*['"](.*?)['"]\s*;""", re.MULTILINE)
    concat_pattern = re.compile(r"""^([a-zA-Z0-9_]+)\s*=\s*(?:[a-zA-Z0-9_]+\s*\+\s*)+[a-zA-Z0-9_]+\s*;""", re.MULTILINE)
    
    var_matches = var_pattern.findall(dataToDecode)
    var_dict = ConvertVarsToDict(var_matches)

    concat_matches = concat_pattern.findall(dataToDecode)
    Obfuscated1Text = convertConcatToString(concat_matches, var_dict)

    round1Result = decodeString(Obfuscated1Text)
    CodeMatch = re.findall(r"(?<!\\)(?:\\\\)*'([^'\\]*(?:\\.[^'\\]*)*)'", round1Result)[0]

    round2Result = decodeString(CodeMatch.encode('raw_unicode_escape').decode('unicode_escape'))
    round2Code, round2FileName = parseRound2Data(round2Result, round1Result, var_dict, gootloader3sample)

    with open(round2FileName, mode="w") as file:
        file.write(round2Code)

gootDecode(args.jsFilePath)

if 'goot3detected' in globals() and goot3detected:
    gootDecode('GootLoader3Stage2.js_')
