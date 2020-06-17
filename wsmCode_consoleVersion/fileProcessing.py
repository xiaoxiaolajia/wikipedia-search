
"""
White the inverted index into file and merge files.
"""
import sys
import bz2
import heapq
import os
import operator
from collections import defaultdict
import pdb
from config import *

#负责写入文件 
def writeSingle(field, data, offset, countFinalFile, pathOfFolder):
    filename = pathOfFolder + '/' + field + str(countFinalFile)
    if COMPRESS_INDEX:
        write_type = bz2.BZ2File(filename+'.bz2', 'w', compresslevel=7)
    else:
        #t0.txt,t1.txt,t2.txt...
        #COMPRESS_INDEX = FALSE,只走这一步 
        write_type = open(filename+'.txt', 'w')

    with write_type as f:
        f.write('\n'.join(data))
    #写offset文件: ob0.txt,ob1.txt,ob2.txt 
    filename = pathOfFolder + '/o' + field + str(countFinalFile) + '.txt'
    with open(filename, 'w') as f:
        f.write('\n'.join(offset))

def get_appropriate_score_type(score):
    if SCORE_TYPE_TYPE == int:
        return SCORE_TYPE_TYPE(float(score))
    if SCORE_TYPE_TYPE == float:
        return SCORE_TYPE_TYPE(score)

def writeFinalIndex(data, countFinalFile, pathOfFolder,offsetSize):
    """
        Write index after merging
    """
    #全是default(dict)类型 
    #字典中有字典 
    title, text, info, category, externalLink = defaultdict(dict), defaultdict(dict), defaultdict(dict), defaultdict(dict), defaultdict(dict)
    
    #print ("Merging file:", countFinalFile)
    uniqueWords, offset = [], []

    min_score_value = str(SCORE_TYPE_TYPE(0))

    for key in sorted(data):
        listOfDoc = data[key]
        temp=[]
        flag=0
        #步长为6
        for i in range(0, len(listOfDoc), 6):
           word = listOfDoc
           docid = word[i]
           try:
               if word[i+1] != min_score_value:
                   title[key][docid]=get_appropriate_score_type(word[i+1])
                   flag=1
               if word[i+2] != min_score_value:
                   text[key][docid]=get_appropriate_score_type(word[i+2])
                   flag=1
               if word[i+3] != min_score_value:
                   info[key][docid]=get_appropriate_score_type(word[i+3])
                   flag=1
               if word[i+4] != min_score_value:
                   category[key][docid]=get_appropriate_score_type(word[i+4])
                   flag=1
               if word[i+5] != min_score_value:
                   externalLink[key][docid]=get_appropriate_score_type(word[i+5])
                   flag=1
           except Exception as e:
               print(e)
               pdb.set_trace()
        if flag == 1:
            string = str(key) + ' ' + str(countFinalFile) + ' ' + str(int(len(listOfDoc)/6))
            uniqueWords.append(string)
            offset.append(str(offsetSize))
            # offsetSize = offsetSize + len(string) + 1
            offsetSize = offsetSize + len(string) + 1

    titleData, textData, infoData, categoryData, externalLinkData = [], [], [], [], []
    titleOffset, textOffset, infoOffset, categoryOffset, externalLinkOffset = [], [], [], [], []

    previousTitle, previousText, previousInfo, previousCategory, previousExternalLink = 0, 0, 0, 0, 0

    for key in sorted(data.keys()):                                                                     #create field wise Index

        if key in title:
            string = str(key) + ' '
            sortedField = title[key]
            sortedField = sorted(sortedField, key=sortedField.get, reverse=True)
            for doc in sortedField:
                string += str(doc) + ' ' + str(title[key][doc]) + ' '
            titleOffset.append(str(previousTitle)+' '+str(len(sortedField)))
            previousTitle += len(string)+1
            # pdb.set_trace()
            titleData.append(string)

        if key in text:
            string = str(key) + ' '
            sortedField = text[key]
            sortedField = sorted(sortedField, key=sortedField.get, reverse=True)
            for doc in sortedField:
                string += str(doc) + ' ' + str(text[key][doc]) + ' '
            textOffset.append(str(previousText)+' '+str(len(sortedField)))
            previousText += len(string)+1
            # pdb.set_trace()
            textData.append(string)

        if key in info:
            string = str(key) + ' '
            sortedField=info[key]
            sortedField = sorted(sortedField, key=sortedField.get, reverse=True)
            for doc in sortedField:
                string += str(doc) + ' ' + str(info[key][doc]) + ' '
            infoOffset.append(str(previousInfo) + ' ' + str(len(sortedField)))
            previousInfo += len(string)+1
            infoData.append(string)

        if key in category:
            string = str(key) + ' '
            sortedField = category[key]
            sortedField = sorted(sortedField, key=sortedField.get, reverse=True)
            for doc in sortedField:
                string += (str(doc) + ' ' + str(category[key][doc]) + ' ')
            categoryOffset.append(str(previousCategory)+' '+str(len(sortedField)))
            previousCategory += len(string)+1
            categoryData.append(string)

        if key in externalLink:
            string = str(key) + ' '
            sortedField=externalLink[key]
            sortedField = sorted(sortedField, key=sortedField.get, reverse=True)
            for doc in sortedField:
                string += str(doc) + ' '+str(externalLink[key][doc])+' '
            externalLinkOffset.append(str(previousExternalLink)+' '+str(len(sortedField)))
            previousExternalLink+=len(string)+1
            externalLinkData.append(string)
            
            #ot,ob,oi,oc,oe.txt文件 
    writeSingle('t', titleData, titleOffset, countFinalFile,pathOfFolder)
    writeSingle('b', textData, textOffset, countFinalFile,pathOfFolder)
    writeSingle('i', infoData, infoOffset, countFinalFile,pathOfFolder)
    writeSingle('c', categoryData, categoryOffset, countFinalFile,pathOfFolder)
    writeSingle('e', externalLinkData, externalLinkOffset, countFinalFile,pathOfFolder)

    try:
 	# Change file of size > 30.48 Mb, 30485760
        if os.path.getsize(pathOfFolder+'/b'+str(countFinalFile)+('.txt.bz2' if COMPRESS_INDEX else '.txt')) > 30485760:
            countFinalFile += 1
    except:
        pass

    # with open(pathOfFolder+"/vocabularyList.txt", "ab") as f:
    #   f.write(('\n'.join(uniqueWords)).encode('utf8'))
    with open(pathOfFolder+"/vocabularyList.txt", "a") as f:
      f.write(('\n'.join(uniqueWords)))
    # with open(pathOfFolder+"/offset.txt","ab") as f:
    #   f.write(('\n'.join(offset)).encode('utf8'))
    with open(pathOfFolder+"/offset.txt","a") as f:
      f.write(('\n'.join(offset)))
    return countFinalFile, offsetSize

    """
        Write partial index to file
    """
def writeIntoFile(pathOfFolder, index, dict_Id, countFile, titleOffset):
    #index类型: {1:[],2:[],3:[]}, offset: int型, titleOffset,previoustileoffset
    data=[]                                                                             #write the primary index
    previousTitleOffset = titleOffset

    # Iterating index over key essentially DOES NOT sort the index based on 'word'
    for key in sorted(index.keys()): #获得索引中的所有单词
        string = str(key) + ' ' + ' '.join(index[key])
        data.append(string)

    # Compress if required and then write into file
    filename = pathOfFolder + '/index' + str(countFile) + ('.txt.bz2' if COMPRESS_INDEX else '.txt')
    write_type = bz2.BZ2File(filename, 'a', compresslevel=9) if COMPRESS_INDEX else open(filename, 'a')
    with write_type as f:
        f.write('\n'.join(data))

    data,dataOffset = [], []
    for key in sorted(dict_Id.keys()):
        data.append(str(key) + ' ' + str(dict_Id[key]))
        dataOffset.append(str(previousTitleOffset))
        previousTitleOffset += len(str(key) + ' ' + str(dict_Id[key]))

    with open(pathOfFolder + '/title.txt', 'a') as f:
        f.write('\n'.join(data))

    filename=pathOfFolder+'/titleoffset.txt'
    with open(filename, 'a') as f:
        f.write('\n'.join(dataOffset))

    return  previousTitleOffset


def mergeFiles(pathOfFolder, countFile):
    global oldCountFile
    oldCountFile = 0 + 0
    #词典 
    listOfWords, indexFile, topOfFile = {}, {}, {}
    flag = [0]*countFile
    
    #data类型: {1:[列表1],2:[列表2]}
    data = defaultdict(list)
    heap = []
    countFinalFile, offsetSize = 0, 0
    for i in range(countFile):
        fileName = pathOfFolder + '/index' + str(i) + ('.txt.bz2' if COMPRESS_INDEX else '.txt')
        indexFile[i] = bz2.BZ2File(fileName, 'r') if COMPRESS_INDEX else open(fileName, 'r')
        flag[i] = 1
        topOfFile[i] = indexFile[i].readline().strip()
        listOfWords[i] = topOfFile[i].split()
        if listOfWords[i][0] not in heap:
            heapq.heappush(heap, listOfWords[i][0])
            
    count=0
    #这儿可能一直循环停不下来 
    while any(flag) == 1:
        temp = heapq.heappop(heap)
        count += 1
        for i in range(countFile):
            if flag[i]:
                if listOfWords[i][0] == temp:
                    data[temp].extend(listOfWords[i][1:])
                    topOfFile[i] = indexFile[i].readline().strip()
                    if topOfFile[i] == '':
                        flag[i] = 0
                        indexFile[i].close()
                        print("\tRemoved:", str(i))
                        os.remove(pathOfFolder + '/index' + str(i) + ('.txt.bz2' if COMPRESS_INDEX else '.txt'))
                    else:
                        #listOfWords[i]是list格式 
                        listOfWords[i] = topOfFile[i].split()
                        if listOfWords[i][0] not in heap:
                            heapq.heappush(heap, listOfWords[i][0])

        if not count % 5000:
            print("Done Words:", count)
        if count > 0 and count % 20000 == 0:
            oldCountFile = countFinalFile
            countFinalFile, offsetSize = writeFinalIndex(data, countFinalFile, pathOfFolder, offsetSize)
        if oldCountFile !=  countFinalFile:
            data = defaultdict(list)
            countFinalFile, offsetSize = writeFinalIndex(data, countFinalFile, pathOfFolder, offsetSize)