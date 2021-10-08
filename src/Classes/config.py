# location and file extension keywords
# needs to be a string
# any EXT(file extension) need to include a dot
from pathlib import Path
YML_LOC = Path("profile_yml")
PROFILE_EXT =".json"
PROFILE_LOC = Path("profile_json")
METADATA_EXT =".jsonld"
METADATA_LOC = Path("profileLive")
PROFILE_MARG_EXT =".txt"
PROFILE_MARG_LOC = Path("profile_marginality")
METADATA_DEFAULT_PROP = Path("src/Classes/metadataDefaultPropName.txt")

# # Uncomment this for output in a file
OUTPUT_LOCATION = Path("output.txt")
OUTPUT_LOCATION_WRITE = OUTPUT_LOCATION.open('w')

# # Uncomment this for output in terminal
# OUTPUT_LOCATION_WRITE = None
