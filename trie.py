#!/usr/local/bin/python
# Copyright (c) 2016 Allison Sliter
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the 'Software'), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# viterbi.py: simple Viterbi decoding, with protections against underflow


import fst
import argparse

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
        trie.add_arc(p, biggest+1, w[c], w[c], 0) 
        p = biggest+1
        c += 1
        while (c < len(w)-1):
            trie.add_arc(p, p+1, w[c], w[c], 0)
            p+=1
            c+=1        
        trie.add_arc(p, p+1, w[c], w, 0)
        p +=1
        biggest = max(p, biggest)
        last_state = trie[biggest] 
        last_state.final = True
        

    det_trie = trie.determinize()
    det_trie.arc_sort_input()
    
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
    
print "Loading Trie, please wait..."        
trie = fstbuild(words)
wordlist = returnsuffix(trie, suffixreturn(trie, "p"), list())
trie.write("part1.fst")



quit = True
while(quit):
    mode = int(raw_input("Would you like to provide your own dictionary or use mine? \n Type 1 for mine, \n Type 2 to provide your own\n"))

    if not mode == 1 and not mode == 2:
        print "That's not a valid input, you wanna try it again, wiseguy?"
        continue
    elif(mode == 1):
        prefix = raw_input("Please enter the prefix you're looking up: ")        
        words = returnsuffix(trie, suffixreturn(trie, prefix), list())
        if not words:
            print "No entries for that prefix:", prefix
        else:
            print words, "Matches", len(words)
    else:
        file = raw_input("Please provide a file name where your dictionary can be found, each word should be separated by whitespace: ")
        with open(file, 'r') as f:
            dictlist = f.read().split()
        your_trie = fstbuild(dictlist)
        prefix = raw_input("Please enter the prefix you're looking up ")
        words= returnsuffix(your_trie, suffixreturn(your_trie, prefix), list())
        if len(words) == 0:
            print "We don't have anything in the dictionary with that prefix"
        else:
            print words, "Matches", len(words)
    again = str(raw_input("Type q to quit, any other key to start over "))
    if again == "q" or again == "Q":
        quit = False
