"""
The functions of this module are parsing the Wikipedia xml dump and returning
the posting list(output files) so that the search.py can search results according to the posting list.
We use a SAX Parser to parse the Wikipedia xml file.
"""

import xml.sax.handler
from textProcessing import processText,processTitle
from fileProcessing import writeIntoFile,mergeFiles
from collections import defaultdict
import sys
import timeit
from config import *

count, countFile, offset = 0, 0, 0
index = defaultdict(list)
dict_Id = {}

#We use a SAX Parser to parse the wikipedia xml files
class WikiHandler(xml.sax.handler.ContentHandler):                     
  
  flag = 0
  def createIndex(self, title, text, infoBox, category, externalLink): 
    """
            dict of {word: freq} of [title, text, infoBox, category, externalLink]
    """
    global index, dict_Id, countFile, offset, count
    #.keys方法返回所有的键 
    vocabularyList= list(set(list(title.keys()) + list(text.keys()) + list(infoBox.keys())
                             + list(category.keys()) + list(externalLink.keys())))
    #print(vocabularyList) #[b'categori', b'from', b'1', b'shell', b'r', b'africa', b'redirect', b'camelcas']

    t, b, i, c, e = float(len(title)), float(len(text)), float(len(infoBox)), float(len(category)), float(len(externalLink))

#出现频率换成文档中单词出现的频率        
    for key in vocabularyList:
      string = str(count) + ' '
      for (contentType, contentLen) in [(title, t), (text, b), (infoBox, i), (category, c), (externalLink, e)]:
          try:
              if SCORE_TYPE == "freq":
                  string += str(int(contentType[key])) + ' '
              elif SCORE_TYPE == "freq_ratio":
                  string += str(round(contentType[key]/contentLen, 3)) + ' '
              else:
                  print ("ERROR: Unknown scoring type")
          except ZeroDivisionError:
              string += str(SCORE_TYPE_TYPE(0)) + ' '
      index[key].append(string)
    
    count += 1
    #every parse 200 pages write into disk
    if count % 20000 == 0:
      print("pages processed: %d | write partial index to disk ...", count)
      # offset = writeIntoFile('/home/longshui/test1', index, dict_Id, countFile, offset)
      offset = writeIntoFile(sys.argv[2], index, dict_Id, countFile,offset)
      index = defaultdict(list)
      dict_Id = {}
      countFile += 1
      
  def __init__(self):   
#inId,inText都是bool类型,值为0或者1
    self.inTitle, self.inId, self.inText = 0, 0, 0

  # start tag
  def startElement(self, name, attributes):
    if name == "id" and WikiHandler.flag == 0:
      self.bufferId = ""
      self.inId = 1        
      WikiHandler.flag = 1
    elif name == "title":
      self.bufferTitle = ""
      self.inTitle = 1
    elif name == "text":
      self.bufferText = ""
      self.inText = 1
  # body
  def characters(self, data):
    global count, dict_Id
    if self.inId and WikiHandler.flag == 1:
        self.bufferId += data
    elif self.inTitle:
        self.bufferTitle += data
        dict_Id[count] = data
    elif self.inText:
        self.bufferText += data 
  #  end tag
  def endElement(self, name):
    if name == "title":
      WikiHandler.titleWords = processTitle(self.bufferTitle)
      self.inTitle = 0
    elif name == "text":
      WikiHandler.textWords, WikiHandler.infoBoxWords, WikiHandler.categoryWords, WikiHandler.externalLinkWords = processText(self.bufferText)
      WikiHandler.createIndex(self, WikiHandler.titleWords, WikiHandler.textWords, WikiHandler.infoBoxWords, WikiHandler.categoryWords, WikiHandler.externalLinkWords)
      self.inText = 0
    elif name == "id":                                                #End Tag: Id
      self.inId = 0
    elif name == "page":                                              #End Tag: Page
      WikiHandler.flag = 0
    
def main():

    global offset, countFile
    if len(sys.argv)!= 3:                                             #check arguments
        print( "Usage :: python Indexing.py sample.xml /output")
        sys.exit(0)
  
    parser = xml.sax.make_parser(  )                                  #SAX Parser
    handler = WikiHandler(  )
    parser.setContentHandler(handler)
    #解析下载的wiki.xml文件 
    parser.parse(sys.argv[1])
    #D:/enwiki-latest-pages-articles.xml/enwiki-latest-pages-articles_0000001.xml
    # parser.parse('/home/longshui/testxml1.xml')
    #以二进制格式打开一个文件只用于写入,如果该文件已存在则将其覆盖。如果该文件不存在，创建新文件
    
    #文章个数文件 
    # with open('/home/longshui/test1' + '/numberOfFiles.txt', 'w') as f:
    with open(sys.argv[2]+'/numberOfFiles.txt','w') as f:
      f.write(str(count))
    
    offset = writeIntoFile(sys.argv[2], index, dict_Id, countFile,offset)
    #filename=pathOfFolder+'/index'+repr(countFile)+'.txt.bz2'
    
    #offset文件 
    # offset = writeIntoFile('/home/longshui/test1', index, dict_Id, countFile, offset)
    countFile += 1
    mergeFiles(sys.argv[2], countFile)
    # mergeFiles('/home/longshui/test1', countFile)
    titleOffset = []
    with open(sys.argv[2]+'/title.txt','r') as f:
    # with open('/home/longshui/test1' + '/title.txt', 'r') as f:
      titleOffset.append('0')
      for line in f:
        #rule of titeloffset: take the last number of list titleoffset, then plus the length of each line(title)
        titleOffset.append(str(int(titleOffset[-1]) + len(line)))
    titleOffset = titleOffset[:-1]

    with open(sys.argv[2]+'/titleoffset.txt','w') as f:
    # with open('/home/longshui/test1' + '/titleoffset.txt','w') as f:
      f.write('\n'.join(titleOffset))
    
if __name__ == "__main__":                                            #main
    start = timeit.default_timer()
    main()
    stop = timeit.default_timer()
    print( "Index Creation time is: " + str(round(stop - start, 2)) + "s")
