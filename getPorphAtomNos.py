#!/usr/bin/env python3

import numpy as np
import scipy as sp
from scipy import spatial
import cclib
from collections import defaultdict
import sys
import argparse


def getNeighbours(startatom,distmat,threshold=1.8):
    nn=[]
    for ik,x in enumerate(distmat[:,startatom]):
        #print(x)
        if x < threshold:
            if ik != startatom:
                nn.append(ik)
    return nn

def printExcelSums(app,col='D'):
    for line in app:
        line = [i+1 for i in line]
        line = [str(i) for i in line]
        joiner = ','+col
        print('=SUM('+col+joiner.join(line)+')')

def readChargeSpinMulliken(filename):
    #for g16 output and g09
    # returns two dicts: one for charges, one for spins
    # dicts contain type of pop analysis. Implemented so far:
    # 1. mulliken
    # 2. mullikensummed ::: note, here row numbers won't necessarily coincide
    #                       with atom numbers. You would need to assign these
    #                       spins/charges based on a generated list of non-H
    #                       atoms.
    f = open(filename,'r')

    lines = f.read()
    iLastMull = lines.rfind("Mulliken charges and spin densities:")
    iEndMull = lines.rfind('Electronic spatial extent (au):')
    mullines = lines[iLastMull:iEndMull-2]

    mullines = mullines.splitlines()

    charges = defaultdict(list)
    spins = defaultdict(list)

    key = ''
    for i,line in enumerate(mullines):
        if line[0:37] == "Mulliken charges and spin densities:":
            key = 'mulliken'
        if line[1:76] == "Mulliken charges and spin densities with hydrogens summed into heavy atoms:":
            key = 'mullikensummed'

        lineparts = line.split()
        if lineparts[0].isdigit() and len(lineparts) == 4:
            charges[key].append(float(lineparts[2]))
            spins[key].append(float(lineparts[3]))
    return charges,spins


def getAtomNos(filename,Mno):
    data = cclib.io.ccread(filename)


    xyzcoords = data.atomcoords[-1]
    atoms = data.atomnos
    charges,spins = readChargeSpinMulliken(filename)

    #Mno = 30 # Zn
    numM = np.count_nonzero(atoms == Mno)
    atomsPerUnit = len(atoms)/numM

    distmat = sp.spatial.distance.pdist(np.array(xyzcoords))
    distmat = sp.spatial.distance.squareform(distmat)

    ij = 0
    app = [[] for i in range(numM)]
    for ii,atom in enumerate(atoms):
        if atom == 30:
            neighbours = getNeighbours(ii,distmat,3)
            app[ij].append(ii)
            app[ij].extend(neighbours)
                
            for aa in app[ij]:
                
                neighbours = getNeighbours(aa,distmat)

                newitems = np.setdiff1d(neighbours,app[ij])
                if len(newitems) > 1:
                    app[ij].extend(list(newitems))
                else:
                    # does the atom have more than 2 neighbours? if so it's not a
                    # c#c bond so (so is prob a CH)
                    if len(neighbours) > 2:
                        app[ij].extend(list(newitems))
                        
                        # now we need to know if the "parent" atom had just two 
                        # neighbours or more. If it had just two, then we are at 
                        # the "central" butadiyne carbon now so we stop. Otherwise
                        # we add our new atom
                    elif len(neighbours) == 2:
                        # get "previously known" atom number

                        oldatom = np.setdiff1d(neighbours,newitems)

                        # find out how many neighbours it has
                        oldneighbours = getNeighbours(oldatom,distmat)

                        if len(oldneighbours) > 2:
                            app[ij].extend(list(newitems))
                        else:
                            pass
                            #print("Reached butadiyne")
                        

            ij = ij+1
    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find atom numbers for porphyrins in butadiyne-linked porphyrin oligomers")
    parser.add_argument('filename', type=str, help='Gaussian logfile to read')
    parser.add_argument('--metal',metavar='m',type=int,help='atom number of central metal atom',default=30)
    parser.add_argument('--excel', dest='printexcel', action='store_const', const=True, default=False, help='Print excel sum string')
    parser.add_argument('--sumspin', dest='sumspin', action='store_const', const=True, default=False, help='Sum Mulliken spins')
    parser.add_argument('--sumcharge', dest='sumcharge', action='store_const', const=True, default=False, help='Sum Mulliken charges')
    args = parser.parse_args()

    res = getAtomNos(args.filename,args.metal)

    print(res)

    if args.printexcel:
        printExcelSums(res)
    

    if args.sumspin or args.sumcharge:
       charges,spins = readChargeSpinMulliken(args.filename)

    if args.sumspin:
        spintot = []
        for i,p in enumerate(res):
            s = 0
            for ano in p:
                s = s+spins['mulliken'][ano]
            spintot.append(s) 
        spintot = [format(a, "10.5f") for a in spintot]      
        print('Spin per porphyrin:' + ', '.join(spintot))

    if args.sumcharge:
        chargetot = []
        for i,p in enumerate(res):
            s = 0
            for ano in p:
                s = s+charges['mulliken'][ano]
            chargetot.append(s)   
        chargetot = [format(a, "10.5f") for a in chargetot]      
        print('Charge per porphyrin:' + ', '.join(chargetot))
