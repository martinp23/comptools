#!/usr/bin/env python3
# Avogadro v1 tends to split coordinates of the same atom-type 
# into several different atom-type blocks, when generating Dalton output.

# This seemed to screw up something in Dalton2015, maybe to do with
# symmetry. The solution for me was to make the number of atom types 
# correct

# takes a filename (a Dalton formatted molecule file) as input

import re, sys
import periodictable as pt


def main(filename):
    fin = open(filename,'r')
    lines = fin.readlines()
    reslines = []

    for i in lines[0:4]:
        reslines.append(i)


    atoms = []
    atomcounts = []

    coordlines = []
    for line in lines[5:]:
        rx = "^([A-Z][a-z]?)\s+[+-]?\d+\.\d+\s+"
        m = re.match(rx,line)
        if m:
            coordlines.append(line)
            if m.group(1) not in atoms:
                atoms.append(m.group(1))
                atomcounts.append(0)
            
            ii=atoms.index(m.group(1))
            atomcounts[ii] += 1

    reslines.append('Atomtypes={} Angstrom\n'.format(len(atoms)))

    for i,element in enumerate(atoms):
        
        charge = pt.elements.symbol(element).number
        
        reslines.append("Charge={}.0 Atoms={}\n".format(charge,atomcounts[i]))
        for line in coordlines:
            if line[0] is element:
                reslines.append(line)
        
    #outstr = '\n'.join(reslines)

    fout = open(filename,'w')
    fout.writelines(reslines)
    fout.close()


if __name__ == '__main__':
        main(sys.argv[1])
