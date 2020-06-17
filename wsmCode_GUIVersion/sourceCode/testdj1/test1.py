# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 20:41:49 2020

@author: longs
"""
from xml import sax

class WikiHandler(sax.handler.ContentHandler):
    def __init__(self):
        sax.handler.ContentHandler.__init__(self)
        self._buffer = None
        self._values = {}
        self._current_tag = None
        self._pages = []
    def characters(self, content):
        if self._current_tag:
            self._buffer.append(content)
    def startElement(self, name, attrs):
        if name in ('title', 'text'):
            self._current_tag = name
            self._buffer = []
    def endElement(self, name):
        if name == self._current_tag:
            self._values[name] = ' '.join(self._buffer)
            
        if name == 'page':
            self._pages.append((self._values['title'],self._values['text']))
def main():
     parser = sax.make_parser()
   # turn off namepsaces
     #parser.setFeature(sax.handler.feature_namespaces, 0)

   # override the default ContextHandler
     Handler = WikiHandler()
     parser.setContentHandler( Handler )
     #for line in subprocess.Popen(stdin = open('D:\\enwiki-latest-pages-articles.xml\\enwiki-latest-pages-articles.xml'),stdout = subprocess.PIPE).stdout
     parser.parse("E:\\shortest.xml")
     #for i in range(0,len(Handler._pages)):
         # if i < 30:
         #     print(Handler._pages[i])
     #Handler._pages[i]是一个元组,第一个值是title,第二个是text
     tup = Handler._pages[0]
     #tuple元组转成list
     tup = list(tup)
     print(type(tup))
     print(tup)
     # print(Handler._pages[3])
     # if len(Handler._pages) > 2 :
     #     exit()
if __name__ == "__main__":
    main()