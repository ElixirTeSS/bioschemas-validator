from usp.tree import sitemap_tree_for_homepage
import pathlib
from urllib.parse import urlparse
import src.log as log


def extractWebsite(websiteLink, printDetail=False):
    outputName = pathlib.Path(f"{urlparse(websiteLink).netloc}.txt")

    if outputName.exists():
        outputName.unlink()

    log.info(f"Output location: {outputName}")
    with outputName.open(mode="x") as output_file:
        tree = sitemap_tree_for_homepage(websiteLink)
        for page in tree.all_pages():
            output_file.write(page.url + "\n")
            if printDetail:
                log.info(f"{page.url}")
    return(outputName)


def isUrl(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except Exception as errorMessage:
        log.info(f"Not a valid url, please double check. {errorMessage}")
        return False
