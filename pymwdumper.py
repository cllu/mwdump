#!/usr/bin/env python


import sys
from lxml import etree

NS = {
    'xmlns': 'http://www.mediawiki.org/xml/export-0.7/',   
}

class MWDumper(object):
    """Read MediaWiki XML dump file
    """

    def __init__(self, filename):
        """
        """
        self.xmlns = '{http://www.mediawiki.org/xml/export-0.7/}'
        self.filename = filename
        pass

    def iterpages(self):
        """
        """
        context = etree.iterparse(self.filename, events=('end',), tag=self.xmlns+'page') 
        for event, element in context:

            page = {}
            page['ns'] = element.findtext(self.xmlns+'ns')
            page['id'] = element.findtext(self.xmlns+'id')
            page['title'] = element.findtext(self.xmlns+'title')
            page['revision_id'] = element.findtext(self.xmlns+'revision/'+self.xmlns+'id')
            page['revision_text'] = element.findtext(self.xmlns+'revision/'+self.xmlns+'text')
    

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

       
    
def main():
    if len(sys.argv) < 2:
        print "Usage: pymwdumper.py <xml-file>"
        sys.exit(0)
    
    xml_filename = sys.argv[1]
    mwdumper = MWDumper(xml_filename)
    for page in mwdumper.iterpages():
        print page
        break

    count = mwdumper.countpages()
    print "number of pages in this xml:", count


if __name__ == '__main__':
    main()
