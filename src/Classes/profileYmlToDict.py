import sys
import click
def separateSpecAndMapping(file):
    try:
        specInfo = file.split("spec_info:")[1].split("mapping:")[0]
        mapping = file.split("spec_info:")[1].split("mapping:")[1].split("---")[0]
        return specInfo, mapping    
    except IndexError:
        return None, None
        

def tranform_yml_to_dict(yml):
    # print("tranform_lines_to_dict")
    lines = yml.splitlines()
    infoNeeded = ["expected_types:", "marginality:", "cardinality:", "controlled_vocab:"]
    blocks = list()
    infodict = dict()
    i = 0
    while i in range(len(lines)):
        lines[i] = lines[i].strip()
        res = [ele for ele in infoNeeded if(ele in lines[i])]
        if res:
            if (i+1) in range(len(lines)):
                while ":" in lines[i] and ":" not in lines[i+1]:
                    lines[i] = lines[i] +  lines[i+1]
                    lines.remove(lines[i+1])

            blocks.append(lines[i])
        i = i + 1
    for line in blocks:
        key = line.split(":")[0].replace("[^a-zA-Z]", "")
        typess = line.split(":")[1].replace(" ", "").split("-")
        typess = list(filter(None, typess))
        if len(typess) ==0:
#                 print(typess)
            typess.append("")
#             print(len(typess))
        if key == "expected_types":
            infodict[key] = list()
            for types in typess:
                types = types.replace("[^a-zA-Z]", "")
                infodict[key].append(types)
            infodict[key].sort(reverse=True)
        else:
            
            infodict[key] = typess[0]
    return infodict
