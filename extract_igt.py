#@author Daniel Chen, Tiffany Blanchet

import docx
import re
import re
import os
import pandas as pd
import csv
import random

def extract_igt(filename) :
    '''
    @author Tiffany Blanchet

    Identifies 4-line spans from DOCX and writes them into TXT format

    @input {str} filename = filename with DOCX extension
    '''
    
    doc = docx.Document(filename)
    paragraphs = []
    for para in doc.paragraphs:
        paragraphs.append(para.text)
    full_text = '\n'.join(paragraphs)

    ####
    f = open("IGT.txt","x")
    f = open("IGT.txt","w",encoding="UTF-8")
    f.write(full_text)
    f.close()
    ####

    #Strip from whitespace
    f = open("IGT.txt","r",encoding="UTF-8")
    with open("IGT.txt","r",encoding="UTF-8") as r, open("new_IGT.txt","w", encoding="UTF-8") as o:
        for line in r:
            if line.strip():
                o.write(line)
    o.close()


    f = open("new_IGT.txt","r",encoding="UTF-8")
    IGT = f.read()
    IGTs=(re.findall(r"\(\d+\)\t+.*\n.*\n\t+.*\n\t.*\n",IGT)) #this is each group of 4
    with open("IGT_1.txt","w",encoding="UTF-8") as t:
        for x in IGTs:
            t.write(x)
    t.close()
    f.close()
            
def strip_igt_file(filename) :
    '''
    @author Daniel Chen

    Converts 4-line format from input TXT produced by extract_igt...
    ...into dictionary format:

    {
        TdVZ Text (Original) :  Original TdVZ Morphological Word,
        Segmentation         :  Morphological Parse (+ : components of a morphological compound, - : affix, = : clitic),
        Gloss                :  Interlinear Gloss,
        EN Translation       :  English Translation
    }

    Access Dictionary as: 

    sc_lexicon["Segmentation"] -> returns canonical segmentation (underlying morphemes)

    @return {list of lists} new_chunks = each row of dictionary information for 1 morphological word,
                                        to be passed in as input to write_csv
    @return {dict} sc_lexicon = surface -> canonical lookup dictionary
    @return {dict} cs_lexicon = canonical -> surface lookup dictionary 

    '''
    with open(filename, "r") as reader:
        chunks = []
        lines = reader.readlines()

        i = 0
        while i < len(lines) :
            #print('-------------------------')
            #print("Next round of while-loop:")
            line = lines[i] #current line
            #print(line)
            init_cond1 = line[0] in "abcdefghijklmnopqrstuvwxyz" and line[1] == "."
            init_cond2 = line[0] == "("

            local_keys = 1

            curr_chunk = []
            if init_cond1 or init_cond2 :
                stripped = line.split()
                zpt = stripped[1:]
                curr_chunk.append(zpt)
                local_keys += 1

                complete = False
                while not complete :
                    i += 1
                    if i == len(lines) :
                        break

                    line = lines[i]

                    sub_cond1 = line[0] in "abcdefghijklmnopqrstuvwxyz" and line[1] == "."
                    sub_cond2 = line[0] == "("

                    if sub_cond1 or sub_cond2 :
                        complete = True
                    else :
                        if local_keys < 3 :
                            local_keys += 1
                            zpt = line.split()
                            curr_chunk.append(zpt)

                        '''
                        if local_keys < 3 :
                            key_idx += 1
                            key = "Line " + str(key_idx)
                            chunk[key] = zpt
                        '''
            chunks.append(curr_chunk)
        
        new_chunks = []; sc_lexicon = {}; cs_lexicon = {} #surface -> canonical, canonical -> surface
        for chunk in chunks :
            first = chunk[0]; second = chunk[1]
            #Get rid of "a." and "b." artifacts
            for f in first :
                if f[0] in "abcdefghijklmnopqrstuvwxyz" and f[1] == "." :
                    first.remove(f)

            if len(first) == len(second) :
                for i in range(len(first)) :
                    new_chunks.append([first[i], second[i]])
                    if sc_lexicon.get(first[i]) != None :
                        sc_lexicon[first[i]].append(second[i])
                    else :
                        sc_lexicon[first[i]] = [second[i]]
                    if cs_lexicon.get(second[i]) != None :
                        cs_lexicon[second[i]].append(first[i])
                    else :
                        cs_lexicon[second[i]] = [first[i]]

        #Get rid of duplicates
        for key, val in sc_lexicon.items() :
            sc_lexicon[key] = set(val)
        for key, val in cs_lexicon.items() :
            cs_lexicon[key] = set(val)

        return new_chunks, sc_lexicon, cs_lexicon

def write_csv(chunks) :
    '''
    @author Daniel Chen

    Writes a CSV file containing dictionary lookup format for each morphological word in TdVZ corpus

    @input {list of lists} chunks = each row of dictionary information for 1 morphological word
    '''
    with open("igt_train.csv", "w", encoding="UTF-8") as output :
        writer = csv.writer(output)
        #Write header row.
        writer.writerow(["Example #", "TTL_ZPT Text (Original)", "Segmentation"])

        i = 1
        for chunk in chunks :
            a = re.sub("[\[\](RC)]", "", chunk[0])
            b = re.sub("[\[\](RC)]", "", chunk[1])
            if "Laryngeal" in a or "Displacement" in a :
                continue
            writer.writerow([f"Example {i}", a, b])
            i += 1

def main() :
    #Uncomment Lines 176-177 to extract IGT from a new file.
    #file = "Dissertation-Draft-Ambrocio-Gutierrez-2021.docx"
    #extract_igt(file)

    chunks, sc_lexicon, cs_lexicon = strip_igt_file("IGT_1.txt") #loaded from output of extract_igt

    print("\nSurface -> Canonical Lexicon: ")
    i = 0
    for key, val in sc_lexicon.items() :
        key = str(key); val = str(val)
        if i == 100 :
            break
        print("{:11s}{:3s}{:11s}".format(key, ":", val))
        i += 1

    print("\nCanonical -> Surface Lexicon: ")
    j = 0
    for key, val in cs_lexicon.items() :
        key = str(key); val = str(val)
        if j == 100 :
            break
        print("{:11s}{:3s}{:11s}".format(key, ":", val))
        j += 1
    print('\n')

    #Uncomment Line 201 to produce new output CSV (Current form: igt_train.csv)
    #write_csv(chunks)

main()