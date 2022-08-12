#
# compares triples in files in target folder to templates in source folder
#

import sys
import nltk
import string

from ablib import base
from ablib import files
from ablib import semantics3
from ablib import semanticompare2

#semanticompare2.debug = True

extension = "svo"
dictonaryNER = "Dictonary.NER"
dictonaryTerms = "Dictonary.Terms"
dictonaryVerbs = "Dictonary.Verbs"
classificationMax = "Classification.Max"
classificationAvg = "Classification.Avg"
classificationBest = "Classification.Best"
classificationBestAvg = "Classification.BestAvg"
classificationStat = "Classification.Stat"


# first argument - templates folder
templatesPath=sys.argv[1]
# second argument - target folder
targetPath=sys.argv[2]

# third argument - output folder
outputPath=sys.argv[3]

templatesFiles=files.filesWithExtension(templatesPath,extension)
templatesDocs=files.get2(templatesPath,templatesFiles)

targetFiles=files.filesWithExtension(targetPath,extension)
targetDocs=files.get2(targetPath,targetFiles)

templates = []
terms = {}
verbs = {}
ners = {}

print("reading templates ...")
for doc_id in range(len(templatesFiles)):
    doc = templatesDocs[doc_id]
    docName = templatesFiles[doc_id]
    lst = semantics3.readX3List(doc)
    templates.append(lst)
    terms = semantics3.getWNterms(lst,terms)
    verbs = semantics3.getWNverbs(lst,verbs)
    ners = semanticompare2.getNERs(lst,ners)

print("writing dictionaries ...")
# write vocabriaries
fx = open(outputPath+"/"+dictonaryNER,"w")
for key in sorted(ners.keys()):
    fx.write(ners[key].item+"!"+ners[key].itemText+"!"+str(ners[key].itemWN)+"\n")
fx.close()

fx = open(outputPath+"/"+dictonaryTerms,"w")
for key in sorted(terms.keys()):
    fx.write(key+"!"+terms[key]+"\n")
fx.close()

fx = open(outputPath+"/"+dictonaryVerbs,"w")
for key in sorted(verbs.keys()):
    fx.write(key+"!"+verbs[key]+"\n")
fx.close()

print("parsing docs ...")
docs = []
for doc_id in range(len(targetFiles)):
    doc = targetDocs[doc_id]
    docName = targetFiles[doc_id]
    lst = semantics3.readX3List(doc)
    docs.append(lst)

nt = semanticompare2.init()

f3 = open(outputPath+"/"+classificationMax,"w")
f3.write("target!template!semMax!true\n")

f4 = open(outputPath+"/"+classificationAvg,"w")
f4.write("target!template!semAvg!true\n")

f5 = open(outputPath+"/"+classificationBest,"w")
f5.write("target!template!bestMax!true\n")

f6 = open(outputPath+"/"+classificationBestAvg,"w")
f6.write("target!template!bestAvg!true\n")


targetsTotal = len(targetFiles)
templatesTotal = len(templatesFiles)
rightMax = 0
rightAvg = 0
rightBest = 0
rightBestAvg = 0

for i in range(len(targetFiles)):
    target = docs[i]
    targetName = targetFiles[i]
    print("taking target "+targetName+" ...")

    bestMax = 0
    bestMaxTemplate = None
    bestAvg = 0
    bestAvgTemplate = None

    bestBest = 0
    bestBestTemplate = None

    bestBestAvg = 0
    bestBestAvgTemplate = None


    f = open(outputPath+"/"+targetName+".debug","w")
    fy = open(outputPath+"/"+targetName+".debug.short","w")
    f2 = open(outputPath+"/"+targetName+".estimate","w")
    # format description
    f2.write("document!template!"+semanticompare2.s2tHeader("sim")+semanticompare2.s2sHeader('sem')+"\n")

    for j in range(len(templatesFiles)):
        f.write("\n")
        template = templates[j]
        templateName = templatesFiles[j]
        print("   taking template "+templateName+" ...")
        f.write("::: "+templateName+" :::\n")
        fy.write ("\n::: "+templateName+" :::\n")

        bss = semanticompare2.getS2S()
        css = semanticompare2.getS2T()

        for x3t in template:
            if x3t.typ == 'env': continue
            if x3t.typ == 'term': continue

            ss = semanticompare2.getS2T()

            f.write("==========================================================\n")
            fy.write("==========================================================\n")


            for x3d in target:
                # skip triplets with objects as verbs
                if (x3d.objIsVerb): continue
                rez = []
                # add varios comparisons here
                # semantic
                simRez = semanticompare2.semanticMethod2(nt,x3t,x3d,terms,verbs,ners)
                semanticompare2.addS2Tv3(ss,simRez.score1,x3d,simRez)
                # write results
                f.write(semantics3.x3DebugString1(x3t)+"\n")
                f.write(semantics3.x3DebugString1(x3d)+"\n")
                f.write(simRez.debug+"\n")
                #if (simRez.score1>0.45):
                #    fy.write(semantics3.x3DebugString1(x3t)+"\n")
                #    fy.write(semantics3.x3DebugString1(x3d)+"\n")
                #    fy.write(simRez.debug+"\n")
 
            fy.write(semantics3.x3DebugString1(x3t)+"\n")
            fy.write(semantics3.x3DebugString1(ss.x3)+"\n")
            fy.write(ss.simRez.debug)
            fy.write ("[semantic] "+semanticompare2.s2tString(ss)+"\n")

            f.write ("[semantic] "+semanticompare2.s2tString(ss)+"\n")


            semanticompare2.addS2S(bss,x3t.typ,ss.m)
            semanticompare2.addS2Tv2(css,ss.m,0.2)

        semanticompare2.calcS2S(bss)

        # write results !!! add to format description
        f2.write(targetName+"!"+templateName+"!"+semanticompare2.s2tString1(css)+semanticompare2.s2sString(bss)+"\n")

        if (bss.max > bestMax):
           bestMax = bss.max
           bestMaxTemplate = templateName

        if (bss.avg > bestAvg):
           bestAvg = bss.avg
           bestAvgTemplate = templateName

        if (css.m > bestBest):
           bestBest = css.m
           bestBestTemplate = templateName

        if (css.a > bestBestAvg):
           bestBestAvg = css.a
           bestBestAvgTemplate = templateName



    bestRez = "0"
    if bestMaxTemplate != None:
       (name,ext) = bestMaxTemplate.split(".")
       if name in targetName: 
          bestRez = "1"
          rightMax +=1
    f3.write(targetName+"!"+str(bestMaxTemplate)+"!"+format(bestMax,".4f")+"!"+bestRez+"\n")

    bestRez1 = "0"
    if bestAvgTemplate != None:
       (name,ext) = bestAvgTemplate.split(".")
       if name in targetName: 
          bestRez1 = "1"
          rightAvg +=1
    f4.write(targetName+"!"+str(bestAvgTemplate)+"!"+format(bestAvg,".4f")+"!"+bestRez1+"\n")


    bestRez2 = "0"
    if bestBestTemplate != None:
       (name,ext) = bestBestTemplate.split(".")
       if name in targetName: 
          bestRez2 = "1"
          rightBest +=1
    f5.write(targetName+"!"+str(bestBestTemplate)+"!"+format(bestBest,".4f")+"!"+bestRez2+"\n")

    bestRez3 = "0"
    if bestBestAvgTemplate != None:
       (name,ext) = bestBestAvgTemplate.split(".")
       if name in targetName: 
          bestRez3 = "1"
          rightBestAvg +=1
    f6.write(targetName+"!"+str(bestBestAvgTemplate)+"!"+format(bestBestAvg,".4f")+"!"+bestRez3+"\n")


    f.close()
    fy.close()
    f2.close()

f3.close()
f4.close()
f5.close()
f6.close()

f7 = open(outputPath+"/"+classificationStat,"w")
f7.write("targets:    "+str(targetsTotal)+"\n")
f7.write("templates:  "+str(templatesTotal)+"\n")
f7.write("maxScore:   "+format(rightMax/targetsTotal,".4f")+"\n")
f7.write("avgScore:   "+format(rightAvg/targetsTotal,".4f")+"\n")
f7.write("bestScore:  "+format(rightBest/targetsTotal,".4f")+"\n")
f7.write("best1Score: "+format(rightBestAvg/targetsTotal,".4f")+"\n")

f7.close()
