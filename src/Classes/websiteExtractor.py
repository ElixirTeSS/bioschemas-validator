from usp.tree import sitemap_tree_for_homepage
import pathlib
import sys
# ultimate_sitemap_parser
from urllib.parse import urlparse
import click
# try:
#     # python2
#     from urlparse import urlparse
# except:
#     # python3
#     from urllib.parse import urlparse

def extractWebsite(websiteLink, printDetail=False):
    outputName = pathlib.Path(urlparse(websiteLink).netloc+".txt")

    if outputName.exists():
        outputName.unlink()
    f = outputName.open(mode = "x")

    print("Output location: " + str(outputName))

    tree = sitemap_tree_for_homepage(websiteLink)
    for page in tree.all_pages():
        # print(type(page))
        f.write(page.url + "\n")
        if printDetail:
            print(page.url)
    f.close()
    return(outputName)


def isUrl(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except:
        click.echo("This is not a valid url, please double check.")
        return False

# if len(sys.argv) < 2:
#     print("Missing website url")
#     exit


# websiteLink =  sys.argv[1]
# printDetail = False
# if len(sys.argv) == 3 and sys.argv[2] == "-p":
#     printDetail = True

# if not isUrl(websiteLink):
#     click.echo("This is not a valid url, please double check.")
# else:
#     extractWebsite(websiteLink, printDetail)
