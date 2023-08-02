import json
import pyparsing
import codecs
import shutil
import os.path
import sys

system = 'win' #'linux', 'win'
services = ['WebApi', 'RobotLogs', 'Notifications', 'MachineInfo', 'RDP2', 'States'] #'WebApi', 'RobotLogs', 'Notifications', 'States', 'MachineInfo', 'RDP2'
commentStarts = ['// ', '//"', '//en', '//ru', '//Post', '//MS', '//mzL', '//}', '//Win', '//Адреса', '//,']
exceptedText1 = ['/// Настройки дефолтного тенанта']
versions = ['2.2.26.0', '1.23.1.1', '1.23.2.0', '1.23.4.0', '1.23.5.0', '1.23.6.0', '1.23.7.0']

flagRDP = False

sys.stdout = open('output.txt', 'w')

def prepareFiles(text):
    for et in exceptedText1:
        text = text.replace(et, '')
    comment = pyparsing.nestedExpr("/*", "*/").suppress()
    text = comment.transformString(text)
    for cs in commentStarts:
        comment = cs + pyparsing.rest_of_line
        text = comment.suppress().transform_string(text)
    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip() != '']
    text = '\n'.join(non_empty_lines)
    text = text.replace('\\', '\\\\')
    return text

def readConfigFirst(file):
    level = 0
    for elementKey in file:
        path = []
        element = file[elementKey]
        path.append(elementKey)
        printTestInfo(path, level, elementKey, element)
        if type(element) == dict:
            readConfigDict(element, path, (level + 1))
        if type(element) == list:
            readConfigList(element, path, level)
        if type(element) == str:
            exec(jsonPathGenerator('blank', path, element))

def readConfigDict(fileFragment, path, level):
    for elementKey in fileFragment:
        element = fileFragment[elementKey]
        path = pathLengthCheck(path, level)
        path.append(elementKey)
        printTestInfo(path, level, elementKey, element)
        if type(element) == dict:
            readConfigDict(element, path, (level + 1))
        if type(element) == list:
            readConfigList(element, path, (level + 1))
        if type(element) == str:
            exec(jsonPathGenerator('blank', path, element))

def readConfigList(fileFragment, path, level):
    for elementListIndex in range(len(fileFragment)):
        element = fileFragment[elementListIndex]
        path = pathLengthCheck(path, level)
        path.append(elementListIndex)
        printTestInfo(path, level, elementListIndex, element)
        # if type(element) != dict and type(element) != list:
        #     break
        if type(element) == dict:
            readConfigDict(element, path, (level + 1))
        if type(element) == list:
            readConfigList(element, path, (level + 1))
        if type(element) == str:
            exec(jsonPathGenerator('blank', path, element))

def pathLengthCheck(path, level):
    if len(path) >= level:
        del path[level:]
    return path

def printTestInfo(path, level, key, fileFragment):
#     print('Level:', level)
#     print('Path:', path)
    print('Read json key:', key)
#     print(type(fileFragment))
    if type(fileFragment) != dict and type(fileFragment) != list:
        print('Set value:', fileFragment)
    print('-------------------------------------------------')

def jsonPathGenerator(fileName, path, value):
    for pathElement in path:
        if type(pathElement) == int:
            fileName = fileName + '[' + str(pathElement) + ']'
        else:
            fileName = fileName + '["' + str(pathElement) + '"]'
    fileName = fileName + ' = "' + str(value) + '"'
    return fileName

def filePathGenerator(system, service, type):
    if system == 'win':
        if type == 'old':
            path = service + '-old\\\\appsettings.ProdWin.json'
        elif type == 'new':
            path = service + '\\\\appsettings.ProdWin.json'
    elif system == 'linux':
        if type == 'old':
            path = service + '-old/appsettings.ProdLinux.json'
        elif type == 'new':
            path = service + '/appsettings.ProdLinux.json'
    return path

def getVersion(type):
    if type == 'old':
        with open('WebApi-old/Readme.txt', 'r') as file:
            readme = file.read()
    elif type == 'new':
        with open('WebApi/Readme.txt', 'r') as file:
            readme = file.read()
    for readmeLine in readme.split("\n"):
        if "Версия" in readmeLine:
            version = readmeLine.strip()
    version = version.replace('Версия ', '')
    return version

print('Start process')
print("OS:", system)
print('Old version:', getVersion('old'), '   New version:', getVersion('new'))
for service in services:
    print('*********************')
    print('Working with', service)
    print('*********************')
    if os.path.isdir(service) and os.path.isdir(service):

        if service == 'RDP2' and versions.index(getVersion('old')) < 3 and versions.index(getVersion('new')) > 2:
            flagRDP = True
            continue

        shutil.copyfile(filePathGenerator(system, service, 'old'), filePathGenerator(system, service, 'old') + '-backup')
        shutil.copyfile(filePathGenerator(system, service, 'new'), filePathGenerator(system, service, 'new') + '-backup')

        with open((filePathGenerator(system, service, 'old')), 'r') as file:
            text = file.read()
        text = prepareFiles(text)
        with open(filePathGenerator(system, service, 'old'), 'w') as file:
            file.write(text)

        with open(filePathGenerator(system, service, 'new'), 'r') as file:
            text = file.read()
        text = prepareFiles(text)
        with open(filePathGenerator(system, service, 'new'), 'w') as file:
            file.write(text)

        old = json.load(codecs.open(filePathGenerator(system, service, 'old'), 'r', 'utf-8-sig'))
        blank = json.load(codecs.open(filePathGenerator(system, service, 'new'), 'r', 'utf-8-sig'))

        readConfigFirst(old)

        with open(filePathGenerator(system, service, 'new'), 'w') as file:
            json.dump(blank, file, ensure_ascii=False, indent=4)
    else:
        print('Check', service, 'folder!')

print('Errors and warnings:')
if flagRDP:
    print('Please, edit RDP2 config manually!')