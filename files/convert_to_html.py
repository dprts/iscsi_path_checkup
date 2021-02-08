#!/usr/bin/python3

import sys
from json import load
from json2html import *
from datetime import datetime

css_text = """
<style>
    table { table-layout: auto;
        border-collapse: collapse;
        width: 100%;
    }

    table th {
        background-color: blue;
        color: white;
    }

    table td {
        border: 1px solid #ccc;
    }
    table .absorbing-column {
        width: 100%;
    }
    body > table > tbody > tr:nth-of-type(odd) {
        background-color: royalblue;
    }

    body > table > tbody > tr:nth-of-type(even) {
        background-color: cornflowerblue;
    }
</style>
"""


def usage():
    sys.stdout.write("""
Usage: {} <input json file> <output html file>
""".format(sys.argv[0]))


def main():
    if len(sys.argv) == 3:
        (progname, inf, outf) = (sys.argv[0], sys.argv[1], sys.argv[2])
        print("Executing: {} {} {}".format(progname, inf, outf))
    else:
        usage()
        sys.exit(-1)

    try:
        infp = open(inf, "r")
        data = load(infp)
        infp.close()

    except IOError:
        print("Error: File {} not found".format(inf))
        sys.exit(-1)

    try:
        outfp = open(outf, "w")
        outfp.write("<HTML>")
        outfp.write(css_text)
        outfp.write("<BODY>")
        outfp.write(json2html.convert(
            json=data,
            clubbing=True,
            table_attributes="border=\"1\" class=\"absorbing-column\"",
            escape=False))
        outfp.write("<b>Report generated on: {}</b>".format(
            datetime.now().astimezone().strftime("%d/%m/%Y %H:%M:%S %Z")))
        outfp.write("</BODY>")
        outfp.write("</HTML>")
        outfp.close()
        print("Done")
    except FileNotFoundError:
        print("Error: Can't write to {}".format(outf))
        sys.exit(-1)


if __name__ == "__main__":
    main()
