import rdflib
from rdflib import Graph, plugin
from rdflib.serializer import Serializer
from pyld import jsonld
import json
import pprint
import os
import pathlib

#      as the data is converted from nquads to json-ld, the structure of the data is a different at some places  
#      for example,                               
#      "sameAs": {
#      "@id": "http://purl.uniprot.org/uniprot/P32774"
#      } 
#      should be
#      "sameAs": "http://purl.uniprot.org/uniprot/P32774"


def convertIDtoValue(oldDict):
    """If the property only has one kay "@id", assume it to be the value of the property

    Args:
        oldDict (dict): The original directory

    Returns:
        dict: The new directory with property with single "@id" kay to have the value of it instead
    """    
    for k, v in oldDict.items():
        if isinstance(v, dict):
            if len(v.keys()) == 1 and "@id" in v.keys():
                v = v["@id"]
                oldDict[k] = v
        elif isinstance(v, list):
            v = convertIDtoValueListRecur(v)
            oldDict[k] = v
    return oldDict


def convertIDtoValueListRecur(listOfDict):
    """Recursive function of the convertIDtoValue

    Args:
        listOfDict (list): The list of dict in the original dict

    Returns:
        list: The list of directory with property with single "@id" kay to have the value of it instead
    """    
    newList = list()
    for dic in listOfDict:
        if isinstance(dic, dict):
            if len(dic.keys()) == 1 and "@id" in dic.keys():
                newList.append(dic["@id"])
        elif isinstance(dic, list):
            convertIDtoValueListRecur(dic)
    return newList


def convertformattoJSONLD(path, dataFormat):
    """Convert metadata in other format such as NQuards and RDF to JSON-LD

    Args:
        path (Path): Path to the data that needs to be converted
        dataFormat (string): the format of the data
    
    Returns:
        resultPaths(list): The list of path of the resulting metadata in JSONLD

    """
    g = rdflib.ConjunctiveGraph()

    # parse the metadata to a graph
    if type(path) is not str:
        path = str(path)
    result = g.parse(location=path, format=dataFormat)

    # since this is for a bioschemas validator, which uses schema.org vocab
    context = {"@vocab": "https://schema.org/"}
    # serialize from the graph to json-ld
    jsonData = g.serialize(format='json-ld', context=context, indent=4)

    jsonString = jsonData if isinstance(jsonData, str) else jsonData.decode("utf-8")
    pretty_json_dict = json.loads(jsonString)

    # save it to a file of the same name but change from .nq to .txt
    path = pathlib.Path(path)
    dirName = pathlib.Path(str(path.parent) + "_jsonld")

# TODO make it return a list of result path and change command.py and test_wrapper to accomandate it
    bioProfileDict = list()
    resultPaths = list()
    index = 0
    # there are many items in the graph but only the ones conforms to bioschemas profile
    # is the one needed to be validated
    for dic in pretty_json_dict["@graph"]:
        if "http://purl.org/dc/terms/conformsTo" in dic.keys():
            resultPath = dirName.joinpath(pathlib.Path(path.name).stem + "_" + str(index) + ".jsonld" )
            
            if resultPath.exists():
                os.remove(resultPath)
    #         print(resultPath.parent)
            if resultPath.parent.exists() is False:
                os.mkdir(str(resultPath.parent))
            with open(str(resultPath), "x") as f:
                index += 1
                resultPaths.append(resultPath)
                if isinstance(dic["http://purl.org/dc/terms/conformsTo"], str) and ("https://bioschemas.org" in dic["http://purl.org/dc/terms/conformsTo"]):
                    dic = convertIDtoValue(dic)
                    bioProfileDict.append(dic)
                    f.write(str(dic).replace("'", "\"")+ "\n")

                elif isinstance(dic["http://purl.org/dc/terms/conformsTo"], dict) and ("https://bioschemas.org" in dic["http://purl.org/dc/terms/conformsTo"]["@id"]):
                    dic = convertIDtoValue(dic)
                    bioProfileDict.append(dic)
                    f.write(str(dic).replace("'", "\"")+ "\n")
                elif isinstance(dic["http://purl.org/dc/terms/conformsTo"], list) and ("https://bioschemas.org" in dic["http://purl.org/dc/terms/conformsTo"]):
                    dic = convertIDtoValue(dic)
                    bioProfileDict.append(dic)
                    f.write(str(dic).replace("'", "\"")+ "\n")
    return resultPaths
                                    
