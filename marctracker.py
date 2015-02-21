#!/usr/bin/python

import sys
import urllib.request
import argparse
from datetime import datetime
from prettytable import PrettyTable
from lxml import html


class Options:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.options = self.args()

    def args(self):
        self.parser.add_argument('-f', '--file', dest='file',
                                 help='File to write train data.')
        self.parser.add_argument('-l', '--line', dest='line',
                                 help='line to filter for')
        self.parser.add_argument('-d', '--direction', dest='direction',
                                 help='direction to filter for')
        return self.parser.parse_args()


class HTML:
    def __init__(self, url):
        self.url = url
        self.res = urllib.request.urlopen(self.url)
        self.tree = html.fromstring(self.res.read())
        self.tables = []

    def gettables(self):
        return self.tree.xpath('/html/body/table[3]/tr/td/table')


class TrainLine:
    def __init__(self, tree):
        self.tree = tree
        self.name = str(self.tree.xpath('.//td[@class="textStatusLine"]/text()'))
        self.hastrains = False
        self.headers = []
        self.trains = []

    def getheaders(self):
        trees = self.tree.xpath('.//tr[@class="textStatusHdr"]')
        return [tree.xpath('.//th/text()') for tree in trees]

    def gettrains(self):
        trains = []
        trees = self.tree.xpath('.//tr[@class="textStatusAll"]')
        rows = [tree.xpath('.//td') for tree in trees]
        for row in rows:
            text = [str(column.text_content().strip()) for column in row]
            train = {'holder1': text[0],
                     'holder2': text[1],
                     'id': text[2],
                     'dest': text[3],
                     'depart': text[4],
                     'status': text[5],
                     'delay': text[6],
                     'last': text[7],
                     'msg': text[8]}
            trains.append(train)
        return trains


def debug(name, output):
    with open(name+'.debug', 'w') as o:
        for line in output:
            o.write(line)


def buildtable(data):
    table = PrettyTable([k for k, v in data.trains[0].items()])
    for train in data.trains:
        table.padding_width = 1
        table.add_row([v for k, v in train.items()])
    table.sortby = 'depart'
    return table


def isline(filters, linename):
    if not filters.line:
        filters.line = ''
    if not filters.direction:
        filters.direction = ''
    filter = ' '.join([filters.line, filters.direction])
    if filter.strip() in linename:
        return True


def main():
    cmdline = Options()
    lines = []
    webpage = HTML('http://www.marctracker.com/PublicView/status.jsp')
    webpage.tables = webpage.gettables()
    for tbl in webpage.tables:
        line = TrainLine(tbl)
        if isline(cmdline.options, line.name):
            line.headers = line.getheaders()
            line.trains = line.gettrains()
            if len(line.trains) > 0:
                line.hastrains = True
                lines.append(line)

#   Write data to file in Dropbox or STDOUT
    output = ''
    for line in lines:
        output += '\n===========\n{:s}\n'.format(line.name.strip("'[]'"))
        output += str(buildtable(line))
    if not output:
        output = "No train information available."
#   Attach timestamp.
    output += '\n\n{:s}: {:s}'.format("Last updated", str(datetime.now()))
#   Determine output method.
    if not cmdline.options.file:
        print(output)
    else:
        with open(cmdline.options.file, 'w') as o:
            o.write(output)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("{!!Abort!!}")
        sys.exit(1)