from flask import Flask, render_template, request
import os
import sys
sys.path.append("./")

import src.command as command
import src.Classes.config as config
app = Flask(__name__)

global metadataURL
@app.route("/")
def index():
    metadataURL = request.args.get("metadata URL", "")
    metadata = request.args.get("Or metadata", "")
    sitemap = request.args.get("Or sitemap/domain", "")


    # return render_template("index.html")
    if metadataURL:
        result = validation(metadataURL, static_jsonld=True)
    elif metadata:
        tempInputName = "metadataTemp" + config.METADATA_EXT
        
        with open(tempInputName, "w") as inputMetadata:
            inputMetadata.write(metadata)
        print(tempInputName)
        result = validation(tempInputName)
    elif sitemap:
        result = validation(sitemap, sitemap_convert=True)
    else:
        result = ""

    # return render_template("validate.html")
    return ("""
   <!--BOOTSTRAP 5 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-F3w7mX95PdgyTmZZMECAngseQB83DfGTowi0iMjiWaeVhAn4FJkqJByhZMI3AhiU" crossorigin="anonymous">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.1/dist/js/bootstrap.bundle.min.js" integrity="sha384-/bQdsTh/da6pkI1MST/rWKFNjaCP5gBSY4sEBT38Q/9RBh9AH40zEOg7Hlq2THRZ" crossorigin="anonymous"></script>

<!--BIOSCHEMAS -->
<script src="libs/bioschemas/setup.js"></script>
<link rel="stylesheet" type="text/css" href="stylesheet.css">
    <form action="" method="get" id="inputData">
            <p>Input your metadata url <input type="text" name="metadata URL"></p>
            <p>or a domain/sitemap link<input type="text" name="sitemap"></p>
            <label for="metadata">Or enter metadata here:</label>
            <textarea name="metadata" form="inputData"></textarea>
            
            <p><input type="submit" value="Validate"></p>
            </form>
            
            """ 
            + result
            )


def validation(target_data, static_jsonld=False, csv="N", profile="N", convert=False, sitemap_convert=False):
    command.validateData(target_data, static_jsonld, csv,
                         profile, convert, sitemap_convert)
    resultFile = config.OUTPUT_LOCATION.open()
    result = ""
    for line in resultFile.readlines():
        result = result + line + "<br >"

    # config.OUTPUT_LOCATION.unlink()
    
    return result

if __name__ == "__main__":
    port = os.environ.get('PORT') or 8080
    app.run(host="127.0.0.1", port=port, debug=True)
