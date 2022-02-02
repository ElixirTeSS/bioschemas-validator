import pathlib
from src.Classes.profileYmlToDict import separateSpecAndMapping


def testSeparateSpecAndMapping(path=""):
    f = pathlib.Path(path).read_text()
    specInfo, mapping = separateSpecAndMapping(f)
    return specInfo, mapping
