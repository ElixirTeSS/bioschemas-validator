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
from tqdm import tqdm
import click

import src.Classes.config as config
import src.log as log
from src.result import Result

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
    log.stdout(f'Action: {action}')

    # --------------------------------------------------------------------------
    # Check data has been specified

    if target_data == "":
        log.stdout("Missing target_data parameter")
        exit()

    # --------------------------------------------------------------------------
    # Perform action

    if action == 'buildprofile':
        if target_data == "":
            buildProfile('all')
        else:
            buildProfile(target_data)
    elif action == 'validate':
        validateData(target_data, static_jsonld, csv,
                     profile, convert, sitemap_convert)
    elif action == 'tojsonld':
        toJsonLD(target_data, action)
    elif action == "sitemap":
        sitemapExtract(target_data)
    else:
        log.error("No action chosen!")

    # --------------------------------------------------------------------------
    # Exit

    return 0


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
            log.info(path)
            code = build_profile(path)
            log.info("---------------------------------")
            return code
        elif path.suffix == ".txt":
            with path.open() as f:
                profileList = f.readlines()

            start_time = time.time()
            totalProfileNum = len(profileList)

            for ii, line in enumerate(profileList):
                build_profile(pathlib.Path(line.rstrip()))

                log.info(line)
                elapsed_time = time.time() - start_time
                log.stdout(tqdm.format_meter(ii, totalProfileNum, elapsed_time))
                log.info("---------------------------------")
                continue
    else:
        path = pathlib.Path(config.YML_LOC)
        totalProfileNum = len(list(path.rglob('*.html')))
        
        start_time = time.time()
        for ii, line in enumerate(path.glob('**/*.html')):
            build_profile(line)

            log.info(line)
            elapsed_time = time.time() - start_time
            log.stdout(tqdm.format_meter(ii, totalProfileNum, elapsed_time))
            log.info("---------------------------------")

    return 0


def validateData(target_data,
                 static_jsonld=False,
                 csvNeeded=False,
                 profile=None,
                 convert=False,
                 sitemap_convert=False):
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
        dataList = list()

        # ----------------------------------------------------------------------
        # Perform JSON_LD conversion, if requested

        if convert:
            target_data_path = pathlib.Path(target_data)
            target_data = toJsonLD(target_data_path, action="validate")
            if target_data == -1:
                return Result(code=-1, result='No target data found')

        # ----------------------------------------------------------------------
        # Perform sitemap conversion, if requested

        if sitemap_convert:
            # the target data will now be a path to a file with a list of urls that then needs to be extracted
            target_data = sitemapExtract(target_data)

        # ----------------------------------------------------------------------
        # If either conversion was requested, extract the validation data

        if static_jsonld or sitemap_convert:
            # depends on the target data, it could be a dir(if a dir was created), or a list(if the dir exist already)
            target_data = extract(target_data)

            if target_data == "":
                log.info("No data to be validated.")
                return Result(code=-1, result='No data to be validated')
            
        # ----------------------------------------------------------------------
        # Form target data list

        if type(target_data) is list:
            log.info(target_data[0])
            dataList = target_data
        elif os.path.isdir(target_data):
            dataList = pathlib.Path(target_data).glob("*"+config.METADATA_EXT)
        elif os.path.isfile(target_data):
            log.info(target_data + " is a file")
            with pathlib.Path(target_data).open() as f:
                dataList = f.readlines()
                if not targetIsMetadataPath:
                    dataList.append(target_data)
                log.info(target_data)
        else:
            log.info("The path is not a directory or a file.")
            return Result(code=-1, result='The path is not a directory or a file.')

        # ----------------------------------------------------------------------
        # Process target data list

        result = None
        dataName = ""
        for line in dataList:
            log.info(f"Validating: {line}")

            if type(line) is not str:
                line = str(line)

            # ------------------------------------------------------------------
            # Parse line to find if it specifies a profile

            if len(line.split(" ")) > 1:
                containProfile = True
                profile = line.split(" ")[0]
                dataName = line.split(" ")[1].strip()
            else:
                containProfile = False
                dataName = line

            if type(dataName) is str:
                dataName = pathlib.Path(dataName.rstrip())

            # ------------------------------------------------------------------
            # Begin validating

            log.info("####n#######Start Validation#############")
            log.info(f"{profile} {dataName}")
        
            if (targetIsMetadataPath(line, dataName) or
                ((containProfile and not os.path.isdir(target_data)) or (not containProfile))
                ):
                data, dataPath = path_to_dict(pathlib.Path(dataName))
                result = validate(data, profile)
            else:
                log.error("Invalid data type, validation aborted")
                return Result(code=-1, result='Invalid data type, validation aborted')

            if csvNeeded:
                # new = pd.DataFrame.from_dict(result)
                csvWriter(result, dataName)

            log.info("###########End Validation#############\n")
        if csvNeeded:
            csvBulkWriter(dataName)

        return Result(code=0, result=result)
    except KeyboardInterrupt:
        click.secho("Program stopped", fg="red", file=config.OUTPUT_LOCATION_WRITE)
        return Result(code=-1, result="Program stopped")
    except FileNotFoundError as errorMessage:
        click.secho("Missing file error, please double check", fg="red", file=config.OUTPUT_LOCATION_WRITE)
        click.secho(f"Error: {errorMessage}", fg="red", file=config.OUTPUT_LOCATION_WRITE)
        return Result(code=-1, result=errorMessage)
    except Exception as errorMessage:
        click.secho(f"Error: {errorMessage}", fg="red", file=config.OUTPUT_LOCATION_WRITE)
        return Result(code=-1, result=errorMessage)


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
        for input_file in nqFiles:
            if input_file.suffix == ".jsonld":
                log.info(f"{input_file} is a JSONLD file already.")
                continue
            log.info(f"Converting {input_file} to JSON-LD...")

            # guess RDF serialization based on file suffix
            dataFormat = rdflib.util.guess_format(str(input_file))
            if dataFormat is None:
                log.info("The format of this file can not be determined as it is not an RDF type.")
                continue

            resultDictList = convertformattoJSONLD(input_file, dataFormat)
            for resultFile in resultDictList:
                resultDictPathList.append(resultFile)
        if action == "validate":
            return resultDictPathList
        else:
            return 0
    elif target_data.is_file():
        if target_data.suffix == ".jsonld":
            log.info("This is a JSONLD file already.")
            return [target_data]
        target_file = str(target_data)
        log.info(f"Converting {target_file} to JSON-LD...")
        dataFormat = rdflib.util.guess_format(target_file)
        if dataFormat is None:
            log.info("The format of this file can not be determined as it is not an RDF type.")
            exit()
        resultDictList = convertformattoJSONLD(target_file, dataFormat)
        if action == "validate":
            return resultDictList
        else:
            return 0

    else:
        log.error("There is an error with the file metadata file path, please double check")
        return -1

def csvWriter(resultdict, name):
    """Takes the resultdict which is the validation result on validation and save it to a csv file.

    Args:
        resultdict (dict): A dict of the validation result with keys as "Minium", "Recommendation" and "Optional"
        name (string): The name of the file that the validation report is for
    """
    if resultdict == 0 or None:
        log.info("This profile has no list of properties and marginality. No csv is made")
        return 0
    elif resultdict is not None:
        resultdict["File Name"] = name
        for keyName in resultdict.keys():
            if keyName == "Minimum" or keyName == "Recommended" or keyName == "Optional":
                newString = ""
                for k, v in resultdict[keyName].items():
                    newString = newString + "\n" + k + ": " + str(v)
                resultdict[keyName] = newString.strip()

        if type(name) is str:
            name = pathlib.Path(name)
        name = str(name.parent.joinpath(name.stem))

        with open(name + ".csv", "w") as csvfile:
            fieldnames = ["File Name", "Profile Name", "Profile Version",
                "Valid", "Minimum", "Recommended", "Optional"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([resultdict])
            log.info(f"CSV file location: {name}.csv")

        return 1


def csvBulkWriter(name):
    """Merge the csv in the same directory into one for easy viewing

    Args:
        name ([Path]): a PATH to directory
    """
    if type(name) is str:
        name = pathlib.Path(name)
    log.info(name)
    path = name.parent
    all_files = glob.glob(str(path.joinpath("*.csv")))
    if len(all_files) == 0:
        log.info(f"There is no csv file available in path {path}.")
        return
    df_from_each_file = (pd.read_csv(f, sep=',') for f in all_files)
    df_merged = pd.concat(df_from_each_file, ignore_index=True)
    resultPath = path.joinpath("mergedResult.csv")
    if resultPath.exists():
        log.info(f"{resultPath} exist already")
        resultPath.unlink()
        if resultPath.exists() is False:
            log.info("It has been deleted")

    df_merged.to_csv(str(resultPath))
    log.info(f"Merged CSV file location: {resultPath}")

    
def targetIsMetadataPath(line, dataName):
    # If the target metadata is the path to the metadata itself
    return (("{" in line[0]) or (dataName.suffix == config.METADATA_EXT))


if __name__ == '__main__':
    choose()
