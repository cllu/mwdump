#!/usr/bin/env python

import os
import re
import sys
from lxml import etree

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

class MWDump(object):
    """Read MediaWiki XML dump file
    """

    def __init__(self, filename):
        """
        """
        self.filename = filename
        self.getns()

    def getns(self):
        """get xmlns
        """
        context = etree.iterparse(self.filename, events=('start-ns',))
        for action, obj in context:
            # we only care the declaration at firt line
            break

        if not obj or not obj[1].startswith('http://www.mediawiki.org/xml/export'):
            print "Cannot find valid xmlns declarations."
            sys.exit()

        self.ns = obj[1]
        match = re.match(r'http://www.mediawiki.org/xml/export-(\d\.\d)/', self.ns)
        self.version = float(match.group(1))

    def iterpages(self):
        """iterate all the pages in this xml file
        """
        context = etree.iterparse(self.filename, events=('end',), tag='{%s}page' % self.ns) 
        for event, element in context:

            page = {}
            page['id'] = element.findtext('{%s}id' % self.ns)
            page['title'] = element.findtext('{%s}title' % self.ns)
            # currently I only care about the text
            page['text'] = element.findtext('{%s}revision/{%s}text' % (self.ns, self.ns))
            #page['revision'] = {}
            #page['revision_id'] = element.findtext('{%s}revision/{%s}id' % (self.ns, self.ns))
            #page['revision_text'] = element.findtext('{%s}revision/{%s}text' % (self.ns, self.ns))
            
            if self.version >= 0.6:
                # ns field starts from version 0.6
                page['ns'] = element.findtext('{%s}ns' % self.ns)
                
            if self.version >= 0.3:
                redirect = element.find('{%s}redirect' % self.ns)
                if redirect is not None:
                    if self.version >= 0.6:
                        # starting from version 0.6, the redirect target will be in `title` attribute
                        page['redirect'] = redirect.attrib['title']
                    else:
                        # previous versions need to find redirect target from text
                        #match = re.search(r'\[\[(.*)\]\]', page['revision_text'])
                        match = re.search(r'\[\[(.*)\]\]', page['text'])
                        page['redirect'] = match.group(1) if match else 'NOTFOUND'
    
            yield page
            
            # clear the element
            element.clear()
            while element.getprevious() is not None:
                del element.getparent()[0]
    
        del context

    def countpages(self):
        """count number of pages in this xml dump
        """
        count = 0
        context = etree.iterparse(self.filename, events=('end',), tag=self.xmlns+'page') 
        for event, element in context:
            # increase the count
            count += 1
            if count % 10000 == 0:
                print count
            
            # clear the element
            element.clear()
            while element.getprevious() is not None:
                del element.getparent()[0]
    
        del context
        return count

def import2mongo():
    from pymongo import MongoClient
    conn = MongoClient()
    db = conn.enwiki_20091017
    pages = db.pages

    xml_filename = sys.argv[1]
    mwdump = MWDump(xml_filename)
    count = 0
    for page in mwdump.iterpages():
        key = {'_id': page['id']}
        data = {'$set': page}
        pages.update(key, data, True)
        count += 1

        if count % 10000 == 0:
            print count, 
        
    print 'done'

def find_ns():
    
    from pymongo import MongoClient
    conn = MongoClient()
    db = conn.enwiki_20091017
    pages = db.pages

    namespaces = {
        'Media': -2,
        'Special': -1,
        'Talk': 1,
        'User': 2,
        'User talk': 3,
        'Wikipedia': 4,
        'Wikipedia talk': 5,
        'File': 6,
        'File talk': 7,
        'MediaWiki': 8,
        'MediaWiki talk': 9,
        'Template': 10,
        'Template talk': 11,
        'Help': 12,
        'Help talk': 13,
        'Category': 14,
        'Category talk': 15,
        'Portal': 100,
        'Portal talk': 101
        }

    from collections import defaultdict
    counts = defaultdict(int)
    from time import time
    start = time()
    
    count = 0
    for page in pages.find():
        title = page['title']
        ns = 0
        if title.find(':') != -1:
            prefix = title[:title.find(':')]
            if namespaces.has_key(prefix):
                ns = namespaces[prefix]
            else:
                ns = 9999
        key = {'_id': page['id']}
        data = {'$set': {'ns': ns}}
        pages.update(key, data, True)

        counts[ns] += 1

        count += 1
        if count % 10000 == 0:
            print count, 

    print 'done'
    print counts
    elaspe = time() - start
    print 'time used: ', elaspe

    conn.disconnect()
    
def main():
    if len(sys.argv) < 2:
        print "Usage: pymwdumper.py <xml-file>"
        sys.exit(0)

    find_ns()
    sys.exit()
        
    xml_filename = sys.argv[1]
    mwdump = MWDump(xml_filename)
    count = 0
    for page in mwdump.iterpages():
        print page['id'], page['title'], page['redirect'] if 'redirect' in page else 'NOREDIRECT'

        count += 1
        if count > 1000:
            break

    #count = mwdump.countpages()
    #print "number of pages in this xml:", count


if __name__ == '__main__':
    main()
