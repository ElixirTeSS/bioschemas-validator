#from w3lib.html import get_base_url
from src.Classes.profileYmlToDict import tranform_yml_to_dict
from src.Classes.profileYmlToDict import separateSpecAndMapping
import itertools
import json
import os
import pathlib
#import extruct
#import requests
import pprint
import re

import click
import sys
sys.path.append("./")
import src.Classes.config as config
from jsonschema import Draft7Validator

def lowerFirstLetter(string):
    return string[0].lower() + string[1:]
# build a json-LD profile from information in a text file
# as the validator is using profile from text file in form of python dict
    # read a profile data file into a list
global filepath
global title


def build_profile(path):
    try:
        global filepath
        global outputName
        filepath = path

        outputName = pathlib.Path(filepath.name).stem + config.PROFILE_EXT
    #         filepath.parent.mkdir(parents=True, exist_ok=True)
        file = filepath.read_text()
        specInfo, mapping = separateSpecAndMapping(file)
        # outfile = pag
        if specInfo is None or mapping is None:
            click.secho(
                "Something in the profile yml file does not follow the format, the json schema will not be made.", fg="red", file=config.OUTPUT_LOCATION_WRITE)
            return -1
        read_definition()
        read_typeValueDict()
        dictMade = produce_dict(specInfo, mapping)
        print_dict(dictMade, filepath)
        Draft7Validator.check_schema(dictMade)
        click.secho("Done", fg="green", file=config.OUTPUT_LOCATION_WRITE)
        

        return 0
    except KeyboardInterrupt:
        click.secho("Program stopped", fg="red", file=config.OUTPUT_LOCATION_WRITE)
        return -1
    except FileNotFoundError:
        errorMessage = str("The target data " + str(path) +
                           " is not an existing file, please double check")
        click.secho(errorMessage, fg='yellow',
                    file=config.OUTPUT_LOCATION_WRITE)
        # sys.exc_info() is a tuple of type
        errorMessage = ""
        for item in sys.exc_info():
            errorMessage = errorMessage + str(item)

        click.secho("Error:" + errorMessage, fg="red",
                    file=config.OUTPUT_LOCATION_WRITE)
    except:
        errorMessage = ""
        # sys.exc_info() is a tuple of type
        for item in sys.exc_info():
            errorMessage = errorMessage + str(item)

        click.secho("Error:" + errorMessage, fg="red", file=config.OUTPUT_LOCATION_WRITE)

        return -1

def read_definition():
    global definitions
    file = pathlib.Path("src/Classes/definitions.txt").read_text()

    definitions = json.loads(file)



def read_typeValueDict():
    global typeValueDict
    file = pathlib.Path("src/Classes/typeValueDict.txt").read_text()

    typeValueDict = json.loads(file)


def produce_dict(specInfo, mapping):
    """Use the information extracted from the yml file to build a json schemas

    Args:
        specInfo (str): specification of the profile
        mapping (str): all the properties in the profile
    """    
    global requiredProperties
    global recommendedProperties
    global optionalProperties

    # initialize lists
    requiredProperties = list()
    recommendedProperties = list()
    optionalProperties = list()

    # initialize python dict
    dictMade = make_profile_spec(specInfo)
    dictMade["$defs"] = definitions
    dictMade["required"] = list()
    dictMade["properties"] = dict()


    propertyInfos = mapping.split("- property: ")[1:]
    propertyInfos = list(filter(None, propertyInfos))

    for propertyInfo in propertyInfos:
        propertyName = propertyInfo.split("expected_types:")[0].replace("\n", "").strip()
        if "marginality: Minimum" in propertyInfo:
            dictMade["required"].append(propertyName.strip())
            requiredProperties.append(propertyName.strip())
        elif "marginality: Recommended" in propertyInfo:
            recommendedProperties.append(propertyName.strip())
        elif "marginality: Optional" in propertyInfo:
            optionalProperties.append(propertyName.strip())
        individualProp = make_property(propertyInfo, propertyName)
        dictMade["properties"][propertyName.replace(" ", "")] = individualProp


    completenessListFile(requiredProperties, recommendedProperties, optionalProperties)
    dictMade["$defs"] = definitions

    return(dictMade)
    


def completenessListFile(required, recommended, optional):
    global filepath

    outputName = pathlib.Path(filepath.name).stem + config.PROFILE_MARG_EXT
    outputDir = pathlib.Path(config.PROFILE_MARG_LOC)
    resultPath = outputDir.joinpath(filepath.parts[1])
    resultPath = resultPath.joinpath(outputName)
    resultPath.parent.mkdir(parents=True, exist_ok=True)
    if resultPath.exists():
            resultPath.unlink()
    f = resultPath.open(mode = "x")
    # print("output name: ", resultPath + outputName)
    currentDict = dict()
    currentDict["minimum"] = required
    currentDict["recommended"] = recommended
    currentDict["optional"] = optional
    pretty_json = json.dumps(currentDict , indent=2)
    f.write(pretty_json)
        # pprint.pprint(currentDict, log_file)

    f.close()


def make_profile_spec(specInfo):
    global title
    dictMade = {}
    for line in specInfo.splitlines():
        if "  title: " in line:
            dictMade["@type"] = line.split("title: ")[1].strip()
            title = dictMade["@type"]
        elif "  version:" in line:
            dictMade["version"] = line.split("version: ")[1].strip()
            break

    dictMade["$schema"] = "http://json-schema.org/draft-07/schema#"
    dictMade["type"] = "object"
    dictMade["@context"] = "http://schema.org"
    return dictMade


def make_property(propertyInfo, propertyName):
    global title
    title = propertyName
    # as the profile data starts with requiredm if there's no key required
    # in the dictionary, we are at the first property
    currentDict = {}
    lines = propertyInfo.split("  example: |-")[0]
    # print(lines)
    # the yml to dict method has been moved to a separate class for better code management
    # in the future in case the format of the yml file changes
    propertyDict = tranform_yml_to_dict(lines)
    if propertyDict["cardinality"] == "\"\"":
        click.secho("For property \"" + propertyName +
                    "\", the cardinality value is empty. It has been assumes to be MANY for the profile builder, please double check.", fg="cyan", file=config.OUTPUT_LOCATION_WRITE)
    if propertyDict["expected_types"] == "\"\"":
        click.secho("For property \"" + propertyName +
                    "\", the expected types is empty. Please double check.", fg="cyan", file=config.OUTPUT_LOCATION_WRITE)
    if propertyDict["marginality"] == "\"\"":
        click.secho("For property \"" + propertyName +
                    "\", the marginality is empty. It should be Minimum,Recommended or Optional.", fg="cyan", file=config.OUTPUT_LOCATION_WRITE)
    controlledVocab = True if propertyDict["controlled_vocab"] != "" else False
    ManyOrNone = True if propertyDict["cardinality"] == "MANY" or propertyDict["cardinality"] == "\"\"" else False
#         if propertyDict["cardinality"] == "MANY":
#             print(propertyDict["cardinality"])
#         print(ManyOrNone)
#         print(len(propertyDict["expected_types"]))

    multiShemas = "We are expecting one of the following: "
    singleSchema = "We are expecting "
    if ManyOrNone and len(propertyDict["expected_types"])>1:

        currentDict["anyOf"] = list()
        arrayDict = dict()
        arrayDict["type"] = "array"
        currentDict["anyOf"].append(arrayDict)
        arrayDict["items"] = dict()
#             mergeEnumIndex = 0
        arrayDict["items"]["anyOf"] = list()
        currentDict["validityCheck"] = multiShemas
        for item in propertyDict["expected_types"]:
            returned_ref = return_ref_dict(item, controlledVocab)
            currentDict["anyOf"].append(returned_ref)
            currentDict["validityCheck"] = currentDict["validityCheck"] + returned_ref["validityCheck"] + ", "
            arrayDict["items"]["anyOf"] .append(return_ref_dict(item, controlledVocab))


    elif ManyOrNone and len(propertyDict["expected_types"])==1:
        currentDict["anyOf"] = list()
        arrayDict = dict()
        arrayDict["type"] = "array"
        currentDict["anyOf"].append(arrayDict)
        arrayDict["items"] = return_ref_dict(propertyDict["expected_types"][0], controlledVocab)
        currentDict["anyOf"].append(return_ref_dict(propertyDict["expected_types"][0], controlledVocab))
        currentDict["validityCheck"] = singleSchema + currentDict["anyOf"][1]["validityCheck"] + " in an array or as a single object"

    elif propertyDict["cardinality"] == "ONE" and len(propertyDict["expected_types"])>1:
        currentDict["anyOf"] = list()
        arrayDict = dict()
        arrayDict["type"] = "array"
        arrayDict["maxItems"] = 1
        currentDict["anyOf"].append(arrayDict)
        arrayDict["items"] = dict()
        arrayDict["items"]["anyOf"] = list()
        currentDict["validityCheck"] = multiShemas

        for item in propertyDict["expected_types"]:
            returned_ref = return_ref_dict(item, controlledVocab)
            currentDict["anyOf"].append(returned_ref)
            currentDict["validityCheck"] = currentDict["validityCheck"] + returned_ref["validityCheck"] + ", "
            arrayDict["items"]["anyOf"] .append(return_ref_dict(item, controlledVocab))

    elif propertyDict["cardinality"] == "ONE" and len(propertyDict["expected_types"])==1:
        currentDict["anyOf"] = list()
        arrayDict = dict()
        arrayDict["type"] = "array"
        arrayDict["maxItems"] = 1
        currentDict["anyOf"].append(arrayDict)
        arrayDict["items"] = return_ref_dict(propertyDict["expected_types"][0], controlledVocab)
        currentDict["anyOf"].append(return_ref_dict(propertyDict["expected_types"][0], controlledVocab))
        currentDict["validityCheck"] = singleSchema + currentDict["anyOf"][1]["validityCheck"] + " in an array or as a single object"


    if "validityCheck" in currentDict.keys():
        currentDict["validityCheck"] = currentDict["validityCheck"].rstrip(", ")
    return currentDict

def simplifyingDef(dictNeeded):
    global title
    if type(dictNeeded) is dict:
        for key, value in dictNeeded.items():
            # if the property reference to another shemas
            if "$ref" == key:
                if value == title:
                    dictNeeded["$ref"] = "#/"
                elif value in definitions.keys():
                    dictNeeded["$ref"] = "#/$defs/" + value
            elif type(value) is dict or list:
                simplifyingDef(dictNeeded[key])
    elif type(dictNeeded) is list:
        for item in dictNeeded:
            simplifyingDef(item)


def return_ref_dict(name, controlledVocab):
    global title
    ref = dict()
    filepath = pathlib.Path(config.PROFILE_LOC)
    if filepath.exists() != True:
        filepath.mkdir(parents=True)
    existProfile = list()
    for child in filepath.iterdir():
        if child.is_dir():
            for profiledes in child.iterdir():
                if str(profiledes.name).find("RELEASE") != -1:
#                         existProfileName.append(child)
                    existProfile.append(child)
    if name == title:
        ref["$ref"] = "#/"
        ref["validityCheck"] = "profile type \"" + name + "\""

    # if the reference type is one of the profile with a released version
    # the profile name would be in the existProfile list
    elif filepath.joinpath(pathlib.Path(name)) in existProfile:
        profileReleased = sorted(filepath.joinpath(pathlib.Path(name)).glob("*RELEASE*"))[0]
#             print(profileReleased)
        f = profileReleased.read_text()
        definitions[name] = json.loads(f)
        ref["$ref"] = "#/$defs/" + name
        ref["validityCheck"] = "profile type \"" + name + "\", version " +  str(pathlib.Path(profileReleased.name).stem)
        # check if the definition in the profile already exist in $def
        same = set(list(definitions.keys())).intersection(list(definitions[name]["$defs"].keys()))
        for s in same:
            del  definitions[name]["$defs"][s]

        # if the title profile is a definition in a ref profile,
        # remove it from the def in ref and replace all ref link to point
        # to the title profile instead
        if title in list(definitions[name]["$defs"].keys()):
            del  definitions[name]["$defs"][title]
            simplifyingDef(definitions[name]["properties"])
    elif name in definitions.keys():
        ref["$ref"] = "#/$defs/" + name
        ref["validityCheck"] = "type \"" + name + "\""
    elif name in typeValueDict.keys():
        ref["type"] = "object"
        ref["validityCheck"] = "schema.org type \"" + name + "\""
        ref["properties"] = dict()
        ref["properties"]["@type"] = dict()
        ref["properties"]["@type"]["anyOf"] = list()

        enum = typeValueDict[name]

        arrayType = dict()
        arrayType["type"] = "array"
        arrayType["items"] = dict()
        arrayType["items"]["enum"] = enum

        singleType = dict()
        singleType["enum"] = enum

        ref["properties"]["@type"]["anyOf"].append(arrayType)
        ref["properties"]["@type"]["anyOf"].append(singleType)

        # ref["properties"]["@type"]["enum"] = typeValueDict[name]
        ref["properties"]["@type"]["validityCheck"] = "schema.org type or subtype of\"" + name + "\""
    elif name == "Thing":
        ref["type"] = "object"
        ref["validityCheck"] = "schema.org or subtype of \"" + name + "\""
        ref["properties"] = dict()
        ref["properties"]["@type"] = dict()
        thingList = list(typeValueDict.values())
        # thingList = list(set(thingList))
        thingList = list(itertools.chain.from_iterable(thingList))
        ref["properties"]["@type"]["enum"] = thingList
        ref["properties"]["@type"]["validityCheck"] = "schema.org type or subtype of \"" + name + "\""
    elif name == "Text":
        ref["type"] = "string"
        # ref["minLength"] = 1
        ref["validityCheck"] = "string"
    elif name == "Number":
        ref["type"] = list()
        ref["validityCheck"] = "Number"
        ref["type"].append("number")
        ref["type"].append("string")
    elif name == "DateTime":
        ref["type"] = "string"
        ref["pattern"] = "date-time"
        ref["validityCheck"] = "value of type \"date-time\" in the format CCYY-MM-DDThh:mm:ss[Z|(+|-)hh:mm]  (e.g. 2018-11-13T20:20:39, 2018-11-13T20:20:39+00:00)"
    elif name == "Date":
        ref["type"] = "string"
        ref["pattern"] = "date"
        ref["validityCheck"] = "value of type \"date\" in the format CCYY-MM-DD (e.g. 2018-11-13)"
    elif name == "Time":
        ref["type"] = "string"
        ref["pattern"] = "time"
        ref["validityCheck"] = "value of type time in the format hh:mm:ss[Z|(+|-)hh:mm]  (e.g. 20:20:39, 20:20:39+00:00)"

    elif name == "Boolean":
        ref["type"] = list()
        ref["validityCheck"] = "boolean"
        ref["type"].append("boolean")
#             *allow string for type boolean?
#             ref["type"].append("string")
#             ref["enum"] = ["true", "false"]
    else:
        ref["type"] = "object"
        ref["validityCheck"] = "\"" + name + "\""
        ref["properties"] = dict()
        ref["properties"]["@type"] = dict()
        ref["properties"]["@type"]["const"] = name
        ref["properties"]["@type"]["validityCheck"] = "item \"" + name + "\""
        if (name == "DefinedTerm" or name == "PropertyValue") and controlledVocab:
            ref["required"] = ["url"]
            ref["properties"]["url"] = {"$ref": "#/$defs/URL"}
    return ref

def remove_duplicate_in_list(x):
    return list(dict.fromkeys(x))

def print_dict(currentDict, filepath):
    outputName = pathlib.Path(filepath.name).stem + config.PROFILE_EXT
    outputDir = pathlib.Path(config.PROFILE_LOC)
    resultPath = outputDir.joinpath(filepath.parts[1])
    resultPath = resultPath.joinpath(outputName)
    resultPath.parent.mkdir(parents=True, exist_ok=True)
    if resultPath.exists():
            resultPath.unlink()
    f = resultPath.open(mode = "x")
    # print("output name: ", resultPath + outputName)
    pretty_json = json.dumps(currentDict , indent=2)
    f.write(pretty_json)
        # pprint.pprint(currentDict, log_file)

    f.close()
