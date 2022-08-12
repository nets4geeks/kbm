
#
# set of catched terms used in security enumerations 
#

NERs = {
  'Term_WindowsHostsFile': 'C:\Windows\System32\Drivers\etc\hosts',
  'Term_LinuxHostsFile': '/etc/hosts'
}

PUNKT = ('.',',',':',';','?','!')

def replace(sent):
    sent1 = []
    # remove punctuation at end of each word
    for item in sent.lower().split():
        if item.endswith(PUNKT):
           item = item[:-1]
        sent1.append(item)
    # iterate over NERs to find and replace by keywords
    for idn in NERs:
        if NERs[idn].lower() in sent1:
           sent = sent.replace(NERs[idn],idn)
    return sent

# !!! use lower() to check 
#def getNER(token):
#    for idn in NERs:
#        if NERs[idn].lower() == token.lower():
#           return idn
#    return None



