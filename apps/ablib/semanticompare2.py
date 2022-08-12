
from ablib import semantics3
import wn
from wn.similarity import wup
import Levenshtein as lev

#######################################################################################################

debug = False

# used in the list of known NERs and for estimating items
class BNER: pass
# item
# itemText
# itemWN
# itemNER - contains BNER 
# itemIsVerb - for objects that in some cases can be verbs

# get a list of NERs from model
def getNERs(x3List,ners):
    for x3 in x3List:
        if x3.hasNERSubj == True:
            ner = BNER()
            ner.item = x3.subj
            ner.itemText = x3.subjText
            ner.itemWN = None
            if (hasattr(x3,'subjWN')):
                ner.itemWN = x3.subjWN
            ners[x3.subj] = ner
        if x3.hasNERObj == True:
            ner = BNER()
            ner.item = x3.obj
            ner.itemText = x3.objText
            ner.itemWN = None
            if (hasattr(x3,'objWN')):
                ner.itemWN = x3.objWN
            ners[x3.obj] = ner
        if x3.isNER == True:
            ner = BNER()
            ner.item = x3.pred
            ner.itemText = x3.predText
            ner.itemWN = None
            if (hasattr(x3,'predWN')):
                ner.itemWN = x3.predWN
            ners[x3.pred] = ner
    return ners


#######################################################################################################

# creates filter object
def init():
    return wn.Wordnet('oewn:2021')

def synInfo(word):
    nt = init()
    synsets = nt.synsets(word)
    for i, syn in enumerate(synsets):
        print('%s' % syn.id)
        print('  lemmas: "%s"' % '", "'.join(syn.lemmas()))
        print('  definition: "%s"' % syn.definition())


def synInfo1(synsetWord):
    nt = init()
    synset = nt.synset(synsetWord)

    print('%s' % synset.id)
    print('  lemmas: "%s"' % '", "'.join(synset.lemmas()))
    print('  definition: "%s"' % synset.definition())

# finds pos of synset
def wnPOS(synsetWord):
    if synsetWord.endswith("-n"): return "n"
    if synsetWord.endswith("-v"): return "v"
    return None

# finds the best similarity between two nouns
# nt is a filter object
def wnSimNoun(nt,word1,word2):
    syn1 = nt.synsets(word1,pos='n')
    syn2 = nt.synsets(word2,pos='n')
    symMax = 0
    s1word = None
    s2word = None
    if len(syn1)>0 and len(syn2)>0:
        for s1 in syn1:
            for s2 in syn2:
               sym = wup(s1,s2,simulate_root=True)
               if sym > symMax: 
                  symMax = sym
                  s1word = s1.id
                  s2word = s2.id
        if (debug): print("wnSimNoun:",word1+"/"+str(s1word),word2+"/"+str(s2word),symMax)
        return symMax
    return None

def wnSimVerb1(nt,word1,word2):
    syn1 = nt.synsets(word1,pos='v')
    syn2 = nt.synsets(word2,pos='v')
    symMax = 0
    s1word = None
    s2word = None
    if len(syn1)>0 and len(syn2)>0:
        for s1 in syn1:
            for s2 in syn2:
               sym = wup(s1,s2,simulate_root=True)
               if sym > symMax: 
                  symMax = sym
                  s1word = s1.id
                  s2word = s2.id
        if (debug): print("wnSimVerb1:",word1+"/"+str(s1word),word2+"/"+str(s2word),symMax)
        return symMax
    return None


# finds the best similarity between two verbs
def wnSimVerb(nt,word1,word2):
    syn1 = nt.synsets(word1,pos='v')
    syn2 = nt.synsets(word2,pos='v')
    symMax = 0
    if len(syn1)>0 and len(syn2)>0:
        for s1 in syn1:
            for s2 in syn2:
               sym = wup(s1,s2,simulate_root=True)
               if sym > symMax: symMax = sym
        return symMax
    return None

# compare synset and word (code.n.03, application)
# by the best meaning of word
def wnSimSynsetWordX(nt,synsetWord,word):
    pos = wnPOS(synsetWord)
    if pos!=None:
        syn1 = nt.synset(synsetWord)
        syn2 = nt.synsets(word)
        if len(syn2)>0:
           symMax = 0
           target = None
           for syn in syn2:
               if syn.pos == pos:
                   sym = wup(syn1, syn, simulate_root=True)
                   if sym > symMax: 
                       symMax = sym
                       target = syn.id
           if (debug): print ("wnSimSynsetWordX:",syn1.id, word+"/"+str(target),symMax)
           return symMax
    return None

# compare word & synset (application,code.n.03)
def wnSimSynsetWordY(nt,word,synsetWord):
    return wnSimSynsetWordX(nt,synsetWord,word)

# compare two synsets (application.n.04, code.n.03)
def wnSimSynsetWordXY(nt,synsetWord1,synsetWord2):
    syn1 = nt.synset(synsetWord1)
    syn2 = nt.synset(synsetWord2)
    if syn1.pos == syn2.pos:
        sym = wup(syn1,syn2, simulate_root=True)
        if (debug): print("wnSimSynsetWordXY:",synsetWord1,synsetWord2,sym)
        return sym
    return None

# compare two words/synsets by their best meaning
# automatically detect synsets
def wnSimUniversal(nt,word1,word2):
    pos1 = wnPOS(word1)
    pos2 = wnPOS(word2)
    if (pos1!=None) and (pos2!=None):
       return wnSimSynsetWordXY(nt,word1,word2)

    if pos1!=None:
       return wnSimSynsetWordX(nt,word1,word2)

    if pos2!=None:
       return wnSimSynsetWordY(nt,word1,word2)

    return wnSimNoun(nt,word1,word2)

#################################################################################################################

def nerSim(x,y):
    word1 = x.itemText.lower()
    if (x.itemNER != None): word1 = x.itemNER.itemText

    word2 = y.itemText.lower()
    if (y.itemNER != None): word2 = y.itemNER.itemText


    dist = lev.distance(word1, word2)
    ln = max(len(word1),len(word2))
    rez = 1-(dist/ln)
    if (debug): print ("nerSim: ", word1, " vs ",word2, " = ",rez)
    return rez

#################################################################################################################

# contains results of comparing of two triples
class SimX3new: pass
# subj
# pred
# obj
# debug
# score1

# finds dictionary items for a BNER object
# for verbs terms = verbs
def addExtra(x,terms,ners):

    x.itemNER = None
    txt1 = x.itemText.lower()
    if x.item in ners.keys(): x.itemNER = ners[x.item]
    else:
      for key in ners:
          txt2 = ners[key].itemText.lower()
          if (txt1 == txt2):
             x.itemNER = ners[key]
             break

    if x.item in terms.keys(): x.itemWN = terms[x.item]
    else: x.itemWN = None

    return x

# returns BNER as a string
def bnerString(x):
    if x.itemNER != None:
       return x.item+"/"+x.itemText+"/"+str(x.itemWN)+"/"+str(x.itemNER.item)+"/"+str(x.itemNER.itemText) 
    else:
       return x.item+"/"+x.itemText+"/"+str(x.itemWN)+"/None"

# takes two BNER items and finds their similarity
def similarity(nt,x,y,isVerb):

    #return nerSim(x,y)

    if (x.itemNER != None) or (y.itemNER != None):
       #if (x.itemWN == None) or (y.itemWN == None):
       return nerSim(x,y)

    if (x.item == y.item):
       if (x.item == "use"): return 0.8
       if (x.item == "get"): return 0.8
       return 1.0

    if (x.itemWN != None ) and (y.itemWN !=None):
       return wnSimSynsetWordXY(nt,x.itemWN,y.itemWN)
 
    if (x.itemWN != None):
       return wnSimSynsetWordX(nt,x.itemWN,y.item)
    if (y.itemWN != None):
       return wnSimSynsetWordY(nt,x.item,y.itemWN)

    if isVerb:
       return wnSimVerb(nt,x.item,y.item)

    return wnSimNoun(nt,x.item,y.item)

# The main semantic method
#    nt - lexicon
#    x - BNER object
#    y - BNER object
#    terms - dictionary of terms with known synsets
#    verbs - dictionary of verbs with known synsets
#    ners  - local NER objects
def semanticMethod2(nt,x,y,terms,verbs,ners):

    sim = SimX3new()

    sim.subj = 0
    sim.obj = 0
    sim.pred = 0
    sim.score1 = 0
    sim.debug = ""

    # creates BNER objects for subjects
    xSubj = BNER()
    ySubj = BNER()
    # use object as a subject for passive voice
    if (x.isPassiveVoice):
        xSubj.item = x.obj
        if hasattr(x,'objText'): xSubj.itemText = x.objText
        else: xSubj.itemText = None
    else: 
        xSubj.item = x.subj
        if hasattr(x,'subjText'): xSubj.itemText = x.subjText
        else: xSubj.itemText = None
    if (y.isPassiveVoice):
        ySubj.item = y.obj
        if hasattr(y,'objText'): ySubj.itemText = y.objText
        else: ySubj.itemText = None
    else: 
        ySubj.item = y.subj
        if hasattr(y,'subjText'): ySubj.itemText = y.subjText
        else: ySubj.itemText = None
    # compare if they are not empty
    if (xSubj.item != semantics3.EMPTY) and (ySubj.item != semantics3.EMPTY):
        # add extra data from dictonaries
        xSubj = addExtra(xSubj,terms,ners)
        ySubj = addExtra(ySubj,terms,ners)
        # estimate similarity
        tmp = similarity(nt,xSubj,ySubj,False)
        if tmp !=None: sim.subj = tmp
        sim.debug = sim.debug+"   S: ("+bnerString(xSubj)+", "+bnerString(ySubj)+")="+format(sim.subj,'.4f')+"\n"
    else:
        sim.debug = sim.debug+"   S: ("+xSubj.item+", "+ySubj.item+")=0 (skipped)"+"\n"

    # compare predicates
    xPred = BNER()
    yPred = BNER()
    xPred.item = x.pred
    if (hasattr(x,'predText')): xPred.itemText = x.predText
    else: xPred.itemText = None
    yPred.item = y.pred
    if (hasattr(y,'predText')): yPred.itemText = y.predText
    else: yPred.itemText = None
    xPred = addExtra(xPred,verbs,ners)
    yPred = addExtra(yPred,verbs,ners)
    tmp = similarity(nt,xPred,yPred,True)
    if tmp !=None: sim.pred = tmp
    sim.debug = sim.debug+"   P: ("+bnerString(xPred)+", "+bnerString(yPred)+")="+format(sim.pred,'.4f')+"\n"

    # compare objects
    xObj = BNER()
    yObj = BNER()
    if (x.isPassiveVoice):
        xObj.item = x.subj
        if hasattr(x,'subjText'): xObj.itemText = x.subjText
        else: xObj.itemText = None
    else: 
        xObj.item = x.obj
        if hasattr(x,'objText'): xObj.itemText = x.objText
        else: xObj.itemText = None
    if (y.isPassiveVoice):
        yObj.item = y.subj
        if hasattr(y,'subjText'): yObj.itemText = y.subjText
        else: yObj.itemText = None
    else: 
        yObj.item = y.obj
        if hasattr(y,'objText'): yObj.itemText = y.objText
        else: yObj.itemText = None
    if ((xObj.item != semantics3.EMPTY) and (yObj.item != semantics3.EMPTY)):
        xObj = addExtra(xObj,terms,ners)
        yObj = addExtra(yObj,terms,ners)
        tmp = similarity(nt,xObj,yObj,False)
        if tmp !=None: sim.obj = tmp
        sim.debug = sim.debug+"   O: ("+bnerString(xObj)+", "+bnerString(yObj)+")="+format(sim.obj,'.4f')+"\n"
    else:
        sim.debug = sim.debug+"   O: ("+xObj.item+", "+yObj.item+")=0 (skipped)"+"\n"

    # estimate similarity
    #if (sim.subj>0.2) and (sim.pred>0.2) and (sim.obj>0.5):
    sim.score1 = (sim.subj*0.2)+(sim.pred*0.4)+(sim.obj*0.4)
    #sim.score1 = (sim.pred*0.4)+(sim.obj*0.6)

    #else:
    #   sim.score1= 0

    sim.debug = "   score1: "+format(sim.score1,'.4f')+"\n"+sim.debug

    return sim


########################################################################################################
def stupidMethod(x,y):
    rez = 0
    if not(x.hasEmptySubj) and not(y.hasEmptySubj):
       if (x.subj == y.subj): rez +=1
       if (x.subjText == y.subjText): rez+=1 
    if not(x.hasEmptyObj) and not(y.hasEmptyObj):
       if (x.obj == y.obj): rez +=1
       if (x.objText == y.objText): rez +=1
    if (x.pred == y.pred): rez +=1
    if (x.predText == y.predText): rez +=1

    return rez/6

########################################################################################################

# if a triple is compared to a set of other triples
class S2T: pass
# c - number of triples
# m - maximum score
# mT - maximum triplet
# t - total score
# a - average

def getS2T():
    s2t = S2T()
    s2t.c = 0
    s2t.m = 0
    s2t.t = 0
    s2t.a = 0
    return s2t

def addS2T(s2t,val):
    s2t.c +=1
    s2t.t = s2t.t + val
    if (val>s2t.m):
       s2t.m = val
    return s2t

def addS2T(s2t,val):
    s2t.c +=1
    s2t.t = s2t.t + val
    if (val>s2t.m):
       s2t.m = val
    return s2t

def addS2Tv2(s2t,val,lim):
   if (val > lim) :
      s2t.c +=1
      s2t.t = s2t.t + val
      if (val>s2t.m):
         s2t.m = val
      return s2t

def addS2Tv3(s2t,val,x3,simRez):
    s2t.c +=1
    s2t.t = s2t.t + val
    if (val>s2t.m):
       s2t.m = val
       s2t.x3 = x3
       s2t.simRez = simRez
    return s2t


def avgS2T(s2t):
    if s2t.c != 0:
       s2t.a = s2t.t/s2t.c
    return s2t.a

def s2tString(s2t):
    return "max: "+format(s2t.m,'.4f')+" avg: "+format(avgS2T(s2t),'.4f')+" count: "+str(s2t.c)

def s2tHeader(pref):
    return pref+"Max!"+pref+"Avg!"

def s2tString1(s2t):
    maxStr = format(s2t.m,'.4f')+"!"
    avgStr = format(avgS2T(s2t),'.4f')+"!"
    return maxStr+avgStr


###################################################################################################

# estimate template and document keeping semantic aspects (intent, action ...)
class S2S: pass
# intent (S2T)
# action (S2T)
# tech (S2T)
# env (S2T)
# avg - average of average (float)
# max = avetage of maximums (float)

def getS2S():
    s2s = S2S()
    s2s.intent = getS2T()
    s2s.action = getS2T()
    s2s.tech = getS2T()
    return s2s

def addS2S(s2s,typ,score):

    if typ == 'intent' :
       s2s.intent = addS2T(s2s.intent,score)
    if typ == 'action' :
       s2s.action = addS2T(s2s.action,score)
    if typ == 'tech' :
       s2s.tech = addS2T(s2s.tech,score)


    return s2s

def calcS2S(s2s):
    avgS2T(s2s.intent)
    avgS2T(s2s.action)
    avgS2T(s2s.tech)
    divAvg = 3
    if ((s2s.intent.a == 0) or (s2s.action.a == 0) or (s2s.tech.a == 0)): divAvg = 2
    divMax = 3
    if ((s2s.intent.m == 0) or (s2s.action.m == 0) or (s2s.tech.m == 0)): divMax = 2
    s2s.avg = (s2s.intent.a+s2s.action.a+s2s.tech.a)/divAvg
    s2s.max= (s2s.intent.m+s2s.action.m+s2s.tech.m)/divMax

    return s2s

def s2sHeader(pref):
    return pref+"Max!"+pref+"Avg!"+pref+"IntentMax!"+pref+"IntentAvg!"+pref+"ActionMax!"+pref+"ActionAvg!"+pref+"TechMax!"+pref+"TechAvg!"

def s2sString(s2s):
    avgStr = format(s2s.avg,'.4f')+"!"
    maxStr = format(s2s.max,'.4f')+"!"
    intentStr = format(s2s.intent.m,'.4f')+"!"+format(s2s.intent.a,'.4f')+"!"
    actionStr = format(s2s.action.m,'.4f')+"!"+format(s2s.action.a,'.4f')+"!"
    techStr = format(s2s.tech.m,'.4f')+"!"+format(s2s.tech.a,'.4f')+"!"

    return maxStr+avgStr+intentStr+actionStr+techStr


