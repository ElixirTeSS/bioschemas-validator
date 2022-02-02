from test.unit.test_profileBuilding import testSeparateSpecAndMapping
import unittest
import sys
import json
import pathlib
import os

from src.Classes.validator import check_completeness
from src.Classes.staticJSONLDExtractor import extract


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


class TestUnits(unittest.TestCase):
    def testYmlToDictError(self):
        # assert testYmlToDictError() is None
        specInfo, mapping = testSeparateSpecAndMapping(
            "test/profile_lib/wrong_format_profile_yml.html")
        self.assertIsNone(
            specInfo, "The specification was extracted")
        self.assertIsNone(
            mapping, "The mapping extracted was extracted")

    def testYmlToDictCorrect(self):
        specInfo, mapping = testSeparateSpecAndMapping(
            "test/profile_lib/correct_format_profile_yml.html")
        self.assertIsNotNone(
            specInfo,  "The specification was not extracted")
        self.assertIsNotNone(
            mapping,  "The mapping was not extracted")
        
    def testCheckCompletenessNum(self):
        blockPrint()
        profileListDictPath = pathlib.Path("test/profile_lib/profile_marg.txt")
        profileListDict = json.loads(profileListDictPath.read_text())

        profileExistPath = pathlib.Path(
            "test/profile_lib/profile_exist_prop.txt")
        with profileExistPath.open() as f:
            existProperty = f.read().splitlines()
        diffKeys = []
        result = check_completeness(existProperty, diffKeys, profileListDictPath,
                        "ComputationalWorkflow", "1.0-RELEASE", "num")
        propMinExist = str(len(set(existProperty).intersection(
            set(profileListDict["minimum"]))))
        enablePrint()
        self.assertEqual(propMinExist,
                            result["Minimum"]["Implemented"])

    def testCheckCompletenessName(self):
        blockPrint()
        profileListDictPath = pathlib.Path("test/profile_lib/profile_marg.txt")
        profileListDict = json.loads(profileListDictPath.read_text())

        profileExistPath = pathlib.Path(
            "test/profile_lib/profile_exist_prop.txt")
        with profileExistPath.open() as f:
            existProperty = f.read().splitlines()
        diffKeys = []
        result = check_completeness(existProperty, diffKeys, profileListDictPath,
                        "ComputationalWorkflow", "1.0-RELEASE", "name")
        propMinExist = sorted(list(set(existProperty).intersection(
            set(profileListDict["minimum"]))))
        enablePrint()
        self.assertListEqual(propMinExist,
                            result["Minimum"]["Implemented"])

    def testCheckCompletenessAll(self):
        blockPrint()
        profileListDictPath = pathlib.Path("test/profile_lib/profile_marg.txt")
        profileListDict = json.loads(profileListDictPath.read_text())

        profileExistPath = pathlib.Path(
            "test/profile_lib/profile_exist_prop.txt")
        with profileExistPath.open() as f:
            existProperty = f.read().splitlines()
        diffKeys = []
        result = check_completeness(existProperty, diffKeys, profileListDictPath,
                        "ComputationalWorkflow", "1.0-RELEASE", "all")
        propMinExist = sorted(list(set(existProperty).intersection(
            set(profileListDict["minimum"]))))
        propMinExist.append("Total: "+str(len(propMinExist)))
        enablePrint()
        self.assertListEqual(propMinExist,
                            result["Minimum"]["Implemented"])
        


if __name__ == '__main__':
    unittest.main()
