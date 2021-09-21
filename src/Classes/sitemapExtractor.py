from xml.dom.minidom import parse
import xml.dom.minidom
import sys
import pathlib
import requests
# ultimate_sitemap_parser
from usp.tree import sitemap_tree_for_homepage


# For a sitemap that has been downloaded
# extract all the link inside and store in a file of the same name in the same directory as this program
# xml_file =  sys.argv[1]


def sitemapExtractor(xml_file):
    if type(xml_file) is not pathlib.PosixPath:
        xml_file_path = pathlib.Path(xml_file)
    outputName = xml_file_path.parent.joinpath(xml_file_path.stem+ ".txt")
    
    if xml_file_path.exists():
        DOMTree = xml.dom.minidom.parse(xml_file)
        root_node = DOMTree.documentElement
        loc_nodes = root_node.getElementsByTagName("loc")


    if outputName.exists():
        outputName.unlink()
    f = outputName.open(mode = "x")

    print("Output location: " + str(outputName))

    for loc in loc_nodes:
        location = loc.childNodes[0].data
        
        if ".xml" in location:
            print("There is a sitemap ", location, "in this sitemap, it will also need to be downloaded to be extracted.")
        else:
            f.write(location + "\n")

    f.close()
    return(outputName)

# sitemapExtractor(xml_file)
