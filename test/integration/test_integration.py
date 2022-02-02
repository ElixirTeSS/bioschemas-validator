import src.command as command
from src.Classes.staticJSONLDExtractor import extract
import test.integration.config as config

import unittest
import pathlib
import os
import json
import sys


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


def testValidation(action, target_data="", static_jsonld=False, csv=False, profile="N", convert=False, sitemap_convert=False):
    blockPrint()
    if action == 'buildprofile':
        return command.buildProfile(target_data)

    elif action == 'validate':
        return command.validateData(target_data, static_jsonld, csv, profile, convert, sitemap_convert)

    elif action == 'tojsonld':
        return command.toJsonLD(target_data, action)
    elif action == "sitemap":
        return command.sitemapExtract(target_data)


def expectedCode(target_data="", static_jsonld=False, csv=False, profile="N", convert=False):
    code = 0
    if profile != "N":
        code += 3*100
    if convert:
        code += 2*100
    if static_jsonld:
        code += 1*100
        if type(extract(str(target_data))) is dir:
            code += 3*10
    if csv:
        code += 1
        
    target_data = pathlib.Path(target_data)

    if target_data.is_file():
        # print(type(target_data))
        # if it's metadata
        if target_data.suffix == testConfig.METADATA_EXT:
            code += 1*10
        # if it's txt file, which would be a list of path
        elif target_data.suffix == ".txt":
            code += 2*10
    elif target_data.is_dir():
        code += 3*10

    # print("expectedCode" , code)

    return 0
    
def cleanup(path="testOutput"):
    # print(path)
    # print("*************************************************")
    if type(path) == str:
        path = pathlib.Path(path)
    if path.exists():
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            cleanupDir(path)


def cleanupDir(path):
    for child in path.iterdir():
        if child.is_file():
            child.unlink()
        elif child.is_dir():
            cleanupDir(child)
    path.rmdir()
    return

# move into directory before testing
# remove testing result unless error occur
def cleanupProfileMade(path):
    initialPath = pathlib.Path(path)
    parentNo = len(initialPath.parents)
    rootDir = initialPath.parents[parentNo-2]
    subPath = str(initialPath.parent).lstrip(str(rootDir) + "/")
    
    resultJSON = testConfig.PROFILE_LOC / \
        pathlib.Path(subPath) 

    resultMarg = testConfig.PROFILE_MARG_LOC / \
        pathlib.Path(subPath)

    cleanupDir(resultJSON)
    cleanupDir(resultMarg)

class TestIntegration(unittest.TestCase):
    """Testing how the validator behave for different validation command the file type
        The code is hand calculated and using src/command_returns.txt
    """


    def testCLIBuildProfileMultiple(self):
        action = "buildprofile"
        target = "test/profile_lib/demo_profile.txt"
        code = testValidation(action, target_data=target)
        expected = 0
        enablePrint()
        self.assertEqual(code, expected)
        cleanupProfileMade(target)

    # @unittest.skip
    def testCLIBuildProfileCorrect(self):
        action = "buildprofile"
        target = "test/profile_lib/correct_format_profile_yml.html"
        code = testValidation(action, target_data=target)
        expected = 0
        enablePrint()
        self.assertEqual(code, expected)
        cleanupProfileMade(target)

    # @unittest.skip
    def testCLIBuildProfileMarginalityCorrect(self):
        action = "buildprofile"
        target = "test/profile_lib/correct_format_profile_yml.html"
        code = testValidation(action, target_data=target)
        expected = 0
        resultMargLoc = testConfig.PROFILE_MARG_LOC + \
            "/profile_lib/correct_format_profile_yml" + testConfig.PROFILE_MARG_EXT
        resultSchemaLoc = testConfig.PROFILE_LOC + \
            "/profile_lib/correct_format_profile_yml" + testConfig.PROFILE_EXT
        resultMarg = json.loads(pathlib.Path(resultMargLoc).read_text())
        resultSchema = json.loads(pathlib.Path(resultSchemaLoc).read_text())
        enablePrint()
        self.assertEqual(code, expected)
        self.assertEqual(len(resultMarg.keys()), 3)
        self.assertEqual(sum(map(len, resultMarg.values())),
                         len(resultSchema["properties"].keys()))

        cleanupProfileMade(target)

    # @unittest.skip
    def testCLIBuildProfileError(self):
        action = "buildprofile"
        target = "test/profile_lib/wrong_format_profile_yml.html"
        code = testValidation(action, target_data=target)
        expected = -1
        enablePrint()
        self.assertEqual(code, expected)


    # @unittest.skip
    def testCLILiveDataOnePageJSONLDToBeExtracted(self):
        # pathlib.Path(testConfig.METADATA_LOC).mkdir()
        action = "validate"
        target = "https://workflowhub.eu/workflows/137"
        staticJsonld = True
        code = testValidation(action, target_data=target, static_jsonld=staticJsonld)
        expected = expectedCode(target_data=target, static_jsonld=staticJsonld)
        enablePrint()
        # print("expected:", expected)
        self.assertEqual(code, expected)

    # @unittest.skip
    def testCLILiveDataMultiPageJSONLDToBeExtracted(self):
        action = "validate"
        target = pathlib.Path("test/metadata_lib/static_jsonld_url_1to1.txt")
        staticJsonld = True
        code = testValidation(action, target_data=str(
            target), static_jsonld=staticJsonld)
        expected = expectedCode(target_data=target, static_jsonld=staticJsonld)
        enablePrint()
        self.assertEqual(code, expected)
        


    # @unittest.skip
    def testCLILiveDataMultiPageMultiJSONLDToBeExtracted(self):
        action = "validate"
        target = pathlib.Path("test/metadata_lib/static_jsonld_url_1toN.txt")
        staticJsonld = True
        code = testValidation(action, target_data=str(
            target), static_jsonld=staticJsonld)
        expected = expectedCode(target_data=target, static_jsonld=staticJsonld)

        enablePrint()
        self.assertEqual(code, expected)

    # @unittest.skip
    def testCLINQfileToConvert(self):
        action = "tojsonld"
        target = pathlib.Path("test/metadata_lib/format_NQuads/3.nq")
        code = testValidation(action, target_data=str(
            target))
        expected = 0
        enablePrint()
        self.assertEqual(code, expected)


    # @unittest.skip
    def testCLINQDirToConvert(self):
        action = "tojsonld"
        target = pathlib.Path("test/metadata_lib/format_NQuads")
        code = testValidation(action, target_data=str(
            target))
        expected = 0
        enablePrint()
        self.assertEqual(code, expected)

    # @unittest.skip
    def testCLINQfileToConvertValidate(self):
        action = "validate"
        target = pathlib.Path("test/metadata_lib/format_NQuads/3.nq")
        convert = True
        code = testValidation(action, target_data=str(
            target), convert=convert)
        expected = expectedCode(target_data=target, convert=convert)

        enablePrint()
        self.assertEqual(code, expected)


    # @unittest.skip
    def testCLINQDirToConvertValidate(self):
        action = "validate"
        target = pathlib.Path("test/metadata_lib/format_NQuads")
        convert = True
        code = testValidation(action, target_data=str(
            target), convert=convert)
        expected = expectedCode(target_data=target, convert=convert)

        enablePrint()
        self.assertEqual(code, expected)

    # @unittest.skip
    def testCLILiveDataOnePageJSONLDToBeExtractedCSV(self):
        action = "validate"
        target = "https://workflowhub.eu/workflows/137"
        staticJsonld = True
        csv = True
        code = testValidation(action, target_data=target, static_jsonld=staticJsonld,csv=csv)
        expected = expectedCode(target_data=target, static_jsonld=staticJsonld, csv=csv) #101
        enablePrint()
        self.assertEqual(code, expected)

    # @unittest.skip
    def testCLIMetadataWithProfile(self):
        action = "validate"
        target = "test/metadata_lib/dataset_metadata"
        profileLoc = "profile_json/Dataset/0.3-RELEASE-2019_06_14.json"
        code = testValidation(action, target_data=target, profile=profileLoc)
        expected = expectedCode(
            target_data=target, profile=profileLoc)
        enablePrint()
        self.assertEqual(code, expected)

    def testCLISitemapExtractor(self):
        action = "sitemap"
        target = "test/sitemap/sitemap_index_shorten.xml"
        result = testValidation(action, target_data=target)
        # click.echo("result" + str(result))

        cleanup(result)


    def testCLIWebsiteExtractor(self):
        blockPrint()
        action = "sitemap"
        target="https://disprot.org/"
        result = testValidation(action, target_data=target)
        enablePrint()
        # click.echo("result" + str(result))
        cleanup(result)

    # @unittest.skip

    def testCleanUpLiveData(self):
        cleanup(testConfig.METADATA_LOC)
        cleanup("test/metadata_lib/format_NQuads_jsonld")


if __name__ == '__main__':
    unittest.main()
