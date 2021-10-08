from usp.tree import sitemap_tree_for_homepage
import pathlib
import sys
# ultimate_sitemap_parser
from urllib.parse import urlparse
import click
sys.path.append("./")
import src.Classes.config as config

def extractWebsite(websiteLink, printDetail=False):
    outputName = pathlib.Path(urlparse(websiteLink).netloc+".txt")

    if outputName.exists():
        outputName.unlink()
    f = outputName.open(mode = "x")

    click.echo("Output location: " + str(outputName),
          file=config.OUTPUT_LOCATION_WRITE)

    tree = sitemap_tree_for_homepage(websiteLink)
    for page in tree.all_pages():
        f.write(page.url + "\n")
        if printDetail:
            click.echo(str(page.url),
                       file=config.OUTPUT_LOCATION_WRITE)
    f.close()
    return(outputName)


def isUrl(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except:
        click.echo("This is not a valid url, please double check.",
                   file=config.OUTPUT_LOCATION_WRITE)
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
