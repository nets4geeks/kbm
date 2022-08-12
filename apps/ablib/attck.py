
#
# attck
# 

import json


# parse names & descriptions of ATTCK techniques  as files    
#    outFolderTechniques - for techniques
#    outFolderSubTechniques - for subtechniques
#    isUsenames: True - names like TXXXX, False - names like ids (attack-pattern-xxxx...)
def parseAsTextFiles1(inFile, outFolderTechniques, outFolderSubTechniques,isUseNames):
    f = open(inFile)
    data = json.load(f)
    for item in data['objects']:
        if item['type'] != "attack-pattern": continue
        if ( 'x_mitre_deprecated' in item and item['x_mitre_deprecated'] ) : continue
        if (not 'description' in item) : continue 
        name = getTechniqueName(item['external_references'])
        if name == None : continue
        if not isUseNames: name = item['id']
        outFolder = outFolderTechniques
        if ( 'x_mitre_is_subtechnique' in item and item['x_mitre_is_subtechnique']) :
             outFolder = outFolderSubTechniques
        with open(outFolder+"/"+name, 'a') as outFile:
             outFile.write(item['description'] + '\n')
             outFile.close()
    f.close()


# get TechniqueName from 'external_references' json tag
def getTechniqueName(jsonItem):
    for item in jsonItem:
        if item['source_name'] == 'mitre-attack':
           return item['external_id']
    return None



