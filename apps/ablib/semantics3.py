#
# semantics functions
#

import spacy
import copy
import re

from ablib import bitNER


class X3: pass
# subj  = <token>.lemma_ or "EMPTY"
# hasEmptySubj = True|False (an object of the EmptyToken class)
# hasNERSubj = True|False (has subj that is not recognized by wordnet)
# subjText
# subjChunk
# subjChunkDbg
# pred  = <token>.lemma_  or "be + 3dform"
# predText
# isPassiveVoice = True|False
# isNegativePredicate = True|False (neg)
# isNER = True|False
# obj = <token>.lemma_ or "EMPTY" (an object of the EmptyToken class)
# objText
# objChunk
# objChunkDbg
# objIsVerb = False | True (if object has pos_ verb or ing form
# hasEmptyObj = True|False
# hasNERObj = True|False 
# dbg = output of x3DebugString
# subjWN = item from wordnet
# objWN = item from wordnet

# for empty tokens
class EmptyToken: pass

class MyChunk: pass
# text
# chunk
# dbg


EMPTY="EMPTY"

SKIPSUBJ = ["that","which","who"]
PRONOUNS = ["it","they"]

OBJS = ["nsubj","nsubjpass","dobj","pobj"]

###################################################################
# prepare sentence

def prepSent(sent):
    # remove tags 
    sent = re.sub(re.compile('<.*?>'), '', sent)

    # replace predefined terms (see bitNER)
    sent = bitNER.replace(sent)

    # remove urls
    sent = re.sub('http[s]?://\S+', '', sent)

    # replace '/' by '\' , because spacy parses all between '/' as words 
    sent = sent.replace("/", "\\")

    # remove different symbols
    sent = re.sub(r'[()]', '', sent)
    sent = re.sub(r'[\[\]]', '', sent)
    # ! should be removed
    sent = re.sub('[<!@#$>]', '', sent)
    sent = re.sub(r'[-]','',sent)

    return sent


###################################################################
# debug and printing

def tokensDebugString(doc):
    res = ""
    for token in doc: 
        res = res+token.text+"["+token.pos_+"/"+token.dep_+"] "
    return res


def x3DebugStringFormatted(x3):
    res = "X3|"

    if x3.hasEmptySubj: res = res + EMPTY+"|"
    else: res = res+ x3.subj +"!"+ x3.subjText +"|"

    res = res+ x3.pred+"!"+x3.predText+"|"

    if x3.hasEmptyObj: res = res + EMPTY+"|"
    else:
        res = res+ x3.obj +"!"+ x3.objText +"|"
        if (x3.objIsVerb == True): res = res+ "objverb!"

    if (x3.isPassiveVoice == True): res = res+ "passive!" 
    if (x3.isNegativePredicate == True): res = res+ "negative!"

    return res


def x3DebugString(x3):
    res = "X3: "

    if x3.hasEmptySubj: res = res + EMPTY+"("+EMPTY+")[subj] "
    else: res = res+ x3.subj +"("+ x3.subjText +")"+ "[subj] "

    res = res+ x3.pred+"("+x3.predText+")"
    if (x3.isPassiveVoice == True): res = res+ "/passive/" 
    if (x3.isNegativePredicate == True): res = res+ "/negative/" 
    res = res + "[pred] "

    if x3.hasEmptyObj: res = res+ EMPTY+"("+EMPTY+")[obj] "
    else:
       if x3.objIsVerb == False: 
           res = res+ x3.obj +"("+ x3.objText +")"+ "[obj] "
       else:
           res = res+ x3.obj +"("+ x3.objText +")"+ "[verb][obj] "

    return res


def x3DebugString1(x3):
    res = ""

    if x3.hasEmptySubj: res = res + EMPTY+"("+EMPTY+") "
    else: 
        res = res+ x3.subj +"("+ x3.subjText +")"
        if (x3.hasNERSubj == True): res = res+"/ner/"
        res = res + " "


    res = res+ x3.pred+"("+x3.predText+")"
    if (x3.isPassiveVoice == True): res = res+ "/passive/" 
    if (x3.isNegativePredicate == True): res = res+ "/negative/" 
    if (x3.isNER == True): res = res+"/ner/"
    res = res + " "

    if x3.hasEmptyObj: res = res+ EMPTY+"("+EMPTY+") "
    else:
       if x3.objIsVerb == False: 
           res = res+ x3.obj +"("+ x3.objText +")"
       else:
           res = res+ x3.obj +"("+ x3.objText +")"+ "/verb"
       if (x3.hasNERObj == True): res = res+"/ner/"
       res = res + " "


    return res


def childrenDebug(token):
    rez = "CHILDREN: "
    for child in token.children:
       rez = rez +child.text + "/"+child.pos_+"/"+child.dep_+ " "
    return rez

def parentsDebug(token):
    rez = "PARENTS: "
    parents = findParents(token)
    for anc in parents:
       rez = rez +anc.text + "/"+anc.pos_+"/"+anc.dep_+ " "
    return rez

def ancestorsDebug(token):
    rez = "ANCESTORS: "
    for anc in token.ancestors:
       rez = rez +anc.text + "/"+anc.pos_+"/"+anc.dep_+ " "
    return rez


#############################################################################################
# lingvo functions

# check if token is a passive voice, like "This product is made in China"
def isPassiveVoice(token):

    for child in token.children:
        if (child.dep_ == "auxpass"): return True

    for anc in token.ancestors:
        if (anc.dep_ == "nsubjpass"): return True

    return False

# check if token is a passive voice, like "This product is made in China"
def isNegative(token):

    for child in token.children:
        if (child.dep_ == "neg"): return True
    return False


# find a direct child by token's dependency
# token -> child(dep_="agent")
def findDep(token,dep):
    for child in token.children:
        if child.dep_ == dep:
            return child
    return None

# !!! not used
# find a child with dep2 of a child with dep1 
# token -> 'by' (dep1="agent") -> child
def findDep2(token,dep1,dep2):
    tmp = findDep(token,dep1)
    if tmp != None:
       return findDep(tmp,dep2)
    return None

# tell is it direct subject of predicate or not
def isDirectSubject(token):
    # nsubj (nominal subject or a noun phrase which is the subject of a clause)
    if (token.dep_ == "nsubj"): 
        return True
    # nsubjpass (subject of a passive clause)
    if token.dep_ == "nsubjpass": 
        return True
    # todo: csubj, csubjpass

    return False

def findConjunctions(token):
    lst = []
    for child in token.children:
         if (child.dep_ == "conj"):
             lst.append(child)
             # recursion used is here
             lst.extend(findConjunctions(child))
    return lst


def findParents(token):
    lst = []
    # take all ancestors
    for anc in token.ancestors:
        # interates over ancestor's childern
        for child in anc.children:
            # if children is token, anc is a direct parent
            if (child == token): lst.append(anc)

    return lst



def addDirectSubject(token):
    lst = []
    lst.append(token)
    # if found subject has a conjunction (conj) child - the relation between two elements connected by 'and', 'or', etc.
    #    like "Mike(found subject) and I[conj] live(token) in a small town" (both Mike and me live in town) 
    # add its conjunction child too
    lst.extend(findConjunctions(token))
    return lst

def findDirectSubjects(token):
    lst = []
    for child in token.children:
        # looking for direct subjects
        if (isDirectSubject(child)):
            lst.extend(addDirectSubject(child))
    return lst


def hasSkipSubject(lst):
    for token in lst:
         if token.lemma_ in SKIPSUBJ: return True
    return False

def isSkipSubject (token):
    if (isinstance(token, EmptyToken) == True): return False
    if token.lemma_ in SKIPSUBJ: return True
    return False

# creates a list of subjects for the given predicate
def findSubjects(token):
    subjs = []

    # get direct subjects from token's children
    subjs.extend(findDirectSubjects(token))

    # get token's direct parents
    parents = findParents(token)

    # if the predicate is a conjunction like "We read and write(token)[conj] ..."
    # we should find an initial item of conjuntion ("read") and recursively find subjects on it
    if (token.dep_ =="conj"):
        # looking for parents
        for anc in parents:
            # add recusion to find its subjects
            subjs1 = findSubjects(anc)
            if (isinstance(subjs1[0], EmptyToken) == False):
                subjs.extend(subjs1)

    # if no direct subject
    # tryning to use parent object as a subject
    if (len(subjs) == 0):
        for anc in parents:
            if (anc.dep_ == "pobj") or (anc.dep_ == "dobj") or (anc.dep_ == "nsubj") or (anc.dep_ == "nsubjpass"):
                subjs.extend(addDirectSubject(anc))
   
    # if still no subject
    # you can do several tricks that are incorrect
    if (len(subjs) == 0):
        # advcl: adverbial clause modifier (a clause modifying the verb), so, trying to find a subject of the parent verb
        #     "Born in a small town, she took ..."
        if (token.dep_ == "advcl"):
            for anc in parents:
                 subjs.extend(findDirectSubjects(anc))

        if (token.dep_ == "xcomp" ):
            find_xcomp = False
            # xcomp has a dobj as a parent
            #   "Sue asked George[PROPN/dobj](target) to respond[VERB/xcomp]..."
            for anc in parents:
                if (anc.pos_ == "VERB"):
                    for child in anc.children:
                        if (child.dep_ == "dobj"):
                            subjs.extend(addDirectSubject(child))
                            find_xcomp = True
            # if not xcomp should be a child of nearst nsubj
            #   "He[nsubj](not target) says that you[nsubj](target) like to swim[VERB/xcomp]."
            if (find_xcomp == False):
                for anc in parents:
                    if (anc.pos_ == "VERB") or (anc.dep_ == "ROOT"):
                        subjs.extend(findDirectSubjects(anc))


    # trying to find alternatives to subjects like who, that, which
    if (token.dep_ == "relcl") and hasSkipSubject(subjs):
        for anc in parents:
            if (anc.dep_ == "dobj") or (anc.dep_ == "nsubj") or (anc.dep_ == "nsubjpass"):
                subjs.extend(addDirectSubject(anc))


    # add empty subject if no match
    if (len(subjs) == 0):
        tmp = EmptyToken()
        subjs.append(tmp)

    return subjs

# tells is it a direct object or not
def isDirectObject(token):
    # dobj: the noun phrase which is the (accusative) object of the verb.
    #    like "She gave(parent) me a raise[dobj]"
    if token.dep_ == "dobj" : 
        return True
    # pobj: a noun phrase following the preposition
    #    like "I sat(parent) on the chair[pobj]"
    if token.dep_ == "pobj" : 
        return True
    # dative (iobj): the noun phrase which is the (dative) object of the verb.
    #    like "She gave(parent) me[dative] a raise"
    if token.dep_ == "dative" : 
        return True
    # advmod:  a (non-clausal) adverb or adverbial phrase (ADVP) that serves to modify the meaning of the word.
    #    like "...she took the midnight train going(parent) anywhere[advmod]"
    if token.dep_ == "advmod" : 
        return True
    # acomp: adjectival complement
    # An adjectival complement of a verb is an adjectival phrase which functions as the complement (like an
    # object of the verb).
    #    like "Bill is[AUX/ROOT](parent) big[ADJ/acomp] ..."
    if token.dep_ == "acomp" : 
        return True
    # An adjectival modifier of an NP is any adjectival phrase that serves to modify the meaning of the NP.
    # ???
    if token.dep_ == "amod" : 
        return True

    return False

def findDirectObjects(token):
    lst = []
    for child in token.children:
         if (isDirectObject(child)):
            lst.append(child)
            lst.extend(findConjunctions(child))
    return lst

# find objects of a predicate
def findObjects(token):
    objs = []

    # if token is not a verb 
    if (token.pos_ != "VERB") and (token.pos_ != "AUX"):
        # add it to objects
        objs = [token]
        # looking for conjunctions of that objects
        objs.extend(findConjunctions(token))
        # and well done, these objects will be added to a fake predicate 'be'
        return objs

    objs.extend(findDirectObjects(token))

    parents = findParents(token)

    # iterating over token's children
    for child in token.children:
        # if token is conjuction like "write(token) and read[conj] data(object)" 
        # it should go into recursive looking of objects
        if (child.dep_ == "conj"):
            objs1 = findObjects(child)
            if (isinstance(objs1[0], EmptyToken) == False):
                objs.extend(objs1)

        # object may be hidden by:
        #    agent: the complement of a passive verb which is introduced by the preposition "by" and does the action
        #        like "killed(parent) by[agent] her husband(target object)" 
        #    prep: a preposition in, on, at like "find on[prep] the tree"
        if (child.dep_ == "agent") or (child.dep_ == "prep"): 
            objs.extend(findDirectObjects(child))


        # xcomp: a predicative or clausal complement without its own subject.
        #   "you like(token) to swim[xcomp]"
        #   "Sue asked(token) George to respond[xcomp] to her offer." 
        # adds the object like to_<verb>
        if (child.dep_ == "xcomp"):
             objs.append(child)
             objs.extend(findConjunctions(child))

    # several tricks to enhance the creation of triplets
    if (len(objs) == 0):
        for child in token.children:
            # because subj of ccomp might be a nsubj in spacy
            #   "I consider(token)[VERB/ROOT] him[PRON/nsubj](target object) honest[ADJ/ccomp](child)."
            if (child.dep_ == "ccomp"):
                objs1 = findSubjects(child)
                if (isinstance(objs1[0], EmptyToken) == False):
                    objs.extend(objs1)

    # add empty token if no object
    if (len(objs) == 0):
        tmp = EmptyToken()
        objs.append(tmp)

    return objs


# finds a chunk for subjects and objects
def findChunk(token):
    if (token.pos_ !="NOUN") and (token.pos_ != "PROPN"): return None
    for chunk in token.doc.noun_chunks:
        if (chunk.root == token):
            mychunk = MyChunk()
            mychunk.chunk = chunk.text 
            mychunk.dbg = ""
            mychunk.text = ""
            for token1 in chunk:
               mychunk.dbg = mychunk.dbg+ " "+token1.text+"/"+token1.pos_
               if (token1 == token):
                   plur = token1.morph.get("Number")[0]
                   if (plur == "Plur") and (token1.text.endswith("s")):
                       mychunk.text = mychunk.text + token1.lemma_
                   else:
                       mychunk.text = mychunk.text + token1.text
               else:
                   if (token1.pos_ == "DET"): continue
                   if (token1.pos_ == "PRON"): continue
                   mychunk.text = mychunk.text + token1.text+ " "
            #print (mychunk.dbg)
            return mychunk
    return None

#################################################################################################
# related to the getX3 function

# creates an X3 object and add predicate data
def craftPredicate(token):
    x3 = X3()

    # check if it is negative sentence
    if isNegative(token):
        x3.isNegativePredicate = True
    else:
        x3.isNegativePredicate = False


    if (token.pos_ == "VERB") or (token.pos_ == "AUX"):
        # if it is a passive voice
        x3.pred = token.lemma_
        if isPassiveVoice(token):
            # todo: generate third form
            if x3.isNegativePredicate: x3.predText = "be not "+token.text
            else: x3.predText = "be "+token.text
            x3.isPassiveVoice = True
        else:
        # 'normal' verb
            if x3.isNegativePredicate: x3.predText = "not " + token.lemma_
            else: x3.predText = token.lemma_
            x3.isPassiveVoice = False
    else:
        if (token.pos_ == "ADP"):
            x3.pred = "prep_"+token.lemma_
            x3.predText = token.lemma_
            x3.isPassiveVoice = False
        else:
            # it will be an object
            # create a fake predicate for it
            x3.pred = "be"
            if x3.isNegativePredicate: x3.predText = "be not"
            else: x3.predText = "be"
            x3.isPassiveVoice = False

    return x3


# add to X3 subject from token
def addSubject(token,x3):
    if (isinstance(token, EmptyToken) == True):
        x3.subj = EMPTY
        x3.hasEmptySubj = True
    else:
        # ??? convert verbs to nouns
        x3.subj = token.lemma_
        x3.hasEmptySubj = False
        chunk = findChunk(token)
        if chunk != None:
            x3.subjText = chunk.text
            x3.subjChunk = chunk.chunk
            x3.subjChunkDbg = chunk.dbg
        else:
            x3.subjText = token.lemma_
    return x3

# add to X3 object from token
def addObject(token,x3):
    verbs = ["VERB","AUX"]

    if (isinstance(token, EmptyToken) == True):
        x3.obj = EMPTY
        x3.hasEmptyObj = True
    else:
        x3.obj = token.lemma_
        x3.hasEmptyObj = False
        x3.objIsVerb = False
        x3.objChunk = findChunk(token)
        chunk = findChunk(token)
        if chunk != None:
            x3.objText = chunk.text
            x3.objChunk = chunk.chunk
            x3.objChunkDbg = chunk.dbg
        else:
            # convert verb to noun
            if (token.pos_ in verbs): 
                x3.objText = token.text
                x3.objIsVerb = True
            else: x3.objText = token.lemma_
    return x3


# creates a list of triples (subject,predicate,object) around given predicate
def getX3(token):
    if (token.pos_ != "VERB") and (token.dep_ != "ROOT") and (token.dep_ !="xcomp") and (token.dep_ != "relcl") and ( token.dep_ != "ccomp" ): return None
    if (token.dep_ == "amod"): return None

#    if (token.pos_ != "VERB") and (token.pos_ != "AUX") and (token.dep_ != "ROOT") and (): return None
#    if (token.dep_ == "amod") or (token.dep_ == "neg") or (token.dep_ == "aux") or (token.dep_ == "auxpass") : return None

    # creates list of subjects
    subjs = findSubjects(token)
    # create lisr of objects
    objs = findObjects(token)

    # a base X3 object with the predicate data
    baseWithPredicate = craftPredicate(token)

    # target list
    lst = []
    # iterate over subjects
    for subjToken in subjs:
       #if (isSkipSubject(subjToken)): continue
       # copy the X3 object with predicate
       baseWithSubject = copy.copy(baseWithPredicate)
       # add subject's info
       baseWithSubject = addSubject(subjToken,baseWithSubject)
       for objToken in objs:
           #if (isSkipSubject(objToken)): continue
           # copy X3 with predicate and subject
           x3 = copy.copy(baseWithSubject)
           # add object's data
           x3 = addObject(objToken,x3)
           x3.dbg = "   " +x3DebugString(x3)+"\n           "+childrenDebug(token)+"\n           "+parentsDebug(token)+"\n           "+ancestorsDebug(token)
           # add X3 to list 
           lst.append(x3)

    return lst


def getX3extra(token):

    go = False
    for item in OBJS:
        if (item == token.dep_): go = True
    if (go == False): return None

    lst = []

    for child in token.children:
        if (child.dep_ == "prep"):
            base = craftPredicate(child)
            base = addSubject(token,base)

            for child1 in child.children:
                if child1.dep_ in OBJS:
                   lst1 = [child1]
                   lst1.extend(findConjunctions(child1))
                   for obj in lst1:
                       x3 = copy.copy(base)
                       x3 = addObject(obj,x3)
                       x3.dbg = "   "+x3DebugString(x3)+"\n           "+childrenDebug(token)+"\n           "+parentsDebug(token)+"\n           "+ancestorsDebug(token)
                       lst.append(x3)

    return lst

###############################################################################################
# create predicate list from a given document

def makeX3List(doc):
    lst = []
    for token in doc:
        x3s = getX3(token)
        if x3s != None :
            lst.extend(x3s)
        x3e = getX3extra(token)
        if x3e != None :
            lst.extend(x3e)
    return lst


###################################################################
# resulting data

# reads formatted string like
#    X3|+browser!user 's web browser|target!be targeted|website!compromised website|passive!
# and creates an X3 object
def readX3Formatted(strng):
    #print(strng)
    x3 = X3()
    (typ,subjData,predData,objData,args) = strng.split("|")

    x3.typ = typ

    lst1 = subjData.split("!")
    x3.subj = lst1[0]
    x3.hasNERSubj = False
    if x3.subj.startswith("+"):
        x3.subj = x3.subj.lstrip('+')
        x3.hasNERSubj = True
    if x3.subj == EMPTY:
        x3.hasEmptySubj = True
    else:
        x3.hasEmptySubj = False
        x3.subjText = lst1[1]
        if len(lst1)==3:
           x3.subjWN = lst1[2]

    lst2 = objData.split("!")
    x3.obj = lst2[0]
    x3.hasNERObj = False
    x3.objIsVerb = False
    if x3.obj.startswith("+"):
        x3.obj = x3.obj.lstrip('+')
        x3.hasNERObj = True
    if x3.obj == EMPTY:
        x3.hasEmptyObj = True
    else:
        x3.hasEmptyObj = False
        x3.objText = lst2[1] 
        if len(lst2)==3:
           x3.objWN = lst2[2]

    lst3 = predData.split("!")
    x3.pred = lst3[0]
    x3.isNER = False
    if x3.pred.startswith("+"):
        x3.pred = x3.pred.lstrip('+')
        x3.isNER = True
    x3.predText = lst3[1]
    if len(lst3)==3:
        x3.predWN = lst3[2]

    lst3 = args.split("!")
    x3.isPassiveVoice = False
    x3.isNegativePredicate = False
    for arg in lst3:
        if arg == "passive": x3.isPassiveVoice = True
        if arg == "negative": x3.isNegativePredicate = True
        if arg == "objverb": x3.objIsVerb = True

    return x3

def readX3List(doc):
    lst = []
    for strng in doc:
        x3 = readX3Formatted(strng)
        if x3 != None:
           lst.append(readX3Formatted(strng))
    return lst

def getWNterms(x3List,terms):
    for x3 in x3List:
        if hasattr(x3,'subjWN'):
            terms[x3.subj] = x3.subjWN
        if hasattr(x3,'objWN'):
            terms[x3.obj] = x3.objWN
    return terms



def getWNverbs(x3List,verbs):
    for x3 in x3List:
        if hasattr(x3,'predWN'):
            verbs[x3.pred] = x3.predWN
    return verbs
