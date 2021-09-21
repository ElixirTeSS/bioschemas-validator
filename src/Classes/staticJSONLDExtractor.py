import extruct
import requests
import pprint
import json
import os
from w3lib.html import get_base_url
from urllib.parse import urlparse
import time
import sys
sys.path.append("./")
from bs4 import BeautifulSoup
import re
import pathlib 
import rdflib
import src.Classes.config as config
def progressPerc(total, current):
    sys.stdout.write("\r%d%%" % (current*100/total))
    sys.stdout.flush()

def urlValidation(url):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

    # print(url)
    return bool(re.match(regex, url))


def extract(oriPath):
    """This function 
    Args:
        oriPath (str/Path): A path that can be a url, a file path or a dir path
    """
    print("Extracting static JSON-LD data from the link in/of", str(oriPath))
    # pp = pprint.PrettyPrinter(indent=2)
    links = list()
    
    # the path have to be check if it is an url as if parse
    if urlValidation(str(oriPath)):
        print("This is a url/path")
        links.append(str(oriPath))
    else:
        if type(oriPath) is str:
            oriPath = pathlib.Path(oriPath)

        if oriPath.is_file() and oriPath.suffix == ".txt":
            print("This is a file of a list of url/path")
            with open(oriPath, "r") as file:
                links = file.readlines()
            # print(links)
        elif oriPath.is_dir():
            print("Extracting static JSON-LD data from the files in directory" + str(oriPath))
            links = list(oriPath.iterdir())
        else:
            links.append(str(oriPath))

    # print(links)
    resultPath = config.METADATA_LOC
    totalNumLinks = len(links)
    newPath = None


    for n in range(totalNumLinks):
        # print(links[n])
        link = links[n].rstrip() if type(links[n]) is str else str(links[n]).rstrip()
        # print(link)

        html = ""
        url  = ""
        domain = ""
        # print(urlValidation(link))
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
            print("Local HTML file")
        
        else:
            print("\nThis path in \"" + str(oriPath) + "\" is neither url nor local html document, please double check.")
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
#                     print("outputFile",outputFile)
                if os.path.exists(outputFile):
                    os.remove(outputFile)
                f = open(outputFile, "x")
#                     print("output name: ", outputFile)
                dataJSONLD = data["json-ld"][i]
                pretty_json = json.dumps(dataJSONLD , indent=2) 
                f.write(pretty_json)
                f.close()
                resultList.append(outputFile)
                # print(outputFile)
                # print(newPath)

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

                    


            print("This is no JSON-LD data to extract in " + link)
            pass
        # print(newPath)
        progressPerc(totalNumLinks, n)
    progressPerc(totalNumLinks, n+1)
    print("Extraction done.") 
    # print(str(newPath))
    if dirCreated:
        return str(newPath)
    return resultList
    
