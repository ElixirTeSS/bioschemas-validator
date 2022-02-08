import src.command as command
from src.Classes.staticJSONLDExtractor import extract
import test.integration.config as config

import unittest
import pathlib
import os
import json
import shutil

def testValidation(action="", target_data="", static_jsonld=False, csvNeeded=False, profile=None, convert=False, sitemap_convert=False):
    if action == 'buildprofile':
        return command.buildProfile(target_data)
    elif action == 'validate':
        return command.validateData(target_data, static_jsonld, csvNeeded, profile, convert, sitemap_convert)
    elif action == 'tojsonld':
        return command.toJsonLD(target_data, action)
    elif action == "sitemap":
        return command.sitemapExtract(target_data)


def expectedCode(target_data="", static_jsonld=False, csvNeeded=False, profile=None, convert=False):
    code = 0
    if profile != None:
        code += 3*100
    if convert:
        code += 2*100
    if static_jsonld:
        code += 1*100
        if type(extract(str(target_data))) is dir:
            code += 3*10
    if csvNeeded:
        code += 1
        
    target_data = pathlib.Path(target_data)

    if target_data.is_file():
        # print(type(target_data))
        # if it's metadata
        if target_data.suffix == config.METADATA_EXT:
            code += 1*10
        # if it's txt file, which would be a list of path
        elif target_data.suffix == ".txt":
            code += 2*10
    elif target_data.is_dir():
        code += 3*10

    # print("expectedCode" , code)

    return 0


def cleanup(path):
    """ param <path> could either be relative or absolute. """

    # https://stackoverflow.com/questions/6996603/how-to-delete-a-file-or-folder-in-python
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


class TestIntegration(unittest.TestCase):
    """
    Testing how the validator behave for different validation command file type
    The code is hand calculated and using src/command_returns.txt
    """

    def testCLIBuildProfileMultiple(self):
        action = "buildprofile"
        target = "test/fixtures/profile_lib/demo_profile.txt"
        code = testValidation(action, target_data=target)
        expected = 0
        self.assertEqual(code, expected)

    def testCLIBuildProfileCorrect(self):
        action = "buildprofile"
        target = "test/fixtures/profile_lib/correct_format_profile_yml.html"
        code = testValidation(action, target_data=target)
        expected = 0
        self.assertEqual(code, expected)

    def testCLIBuildProfileMarginalityCorrect(self):
        action = "buildprofile"
        target = "test/fixtures/profile_lib/correct_format_profile_yml.html"
        code = testValidation(action, target_data=target)
        expected = 0
        resultMargLoc = config.PROFILE_MARG_LOC + \
            "/fixtures/correct_format_profile_yml" + config.PROFILE_MARG_EXT
        resultSchemaLoc = config.PROFILE_LOC + \
            "/fixtures/correct_format_profile_yml" + config.PROFILE_EXT
        resultMarg = json.loads(pathlib.Path(resultMargLoc).read_text())
        resultSchema = json.loads(pathlib.Path(resultSchemaLoc).read_text())
        self.assertEqual(code, expected)
        self.assertEqual(len(resultMarg.keys()), 3)
        self.assertEqual(sum(map(len, resultMarg.values())),
                         len(resultSchema["properties"].keys()))

    def testCLIBuildProfileError(self):
        action = "buildprofile"
        target = "test/fixtures/profile_lib/wrong_format_profile_yml.html"
        code = testValidation(action, target_data=target)
        expected = -1
        self.assertEqual(code, expected)

    def testCLILiveDataOnePageJSONLDToBeExtracted(self):
        # pathlib.Path(config.METADATA_LOC).mkdir()
        action = "validate"
        target = "https://workflowhub.eu/workflows/137"
        staticJsonld = True
        code = testValidation(action, target_data=target, static_jsonld=staticJsonld)
        expected = expectedCode(target_data=target, static_jsonld=staticJsonld)
        # print("expected:", expected)
        self.assertEqual(code, expected)

    def testCLILiveDataMultiPageJSONLDToBeExtracted(self):
        action = "validate"
        target = pathlib.Path("test/fixtures/metadata_lib/static_jsonld_url_1to1.txt")
        staticJsonld = True
        code = testValidation(action, target_data=str(
            target), static_jsonld=staticJsonld)
        expected = expectedCode(target_data=target, static_jsonld=staticJsonld)
        self.assertEqual(code, expected)
        
    def testCLILiveDataMultiPageMultiJSONLDToBeExtracted(self):
        action = "validate"
        target = pathlib.Path("test/fixtures/metadata_lib/static_jsonld_url_1toN.txt")
        staticJsonld = True
        code = testValidation(action, target_data=str(
            target), static_jsonld=staticJsonld)
        expected = expectedCode(target_data=target, static_jsonld=staticJsonld)

        self.assertEqual(code, expected)

    def testCLINQfileToConvert(self):
        action = "tojsonld"
        target = pathlib.Path("test/fixtures/metadata_lib/format_NQuads/3.nq")
        code = testValidation(action, target_data=str(target))
        expected = 0
        self.assertEqual(code, expected)

    def testCLINQDirToConvert(self):
        action = "tojsonld"
        target = pathlib.Path("test/fixtures/metadata_lib/format_NQuads")
        code = testValidation(action, target_data=str(target))
        expected = 0
        self.assertEqual(code, expected)

    def testCLINQfileToConvertValidate(self):
        action = "validate"
        target = pathlib.Path("test/fixtures/metadata_lib/format_NQuads/3.nq")
        convert = True
        code = testValidation(action, target_data=str(target), convert=convert)
        expected = expectedCode(target_data=target, convert=convert)

        self.assertEqual(code, expected)

    def testCLINQDirToConvertValidate(self):
        action = "validate"
        target = pathlib.Path("test/fixtures/metadata_lib/format_NQuads")
        convert = True
        code = testValidation(action, target_data=str(
            target), convert=convert)
        expected = expectedCode(target_data=target, convert=convert)

        self.assertEqual(code, expected)

    def testCLILiveDataOnePageJSONLDToBeExtractedCSV(self):
        action = "validate"
        target = "https://workflowhub.eu/workflows/137"
        staticJsonld = True
        csv = True
        code = testValidation(action, target_data=target, static_jsonld=staticJsonld, csvNeeded=csv)
        expected = expectedCode(target_data=target, static_jsonld=staticJsonld, csvNeeded=csv) #101
        self.assertEqual(code, expected)

    def testCLIMetadataWithProfile(self):
        action = "validate"
        target = "test/fixtures/metadata_lib/dataset_metadata"
        profileLoc = "profile_json/Dataset/0.3-RELEASE-2019_06_14.json"
        code = testValidation(action, target_data=target, profile=profileLoc)
        expected = expectedCode(
            target_data=target, profile=profileLoc)
        self.assertEqual(code, expected)

    def testCLISitemapExtractor(self):
        action = "sitemap"
        target = "test/fixtures/sitemap/sitemap_index_shorten.xml"
        result = testValidation(action, target_data=target)
        # click.echo("result" + str(result))

        cleanup(result)

    def testCLIWebsiteExtractor(self):
        action = "sitemap"
        target="https://disprot.org/"
        result = testValidation(action, target_data=target)
        # click.echo("result" + str(result))
        cleanup(result)

    def testCleanUpLiveData(self):
        cleanup(config.METADATA_LOC)
        cleanup("test/fixtures/metadata_lib/format_NQuads_jsonld")


if __name__ == '__main__':
    unittest.main()
