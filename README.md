A Python package similiar to [MWDumper](http://www.mediawiki.org/wiki/Manual:MWDumper)

This package try to handle different versions of dump file, according to the dtd found at
http://www.mediawiki.org/xml/export-0.{1-7}.xsd

Dependencies
-----------
- lxml

Related Projects
----------------
- ssffsd's [wikdump](https://github.com/saffsd/wikidump) use regex to extract page info, it should be faster.
- gareth-lloyd's [visualizing-events](https://github.com/gareth-lloyd/visualizing-events/blob/master/wikipedia_processor/page_parser.py)
  use `xml.sax`.
