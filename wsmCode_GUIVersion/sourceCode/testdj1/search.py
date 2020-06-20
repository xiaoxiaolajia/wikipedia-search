# encoding: utf-8

"""
This is search module which offers you a friendly GUI
"""
from django.http import HttpResponse
from django.shortcuts import render_to_response

# import wikipediaapi
import linecache
import timeit
from .config import COMPRESS_INDEX, TOP_N_POSTINGS_FOR_EACH_WORD, CONSIDER_TOP_N_POSTINGS_OF_EACH_WORD, FIELD_WEIGHTS,\
    TOP_N_RESULTS, FIELD_WEIGHTS2
from collections import defaultdict
import sys
import re
import math
from django.http import JsonResponse

offset, titleOffset = [], []

def findFileNumber(low, high, offset, pathFolder, word, filePath):  # Binary Search on offset
    if len(offset) > 0:
        while low <= high:
            mid = int((low + high) / 2)
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
        if len(returnedList) > 0:
            fileNumber = returnedList[0]
            fileName = pathOfFolder + '/' + key + str(fileNumber) + '.txt'
            returnedList, docfreq = findFileList(fileName, fileNumber, key, pathOfFolder, word)
            fileList[word][key], df[word] = returnedList, docfreq
    return fileList, df

def ranking1(results, documentFreq, numberOfFiles):
    listOfDocuments, idf_of_word = defaultdict(float), defaultdict(float)

    # Compute the IDF for each word
    for key in documentFreq:
        idf_of_word[key] = math.log((float(numberOfFiles) / (float(documentFreq[key]) + 1)))

    for word in results:
        fieldWisePostingList = results[word]
        for field in fieldWisePostingList:
            if len(field) > 0:
                postingList = fieldWisePostingList[field]
                postingList = postingList[:TOP_N_POSTINGS_FOR_EACH_WORD * 2] if CONSIDER_TOP_N_POSTINGS_OF_EACH_WORD else postingList
                factor = FIELD_WEIGHTS[field]
                for i in range(0, len(postingList), 2):
                    listOfDocuments[postingList[i]] += math.log(1 + float(postingList[i + 1])) * idf_of_word[word] * factor
                    # listOfDocuments[postingList[i]] += idf_of_word[word] * factor

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

#tf based FIELD_WEIGHTS = {0.3, 0.3, 0.2, 0.1, 0.1}
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

#返回表单
def search_form(request):
    # init()
    return render_to_response('search_form.html')

def init():
    with open('./output' + '/offset.txt', 'r') as f:
        for line in f:
            offset.append(int(line.strip()))
    with open('./output' + '/titleoffset.txt', 'r') as f:
        for line in f:
            titleOffset.append(int(line.strip()))
init()
def search(request):
    request.encoding = 'utf-8'
    query = ''
    # init()
    if 'q' in request.GET and request.GET['q']:
        query = request.GET['q']
        message = "你搜索的内容为：" + request.GET['q'] + "<br>" + "<br>"
        message += "搜索结果如下:" + "<br>" + "<br>"
        message1 = ''

        start_time = timeit.default_timer()
        fVocabulary = './output' + '/vocabularyList.txt'

        queryWords = query.lower().strip().split(' ')
        listOfFields, temp = [], []
        for word in queryWords:
            if re.search(r'[t|b|c|e|i]{1,}:', word):
                _fields = list(word.split(':')[0])
                _words = [word.split(':')[1]] * len(_fields)
            else:
                _fields = ['t', 'b', 'c', 'e', 'i']
                _words = [word] * len(_fields)
            listOfFields.extend(_fields)
            temp.extend(_words)
        results, documentFrequency = queryMultifield(temp, listOfFields, './output', fVocabulary)
        # 这儿执行完之后,产生一串数字,以0结束
        with open('./output' + '/numberOfFiles.txt', 'r') as f:
            numberOfFiles = int(f.read().strip())
        results = ranking1(results, documentFrequency, numberOfFiles)
        end_time = timeit.default_timer()

        if len(results) > 0:
            top_n_docs = sorted(results, key = results.get, reverse = True)[:TOP_N_RESULTS]
            titleFile = './output' + '/title.txt'
            dict_Title = {}
            for docid in top_n_docs:
                title, _ = findFileNumber_forTitleSearch(0, len(titleOffset), titleOffset, './output', docid, titleFile)
                if not len(title):
                    print("Title not found:", docid, titleFile, len(titleOffset))
                dict_Title[docid] = ' '.join(title)
            # for rank, docid in enumerate(top_n_docs):
            #     message +=  str(rank + 1) + ": " + str(dict_Title[docid]) + " (score: " + str(round(results[docid], 3)) + ")" + "<br>" + "<br>"
            for rank, docid in enumerate(top_n_docs):
                # wiki_lang = wikipediaapi.Wikipedia('en')
                # string = str(dict_Title[docid])
                # page = wiki_lang.page(string)
                # pageurl = page.fullurl
                pageurl = 'https://en.wikipedia.org/wiki/'
                titlenames = dict_Title[docid].strip().split(' ')
                for titlename in titlenames:
                    pageurl += titlename + "_"
                pageurl = pageurl.strip('_')
                message +=  str(rank + 1) + ": " + '<a href=\"' + pageurl + '\">' + str(dict_Title[docid])+ '</a>' \
                            + " (score: " + str(round(results[docid], 3)) + ")" + "<br>" + "<br>"
            message1 = "查询共花费: " + str(round(end_time - start_time, 2)) + "秒"
        else:
            message1 = "Phrase Not Found." + "<br>" + "查询共花费: " + str(round(end_time - start_time, 2)) + "秒"
    return HttpResponse(message + message1)

#接受请求数据(queryWords)
def searchui(request):
    request.encoding = 'utf-8'
    query = ''
    while(True):
        if 'q' in request.GET and request.GET['q']:
            query = request.GET['q']
            message = "你搜索的内容为：" + request.GET['q'] + "<br>" + "<br>"
            message += "搜索结果如下:" + "<br>" + "<br>"
            message1 = ''
            with open('./output' + '/offset.txt','r') as f:
                for line in f:
                    offset.append(int(line.strip()))
            titleOffset = []
            with open('./output' + '/titleoffset.txt', 'r') as f:
                for line in f:
                    titleOffset.append(int(line.strip()))
            start_time = timeit.default_timer()
            fVocabulary = './output' + '/vocabularyList.txt'
            # start_time = timeit.default_timer()
            queryWords = query.lower().strip().split(' ')
            listOfFields, temp = [], []
            for word in queryWords:
                if re.search(r'[t|b|c|e|i]{1,}:', word):
                    _fields = list(word.split(':')[0])
                    _words = [word.split(':')[1]] * len(_fields)
                else:
                    _fields = ['t', 'b', 'c', 'e', 'i']
                    _words = [word] * len(_fields)
                listOfFields.extend(_fields)
                temp.extend(_words)
            results, documentFrequency = queryMultifield(temp, listOfFields, './output', fVocabulary)

            with open('./output' + '/numberOfFiles.txt', 'r') as f:
                numberOfFiles = int(f.read().strip())
            results = ranking1(results, documentFrequency, numberOfFiles)
            end_time = timeit.default_timer()
            if len(results) > 0:
                top_n_docs = sorted(results, key = results.get, reverse = True)[:TOP_N_RESULTS]
                titleFile = './output' + '/title.txt'
                dict_Title = {}
                for docid in top_n_docs:
                    title, _ = findFileNumber_forTitleSearch(0, len(titleOffset), titleOffset, './output', docid, titleFile)
                    if not len(title):
                        print("Title not found:", docid, titleFile, len(titleOffset))
                    dict_Title[docid] = ' '.join(title)
                # for rank, docid in enumerate(top_n_docs):
                #     message +=  str(rank + 1) + ": " + str(dict_Title[docid]) + " (score: " + str(round(results[docid], 3)) + ")" + "<br>" + "<br>"

                for rank, docid in enumerate(top_n_docs):
                    # wiki_lang = wikipediaapi.Wikipedia('en')
                    # string = str(dict_Title[docid])
                    # page = wiki_lang.page(string)
                    # pageurl = page.fullurl
                    pageurl = 'https://en.wikipedia.org/wiki/'
                    titlenames = dict_Title[docid].strip().split(' ')
                    for titlename in titlenames:
                        pageurl += titlename + "_"
                    pageurl = string.strip('_')
                    message +=  str(rank + 1) + ": " + '<a href=\"' + pageurl + '\">' + str(dict_Title[docid])+ '</a>' \
                                + " (score: " + str(round(results[docid], 3)) + ")" + "<br>" + "<br>"
                message1 = "查询共花费: " + str(round(end_time - start_time, 2)) + "秒"
            else:
                message1 = "Phrase Not Found." + "<br>" + "查询共花费: " + str(round(end_time - start_time, 2)) + "秒"
        return HttpResponse(message + message1)