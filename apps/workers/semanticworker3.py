#
# makes 3xs (subject,predicates,object) and terms list from given documents 
# file (xxx.svo) includes lines formatted:
#   x3|subject!phrase|predicate!phrase|object!phrase|attribute1!attribute2
# like:
#   X3|bus!bus|hear!be heard|to_go!to go|passive!
# 
# file (xxx.term) includes lines formatted 
#   term|id|phrase|description
# like:
#   

import sys
import nltk
import string
import spacy

from ablib import base
from ablib import files
from ablib import semantics3


# first argument - source folder
path=sys.argv[1]
# second argument - target folder
output=sys.argv[2]

docsFiles=files.files(path)
docs=files.get(path)

tot =0
for doc_id in range(len(docs)):
    #if tot>0: break
    doc = docs[doc_id]
    docName = docsFiles[doc_id]
    print(docName)

    # make list of sentenses
    sents = nltk.sent_tokenize(doc)

    f = open(output+"/"+docName+".debug","w")
    f1 = open(output+"/"+docName+".term","w")
    f2 = open(output+"/"+docName+".svo","w")

    terms = []

    for sent in sents:
        # prepare sentence for spacy processing, including NER replacement
        sent = semantics3.prepSent(sent)

        # make a spacy doc from the sentence
        nlp = spacy.load("en_core_web_sm")
        subDoc = nlp(sent)

        res1 = semantics3.tokensDebugString(subDoc)
        f.write("\n"+sent+"\n")
        f.write(res1+"\n")

        # array of triples
        res2 = semantics3.makeX3List(subDoc)
        # list of terms
        for x3 in res2:
            f.write(x3.dbg+"\n")
            #f2.write(x3.subj +"("+ x3.subjText +") "+x3.pred +"("+ x3.predText +") "+x3.obj+"("+ x3.objText +") "+"pass="+x3.isPassive)
            f2.write(semantics3.x3DebugStringFormatted(x3)+"\n")

            #if hasattr(x3,'subjChunkDbg'):
            if not (x3.hasEmptySubj):
                terms.append("term|"+x3.subj+"!"+x3.subjText)
            #if hasattr(x3,'objChunkDbg'):
            if not (x3.hasEmptyObj):
                terms.append("term|"+x3.obj+"!"+x3.objText)

    #terms = set(terms)
    for term in sorted(set(terms)):
        f1.write(term+"\n")

    f.close()
    f1.close()
    f2.close()
    tot =tot+1
