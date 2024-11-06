import argparse
import re

# Argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('jsFilePath', help='Path to the GOOTLOADER JS file.')
args = parser.parse_args()

goot3detected = False

def defang(input):
    if not input.strip():
        return input
    
    start = input
    end = ""
    ignoreNext = False
    for i, _ in enumerate(input):
        if ignoreNext:
            ignoreNext = False
            continue
        
        if input[i] == '/':
            if (i + 1) < len(input) and input[i + 1] == '/':
                ignoreNext = True
                continue
            
            start = input[:i]
            end = input[i:]
            break
    
    result = re.compile(r"([^\[])\.([^\]])").sub(r"\1[.]\2", start) + end
    result = re.compile(r"([^\[]):([^\]])").sub(r"\1[:]\2", result)
    if result.lower().startswith("http"):
        result = result.replace("https", "hxxps")
        result = result.replace("http", "hxxp")
    return result

def ConvertVarsToDict(inArray):
    varDict = {}
    for arItem in inArray:
        varDict.update({arItem[0]: arItem[1]})
    return varDict

def convertConcatToString(inputConcatMatches, inputVarsDict, noEquals=False):
    if noEquals:
        dummyEquals = 'dummy=' + inputConcatMatches.replace('(', '').replace(')', '')
        inputConcatMatches = [dummyEquals]
    
    for index, concatItem in enumerate(inputConcatMatches):
        splitItem = re.sub(r'[;\s\(\)]', '', concatItem).split('=')
        currentLineString = ''
        for additionItem in splitItem[1].split('+'):
            try:
                currentLineString += inputVarsDict[additionItem]
            except:
                continue
            
        if index != len(inputConcatMatches) - 1:
            inputVarsDict.update({splitItem[0]: currentLineString})
        else:
            return currentLineString.encode('raw_unicode_escape').decode('unicode_escape')

def decodeString(scripttext):
    ans = ""
    for i in range(0, len(scripttext)):
        if i % 2 == 1:
            ans += scripttext[i]
        else:
            ans = scripttext[i] + ans
    return ans

def rotateSplitText(string, count):
    for i in range(count + 1):
        string = string[1:] + string[0]
    return str(string)

def remainder(v1, v2, v3):
    if(v3 % (3 - 1)):
        rtn = v1 + v2
    else:
        rtn = v2 + v1
    return rtn

def rtrSub(inputStr, idx1): 
    return inputStr[idx1:(idx1 + 1)]

def workFunc(inputStr):
    outputStr = ''
    for i in range(len(inputStr)):
        var1 = rtrSub(inputStr, i)
        outputStr = remainder(outputStr, var1, i)
    return outputStr

def findFileInStr(fileExtension, stringToSearch):
    fileExtensionPattern = re.compile(r'''["']([a-zA-Z0-9_\-\s]+\.''' + fileExtension + r''')["']''')
    regexMatch = fileExtensionPattern.search(stringToSearch)
    if regexMatch:
        dataFound = regexMatch.group(1)
    else:
        dataFound = 'NOT FOUND'
    return dataFound

def getGootVersion(topFileData):
    goot3linesRegex = r"""GOOT3"""
    goot3linesPattern = re.compile(goot3linesRegex, re.MULTILINE)
    gloader3sample = False
    gloader21sample = False
    if re.search(r'jQuery JavaScript Library v\d+\.\d+\.\d+$', topFileData):
        print('\nGootLoader Obfuscation Variant 2.0 detected')
        gloader21sample = False
    elif goot3linesPattern.match(topFileData):
        print('\nGootLoader Obfuscation Variant 3.0 detected\n\nIf this fails try using CyberChef "JavaScript Beautify" against the file first.')
        gloader3sample = True
        gloader21sample = True
    else:
        print('\nGootLoader Obfuscation Variant 2.1 or higher detected')
        gloader21sample = True
    return gloader21sample, gloader3sample

def getFileandTaskData(inputString):
    if 'noitcnuf' in inputString:
        inputString = inputString[::-1]
    
    splitTextPattern = re.compile(r'''["']((?:.{3,30}?\|.{3,30}){5,})["'];''')
    try:
        splitTextArray = splitTextPattern.search(inputString).group(1).split('|')
    except:
        splitTextPattern = re.compile(r'''["']((?:.{3,30}?\@.{3,30}){5,})["'];''')
        splitTextArray = splitTextPattern.search(inputString).group(1).split('@')
    
    fixedStrings = []
    for i in range(len(splitTextArray)):
        fixedStrings.append(rotateSplitText(splitTextArray[i], i))
    
    for fixedString in fixedStrings:
        if fixedString.endswith('.log') or fixedString.endswith('.dat'):
            s2FirstFileName = fixedString
        elif fixedString.endswith('.js'):
            s2JsFileName = fixedString
    
    if 's2FirstFileName' not in locals():
        s2FirstFileName = findFileInStr('(?:log|dat)', inputString)
    if 's2JsFileName' not in locals():
        s2JsFileName = findFileInStr('js', inputString)
    
    taskCreationRegexPattern = re.compile(r'''\((\w+),\s?(\w+),\s?6,\s['"]{2}\s?,\s?['"]{2}\s?,\s?3\s?\)''')
    taskCreationVarname = taskCreationRegexPattern.search(inputString).group(1)
    taskNameOffsetPattern = re.compile(r'''\}''' + taskCreationVarname + r'''\s?=\s\w{1,2}\((\d{1,3})\);''')
    taskNameOffsetMatch = taskNameOffsetPattern.search(inputString)
    
    if taskNameOffsetMatch:
        taskNameOffset = int(taskNameOffsetMatch.group(1))
        scheduledTaskName = fixedStrings[taskNameOffset]
    else:
        taskNameStrPattern = re.compile(r'''\}''' + taskCreationVarname + r'''\s?=\s"(.{10,232})";''')
        taskNameStrMatch = taskNameStrPattern.search(inputString)
        if taskNameStrMatch:
            scheduledTaskName = taskNameStrMatch.group(1)
        else:
            scheduledTaskName = 'NOT FOUND'
    
    Stage2Data = 'File and Scheduled task data:\n'
    FileTaskFileName = 'FileAndTaskData.txt'
    Stage2Data += '\nFirst File Name:       ' + s2FirstFileName
    Stage2Data += '\nJS File Name:          ' + s2JsFileName
    Stage2Data += '\nScheduled Task Name:   ' + scheduledTaskName
    
    with open(FileTaskFileName, mode="w") as file:
        file.write(Stage2Data)
    
    Stage2Data += '\n\nData Saved to: ' + FileTaskFileName
    print('\n' + Stage2Data + '\n')

def invokeStage2Decode(inputString, inputVarsDict):
    v3workFuncVarsPattern = re.compile(r'''(?:\((?:[a-zA-Z0-9_]{2,}\s*\+\s*){1,}[a-zA-Z0-9_]{2,}\s*\))''')
    v3WorkFuncVars = v3workFuncVarsPattern.search(inputString)[0]
    stage2JavaScript = workFunc(convertConcatToString(v3WorkFuncVars, inputVarsDict, True))
    strVarPattern = re.compile(
        r'''([a-zA-Z0-9_]{2,}\s*=(["'])((?:\\\2|(?:(?!\2)).)*)(\2);)(?=([a-zA-Z0-9_]{2,}\s*=)|function)'''
    )
    strVarsNewLine = re.sub(strVarPattern, r'\n\1\n', stage2JavaScript)
    strConcPattern = re.compile(
        r'''([a-zA-Z0-9_]{2,}\s*=\s*(?:[a-zA-Z0-9_]{2,}\s*\+\s*){1,}[a-zA-Z0-9_]{2,}\s*;)'''
    )
    strConcatNewLine = re.sub(strConcPattern, r'\n\1\n', strVarsNewLine)
    finalStrConcPattern = re.compile(
        r'''([a-zA-Z0-9_]{2,}\s*=\s*(?:[a-zA-Z0-9_]{2,}\s*\+\s*){5,}[a-zA-Z0-9_]{2,}\s*;)'''
    )
    finalStrConcNewLine = re.sub(finalStrConcPattern, r'\n\t\1\n', strConcatNewLine)
    strVar1to1Pattern = re.compile(
        r'''((?:\n|^)[a-zA-Z0-9_]{2,}\s*=\s*[a-zA-Z0-9_]{2,};)'''
    )
    str1to1NewLine = re.sub(strVar1to1Pattern, r'\n\1\n', finalStrConcNewLine)
    strLongDigitPattern = re.compile(r''';(\d{15,};)''')
    finalRegexStr = re.sub(strLongDigitPattern, r';\n\1\n', str1to1NewLine)
    outputString = []
    for line in finalRegexStr.splitlines():
        if line.strip():
            outputString.append(line)
    outputString = '\n'.join(outputString)
    return outputString

def findCodeMatchInRound1Result(inputStr):
    findCodeinQuotePattern = re.compile(r"(?<!\\)(?:\\\\)*'([^'\\]*(?:\\.[^'\\]*)*)'")
    outputStr = findCodeinQuotePattern.findall(inputStr)[0]
    return outputStr

def getVariableAndConcatPatterns(isGloader21Sample):
    if isGloader21Sample:
        varPattern = re.compile(
            r"""(?:^([a-zA-Z0-9_]{2,})\s*=\s*'(.*)'\s*;)|""" +
            r"""(?:^([a-zA-Z0-9_]{2,})\s*=\s*"(.*)"\s*;)|""" +
            r"""(?:^([a-zA-Z0-9_]{2,})\s*=\s*(\d+);)""", re.MULTILINE
        )
        concPattern = re.compile(
            r"""(?:^[a-zA-Z0-9_]{2,}\s*=\s*(?:\(?[a-zA-Z0-9_]{2,}\)?\s*(?:\+|\-)\s*){1,}\(?[a-zA-Z0-9_]{2,}\)?\s*;)|""" +
            r"""(?:^[a-zA-Z0-9_]{2,}\s*=\s*[a-zA-Z0-9_]{2,}\s*;)""", re.MULTILINE
        )
    else:
        varPattern = re.compile(
            r"""(?:([a-zA-Z0-9_]{2,})\s*=\s*'(.+?)'\s*;)|""" +
            r"""(?:([a-zA-Z0-9_]{2,})\s*=\s*"(.+?)"\s*;)""", re.MULTILINE
        )
        concPattern = re.compile(
            r"""(?:[a-zA-Z0-9_]{2,}\s*=\s*(?:[a-zA-Z0-9_]{2,}\s*\+\s*){1,}[a-zA-Z0-9_]{2,}\s*;)|""" +
            r"""(?:[a-zA-Z0-9_]{2,}\s*=\s*[a-zA-Z0-9_]{2,}\s*;)""", re.MULTILINE
        )
    return varPattern, concPattern

def getDataToDecode(isGloader21Sample, inputData):
    if isGloader21Sample:
        outputData = inputData
    else:
        findObfuscatedPattern = re.compile(r'''((?<=\t)|(?<=\;))(.{800,})(\n.*\=.*\+.*)*''')
        outputData = findObfuscatedPattern.search(inputData)[0].replace("\n", " ").replace("\r", " ")
    return outputData

def parseRound2Data(round2InputStr, round1InputStr, variablesDict, isGootloader3sample):
    if round2InputStr.startswith('function'):
        print('GootLoader Obfuscation Variant 3.0 sample detected.')
        try:
            getFileandTaskData(decodeString(round1InputStr.encode('raw_unicode_escape').decode('unicode_escape')))
        except:
            print('Unable to parse Scheduled Task and Second Stage File Names')
        global goot3detected
        goot3detected = True
        outputCode = 'GOOT3\n' + invokeStage2Decode(round2InputStr, variablesDict)
        outputFileName = 'GootLoader3Stage2.js_'
        print('\nScript output Saved to: %s\n' % outputFileName)
        print('\nThe script will now attempt to deobfuscate the %s file.' % outputFileName)
    else:
        if isGootloader3sample:
            outputCode = round2InputStr.replace("'+'", '').replace("')+('", '').replace("+()+", '').replace("?+?", '')
            if 'sptth' in outputCode:
                outputCode = outputCode[::-1]
            v3DomainRegex = re.compile(r'''(?:(?:https?):\/\/)[^\[|^\]|^\/|^\\|\s]*\.[^'"]+''')
            maliciousDomains = re.findall(v3DomainRegex, outputCode)
        else:
            outputCode = round2InputStr
            v2DomainRegex = re.compile(r'(.*)(\[\".*?\"\])(.*)')
            domainsMatch = v2DomainRegex.search(round2InputStr)[2]
            maliciousDomains = domainsMatch.replace("[", "").replace("]", "").replace("\"", "").replace("+(", "").replace(")+", "").split(',')
        outputFileName = 'DecodedJsPayload.js_'
        print('\nScript output Saved to: %s\n' % outputFileName)
        outputDomains = ''
        for dom in maliciousDomains:
            outputDomains += defang(dom) + '\n'
        print('\nMalicious Domains: \n\n%s' % outputDomains)
    return outputCode, outputFileName

def gootDecode(path):
    with open(path, mode="r", encoding="utf-8") as file:
        fileTopLines = ''.join(file.readlines(5))
        gootloader21sample, gootloader3sample = getGootVersion(fileTopLines)
        file.seek(0)
        fileData = file.read()
    
    dataToDecode = getDataToDecode(gootloader21sample, fileData)
    variablesPattern, concatPattern = getVariableAndConcatPatterns(gootloader21sample)
    variablesAllmatches = variablesPattern.findall(dataToDecode)
    VarsDict = ConvertVarsToDict(variablesAllmatches)
    concatAllmatches = concatPattern.findall(dataToDecode)
    if gootloader21sample:
        lastConcatPattern = re.compile(
            r"""(?:^\t[a-zA-Z0-9_]{2,}\s*=(?:\s*[a-zA-Z0-9_]{2,}\s*\+?\s*){5,}\s*;)""", re.MULTILINE
        )
        concatAllmatches += list(sorted(lastConcatPattern.findall(fileData), key=len))
    Obfuscated1Text = convertConcatToString(concatAllmatches, VarsDict)
    round1Result = decodeString(Obfuscated1Text)
    CodeMatch = findCodeMatchInRound1Result(round1Result)
    round2Result = decodeString(CodeMatch.encode('raw_unicode_escape').decode('unicode_escape'))
    round2Code, round2FileName = parseRound2Data(round2Result, round1Result, VarsDict, gootloader3sample)
    with open(round2FileName, mode="w") as file:
        file.write(round2Code)

gootDecode(args.jsFilePath)

if 'goot3detected' in globals() and goot3detected:
    gootDecode('GootLoader3Stage2.js_')
