Bioschemas validation suite
===============
This is the validation suite for Bioschemas. It is currently under development with a web GUI on the way


# Structure of the code

The suite is made up of many different smaller components, as shown in the diagram below. This was designed for the adaptability and maintainability of the code.

![uml_1__10_-Page-1](/uploads/2ef2bb91625b44d2609dbb00c2bb1c72/uml_1__10_-Page-1.png)

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

![commandCLI.drawio](/uploads/f26ac70810c5e5f091395d438ac718ec/commandCLI.drawio.png)


 
 The command-line interface requires one argument to decide which route it will take, buildprofile(1), validate(2), tojsonld(3) or sitemap(4).
 
 
 
 
### Step 1
#### Build the profile JSON schema

![route1-buildprofile](/uploads/62a99bf1fb8e9eb9af7ed07df111601f/route1-buildprofile.png)


  The first step needed to use this validation suite. It will build the JSON schema for Bioschemas profiles necessary for validation.
  
  The default is to build all the profiles in the Bioschemas profile location which is the directory "profileBase", set in `YML_LOC` in **config.py**.
  
  `target_data` is not necessary for route 1, unless you want to build certain profile(s) instead of refreshing all the JSON schemas, in which case it needs to be a path to the yml file or if want to build multiple profiles, a path to a file containing the path to the profile YML files.
  
  For example:

*   `python src/command.py buildprofile`
*   `python src/command.py buildprofile --target_data=test/profile_lib/demo_profile.txt`
*   `python src/command.py buildprofile --target_data=profile_yml/Gene/0.7-RELEASE.html`




### Step 2
#### Validate your metadata

![route2](/uploads/7b61a972c0cd6bea12440b9f5650d782/route2.png)

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
  
*   `python command.py validate --target_data=profileLive/jrc/jrc_1.jsonld --csv="all"`
*   `python command.py validate --target_data=profileLive/jrc/jrc_1.jsonld`
*   `python src/command.py validate --target_data=https://nanocommons.github.io/specifications/jrc/ --static_jsonld`


### EXTRA ROUTES
#### Route 1 - tojsonld

It will convert the files to JSON-LD before validation, without the validation.

`target_data` is necessary and can be a path to a directory or a file of paths to metadata.

  For example:
  * ` python src/command.py tojsonld --target_data=test/metadata_lib/format_NQuads`
  
  
#### Route 2 - sitemap

It will extract the URL from a downloaded sitemap or look for a sitemap from a website domain and extract it online.

`target_data` is necessary and can be a path to a directory or a file of paths to metadata.

  For example:
  *  `python src/command.py sitemap --target_data=https://disprot.org/`


### Possible Scenarios 1

User A wishes to validate if all the resources on a dataset website that claims to conforms to Bioschemas profile are correct and:
*  The metadata is coded within the HTML of the webpages
*  The metadata are in JSON-LD format
*  The web pages wanted are all contained in a sitemap


How to use this tool suite:
1.  Run `python src/command.py buildprofile` to build the profile in JSON Schemas
2.  Add `--sitemap_convert` to the validation command will extract all URLs from the sitemap, `--staticJSONLD` will extract all the static JSON-LD metadata from the URLs. Run `python src/command.py validate --target_data=[pathToSitemap] --staticJSONLD --sitemap_convert`, each URL in the the sitemap will be visited, its metadata extracted and validated, the reports will be shown in the terminal
4.  User A thinks the detailed results are very long so he decided to read the shortened version instead: `python src/command.py validate --target_data=[pathToSitemap] --staticJSONLD --sitemap_convert --csv="all"`. Instead of the detailed report, a csv file is created with the marginality of the metadata reported.

 
### Possible Scenarios 2

User A wishes to validate if all the resources on a dataset website that claims to conforms to Bioschemas profile are correct and:
*  The metadata are generated dynamically using javascript


How to use this tool suite:
1.  Run `python3 command.py buildProfile` to build the profile in JSON Schemas
2.  If the webpages are not contained in a sitemap, samples must be manually collected
3.  The tool suite currently has no way to extract dynamically generated metadata, other tools must be used such as BMUSE
3.  Assume BMUSE was used to extract metadata, run `python3 command.py validate [pathToMetadata] --convert`. The metadata extracted will be converted to JSON-LD and validated


<!--and(test_wrapper.py)-->

<!--#### Building Bioschemas profile in JSONS schema-->

<!--If this is the first time the program is used, run this command first.-->

<!--`python command.py buildprofile`-->

<!--This command would build the profiles, using all the YML files in the *profileBase* directory-->

<!--`python command.py buildprofile --target_data=[pathToFile]`-->

<!--This command would build the profiles using the YML file path included in the file.-->

<!--*Note*: If the profile were successfully built, the resulting JSON schemas will be put into the *profileMade* directory-->

<!--#### Validation using existing JSON-LD metadata in local-->

<!--The following command can be used when the JSON-LD metadata to be validated is already in the local directory-->

<!--`python command.py validate --target_data=[pathToMetadata]`-->

<!--The path can either be a directory, where all the files inside are metadata or a file that is the metadata.-->

<!--The profile validating again will be:-->
<!--*  The profile the metadata conforms to if mentioned in the metadata using property name `http://purl.org/dc/terms/conformsTo`, or-->
<!--*  The profile the metadata is a type of, using the latest released version or the latest draft version of the profile has not yet been released-->

<!--If a specific profile version is wanted that is not the default, add `profile [pathToProfile]` at the end so `[pathToProfile]` will be the JSON Schemas the validator uses. The command will become:-->

<!--`python command.py validate --target_data=[pathToMetadata] --profile=[pathToProfile]`-->



<!--#### Validation using live metadata in static JSON-LD-->

<!--The following command can be used when the JSON-LD metadata to be validated is live, for the scenario where a live database needs to be validated.-->

<!--`python3 command.py validate --target_data=[pathToLinkFile] --static_jsonld`-->

<!--`[pathToLinkFile]` should point to a file with the URL of webpages that contains the metadata that needs to be validated in static JSON-LD format. The file of URLs can be obtained by extracting URLs from a sitemap (see *Sitemap extraction* below)-->

<!--It can also contain the path to HTML file in local.-->

<!--The addition of staticJSONLD tells the tool suit that the metadata still needs to be extracted from live or local HTML.-->

<!--`--profile=[pathToProfile]` can be added at the end to assign the profile used by the validator.-->

<!--#### Validation for Non JSON-LD metadata(e.g. NQuads)-->

<!--##### Convert metadata to JSON-LD format-->

<!--This command would convert the files in the directory from a non-JSON-LD format to JSON-LD.-->


<!--`python3 command.py tojsonld --target_data=[pathToMetadata]`-->

<!--The path can either be a directory or a file.-->


<!--##### Convert metadata to JSON-LD format then validate-->

<!--`python3 command.py validate --target_data=[pathToMetadata] --convert`-->

<!--This command would first convert the file(s) from a non-JSON-LD format to JSON-LD, then validate using the validator.-->


<!--### Validation against a specific profile or version-->
<!--`python3 command.py validate --target_data=[pathToMetadata]  --profile=[pathToProfile]`-->

<!--This would convert a file of structure data to JSON-LD format, validate it against `[pathToProfile]` rather than the profile the data conforms to.-->


<!--#### Sitemap extraction-->

<!--`python3 sitemapExtractor.py [pathToSitemap]`-->

<!--This will extract all links from a sitemap(.xml) file in local. Useful if the user wants to validate a live database.-->

### FAQ

What do I do if the structured data I want to validate is generated dynamically by javascript?

Live data scraping is not currently available on this tool suite. It is recommended by the developer to use BMUSE for this purpose. It is a Bioschemas scraper that is publicly available and it can handle JSON-LD data that is created by Javascript.
BMUSE store all its output in NQauds format so "toJsonLD" need to be added in the command between test_wrapper and data path so the tool suite knows to convert the format from NQauds to JSON-LD.
`python3 test_wrapper.py toJsonLD [pathToMetadata] validate`

<!--### Command flowchart-->
<!--*Note*: The name of the profile must come right after "profile" in the command.-->

<!--![commandFlowchart](/uploads/ecd9eea151c4470463321e455cbb7c4d/commandFlowchart.png)-->

<!--ChromeDriver version: 89.0.4389.23-->

<!--# Testing-->
<!--## Unit testing-->
<!--Unit testing is currently done using GitLab CI which will run all test every time a new change is commit and pushed.-->


<!--## KaTeX-->

<!--You can render LaTeX mathematical expressions using [KaTeX](https://khan.github.io/KaTeX/):-->

<!--The *Gamma function* satisfying $\Gamma(n) = (n-1)!\quad\forall n\in\mathbb N$ is via the Euler integral-->

<!--$$-->
<!--\Gamma(z) = \int_0^\infty t^{z-1}e^{-t}dt\,.-->
<!--$$-->

<!--> You can find more information about **LaTeX** mathematical expressions [here](http://meta.math.stackexchange.com/questions/5020/mathjax-basic-tutorial-and-quick-reference).-->


<!--## UML diagrams-->

<!--You can render UML diagrams using [Mermaid](https://mermaidjs.github.io/). For example, this will produce a sequence diagram:-->

<!--```mermaid-->
<!--sequenceDiagram-->
<!--Alice ->> Bob: Hello Bob, how are you?-->
<!--Bob-->>John: How about you John?-->
<!--Bob--x Alice: I am good thanks!-->
<!--Bob-x John: I am good thanks!-->
<!--Note right of John: Bob thinks a long<br/>long time, so long<br/>that the text does<br/>not fit on a row.-->

<!--Bob-->Alice: Checking with John...-->
<!--Alice->John: Yes... John, how are you?-->
<!--```-->

<!--And this will produce a flow chart:-->

<!--```mermaid-->
<!--graph LR-->
<!--A[Square Rect] -- Link text --> B((Circle))-->
<!--A --> C(Round Rect)-->
<!--B --> D{Rhombus}-->
<!--C --> D-->
<!--```-->


<!--ChromeDriver version: 89.0.4389.23-->
