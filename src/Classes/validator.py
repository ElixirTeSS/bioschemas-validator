import json
from jsonschema import Draft7Validator
import datetime
import os
import re
from dateutil.parser import parse
import pathlib
import sys
sys.path.append("./")
import src.Classes.config as config
import click

semanticPairDatePath = pathlib.Path("./src/Classes/semanticPairDate.txt")
# validate a data using a schema
def validate(data, csv, schema = None, profilePath = ""):
    global errorPaths
    global existProperty
    global diffKeys
    existProperty = list(data.keys())
    errorPaths = list()
    correctData = data
    profileName = ""
    if schema is None:
        # if "@type" in data.keys():
        predicate = ""
        path = pathlib.Path(config.PROFILE_LOC)
        existProfile = os.listdir(path)
        if "@context" in data.keys():
            if type(data["@context"]) is list:
                for item in data["@context"]:
                    if type(item) is dict:
                        for key, value in item.items():
                            if "http://bioschemas.org/" in value or "https://bioschemas.org/" in value:
                                predicate = key + ":"
        # find the profile the data conforms to
        if "http://purl.org/dc/terms/conformsTo" in data.keys():
            profileName, version = profileVersionConform(data["http://purl.org/dc/terms/conformsTo"])
            # if the property value has a profile version
            if version != -1:
                profilePath = pathlib.Path(config.PROFILE_LOC) / profileName / (version + config.PROFILE_EXT)
#                     if the path the data conform does not exist, erase the profilePath value
                if profilePath.exists() is False:
                    click.secho("The profile the data claims to conform to, " + str(profilePath) + ", is does not exist. Therefore the most recently release or draft version of the same type will be used to validate the data instead.", fg="yellow",
                                file=config.OUTPUT_LOCATION_WRITE)
                    profilePath = ""

        
        # if there is no conformTo, see the metadata type
        elif "@type" in data.keys():
            # print(type(data["@type"] ))
            if type(data["@type"]) is str:
                profileName = data["@type"] 
            
            elif type(data["@type"]) is list:
                # print("type")

                for t in data["@type"]:
                    # print(t)
                    if t in existProfile:
                        profileName = t
                # if none of the type in the array is a Bioschemas profile
                if profileName == "":                        
                    click.secho("This metadata is of type: "+str(data["@type"])+", none is an existing Bioschemas profile type.",
                                file=config.OUTPUT_LOCATION_WRITE)
                    return
            
        data = bioschemasPredicateRemoval(data, predicate)
#           if the data did not have a profile link it conform to, only the type
        if profilePath == "":
            
            if profileName in existProfile:
                pathWithProfileName = path / profileName
                if pathWithProfileName.is_dir():
                    listv = os.listdir(pathWithProfileName)
                    listv.sort(key=sortby, reverse=True)
                    releaseList = [item for item in listv if "RELEASE" in item]
                    if releaseList != []:
                        version = releaseList[0]
                    else:
                        version = listv[0]

                profilePath = pathlib.Path(config.PROFILE_LOC,  profileName ,version)

                
        if profilePath != "":
            schema,  profilePath= path_to_dict(profilePath)
            click.secho("Validating against profile " + str(profileName) + " " + str(version),
                        file=config.OUTPUT_LOCATION_WRITE)
        elif profilePath == "":
            click.secho("The profile schemas, \"" + str(profileName) + "\", does not yet exist in the profile JSON schema directory, please add it first by running buildprofile with the source data for \"" + str(profileName) + "\".",
                        file=config.OUTPUT_LOCATION_WRITE)

    if schema is not None:
        version = profilePath.name
#             if the data uses only schemas.org properties, all property names should be lowerCamelCase
        if "@context" in data.keys() and type(data["@context"]) != list and "http://schema.org" in data["@context"]:
            schema["propertyNames"] = {"pattern": "^[a-z@\$][a-zA-Z]*$"}
        v = Draft7Validator(schema)
        errors = v.iter_errors(data)
        click.secho("=======================Validator Message:=================================",
                    file=config.OUTPUT_LOCATION_WRITE)
        for e in sorted(errors, key=lambda e: e.path):
            # if property does not exist
            if "is a required property" in e.message:
                click.secho(e.message + " but it's missing.", fg="red",
                            file=config.OUTPUT_LOCATION_WRITE)
            # if property exist but has error(s)
            else:
                if e.schema_path[0] == "properties":
                    del correctData[e.schema_path[1]]
                if "is not valid under any of the given schemas" in e.message:
                    click.secho("For property:" + str(e.schema_path[1])+" , " + str(e.message), fg="red",
                                file=config.OUTPUT_LOCATION_WRITE)
                elif "does not match" in e.message:
                    click.secho("Property name: "+str(e.message), fg="red",
                                file=config.OUTPUT_LOCATION_WRITE)

                else:
                    click.secho(e.message,
                                file=config.OUTPUT_LOCATION_WRITE)
                if "validityCheck" in e.schema.keys() :
                    click.secho(e.schema["validityCheck"],
                                file=config.OUTPUT_LOCATION_WRITE)
            click.secho("------",
                        file=config.OUTPUT_LOCATION_WRITE)
            errorPaths.append(e.schema_path[len(e.schema_path)-1])

        diffKeys = set(list(existProperty)) - set(list(data.keys()))
        if len(errorPaths)==0:
            click.secho("The data is valid against this profile",
                        file=config.OUTPUT_LOCATION_WRITE)
        elif len(errorPaths)>0:
            diffKeys = set(list(existProperty)) - set(list(data.keys()))
            click.secho("Existing property value(s) that has error: " + str(list(diffKeys)),
                        file=config.OUTPUT_LOCATION_WRITE)


        date_semantic_check(correctData)

        profilePathParts = list(profilePath.parts)
        # click.secho(str(profilePathParts),
                    # file=config.OUTPUT_LOCATION_WRITE)
        listPath = pathlib.Path(config.PROFILE_MARG_LOC) / profilePathParts[-2] / profilePathParts[-1]
        listPath = listPath.with_suffix(config.PROFILE_MARG_EXT)
        # click.secho(str(listPath),
                    # file=config.OUTPUT_LOCATION_WRITE)
        if listPath.exists() is True:
            result = check_completeness(
                existProperty, diffKeys, listPath, profileName, version, csv)
            return result
        return 0

def bioschemasPredicateRemoval(data, predicate):

    if type(data) is dict and "@type" in data.keys():
        for key, value in data.items():
            if type(value) is str and predicate in value:
                data[key] = value.replace(predicate, "")
            if type(value) is dict:
                bioschemasPredicateRemoval(value, predicate)
            if type(value) is list:
                for instance in value:
                    bioschemasPredicateRemoval(instance, predicate)
    return data

def profileVersionConform(value):
    valueType = type(value)
    profileName = ""
    version = ""
    url = ""
    if valueType is dict:
        for k, v in value.items():
            if type(v) is str and "bioschemas.org" in v:
                url = v
    elif valueType is list:
        for v in value:
            if type(v) is str and "bioschemas.org" in v:
                url = v
    elif valueType is str and "bioschemas.org" in value:
        url = value
    else:
        return "", -1

    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    if bool(re.match(regex, url)) is True:
        infoList = url.split("/")
        while "" in infoList:
            infoList.remove("")

#       the value is always a url link to the profile webpage on bioschemas which follows the same format
#             click.secho(infoList)
        profileName = infoList[3]
        version = infoList[4]
#         click.secho(profileName, version)
        return profileName, version

#         if the format of the string is not a url
    else:
        return "", -1


def create_marg_dict(profileName, version):
    result = dict()
    result["Profile Name"] = profileName
    result["Profile Version"] = version
    result["Minimum"] = dict()
    result["Recommended"] = dict()
    result["Optional"] = dict()
    return result

def create_completeness_dir(format, result, key1, key2, properties):

    number = str(len(properties)) if properties != "" else str(0)
    names = sorted(list(properties)) if properties != "" else None
    value = "None"
    if format == "num":
        value = number
    elif format == "name":
        value = names
    elif format == "all":
        names.append("Total: "+number)
        value = names
        
    result[key1][key2] = value

    return result

def check_completeness(existProperty, diffKeys, listPath, profileName, version, csv):


    result = create_marg_dict(profileName, version)


    profileListDict = json.loads(listPath.read_text())
    # property name such as @type that are not in the Bioschemas profile but should be in the json ld therefore will not be count as extra properties
    with pathlib.Path(config.METADATA_DEFAULT_PROP).open() as f:
        metadataDefaultProp = f.read().splitlines()

    noMinimum  = len(profileListDict["minimum"])
    noRecommended = len(profileListDict["recommended"])
    noOptional = len(profileListDict["optional"])

    existMinimum = set(profileListDict["minimum"]).intersection(existProperty)
    existRecommended = set(profileListDict["recommended"]).intersection(existProperty)
    existOptional = set(
        profileListDict["optional"]).intersection(existProperty)

    errorMinimum = set(profileListDict["minimum"]).intersection(diffKeys)
    errorRecommended = set(profileListDict["recommended"]).intersection(diffKeys)
    errorOptional = set(profileListDict["optional"]).intersection(diffKeys)

    diffMinimum = set(profileListDict["minimum"]) - set(existProperty)
    diffRecommended = set(profileListDict["recommended"]) - set(existProperty)
    diffOptional = set(profileListDict["optional"]) - set(existProperty)

    profileListDictValues = list(profileListDict.values())
    profileListDictValue = list()
    for v in profileListDictValues:
        profileListDictValue += v

    extraProp = (set(existProperty).difference(
        set(profileListDictValue))).difference(set(metadataDefaultProp))

    click.secho("============Properties Marginality Report:============",
                file=config.OUTPUT_LOCATION_WRITE)
    # Minimum
    click.secho("Marginality: Minimum",
                file=config.OUTPUT_LOCATION_WRITE)
    if noMinimum == 0:
        click.secho("    There are no minimum property required by this profile.",
                    file=config.OUTPUT_LOCATION_WRITE)
        create_completeness_dir(csv, result, "Minimum", "Missing", "")
        create_completeness_dir(csv, result, "Minimum", "Implemented", "")
        create_completeness_dir(csv, result, "Minimum", "Error", "")
    else:
        if len(list(diffMinimum)) != 0:
            click.secho("    Required property that are missing: " + str(list(diffMinimum)), fg="red",
                        file=config.OUTPUT_LOCATION_WRITE)
        else:
            click.secho("    The data has all the required property(ies).", 
                        file=config.OUTPUT_LOCATION_WRITE)

        if len(errorMinimum) != 0:
            click.secho("    Required property that has error: " +
                        str(list(errorMinimum)), fg="red",
                        file=config.OUTPUT_LOCATION_WRITE)
        else:
            click.secho("    Implemented required property has no error.", fg="green",
                        file=config.OUTPUT_LOCATION_WRITE)


        create_completeness_dir(csv, result, "Minimum", "Missing", diffMinimum)
        create_completeness_dir(csv, result, "Minimum",
                                "Implemented", existMinimum)
        create_completeness_dir(csv, result, "Minimum", "Error", errorMinimum)

    result["Valid"] = "True" if len(diffMinimum) == 0 and len(
        errorMinimum) == 0 else "False"
    # Recommended
    click.secho("Marginality: Recommended",
                file=config.OUTPUT_LOCATION_WRITE)
    if noRecommended == 0:
        click.secho("    There are no recommended property recommended by this profile.",
                    file=config.OUTPUT_LOCATION_WRITE)

        create_completeness_dir(csv, result, "Recommended", "Missing", "")
        create_completeness_dir(csv, result, "Recommended", "Implemented", "")
        create_completeness_dir(csv, result, "Recommended", "Error", "")
    else:
        if len(list(diffRecommended)) != 0:
            click.secho("    Recommended property that are missing: " + str(list(diffRecommended)), fg="yellow",
                        file=config.OUTPUT_LOCATION_WRITE)
        else:
            click.secho("    The data has all the recommended property(ies).",
                        file=config.OUTPUT_LOCATION_WRITE)


        if len(errorRecommended) != 0:
            click.secho("    Recommended property that has error: " +
                        str(list(errorRecommended)), fg="yellow",
                        file=config.OUTPUT_LOCATION_WRITE)
        else:
            click.secho("    Implemented recommended property has no error.",
                        file=config.OUTPUT_LOCATION_WRITE)

        create_completeness_dir(
            csv, result, "Recommended", "Missing", diffRecommended)
        create_completeness_dir(csv, result, "Recommended",
                                "Implemented", existRecommended)
        create_completeness_dir(
            csv, result, "Recommended", "Error", errorRecommended)

    # Optional
    click.secho("Marginality: Optional",
                file=config.OUTPUT_LOCATION_WRITE)
    if noOptional == 0:
        click.secho("    There are no optional property recommended by this profile.",
                    file=config.OUTPUT_LOCATION_WRITE)
        create_completeness_dir(
            csv, result, "Optional", "Missing", "")
        create_completeness_dir(csv, result, "Optional",
                                "Implemented", "")
        create_completeness_dir(
            csv, result, "Optional", "Error", "")
    else:
        if len(list(diffOptional)) != 0:
            click.secho("    Optional property that are missing: " + str(list(diffOptional)), fg="cyan",
                        file=config.OUTPUT_LOCATION_WRITE)
        else:
            click.secho("    The data has all the optional property(ies).",
                               file=config.OUTPUT_LOCATION_WRITE)

        if len(errorOptional) != 0:
            click.secho("    Optional property that has error: " +
                        str(list(errorOptional)), fg="cyan",
                        file=config.OUTPUT_LOCATION_WRITE)
        else:
            click.secho("    Implemented optional property has no error.",
                        file=config.OUTPUT_LOCATION_WRITE)


        create_completeness_dir(
            csv, result, "Optional", "Missing", diffOptional)
        create_completeness_dir(csv, result, "Optional",
                                "Implemented", existOptional)
        create_completeness_dir(
            csv, result, "Optional", "Error", errorOptional)


    # Extra properties not included in the Bioschemas profile
    if len(list(extraProp)) == 0:
        click.secho(file=config.OUTPUT_LOCATION_WRITE)
        click.secho("There is no property name in the metadata outside of the Bioschemas profile.",
                    file=config.OUTPUT_LOCATION_WRITE)
    if len(list(extraProp)) != 0:
        click.secho(file=config.OUTPUT_LOCATION_WRITE)
        click.secho("These properties names are in the metadata but not in the Bioschemas profile:"+
                    str(list(extraProp)), fg="cyan",
                    file=config.OUTPUT_LOCATION_WRITE)

    return result

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

# perform semantic check base on the relationship between property
def date_semantic_check(data):
   
    # print("test")
    with semanticPairDatePath.open() as f:
        semanticPairDate = f.readlines()
        f.close()

    # semanticPairDate = filePath.read_text().split("\n")

    for line in semanticPairDate:
        pair = line.split()
        start = pair[0]
        end = pair[1]

        if start in data.keys() and is_date(data.get(start)) is False:
                click.secho("In property \"" + start + "\", \""
                        + data.get(start)
                            + "\" has incorrect data format, months should be between 1 and 12, date should be between 1 and 31",
                            file=config.OUTPUT_LOCATION_WRITE)
                click.secho("------",
                            file=config.OUTPUT_LOCATION_WRITE)
        if end in data.keys() and is_date(data.get(end)) is False:
                click.secho("In property \"" + end + "\", \""
                        + data.get(end)
                            + "\" has incorrect data format, months should be between 1 and 12, date should be between 1 and 31",
                            file=config.OUTPUT_LOCATION_WRITE)
                click.secho("------",
                            file=config.OUTPUT_LOCATION_WRITE)
#                as the date format check is done with the json schemas and incorrect property are removed
#                there is no point to check formate again
        if start in data.keys() and end in data.keys() and is_date(data.get(start)) and is_date(data.get(end)):
                staS = parse(data.get(start))
                endS = parse(data.get(end))
#                    staS = datetime.datetime.strptime(data.get(start), '%Y-%m-%d')
#                    endS = datetime.datetime.strptime(data.get(end), '%Y-%m-%d')
                if staS > endS:
                    click.secho("\"" + start + "\" : " + "\"" + data.get(start) + "\" is after \"" + end
                                + "\" : " + "\"" +
                                data.get(start) + "\", please double check.",
                                file=config.OUTPUT_LOCATION_WRITE)
                    click.secho("------",
                                file=config.OUTPUT_LOCATION_WRITE)
    for key, value in data.items():
        if type(value) is dict:
            masterKeys = list()
            masterKeys.append(key)
            date_semantic_check_in_property(value, key, masterKeys)

# perform semantic check base on the relationship between property, inside other properties
def date_semantic_check_in_property(data, key, masterKeys):
    # filePath = "./src/Classes/semanticPairDate.txt"
    with semanticPairDatePath.open() as f:
        semanticPairDate = f.readlines()
        f.close()

    for line in semanticPairDate:
        pair = line.split()
        start = pair[0]
        end = pair[1]

#                as the date format check is done with the json schemas and incorrect property are removed
#                there is no point to check formate again
#                click.secho(data.get(start))
#                click.secho(data.get(end))
        if start in data.keys() and is_date(data.get(start)) is False:
            click.secho("Inside property "+ masterKeys + ",  \""
                    + data.get(start) + "\"" + " for property \""
                    + start
                        + "\" has incorrect data format, months should be between 1 and 12, date should be between 1 and 31",
                        file=config.OUTPUT_LOCATION_WRITE)
            click.secho("------",
                        file=config.OUTPUT_LOCATION_WRITE)
        if end in data.keys() and is_date(data.get(end)) is False:
            click.secho("Inside property " + masterKeys+", \""
                    + data.get(end)
                    + "\"" + " for property \"" + end
                        + "\" has incorrect data format, months should be between 1 and 12, date should be between 1 and 31",
                        file=config.OUTPUT_LOCATION_WRITE)
            click.secho("------",
                        file=config.OUTPUT_LOCATION_WRITE)
        if start in data.keys() and end in data.keys() and is_date(data.get(start)) and is_date(data.get(end)):
            staS = parse(data.get(start))
            endS = parse(data.get(end))
            if staS > endS:
                click.secho("Inside property"+ masterKeys+",""\"" + start + "\" : " + "\"" + data.get(start) + "\" is after \"" + end
                            + "\" : " + "\"" +
                            data.get(start) + "\", please double check.",
                            file=config.OUTPUT_LOCATION_WRITE)
    for key, value in data.items():
        if type(value) is dict:
#                 masterKey = ke
            masterKeys.append(key)
            date_semantic_check_in_property(value, key, masterKeys)

# loads the string from the file to a json object
def path_to_dict(path):
    path = pathlib.Path(path)
    orgString = path.read_text()
    newDict = json.loads(orgString,
                            object_pairs_hook=dict_raise_on_duplicates)
    return newDict, path

def str_to_dict(orgString):
    newDict = json.loads(orgString,
                            object_pairs_hook=dict_raise_on_duplicates)
#         click.secho(newDict)
    return newDict


# supply method used to reject duplicate keys
def dict_raise_on_duplicates(ordered_pairs):
    """Reject duplicate keys."""
    d = {}
    schemaOrg = False
    for k, v in ordered_pairs:
        if re.search(r"\s", k):
#             click.secho(k)
            click.secho("Please remove the whitespace(s) in property name " + k+
                        "the Validator will proceed without the whitespace(s)\n",
                        file=config.OUTPUT_LOCATION_WRITE)
            k = k.strip()
        if re.search("[^a-zA-Z@\$]", k) != None and "conformsTo" not in k:
#             click.secho(k)
            click.secho("Please be noted there are non alphabetic character in property name " + k +
                        "schema.org has no property name with non alphabetic character therefore the Bioschemas validator will not validate this property.",
                        file=config.OUTPUT_LOCATION_WRITE)
        if k in d:
            click.secho("duplicate property: " + k +
                        "the value for the last %r will be used" + k,
                        file=config.OUTPUT_LOCATION_WRITE)
        elif type(v) is dict:
            masterKeys = list()
            masterKeys.append(k)
            d[k] = dict_raise_on_duplicates_recursive(v, masterKeys)
        else:
            d[k] = v
    return d


def dict_raise_on_duplicates_recursive(ordered_pairs, masterKeys):
    """Reject duplicate keys."""
    d = {}
    # print(ordered_pairs)
    for k, v in ordered_pairs.items():

        if re.search(r"\s", k)!= None:
#             click.secho("Please remove the whitespace in property name %r," % (k,),
#                   "\n inside property" , masterKeys ,". The Validator will proceed without the whitespaces\n")
#             k = k.strip()
            click.secho(str(masterKeys),
                        file=config.OUTPUT_LOCATION_WRITE)
        if re.search("[^a-zA-Z@\$]", k) != None :
#             click.secho(k,v)
#             click.secho("Please be noted there are non alphabetic character in property name %r," % (k,),
#                   "\n inside property" ,masterKeys ,". Schema.org has no property name with non alphabetic character therefore the Bioschemas validator will not validate this property.")
            click.secho(str(masterKeys),
                        file=config.OUTPUT_LOCATION_WRITE)
        if k in d:
#             click.secho("duplicate property: %r," % (k,), "inside property", masterKeys,", the value for the last %r will be used"% (k,))
            click.secho(str(masterKeys),
                        file=config.OUTPUT_LOCATION_WRITE)
        elif type(v) is dict:
            masterKeys.append(k)
            d[k] = dict_raise_on_duplicates_recursive(v, masterKeys)
        else:
            d[k] = v
    return d

def hasNumbers(inputString):
     return bool(re.search(r'\d', inputString))

def sortby(x):
    try:
        if x.split(".")[0] == "0":
            x = x[x.index(".")+1:x.index("-")]
        else:
            x = x[:x.index(".")] + x[x.index("."):x.index("-")]
        return float(x)
    except ValueError:
        return float('inf')
