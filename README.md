Bioschemas validation suite
===============
This is the validation suite for Bioschemas. It is currently under development with a web GUI on the way


# Structure of the code

The suite is made up of many different smaller components, as shown in the diagram below. This was designed for the adaptability and maintainability of the code.


![uml_1 (10) (1)](https://user-images.githubusercontent.com/49096202/134204850-dc1c79fb-23f6-46e4-8061-df3eb7151ab9.png)



# Structure of the repository

The YML file for the Bioschemas profiles are stored within the `profileBase` directory, each subdirectory is a  profile type and within is the all the available version of that profile.

The JSON schema for the Bioschemas profiles is stored within the `profileMade` directory in the same repository structure as `profileBase`.

As shown in the diagram, the marginality of the profiles is stored individually in `profileList` with the same repository structure.

These directory names are set in **config.py**, along with the file extension of the results the validation suite created. 

| Note | Name | Default Value |
|--|--|--|
| Location of the YML file| YML_LOC | profileBase |
| Location of the Bioschemas profile JSON schemas made|PROFILE_LOC | profileMade |
| File Extension of the profile JSON schemas|PROFILE_EXT | .json |
|Location of the metadata extracted from live webpage| METADATA_LOC | profileLive |
| File Extension of the live metadata extracted|METADATA_EXT | .jsonld |
| Location of the marginality list of the profile|PROFILE_MARG_LOC | profileList |
| File Extension of the marginality list |PROFILE_MARG_EXT | .txt |


# Requirements

The validation suite is programmed in Python and uses many external Python libraries. 

It is being developed and tested in Linux with plans to test in on Windows.

Requirements.txt contains all the librarys that was installed when tested but these below are the key library and versions:
  - Python-3.9.4
  - jsonschema-3.2.0
  - python-dateutil-2.8.1
  - rdflib-5.0.0
  - rdflib-jsonld-0.5.0
  - PyLD-2.0.3
  - extruct-0.12.0
  - panda-0.3.1
  
# Using the validation suite

![commandCLI drawio](https://user-images.githubusercontent.com/49096202/134204494-0f3d6b19-e35d-4ec4-9574-ab5d58e54c75.png)


 
 The command-line interface requires one argument to decide which route it will take, buildprofile(1), validate(2), tojsonld(3) or sitemap(4).
 
### Setup

Depends on your computer setup, for the installation pip is needs to be able to operate on Python3 environment.

Firstly, to get the repository either download the zip or use:

`$ git clone https://github.com/GloC99/Bioschemas-Validator.git`

Then run this to install the required libraries.

`$ pip install -r requirements.txt` or `$ pip3 install -r requirements.txt`
 
 
### Step 1
#### Build the profile JSON schema

![route1-buildprofile](https://user-images.githubusercontent.com/49096202/134204510-7549e415-8bab-42f1-ba1c-c078ac79d372.png)


  The first step needed to use this validation suite. It will build the JSON schema for Bioschemas profiles necessary for validation.
  
  The default is to build all the profiles in the Bioschemas profile location which is the directory "profileBase", set in `YML_LOC` in **config.py**.
  
  `target_data` is not necessary for route 1, unless you want to build certain profile(s) instead of refreshing all the JSON schemas, in which case it needs to be a path to the yml file or if want to build multiple profiles, a path to a file containing the path to the profile YML files.
  
  For example:

*   `$ python src/command.py buildprofile`
*   `$ python src/command.py buildprofile --target_data=test/profile_lib/demo_profile.txt`
*   `$ python src/command.py buildprofile --target_data=profile_yml/Gene/0.7-RELEASE.html`




### Step 2
#### Validate your metadata

![route2](https://user-images.githubusercontent.com/49096202/134204482-f6940ee2-4281-4d49-a75f-651b5ffde0fd.png)

> Note: The component in containers are depends on the flag used

The main step of this validation suite. It will validate the metadata provided.
    
`target_data` is necessary for route 2, as you need to gave it the metadata you want to validate.
    
There are several optional parameter for this route:
*  `static_jsonld`(flag)
*  `csv`
*  `convert`(flag)
*  `profile`
*  `sitemap_convert`(flag)

`static_jsonld` should be set if the metadata needs to be extracted from HTML. `target_data` needs to be, in this case, a file with the URL of webpages that contains the metadata in static JSON-LD format that needs to be validated. It can also be the path to local HTML files.

`csv` should be set if you want to do a bulk validation as its export shows the marginality validation result of the data against the profile in a CSV file. csv can be set as `num`, `name` or `all`, which will respectfully return numbers, property names or both in the CSV file.

`convert` should be set if the metadata is in the local but in a non-JSON-LD format. It will convert the files to JSON-LD before validation.

`profile` need to be set if you want to validate the metadata against a profile or profile version of your choice. It needs to be a path to the JSON schema of that profile.

`sitemap_convert`need to be set if the `target_data` is an XML sitemap file or a website domain. It will extract the URLs from the sitemap(itself or of the website domain) and extract static JSON-LD data, store them and validate them in a one-line command.


  For example:
  
*   `$ python command.py validate --target_data=profileLive/jrc/jrc_1.jsonld --csv="all"`
*   `$ python command.py validate --target_data=profileLive/jrc/jrc_1.jsonld`
*   `$ python src/command.py validate --target_data=https://nanocommons.github.io/specifications/jrc/ --static_jsonld`


### EXTRA ROUTES
#### Route 1 - tojsonld

It will convert the files to JSON-LD before validation, without the validation.

`target_data` is necessary and can be a path to a directory or a file of paths to metadata.

  For example:
  * ` $ python src/command.py tojsonld --target_data=test/metadata_lib/format_NQuads`
  
  
#### Route 2 - sitemap

It will extract the URL from a downloaded sitemap or look for a sitemap from a website domain and extract it online.

`target_data` is necessary and can be a path to a directory or a file of paths to metadata.

  For example:
  *  `$ python src/command.py sitemap --target_data=https://disprot.org/`


### Possible Scenarios 1

User A wishes to validate if all the resources on a dataset website that claims to conforms to Bioschemas profile are correct and:
*  The metadata is coded within the HTML of the webpages
*  The metadata are in JSON-LD format
*  The web pages wanted are all contained in a sitemap


How to use this tool suite:
1.  Run `$ python src/command.py buildprofile` to build the profile in JSON Schemas
2.  Add `--sitemap_convert` to the validation command will extract all URLs from the sitemap, `--staticJSONLD` will extract all the static JSON-LD metadata from the URLs. Run `python src/command.py validate --target_data=[pathToSitemap] --staticJSONLD --sitemap_convert`, each URL in the the sitemap will be visited, its metadata extracted and validated, the reports will be shown in the terminal
4.  User A thinks the detailed results are very long so he decided to read the shortened version instead: 
    `$ python src/command.py validate --target_data=[pathToSitemap] --staticJSONLD --sitemap_convert --csv="all"`
     Instead of the detailed report, a csv file is created with the marginality of the metadata reported.

 
### Possible Scenarios 2

User A wishes to validate if all the resources on a dataset website that claims to conforms to Bioschemas profile are correct and:
*  The metadata are generated dynamically using javascript


How to use this tool suite:
1.  Run `python3 command.py buildProfile` to build the profile in JSON Schemas
2.  If the webpages are not contained in a sitemap, samples must be manually collected
3.  The tool suite currently has no way to extract dynamically generated metadata, other tools must be used such as BMUSE
3.  Assume BMUSE was used to extract metadata, run `python3 command.py validate [pathToMetadata] --convert`. The metadata extracted will be converted to JSON-LD and validated


### FAQ

What do I do if the structured data I want to validate is generated dynamically by javascript?

Live data scraping is not currently available on this tool suite. It is recommended by the developer to use BMUSE for this purpose. It is a Bioschemas scraper that is publicly available and it can handle JSON-LD data that is created by Javascript.
BMUSE store all its output in NQauds format so "toJsonLD" need to be added in the command between test_wrapper and data path so the tool suite knows to convert the format from NQauds to JSON-LD.


