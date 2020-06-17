# encoding: utf-8
import linecache
import timeit
from config import COMPRESS_INDEX, TOP_N_POSTINGS_FOR_EACH_WORD, CONSIDER_TOP_N_POSTINGS_OF_EACH_WORD, FIELD_WEIGHTS, \
    TOP_N_RESULTS, FIELD_WEIGHTS2
# from textProcessing import tokenise, stopWords, stemmer, stopwords, clean_up_string
from collections import defaultdict
import sys
import re
import math

offset = []
#获取指定行内容，以列表的形式返回
# def get_line_content(filepath, line_number):
#     return linecache.getline(filepath, line_number).strip().split(' ')

#f:可能有三种：fieldfile, fvocabulary, titlefile
#pathFolder: test1
def findFileNumber(low, high, offset, pathFolder, word, filePath):  # Binary Search on offset
    if len(offset) > 0:
        while low <= high:
            mid = int((low + high) / 2)
            # testWord = get_line_content(filePath, mid)
            testWord = linecache.getline(filePath, mid).strip().split(' ')
            if word == testWord[0]:
                return testWord[1:], mid
            elif word > testWord[0]:
                low = mid + 1
            else:
                high = mid - 1
    return [], -1

def findFileNumber_forTitleSearch(low, high, offset, pathFOlder, word, filepath):
    word = int(word)
    while low <= high:
        mid = int((low + high) / 2)
        testWord = linecache.getline(filepath, mid).strip().split()
        if word == int(testWord[0]):
            return testWord[1:], mid
        elif word > int(testWord[0]):
            low = mid + 1
        else:
            high = mid - 1
    return [], -1

# Find posting list(倒排列表)
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
    print(len(tempdf))
    if mid >= 0:
        return fileList, tempdf[mid]
    else:
        return fileList, 0

def queryMultifield(queryWords, listOfFields, pathOfFolder, fVocabulary):  # Deal with multifield query
    fileList = defaultdict(dict)
    df = {}
    for i in range(len(queryWords)):
        word, key = queryWords[i], listOfFields[i]
        returnedList, mid = findFileNumber(0, len(offset), offset, sys.argv[1], word, fVocabulary)
        # print('test')
        # print(len(offset))
        # print(returnedList, mid)
        if len(returnedList) > 0:
            # ob1, ob3...中的1,3就是fileNumber
            fileNumber = returnedList[0]
            fileName = pathOfFolder + '/' + key + str(fileNumber) + '.txt'
            returnedList, docfreq = findFileList(fileName, fileNumber, key, pathOfFolder, word)
            fileList[word][key], df[word] = returnedList, docfreq
    return fileList, df
# fileList[word][key] 形式: {1036 16, 728 3, 249 2, 1462 2}, 文档1036出现16次,728出现3次..., 1036是键,16是值

#tf-idf based, FIELD_WEIGHTS = {1,1,1,1,1}
def ranking1(results, documentFreq, numberOfFiles):
    listOfDocuments, idf_of_word = defaultdict(float), defaultdict(float)

    # Compute the IDF for each word
    for key in documentFreq:
        idf_of_word[key] = math.log((float(numberOfFiles) / (float(documentFreq[key]) + 1)))

    for word in results:
        fieldWisePostingList = results[word]
        for field in fieldWisePostingList:
            if len(field) > 0:

                # Get posting list of a particular (word, field)
                postingList = fieldWisePostingList[field]

                # Champion lists ?
                postingList = postingList[:TOP_N_POSTINGS_FOR_EACH_WORD * 2] if CONSIDER_TOP_N_POSTINGS_OF_EACH_WORD else postingList

                # Weight the scores based on field weights
                factor = FIELD_WEIGHTS[field]

                for i in range(0, len(postingList), 2):
                    listOfDocuments[postingList[i]] += math.log(1 + float(postingList[i + 1])) * idf_of_word[word] * factor

    return listOfDocuments

#TF bases FIELD_WEIGHTS = {1, 1, 1, 1, 1}
def ranking2(results, documentFreq, numberOfFiles):
    listOfDocuments = defaultdict(float)
    for word in results:
        fieldWisePostingList = results[word]
        for field in fieldWisePostingList:
            if len(field) > 0:
                # Get posting list of a particular (word, field)
                postingList = fieldWisePostingList[field]
                # 形式: {1036: 16, 728: 3, 249: 2, 1462: 2}

                postingList = postingList[:TOP_N_POSTINGS_FOR_EACH_WORD * 2] if CONSIDER_TOP_N_POSTINGS_OF_EACH_WORD else postingList
                factor = FIELD_WEIGHTS[field]

                for i in range(0, len(postingList), 2):
                    listOfDocuments[postingList[i]] += math.log(1 + float(postingList[i + 1])) * factor

    return listOfDocuments

#tf based FIELD_WEIGHTS = {0.3, 0.3, 0.3, 0.2, 0.1}
def ranking3(results, documentFreq, numberOfFiles):
    listOfDocuments, idf_of_word = defaultdict(float), defaultdict(float)
    for key in documentFreq:
        idf_of_word[key] = math.log((float(numberOfFiles) / (float(documentFreq[key]) + 1)))
    for word in results:
        fieldWisePostingList = results[word]
        for field in fieldWisePostingList:
            if len(field) > 0:
                postingList = fieldWisePostingList[field]
                postingList = postingList[:TOP_N_POSTINGS_FOR_EACH_WORD * 2] if CONSIDER_TOP_N_POSTINGS_OF_EACH_WORD else postingList
                for i in range(0, len(postingList), 2):
                    # listOfDocuments[postingList[i]] += math.log(1 + float(postingList[i + 1])) * factor
                    listOfDocuments[postingList[i]] += int(postingList[i + 1])
    return listOfDocuments

# ranked boolean retrieval
def ranking4(results, documentFreq, numberOfFiles):
    listOfDocuments = defaultdict(float)
    for word in results:
        fieldWisePostingList = results[word]
        for field in fieldWisePostingList:
            if len(field) > 0:
                postingList = fieldWisePostingList[field]
                factor = FIELD_WEIGHTS2[field]
                for i in range(0, len(postingList), 2):
                    listOfDocuments[postingList[i]] += math.log(1 + float(postingList[i + 1])) * factor
    return listOfDocuments

def main():
    if len(sys.argv) != 2:
        print("正在生成倒排索引，请稍等！")
        sys.exit(0)
    with open(sys.argv[1] + '/offset.txt','r') as f:
        for line in f:
            offset.append(int(line.strip()))
    titleOffset = []
    with open(sys.argv[1] + '/titleoffset.txt', 'r') as f:
        for line in f:
            titleOffset.append(int(line.strip()))

    while True:
        query = input("Please input things you want to search:\n")

        if len(query.strip()) < 1:
            sys.exit(0)
        # fVocabulary = open(sys.argv[1]+'/vocabularyList.txt','r')
        fVocabulary = sys.argv[1] + '/vocabularyList.txt'
        start_time = timeit.default_timer()
        queryWords = query.lower().strip().split(' ')

        listOfFields, temp = [], []
        for word in queryWords:
            if re.search(r'[t|b|c|e|i]{1,}:', word):
                # distinguish between fields and query, eg: t:hello, where t is field and hello is query
                _fields = list(word.split(':')[0])
                _words = [word.split(':')[1]] * len(_fields)
            else:
                _fields = ['t', 'b', 'c', 'e', 'i']
                _words = [word] * len(_fields)
            listOfFields.extend(_fields)
            temp.extend(_words)
        print("Fields:", listOfFields)
        print("Words:", temp)
        print("=" * 40)
        results, documentFrequency = queryMultifield(temp, listOfFields, sys.argv[1], fVocabulary)

        with open(sys.argv[1] + '/numberOfFiles.txt', 'r') as f:
            numberOfFiles = int(f.read().strip())
        # f.close()
        results = ranking1(results, documentFrequency, numberOfFiles)
        end_time = timeit.default_timer()

        if len(results) > 0:
            top_n_docs = sorted(results, key = results.get, reverse = True)[:TOP_N_RESULTS]
            titleFile = sys.argv[1] + '/title.txt'
            dict_Title = {}
            for docid in top_n_docs:
                title, _ = findFileNumber_forTitleSearch(0, len(titleOffset), titleOffset, sys.argv[1], docid, titleFile)
                if not len(title):
                    print("Title not found:", docid, titleFile, len(titleOffset))
                dict_Title[docid] = ' '.join(title)
            for rank, docid in enumerate(top_n_docs):
                print("\t", rank + 1, ":", dict_Title[docid], "(score", round(results[docid], 3), ")")
            print("=" * 40)
            print("Query time:", round(end_time - start_time, 2), "seconds")
        else:
            print("Phrase Not Found")


if __name__ == "__main__":
    main()
