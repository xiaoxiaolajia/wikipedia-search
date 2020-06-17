
import linecache
from collections import defaultdict

filepath = '/home/longshui/test1//hanxi.txt'
def get_line_content(filepath, line_number):
    return linecache.getline(filepath, line_number).strip().split(' ')
list1 = get_line_content(filepath, 1)
print(list1)
def findFileNumber(low, high, offset, pathOfFolder, word, filepath):  # Binary Search on offset
    while low <= high:
        mid = int((low + high) / 2)
        testWord = get_line_content(filepath, mid)
        if word == testWord[0]:
            return testWord[1:], mid
        elif word > testWord[0]:
            low = mid + 1
        else:
            high = mid - 1
    return [], -1
offset = []
with open('/home/longshui/test1/offset.txt', 'rb') as f:
    for line in f:
        # print(f.read())
        offset.append(int(line.decode('utf8').strip()))

# print(offset)

returnList, mid = findFileNumber(0, len(offset), offset, '/home/longshui/test1', 'sa', '/home/longshui/test1' + '/vocabularyList.txt')
print(returnList)
print(mid)

def findFileList(fileName, fileNumber, field, pathFolder, word):
    fieldOffset, tempdf = [], []
    #offsetfilename 就是ot1.txt, ob2.txt...
    offsetFileName = pathFolder + '/o' + field + fileNumber + '.txt'
    with open(offsetFileName, 'r') as fieldOffsetFile:
        for line in fieldOffsetFile:
            offset, docfreq = line.strip().split(' ')
            fieldOffset.append(int(offset))
            tempdf.append(int(docfreq))
    fileList, mid = findFileNumber(0, len(fieldOffset), fieldOffset, pathFolder, word, fileName)
    return fileList, tempdf[mid - 1], mid
filename = '/home/longshui/test1/b0.txt'
fileList, tempdf, mid = findFileList(filename, '0', 'b', '/home/longshui/test1', 'c')
print(fileList)
print(tempdf)
print(mid)

def querySimple(queryWords, pathOfFolder, fVocabulary):  # Deal with single word query
    fileList = defaultdict(dict)
    df = {}
    listOfField = ['t', 'b', 'i', 'c', 'e']
    for word in queryWords:
        # returnedList, _= findFileNumber(0,len(offset),offset,sys.argv[1],word,fVocabulary)
        returnedList, _ = findFileNumber(0, len(offset), offset, '/home/longshui/test1', word, fVocabulary)
        if len(returnedList) > 0:
            fileNumber, df[word] = returnedList[0], returnedList[1]
            for key in listOfField:
                # fileName = pathOfFolder + '/' + key + str(fileNumber[0]) + '.txt'
                fileName = pathOfFolder + '/' + key + str(fileNumber) + '.txt'
                # fieldFile=bz2.BZ2File(fileName,'r')
                # fieldFile = bz2.BZ2File(fileName, 'r') if COMPRESS_INDEX else open(fileName)
                returnedList, _ = findFileList(fileName, fileNumber, key, pathOfFolder, word)
                fileList[word][key] = returnedList
    return fileList, df
query = 'a BLFJDOIJG LFJDL'
print(query.lower())