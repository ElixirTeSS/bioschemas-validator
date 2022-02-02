import extruct
import requests
import json
import os
import click
from w3lib.html import get_base_url
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import pathlib
import rdflib
import src.Classes.config as config
# def progressPerc(total, current):
#     sys.stdout.write("\r%d%%" % (current*100/total))
#     sys.stdout.flush()

def urlValidation(url):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    # print(url)
    return bool(re.match(regex, url))


def extract(oriPath):
    """This function 
    Args:
        oriPath (str/Path): A path that can be a url, a file path or a dir path
    """
    click.echo("Extracting static JSON-LD data from the link in/of "+
          str(oriPath), file=config.OUTPUT_LOCATION_WRITE)
    # pp = pprint.PrettyPrinter(indent=2)
    links = list()
    
    # the path have to be check if it is an url as if parse
    if urlValidation(str(oriPath)):
        click.echo("This is a url/path", file=config.OUTPUT_LOCATION_WRITE)
        links.append(str(oriPath))
    else:
        if type(oriPath) is str:
            oriPath = pathlib.Path(oriPath)

        if oriPath.is_file() and oriPath.suffix == ".txt":
            click.echo("This is a file of a list of url/path",
                  file=config.OUTPUT_LOCATION_WRITE)
            with open(oriPath, "r") as file:
                links = file.readlines()
            # click.echo(links)
        elif oriPath.is_dir():
            click.echo("Extracting static JSON-LD data from the files in directory " +
                  str(oriPath), file=config.OUTPUT_LOCATION_WRITE)
            links = list(oriPath.iterdir())
        else:
            links.append(str(oriPath))

    # click.echo(links)
    resultPath = config.METADATA_LOC
    totalNumLinks = len(links)
    newPath = None


    # click.echo(str(links),
    #        file=config.OUTPUT_LOCATION_WRITE)
    for n in range(totalNumLinks):
        # click.echo(links[n])
        link = links[n].rstrip() if type(links[n]) is str else str(links[n]).rstrip()
        # click.echo(link)

        html = ""
        url  = ""
        domain = ""
        # click.echo(urlValidation(link))
        dirCreated = False
        #  if the link is a url
        if urlValidation(link) is True:
            domain = urlparse(link).netloc
            outputName = link.split("/")[-1].strip() if len(link.split("/")[-1]) != 0 else link.split("/")[-2]
            r = requests.get(link)
            html = r.text
            url = r.url
            
            
        # if the link is a path to a local html file
        elif pathlib.Path(link).exists() and bool(BeautifulSoup(open(link, "r").read(), "html.parser").find()):     
            domain = link.split("/")[-2] if len(link.split("/"))>=2 else link.split("/")[-1]
            outputName = link.split("/")[-1].split(".")[0]
            html = open(link, "r").read()
#         Return the base url if declared in the given HTML text, relative to the given base url.
#         If no base url is found, the given baseurl is returned.
            click.echo("Local HTML file", file=config.OUTPUT_LOCATION_WRITE)
        
        else:
            click.echo("\nThis path in \"" + str(oriPath) +
                  "\" is neither url nor local html document, please double check.", file=config.OUTPUT_LOCATION_WRITE)
            html = open(link, "r").read() 


        base_url = get_base_url(html, url)

# list of syntaxes the library extruct, 'json-ld' is removed from the list as it is prioritied
        syntaxesList = ['microdata',  'opengraph', 'microformat', 'rdfa', 'dublincore']
        
        data = extruct.extract(html, base_url)

        resultList = list()
        # priorities json-ld syntax
        if len(data["json-ld"]) != 0:
            for i in range(len(data["json-ld"])):
                newPath = pathlib.Path(resultPath) / domain
                if not os.path.exists(newPath):
                    dirCreated = True
                    os.makedirs(newPath)
                outputFile = newPath / outputName 
                outputFile = newPath.joinpath(
                    outputName + "_" + str(i) + config.METADATA_EXT)
#                     click.echo("outputFile",outputFile)
                if os.path.exists(outputFile):
                    os.remove(outputFile)
                f = open(outputFile, "x")
#                     click.echo("output name: ", outputFile)
                dataJSONLD = data["json-ld"][i]
                pretty_json = json.dumps(dataJSONLD , indent=2) 
                f.write(pretty_json)
                f.close()
                resultList.append(outputFile)
                # click.echo(outputFile)
                # click.echo(newPath)

        else:
            for syntax in syntaxesList:
                if len(data[syntax]) != 0:
                    if syntax == "rdfa" or syntax == "microdata":
                        #TODO convert rdfa and Microdata to jsonld as they are inclused in the rdflib
                        g = rdflib.ConjunctiveGraph()

                        # # parse the metadata to a graph
                        # if type(path) is not str:
                        #     path = str(path)
                        # result = g.parse(location=path, format=syntax)

                        # # since this is for a bioschemas validator, which uses schema.org vocab
                        # context = {"@vocab": "https://schema.org/"}
                        # # serialize from the graph to json-ld
                        # jsonData = g.serialize(format='json-ld', context=context, indent=4)

                        # pretty_json_dict = json.loads(jsonData.decode("utf-8"))

                    
            click.echo("This is no JSON-LD data to extract in " + link, file = config.OUTPUT_LOCATION_WRITE)
            pass
        # click.echo(newPath)
        # progressPerc(totalNumLinks, n)
    # progressPerc(totalNumLinks, n+1)
    click.echo("Extraction done.", file=config.OUTPUT_LOCATION_WRITE)
    # click.echo(str(newPath))
    if dirCreated:
        return str(newPath)
    return resultList
    
