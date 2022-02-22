from test.unit.profileBuilding import runSeparateSpecAndMapping
import unittest
import json
import pathlib

from src.Classes.validator import check_completeness


class TestUnits(unittest.TestCase):
    def testYmlToDictError(self):
        specInfo, mapping = runSeparateSpecAndMapping(
            "test/fixtures/profile_lib/wrong_format_profile_yml.html")
        self.assertIsNone(
            specInfo, "The specification was extracted")
        self.assertIsNone(
            mapping, "The mapping extracted was extracted")

    def testYmlToDictCorrect(self):
        specInfo, mapping = runSeparateSpecAndMapping(
            "test/fixtures/profile_lib/correct_format_profile_yml.html")
        self.assertIsNotNone(
            specInfo,  "The specification was not extracted")
        self.assertIsNotNone(
            mapping,  "The mapping was not extracted")
        
    def testCheckCompleteness(self):
        profileListDictPath = pathlib.Path("test/fixtures/profile_lib/profile_marg.txt")
        profileListDict = json.loads(profileListDictPath.read_text())

        profileExistPath = pathlib.Path(
            "test/fixtures/profile_lib/profile_exist_prop.txt")
        with profileExistPath.open() as f:
            existProperty = f.read().splitlines()
        diffKeys = []
        result = check_completeness(existProperty,
                                    diffKeys,
                                    profileListDictPath,
                                    "ComputationalWorkflow",
                                    "1.0-RELEASE")
        propMinExist = str(set(profileListDict["minimum"]))
        print(f"OWDB IN  {propMinExist}")
        print(f"OWDB OUT {result['Minimum']['Implemented']}")
        self.assertEqual(propMinExist, result["Minimum"]["Implemented"])
