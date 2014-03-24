#!/usr/bin/env python

import sys
import bz2
import gzip
import copy
import io

class GizaSentenceAlignment(object):

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


    def intersect(self,other):
        if other.target != self.source:
            #print("GizaSentenceAlignment.intersect(): Mismatch between self.source and other.target: " + repr(self.source) + " -- vs -- " + repr(other.target),file=stderr)
            return None

        intersection = copy.copy(self)
        intersection.alignment = []

        for sourceindex, targetindex in self.alignment:
            for targetindex2, sourceindex2 in other.alignment:
                if targetindex2 == targetindex and sourceindex2 == sourceindex:
                    intersection.alignment.append( (sourceindex, targetindex) )

        return intersection

    def __repr__(self):
        s = " ".join(self.source)+ " ||| "
        s += " ".join(self.target) + " ||| "
        for S,T in sorted(self.alignment):
            s += self.source[S] + "->" + self.target[T] + " ; "
        return s


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

class GizaModel(object):
    def __init__(self, filename, encoding= 'utf-8'):
        if filename.split(".")[-1] == "bz2":
            self.f = bz2.BZ2File(filename,'r')
        elif filename.split(".")[-1] == "gz":
            self.f = gzip.GzipFile(filename,'r')
        else:
            self.f = io.open(filename,'r',encoding)
        self.nextlinebuffer = None


    def __iter__(self):
        self.f.seek(0)
        nextlinebuffer = u(next(self.f))
        sentenceindex = 0

        done = False
        while not done:
            sentenceindex += 1
            line = nextlinebuffer
            if line[0] != '#':
                raise Exception("Error parsing GIZA++ Alignment at sentence " +  str(sentenceindex) + ", expected new fragment, found: " + repr(line))

            targetline = u(next(self.f))
            sourceline = u(next(self.f))

            yield GizaSentenceAlignment(sourceline, targetline, sentenceindex)

            try:
                nextlinebuffer = u(next(self.f))
            except StopIteration:
                done = True


    def __del__(self):
        if self.f: self.f.close()
