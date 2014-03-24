#!/usr/bin/env python

from sys import stderr, version
import bz2
import gzip
import copy
import io

class GizaSentenceParser(object):
    def __init__(self, sourceline, targetline, index):
        self.index = index
        self.alignment = []
        if sourceline:
            self.source = self._parsesource(sourceline.strip())
        else:
            self.source = []
        self.target = targetline.strip().split(' ')

    def _parsesource(self, line):
        cleanline = ""

        inalignment = False
        begin = 0
        sourceindex = 0

        for i in range(0,len(line)):
            if line[i] == ' ' or i == len(line) - 1:
                if i == len(line) - 1:
                    offset = 1
                else:
                    offset = 0

                word = line[begin:i+offset]
                if word == '})':
                    inalignment = False
                    begin = i + 1
                    continue
                elif word == "({":
                    inalignment = True
                    begin = i + 1
                    continue
                if word.strip() and word != 'NULL':
                    if not inalignment:
                        sourceindex += 1
                        if cleanline: cleanline += " "
                        cleanline += word
                    else:
                        targetindex = int(word)
                        self.alignment.append( (sourceindex-1, targetindex-1) )
                begin = i + 1

        return cleanline.split(' ')

    def __call__(self):
        sentence_pair = (tuple(self.source), tuple(self.target))
        alignment_val = set((sindex, tindex) for sindex, tindex in sorted(self.alignment) if sindex >= 0)
            
        return (sentence_pair, sorted(alignment_val))


    def getalignedtarget(self, index):
        targetindices = []
        target = None
        foundindex = -1
        for sourceindex, targetindex in self.alignment:
            if sourceindex == index:
                targetindices.append(targetindex)
        if len(targetindices) > 1:
            consecutive = True
            for i in range(1,len(targetindices)):
                if abs(targetindices[i] - targetindices[i-1]) != 1:
                    consecutive  = False
                    break
            if consecutive:
                foundindex = (min(targetindices), max(targetindices))
                target = ' '.join(self.target[min(targetindices):max(targetindices)+1])
        elif targetindices:
            foundindex = targetindices[0]
            target = self.target[foundindex]

        return target, foundindex

class GizaA3Reader(object):
    def __init__(self, filename, encoding=None):
        if filename.split(".")[-1] == "bz2":
            self.f = bz2.BZ2File(filename,'r')
        elif filename.split(".")[-1] == "gz":
            self.f = gzip.GzipFile(filename,'r')
        else:
            self.f = io.open(filename,'r', -1, encoding)
        self.nextlinebuffer = None


    def __iter__(self):
        self.f.seek(0)
        nextlinebuffer = (next(self.f))
        sentenceindex = 0

        done = False
        while not done:
            sentenceindex += 1
            line = nextlinebuffer
            if line[0] != '#':
                raise Exception("Error parsing GIZA++ Alignment at sentence " +  str(sentenceindex))

            targetline = (next(self.f))
            sourceline = (next(self.f))
            
            print sourceline, targetline

            yield GizaSentenceParser(sourceline, targetline, sentenceindex)

            try:
                nextlinebuffer = (next(self.f))
            except StopIteration:
                done = True


    def __del__(self):
        if self.f: self.f.close()
