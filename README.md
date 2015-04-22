A Python package similiar to [MWDumper](http://www.mediawiki.org/wiki/Manual:MWDumper)

This package try to handle different versions of dump file, according to the dtd found at
http://www.mediawiki.org/xml/export-0.{1-7}.xsd

## Usage

Install the package via `pip install mwdump`. Then you can use it like

```python
def process_dump_file(filename):
    from mwdump import MWDump
    with MWDump(xml_filename) as mw:
        count = 0
        for page in mw.iterpages():
            print(page['id'], page['title'], page['redirect'] if 'redirect' in page else 'NOREDIRECT')

            count += 1
            if count > 1000:
                break

if __name__ == '__main__'
    import sys
    process_dump_file(sys.argv[1])

```

## Dependencies

- lxml

## Related Projects

- ssffsd's [wikdump](https://github.com/saffsd/wikidump) use regex to extract page info, it should be faster.
- gareth-lloyd's [visualizing-events](https://github.com/gareth-lloyd/visualizing-events/blob/master/wikipedia_processor/page_parser.py)
  use `xml.sax`.
