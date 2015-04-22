#!/usr/bin/env python3

import os
import re
import sys
from lxml import etree

class MWDump(object):
    """Read MediaWiki XML dump file
    """

    def __init__(self, filename):
        """
        """
        self.filename = filename
        from bz2 import BZ2File
        self.f = BZ2File(self.filename)

        self.getns()

    def getns(self):
        """get xmlns
        """
        context = etree.iterparse(self.f, events=('start-ns',))
        for action, obj in context:
            # we only care the declaration at firt line
            break

        if not obj or not obj[1].startswith('http://www.mediawiki.org/xml/export'):
            print("Cannot find valid xmlns declarations.")
            sys.exit()

        self.ns = obj[1]
        match = re.match('http://www.mediawiki.org/xml/export-(\d\.\d+)/', self.ns)
        self.version = float(match.group(1))

    def iterpages(self):
        """iterate all the pages in this xml file
        """
        self.f.seek(0)
        context = etree.iterparse(self.f, events=('end',), tag='{%s}page' % self.ns) 
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

    def close():
        self.f.close()

    def countpages(self):
        """count number of pages in this xml dump
        """
        count = 0
        context = etree.iterparse(self.filename, events=('end',), tag=self.xmlns+'page') 
        for event, element in context:
            # increase the count
            count += 1
            if count % 10000 == 0:
                print(count)
            
            # clear the element
            element.clear()
            while element.getprevious() is not None:
                del element.getparent()[0]
    
        del context
        return count
    
def main():
    if len(sys.argv) < 2:
        print("Usage: pymwdumper.py <xml-file>")
        sys.exit(0)

    xml_filename = sys.argv[1]
    mwdump = MWDump(xml_filename)
    count = 0
    for page in mwdump.iterpages():
        print(page['id'], page['title'], page['redirect'] if 'redirect' in page else 'NOREDIRECT')

        count += 1
        if count > 1000:
            break

    #count = mwdump.countpages()
    #print("number of pages in this xml:", count)


if __name__ == '__main__':
    main()
