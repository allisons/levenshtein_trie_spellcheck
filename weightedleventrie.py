#!/usr/local/bin/python
# Copyright (c) 2016 Allison Sliter
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# viterbi.py: simple Viterbi decoding, with protections against underflow


import fst
from collections import defaultdict

file = "words.syms.txt"
words = list()

with open(file, 'r') as l:
    words = l.read().split()
words.sort()
mid = len(words)/2
words = words[mid:]
clean = list()
for w in words:
    if len(w) > 1:
        clean.append(w)
words = clean
        
    
def fstbuild(words):
    trie = fst.Transducer()

    letter_syms = fst.read_symbols("ascii.syms.bin")
    trie.isyms = letter_syms
    trie.osyms = letter_syms

    def bs(s):
        letter_syms = fst.read_symbols("ascii.syms.bin")
        return letter_syms[s]


    biggest = 0

    for w in words:
        p = 0
        c = 0
        trie.add_arc(p, biggest+1, w[c], "<epsilon>", 0) 
        p = biggest+1
        c += 1
        while (c < len(w)-1):
            trie.add_arc(p, p+1, w[c], "<epsilon>", 0)
            p+=1
            c+=1        
        trie.add_arc(p, p+1, w[c], w, 0)
        p +=1
        biggest = max(p, biggest)
        last_state = trie[biggest] 
        last_state.final = True
        

    det_trie = trie.determinize()
    det_trie.arc_sort_input()
    det_trie.remove_epsilon()
    
    
    return det_trie

def suffixreturn(trie, prefix):
    p = 0
    s = 0
    while s < len(prefix):
        arc_list = list(trie[p].arcs)
        arc_tup = list()
        for a in arc_list:
            tup = [trie[p], a.nextstate, trie.isyms.find(a.ilabel)]
            arc_tup.append(tup)
        for t in arc_tup:
            if t[2] == prefix[s]:
                p = t[1]
        s += 1
    if p == 0:
        return -1
    return p

def returnsuffix(trie, node, suffixes):
    if node == -1:
        return list()
    elif not list(trie[node].arcs):
        return suffixes 
    else:
        arcs_list = list(trie[node].arcs)
        for a in arcs_list:
            if not list(trie[a.nextstate].arcs):
                word = str(trie.osyms.find(a.olabel))
                suffixes.append(word)
            else:
                returnsuffix(trie, a.nextstate, suffixes)

    return suffixes

def levenshtein(w, editdst):
    
    wts = keyweights()

    trie = fst.Transducer()

    letter_syms = fst.read_symbols("ascii.syms.bin")
    trie.isyms = letter_syms
    trie.osyms = letter_syms
    letttup = list(letter_syms.items())
    letters = list()
    for let in letttup:
        letters.append(let[0])


    class StateCounter(object):
        def __init__(self):
            self.set = {}
            self.count = -1
        
        def __contains__(self, obj):
            return obj in self.set
 
        def __getitem__(self, obj):
            if not obj in self.set:
                self.count += 1
                self.set[obj] = self.count
            return self.set[obj]

    states = StateCounter()




    for x in range(0,len(w)):
        for y in range(0, editdst+1):        
            trie.add_arc(states[str(x)+"^"+str(y)], states[str(x+1)+"^"+str(y)], w[x], w[x], 0)# char in word
            if not y == editdst:
                trie.add_arc(states[str(x)+"^"+str(y)], states[str(x+1)+"^"+str(y+1)], "<epsilon>", "<epsilon>", 1.5)# deletion
                for i in letters:
                    trie.add_arc(states[str(x)+"^"+str(y)], states[str(x+1)+"^"+str(y+1)], i, i, wts[w[x], i])# substitution
                    trie.add_arc(states[str(x)+"^"+str(y)], states[str(x)+"^"+str(y+1)], i, i, wts[w[x], i])# insertion

    for y in range(0, editdst+1):
        trie[states[str(len(w))+"^"+str(y)]].final = True
    

    
    
    trie.remove_epsilon()
    trie.arc_sort_input()
   




    return trie
def other_levenshtein(w, editdst):
    
    wts = freqweights()

    trie = fst.Transducer()

    letter_syms = fst.read_symbols("ascii.syms.bin")
    trie.isyms = letter_syms
    trie.osyms = letter_syms
    letttup = list(letter_syms.items())
    letters = list()
    for let in letttup:
        letters.append(let[0])


    class StateCounter(object):
        def __init__(self):
            self.set = {}
            self.count = -1
        
        def __contains__(self, obj):
            return obj in self.set
 
        def __getitem__(self, obj):
            if not obj in self.set:
                self.count += 1
                self.set[obj] = self.count
            return self.set[obj]

    states = StateCounter()




    for x in range(0,len(w)):
        for y in range(0, editdst+1):        
            trie.add_arc(states[str(x)+"^"+str(y)], states[str(x+1)+"^"+str(y)], w[x], w[x], 0)# char in word
            if not y == editdst:
                trie.add_arc(states[str(x)+"^"+str(y)], states[str(x+1)+"^"+str(y+1)], "<epsilon>", "<epsilon>", 1.5)# deletion
                for i in letters:
                    trie.add_arc(states[str(x)+"^"+str(y)], states[str(x+1)+"^"+str(y+1)], i, i, 1/wts[i])# substitution
                    trie.add_arc(states[str(x)+"^"+str(y)], states[str(x)+"^"+str(y+1)], i, i, 1/wts[i])# insertion

    for y in range(0, editdst+1):
        trie[states[str(len(w))+"^"+str(y)]].final = True
    

    
    
    trie.remove_epsilon()
    trie.arc_sort_input()
   




    return trie


def keyweights():
    top = "qwertyuiop"
    middle = "asdfghjkl;"
    bottom = "zxcvbnm,./"
    
    keyboard = [top, middle, bottom]
    whole = list()
    for r in keyboard:
        n = list()
        for i in r:
            n.append(i)
        whole.append(n)
    weights = defaultdict(lambda: 1.)
    for y in range(0, len(whole)):
        for x in range(0, len(whole[y])):
            for q in range(0, len(whole)):
                for p in range(0, len(whole[q])):
                    weights[whole[y][x], whole[q][p]] = abs(((p-x) + (q-y))/3.42)    
    return weights

def freqweights():
    from collections import defaultdict

    file = "letterfreqtable.txt"

    with open(file) as f:
        total = f.read().split()


    weights = defaultdict(lambda: 1.)

    c = 2

    while c < len(total):
        weights[total[c]] = float(total[c+1])
        c = c+4
    
    
    return weights
        

#dictionary = fstbuild(words)
hands1 = levenshtein("hands", 2)
hands2 = other_levenshtein("hands", 2)
#dictionary.write("dict.fst")
hands1.write("keyweightedhands.fst")
hands2.write("freqweightedhands.fst")

bearclaw1 = levenshtein("bearclaw", 2)
bearclaw2 = levenshtein("bearclaw", 2)
bearclaw1.write("keyweightedbear.fst")
bearclaw2.write("freqeightedbear.fst")

