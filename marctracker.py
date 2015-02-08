#!/usr/bin/python

import re
import sys
import urllib2
from BeautifulSoup import BeautifulSoup

class HTML():
    def __init__(self):
        self.url = ''
        self.soup = self.getsoup()
        self.tables = self.gettables()

    def getsoup(self):
        res = urllib2.urlopen('http://www.marctracker.com/PublicView/status.jsp')
        return BeautifulSoup(res.read())

    def gettables(self):
        tables = self.soup('table')
        return [ Table(table) for table in tables ] 

class Table():
    def __init__(self,soup):
        self.soup = soup
        self.value = self.soup.string
        self.rows = self.getrows()

    def getrows(self):
        rows = self.soup.findAll('tr')
        return [ Row(row) for row in rows ]
        
class Row():
    def __init__(self,soup):
        self.soup = soup
        self.data = self.getdata()

    def getdata(self):
        data = self.soup.findAll('td')
        return [ Data(datum) for datum in data ]

class Data():
    def __init__(self,soup):
        self.soup = soup
        self.value = self.soup.renderContents()

def main():
    html = HTML()
    html.url = 'http://www.marctracker.com/PublicView/status.jsp'
    html.soup = html.getsoup()
    for table in html.tables:
        for row in table.rows:
            for data in row.data:
                if not 'BRUNSWICK' in data.value:
                    print table
                    if table in html.tables:
                        print 'FOUND'
                    html.tables.remove(table)

    print html.tables
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "{!!Abort!!}"
        sys.exit(1)
