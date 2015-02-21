#!/usr/bin/python

import re
import sys
import urllib2
from lxml import html,etree

class HTML():
    def __init__(self,url):
        self.url = url
        self.res = urllib2.urlopen(self.url)
        self.tree = html.fromstring(self.res.read())
        self.tables = []

    def gettables(self):
        return self.tree.xpath('/html/body/table[3]/tr/td/table')

class Table():
    def __init__(self,tree):
        self.tree = tree
        self.line = self.getline()
        self.isline = self.checkline()
        self.hastrains = False
        self.headers = []
        self.trains = []

    def getline(self):
        return str(self.tree.xpath('.//td[@class="textStatusLine"]/text()'))

    def checkline(self):
        if 'BRUNSWICK' in self.line:
            return True

    def getheaders(self):
        trees = self.tree.xpath('.//tr[@class="textStatusHdr"]')
        return [ tree.xpath('.//th/text()') for tree in trees ]

    def gettrains(self):
        trains = []
        trees = self.tree.xpath('.//tr[@class="textStatusAll"]')
        rows = [ tree.xpath('.//td') for tree in trees ]
        for row in rows:
            text = [ column.text_content().strip() for column in row ]
            train = { 'holder1':text[0],
                      'holder2':text[1],
                      'id':text[2],
                      'dest':text[3],
                      'depart':text[4],
                      'status':text[5],
                      'delay':text[6],
                      'last':text[7],
                      'msg':text[8] }
            trains.append(train)
        return trains

def DEBUG(name, output):
    with open(name+'.debug','w') as o:
        for line in output:
            o.write(line)

def main():
    Lines = []
    html = HTML('http://www.marctracker.com/PublicView/status.jsp')
    html = HTML('http://web.archive.org/web/20140114221629/http://www.marctracker.com/PublicView/status.jsp')
    html.tables = html.gettables()
    for tbl in html.tables:
        table = Table(tbl)
        if table.isline:
            table.headers = table.getheaders()
            table.trains = table.gettrains()
            if len(table.trains) > 0:
                Lines.append(table)

    for Line in Lines:
        print '''%s
---''' % (Line.line)
        for train in Line.trains:
            print '%6s || %-25s || %10s || %10s' % (train['id'],train['dest'],train['status'],train['depart'])
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "{!!Abort!!}"
        sys.exit(1)
