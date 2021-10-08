# from pathlib import Path
from tqdm import trange, tqdm
import sys
sys.path.append("./")
from src.Classes.staticJSONLDExtractor import extract
from src.Classes.formatToJSONLD import convertformattoJSONLD
from src.Classes.validator import validate
from src.Classes.buildAProfile import build_profile
from src.Classes.validator import path_to_dict
from src.Classes.sitemapExtractor import sitemapExtractor
from src.Classes.websiteExtractor import extractWebsite

import csv
import glob
import os
import pathlib

import click

import src.Classes.config as config
import pandas as pd
import rdflib
import time


@click.command()
@click.argument('action', type=click.Choice(['validate', 'buildprofile', 'tojsonld', 'sitemap']))
@click.option("--target_data",  default="",
              help="The yml that need to be build or data that needs to be validated, can be the path to a file containing the metadata, a file containing a list of paths or a path to a directory")
@click.option("--convert", is_flag=True,
              help="Convert the metadata from other format such as NQuads to JSON-LD")
@click.option("--csv", default="N", type=click.Choice(['N','num', 'name', 'all']),
              help="Save a simplified output to a csv file, if multiple metadata were validated, both the individual and summary will be saved")
@click.option("--profile", default="N", 
              help="Set specific profile to validated against, needs to be a path to the profile JSON schema")
@click.option("--static_jsonld", is_flag=True,
              help="A URL, A file with the URLs of the webpages or HTML files in local")
@click.option("--sitemap_convert", is_flag=True,
              help="Wether the data is a sitemap or a web domain, if raised the url will be extracted from the sitemap")



def choose(action, target_data, static_jsonld, csv, profile, convert, sitemap_convert):
    if action == 'buildprofile':
        click.echo('Action: %s' % action)
        if target_data == "":
            buildProfile('all')
        else:
            buildProfile(target_data)
    elif action == 'validate':
            click.echo('Action: %s' % action)
            if target_data == "":
                click.echo("Missing target_data parameter")
                exit()
            validateData(target_data, static_jsonld, csv,
                         profile, convert, sitemap_convert)

    elif action == 'tojsonld':
            click.echo('Action: %s' % action)
            if target_data == "":
                click.echo("Missing target_data parameter")
                exit()
            toJsonLD(target_data, action)

    elif action == "sitemap":
        click.echo('Action: %s' % action)

        sitemapExtract(target_data)
    
    

def sitemapExtract(target_data):
    if pathlib.Path(target_data).suffix == ".xml":
        return sitemapExtractor(target_data)
    else:
        return extractWebsite(target_data, "")


def buildProfile(profile_to_make):
    """ROUTE ONE 
        The first step for using this validation suite. 
        This will build the JSON schema for Bioschema profiles necessary for validation 

    Args:
        profile_to_make (string): A path to a file with the list of profile YML file that want to build instead of all the profile in config.YML_LOC
    """
#     the validating of the schemas is done as part of build_profile method
    if profile_to_make != 'all':
        path = pathlib.Path(profile_to_make)
        if path.suffix == ".html":
            click.echo(path, file=config.OUTPUT_LOCATION_WRITE)
            code = build_profile(path)
            click.echo("---------------------------------",
                       file=config.OUTPUT_LOCATION_WRITE)
            return code
        elif path.suffix == ".txt":
            with path.open() as f:
                profileList = f.readlines()
            # if len(profileList) == 0:
            #     click.secho(
            #         "There is no file to be converted in " + config.YML_LOC, fg='yellow', file=config.OUTPUT_LOCATION_WRITE)
            start_time = time.time()
            totalProfileNum = len(profileList)
            i = 0
            for line in profileList:
                i = i + 1
                click.echo(line, file=config.OUTPUT_LOCATION_WRITE)
                build_profile(pathlib.Path(line.rstrip()))
                elapsed_time = time.time() - start_time

                click.echo(tqdm.format_meter(i, totalProfileNum, elapsed_time))
                sys.stdout.flush()
                click.echo("---------------------------------",
                           file=config.OUTPUT_LOCATION_WRITE)
                continue

    else:
        path = pathlib.Path(config.YML_LOC)
        totalProfileNum = len(list(path.rglob('*.html')))
        i = 0
        start_time = time.time()
        for line in path.glob('**/*.html'):
            i = i + 1
            click.echo(line,  file=config.OUTPUT_LOCATION_WRITE)
            build_profile(line)
            elapsed_time = time.time() - start_time
            click.echo(tqdm.format_meter(i, totalProfileNum, elapsed_time))
            click.echo("---------------------------------",
                       file=config.OUTPUT_LOCATION_WRITE)

    return 0


def validateData(target_data, static_jsonld=False, csv="N", profile="N", convert=False, sitemap_convert=False):
    """Validate metadata using the information taken from the target_data path

    Args:
        target_data (string): The location of the metadata that needs to be validated
        static_jsonld (boolean): True if the metadata need to be extracted from live or local html
        csv (string): if only the marginality report is needed, it will include only number, properties names or both
        profile (string): A path to the profile JSON schema the validation will use(instead of default profile base on the metadata type)
        convert (boolean): True is the metadata is in a RDF type not JSONLD
        sitemap_convert(boolean): True if the url of the metadata need to be extrated from the sitemap or a webdomain
    """
    try:
        fileDir = False
        profileSpecific = False
        dataList = list()
        csvNeeded = False
        # returnCode = 0
        if csv != "N":
            csvNeeded = True
        if profile != "N":
            profileSpecific = True
            # returnCode+= 3*100
        if convert:
            target_data = pathlib.Path(target_data)
            target_data = toJsonLD(target_data, action="validate")
            if target_data == -1:
                return -1

        if static_jsonld or sitemap_convert:
            if sitemap_convert:
                # the target data will now be a path to a file with a list of urls that then needs to be extracted
                target_data = sitemapExtract(target_data)
            # depends on the target data, it could be a dir(if a dir was created), or a list(if the dir exist already)
            newCommandFileName = extract(target_data)
            if type(newCommandFileName) is list:
                target_data = pathlib.Path(target_data)
            target_data = newCommandFileName

            if target_data == "":
                click.echo("No data to be validated.",
                           file=config.OUTPUT_LOCATION_WRITE)
                return -1
            
        if profileSpecific:
            schema, schemaPath = path_to_dict(pathlib.Path(profile))

        

        if type(target_data) is not list:
            if os.path.isdir(target_data):
                fileDir = True
                dataList = pathlib.Path(target_data).glob("*"+config.METADATA_EXT)
                # returnCode += 3*10
            elif os.path.isfile(target_data):
                click.echo(target_data + " is a file",
                           file=config.OUTPUT_LOCATION_WRITE)
                f = pathlib.Path(target_data).open()
                dataList = f.readlines()
                # returnCode += 1*10
                # If the target metadata is the path to the metadata itself
                if "{" in dataList[0] or pathlib.Path(target_data).suffix == config.METADATA_EXT:
    
                    click.echo("The target metadata is " +
                               str(target_data), file=config.OUTPUT_LOCATION_WRITE)
                    data, dataPath = path_to_dict(pathlib.Path(target_data))
                    if csvNeeded:
                        blockPrint()
                    click.echo("###########Start Validation#############",
                               file=config.OUTPUT_LOCATION_WRITE)
                    if profileSpecific:
                        click.echo("Validating againest ", schemaPath,
                                   file=config.OUTPUT_LOCATION_WRITE)

                        result = validate(data, csv, schema, schemaPath)
                    else:
                        result = validate(data, csv)

                    if csvNeeded:
                        enablePrint()
                        csvWriter(result, target_data)
                    click.echo("###########End Validation#############\n",
                               file=config.OUTPUT_LOCATION_WRITE)
                    return 
                    # end of output if a single file is being validated

                click.echo(target_data, file=config.OUTPUT_LOCATION_WRITE)


            else:
                dataList.append(target_data)



        elif type(target_data) is list:
            click.echo(target_data[0], file=config.OUTPUT_LOCATION_WRITE)
            dataList = target_data
        else:
            click.echo("The path is not a directory or a file.",
                       file=config.OUTPUT_LOCATION_WRITE)
            return -1
    

        dataName = ""

        for line in dataList:
            if type(line) is not str:
                line = str(line)
            click.echo("Validating: " + line, file=config.OUTPUT_LOCATION_WRITE)
            if type(line) is str and len(line.split(" "))>1:
                containProfile = True
                schemaName = line.split(" ")[0]
                dataName = line.split(" ")[1].strip()
            else:
                dataName = line
                containProfile = False
            if type(dataName) is str:
                dataName = pathlib.Path(dataName.rstrip())

            click.echo("###########Start Validation#############",
                       file=config.OUTPUT_LOCATION_WRITE)
            if csvNeeded:
                blockPrint()

            if fileDir is False and containProfile is True:
                click.echo(schemaName, dataName,
                           file=config.OUTPUT_LOCATION_WRITE)
                data, dataPath = path_to_dict(dataName)
                if profileSpecific:
                    click.echo("Validating againest " + str(schemaPath), file = config.OUTPUT_LOCATION_WRITE)

                    result = validate(data, csv, schema, schemaPath)
                else:
                    schema , schemaPath = path_to_dict(schemaName)

    #             click.echo(schemaName)
                    result = validate(data,csv, schema, schemaPath)
            elif containProfile is False:
    #             dataName = line.strip()
    #             if type(dataName) is str:
    #                 dataName = pathlib.Path(dataName)
                data, dataPath = path_to_dict(dataName)
                if profileSpecific:
                    click.echo("Validating againest " + str(schemaPath),
                               file=config.OUTPUT_LOCATION_WRITE)
                    result = validate(data, csv, schema, schemaPath)
                else:
                    result = validate(data, csv)
            if csvNeeded:
                enablePrint()
                # new = pd.DataFrame.from_dict(result)
                csvWriter(result, dataName)
            click.echo("###########End Validation#############\n",
                       file=config.OUTPUT_LOCATION_WRITE)
        if csvNeeded:
            csvBulkWriter(dataName)
        if type(target_data) is not list and os.path.isfile(target_data):
                f.close()
        return 0 # returnCode
    except KeyboardInterrupt:
        click.secho("Program stopped", fg="red",
                    file=config.OUTPUT_LOCATION_WRITE)
        return -1
    except FileNotFoundError:
        click.secho("Missing file error, please double check", fg="red",
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

        click.secho("Error:" + errorMessage, fg="red",
                    file=config.OUTPUT_LOCATION_WRITE)
        return -1

def toJsonLD(target_data, action):
    """Convert the file from RDF serialization to JSON-LD

    Args:
        target_data (Path to file or dir): file(s) that need to be converted
    Returns:
        list: A list of the result JSONLD file
    """
    if type(target_data) is str:
        target_data = pathlib.Path(target_data)
    if target_data.is_dir():
        nqFiles = target_data.iterdir()
        resultDictPathList = list()
        # file is a Path not a str
        for file in nqFiles:
            if file.suffix == ".jsonld":
                click.echo(str(file) + " is a JSONLD file already.",
                           file=config.OUTPUT_LOCATION_WRITE)
                continue
            click.echo("Converting "+str(file)+" to JSON-LD...",
                       file=config.OUTPUT_LOCATION_WRITE)
            # filePath = target_data / file
            # filePath = file
            # guess RDF serialization based on file suffix
            dataFormat = rdflib.util.guess_format(str(file))
            if dataFormat == None:
                click.echo("The format of this file can not be determined as it is not an RDF type.",
                           file=config.OUTPUT_LOCATION_WRITE)
                continue
            # if dataFormat == ""
            # click.echo("Original format: " + dataFormat)
            resultDictList = convertformattoJSONLD(
                file, dataFormat)
            # click.echo("resultFiles" + str(type(resultDictList)))
            # for resultFile in resultDictList:
            #     resultFile.rename(resultDir.joinpath(resultFile.name))
            # resultDictList = open(resultFile, "r").readlines()
            # click.echo(str(file) + " converted and saved in " +
                #   str(resultDictList))
            for resultFile in resultDictList:
                resultDictPathList.append(resultFile)
        if action == "validate":
            return resultDictPathList
        else:
            return 0
    elif target_data.is_file():
        if target_data.suffix == ".jsonld":
            click.echo("This is a JSONLD file already.",
                       file=config.OUTPUT_LOCATION_WRITE)
            return [target_data]
        file = str(target_data)
        click.echo("Converting " + file + " to JSON-LD...",
                   file=config.OUTPUT_LOCATION_WRITE)
        dataFormat = rdflib.util.guess_format(file)
        if dataFormat == None:
            click.echo("The format of this file can not be determined as it is not an RDF type.",
                       file=config.OUTPUT_LOCATION_WRITE)
            exit()
        resultDictList = convertformattoJSONLD(
            file, dataFormat)
        # click.echo(file + " converted and saved in " + str(resultDictList))
        if action == "validate":
            return resultDictList
        else:
            return 0

    else:
        click.echo("There is an error with the file metadata file path, please double check")
        return -1


def blockPrint():
    """Stops the output displaying on the terminal
    """
    global nullOutput
    nullOutput = open(os.devnull, 'w')
    sys.stdout = nullOutput

# Restore


def enablePrint():
    """Lets the output displaying on the terminal
    """
    global nullOutput
    nullOutput.close()
    sys.stdout = sys.__stdout__

def csvWriter(resultdict, name):
    """Takes the resultdict which is the validation result on validation and save it to a csv file.

    Args:
        resultdict (dict): A dict of the validation result with keys as "Minium", "Recommendation" and "Optional"
        name (string): The name of the file that the validation report is for
    """
    if resultdict == 0 or None:
        click.echo("This profile has no list of properties and marginality. No csv is made",
                   file=config.OUTPUT_LOCATION_WRITE)

        return 0
    elif resultdict != None:
        # click.echo(resultdict)

        resultdict["File Name"] = name
        for keyName in resultdict.keys():
            if keyName == "Minimum" or keyName == "Recommended" or keyName == "Optional":
                newString = ""
                for k, v in resultdict[keyName].items():
                    newString = newString + "\n" + k + ": " + str(v)
                resultdict[keyName] = newString.strip()

        # click.echo(resultdict)

        if type(name) is str:
            name = pathlib.Path(name)
        name = str(name.parent.joinpath(name.stem))

        with open(name + ".csv", "w") as csvfile:
            fieldnames = ["File Name", "Profile Name", "Profile Version",
                "Valid", "Minimum", "Recommended", "Optional"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([resultdict])
            click.echo("CSV file location: " + name + ".csv",
                       file=config.OUTPUT_LOCATION_WRITE)

        return 1


def csvBulkWriter(name):
    """Merge the csv in the same directory into one for easy viewing

    Args:
        name ([Path]): a PATH to directory
    """
    if type(name) is str:
        name = pathlib.Path(name)
    click.echo(name,
               file=config.OUTPUT_LOCATION_WRITE)
    path = name.parent
    all_files = glob.glob(str(path.joinpath("*.csv")))
    if len(all_files) == 0:
        click.echo("There is no csv file available in path "+str(path)+".",
                   file=config.OUTPUT_LOCATION_WRITE)
        return
    df_from_each_file = (pd.read_csv(f, sep=',') for f in all_files)
    df_merged = pd.concat(df_from_each_file, ignore_index=True)
    resultPath = path.joinpath("mergedResult.csv")
    if resultPath.exists():
        click.echo(str(resultPath) + "exist already", file=config.OUTPUT_LOCATION_WRITE)
        resultPath.unlink()
        if resultPath.exists() is False:
            click.echo("It has been deleted",
                       file=config.OUTPUT_LOCATION_WRITE)
    # path.joinpath("mergedResult.csv").unlink(missing_ok=True)

    df_merged.to_csv(str(resultPath))
    click.echo("Merged CSV file location: " + str(resultPath),
               file=config.OUTPUT_LOCATION_WRITE)

if __name__ == '__main__':
    choose()
