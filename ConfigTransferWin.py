import json
import pyparsing
import codecs
import io
import shutil
import os.path
import sys

system = 'win' #'linux', 'win'
services = ['WebApi', 'RobotLogs', 'Notifications', 'MachineInfo', 'RDP2', 'States'] #'WebApi', 'RobotLogs', 'Notifications', 'States', 'MachineInfo', 'RDP2'
commentStarts = ['// ', '//"', '//en', '//ru', '//Post', '//MS', '//mzL', '//}', '//Win', '//Адреса', '//,', '//For']
exceptedText1 = ['/// Настройки дефолтного тенанта']
# excludedKeys = ['LogsDump']
versions = ['2.2.26.0', '1.23.1.1', '1.23.2.0', '1.23.4.0', '1.23.5.0', '1.23.6.0', '1.23.7.0']

flagRDP = False

if system == 'linux':
    textEncoding = ''
sys.stdout = open('Log.txt', 'w')

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
    if system == 'linux':
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
            try:
                exec(jsonPathGenerator('blank', path, element))
            except KeyError:
                print('Key', elementKey, 'from old config does not exist in new config.')

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
            try:
                exec(jsonPathGenerator('blank', path, element))
            except KeyError:
                print('Key', elementKey, 'from old config does not exist in new config.')

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
            try:
                exec(jsonPathGenerator('blank', path, element))
            except KeyError:
                print('Index', elementListIndex, 'from old config does not exist in new config.')

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
    fileName = fileName.replace('\\N', '\\\\N')
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
        with open('WebApi-old/Readme.txt', 'r', encoding="utf8") as file:
            readme = file.read()
    elif type == 'new':
        with open('WebApi/Readme.txt', 'r', encoding="utf8") as file:
            readme = file.read()
    for readmeLine in readme.split("\n"):
        if "Версия" in readmeLine:
            version = readmeLine.strip()
    version = version.replace('Версия ', '')
    return version

print('Start process')
print("OS:", system)

if os.path.isdir('WebApi') and os.path.isdir('WebApi-old'):
    print('Old version:', getVersion('old'), '   New version:', getVersion('new'))
else:
    print('Is WebApi and WebApi-old folders exists?')

for service in services:
    print('*********************')
    print('Working with', service)
    print('*********************')
    if os.path.isdir(service) and os.path.isdir(service + '-old'):

        if service == 'RDP2' and versions.index(getVersion('old')) < 3 and versions.index(getVersion('new')) > 2:
            flagRDP = True
            continue

        shutil.copyfile(filePathGenerator(system, service, 'old'), filePathGenerator(system, service, 'old') + '-backup')
        shutil.copyfile(filePathGenerator(system, service, 'new'), filePathGenerator(system, service, 'new') + '-backup')

        with io.open((filePathGenerator(system, service, 'old')), 'r', encoding="utf-8", errors='ignore') as file:
            text = file.read()
        text = prepareFiles(text)
        with io.open(filePathGenerator(system, service, 'old'), 'w', encoding="utf-8") as file:
            file.write(text)

        with io.open(filePathGenerator(system, service, 'new'), 'r', encoding="utf-8", errors='ignore') as file:
            text = file.read()
        text = prepareFiles(text)
        with io.open(filePathGenerator(system, service, 'new'), 'w', encoding="utf-8") as file:
            file.write(text)

        old = json.load(codecs.open(filePathGenerator(system, service, 'old'), 'r', 'utf-8-sig')) # encoding="utf-8" 'utf-8-sig')
        blank = json.load(codecs.open(filePathGenerator(system, service, 'new'), 'r', 'utf-8-sig'))

        readConfigFirst(old)

        with open(filePathGenerator(system, service, 'new'), 'w') as file:
            json.dump(blank, file, ensure_ascii=False, indent=4)
    else:
        print(service, 'folder unavailable!')

print('Other messages:')
if flagRDP:
    print('Please, edit RDP2 config manually!')