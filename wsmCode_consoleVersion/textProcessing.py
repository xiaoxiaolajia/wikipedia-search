

"""
This is a module that helps Indexing.py. The main functions of this module are
create stopwords list, tokenise, stemming and process the five main parts
(title, body, infoBox, category, externalLinks) of Wikipedia pages.
"""
import re
from collections import defaultdict
from Stemmer import Stemmer

#Create stopwords list
stopwords = defaultdict(int)
with open('./stopwords.txt','r') as f:
    for line in f:
        line = line.strip()
        stopwords[line] = 1
    
#re模块:python特有的匹配字符串的模块

#tokenise
def tokenise(data):
    # regular expression
    tokenisedWords=re.findall("\d+|[\w]+",data)
    tokenisedWords=[key for key in tokenisedWords]
    # tokenisedWords = str(tokenisedWords)
    # tokenisedWords=[key for key in tokenisedWords]
    return tokenisedWords

#清除所有值为1的 从而达到清除stopwords的目的
#stopwordsremove函数 
def stopWords(listOfWords):  
#因为每个stopword的值都是1
    temp = [key for key in listOfWords if stopwords[key] != 1]
    return temp

#提取词干, 用的Stemmer库函数,固定用法 把所有的特殊形式都变成词干:比如:lying--->lie
def stemmer(listofTokens):                                          #Stemming
    stemmer = Stemmer("english")
    stemmedWords = [stemmer.stemWord(key) for key in listofTokens ]
    return stemmedWords

def clean_up_list(list_of_words):
    temp = []
    list_of_words = [s.lower() for s in list_of_words]
    temp = stopWords(temp)
    temp = stemmer(temp)

def clean_up_string(string):
    string = string.lower()
    return clean_up_list(tokenise(string))

#寻找外链,因为xml文件中本来就有==external links==, 和*[之类的
def findExternalLinks(data):
    links=[]
    lines = data.split("==external links==")
    if len(lines)>1:
        lines=lines[1].split("\n")
        for i in range(len(lines)):
            if '* [' in lines[i] or '*[' in lines[i]:
                # word=""
                temp=lines[i].split(' ')
                # word=[key for key in temp if 'http' not in temp]
                # word=' '.join(word).encode('utf-8')
                # links.append(word)
                links.extend(temp)
    # links=tokenise(' '.join(links))
    #.join()方法:listtostring
    links=tokenise(' '.join(links))
    links = stopWords(links)
    links= stemmer(links)

    temp=defaultdict(int)
    for key in links:
       temp[key]+=1
    links=temp
    return links

 #find InfoBox, Text and Category
def findInfoBoxTextCategory(data):                                       
    info, bodyText, category, links = [], [], [], []
    flagtext=1
    #以换行符分行, 一共有多少行就分成多少行
    lines = data.split('\n')
    for i in range(len(lines)):
        if '{{Infobox' in lines[i]:
            flag=0
            temp=lines[i].split('{{Infobox')[1:]
            info.extend(temp)
            while True:
                if '{{' in lines[i]:
                    count=lines[i].count('{{')
                    flag+=count
                if '}}' in lines[i]:
                    count=lines[i].count('}}')
                    flag-=count
                if flag<=0:
                    break
                i+=1
                try:
                    info.append(lines[i])
                except:
                    print("数据超限!")
                    pass

        elif flagtext:
            if '[[category' in lines[i] or '==external links==' in lines[i]:
                flagtext=0
            bodyText.append(lines[i])

        else:
            if "[[category" in lines[i]:
                line = data.split("[[category:")
                if len(line)>1:
                    category.extend(line[1:-1])
                    temp=line[-1].split(']]')
                    category.append(temp[0])

    category=tokenise(' '.join(category))
    category = stopWords(category)
    category= stemmer(category)

    info=tokenise(' '.join(info))
    info = stopWords(info)
    info= stemmer(info)

    bodyText=tokenise(' '.join(bodyText))
    bodyText = stopWords(bodyText)
    bodyText= stemmer(bodyText)

    temp=defaultdict(int)
    for key in info:
        temp[key]+=1
    info=temp

    temp=defaultdict(int)
    for key in bodyText:
        temp[key]+=1
    bodyText=temp

    temp=defaultdict(int)
    for key in category:
        temp[key] += 1
    category=temp

    return info, bodyText, category
     
    
def processTitle(data):
  data=data.lower()
  tokenisedTitle=tokenise(data)
  stopWordsRemoved = stopWords(tokenisedTitle)
  stemmedWords= stemmer(stopWordsRemoved)
#key为tile, value值为其编号
  temp=defaultdict(int)
  for key in stemmedWords:
      temp[key]+=1
  stemmedWords=temp
  return stemmedWords

def processText(data):
    data = data.lower()
    externalLinks = findExternalLinks(data)
    data = data.replace('_',' ').replace(',',' ') #原data = data.replace('_',' ').replace(',','')
    infoBox, bodyText, category = findInfoBoxTextCategory(data)
    return bodyText, infoBox, category, externalLinks
