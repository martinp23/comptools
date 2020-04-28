#!/usr/bin/env python3
import sys
# coding: utf-8

# In[ ]:

import tkinter as tk
from tkinter import filedialog
import re

# diaog to get file path
#root = tk.Tk()
#root.withdraw()
#file_path = filedialog.askopenfilename()

#file_path = u'C:/Users/martinp23/Desktop/mpc092-b3lyp-12cat-4a.log'
file_path = sys.argv[1]

# In[ ]:

# parse whole file into memory (yes naughty)
with open(file_path,'r') as ff:
    logdata = ff.readlines()


# In[ ]:

# find line with l9999: the archive section
index = [ii for ii,x in enumerate(logdata) if 'l9999' in x]

archiveSection = ' '.join(logdata[index[0]:]).split('\\')

atomlist =[]
for line in archiveSection[16:]:
    if line=='':
        break
    aa= re.split('[\n ]',line)
    aa = ''.join([item for item in aa if item])
    aa= re.split('[,]',aa)
    ell = [0,2,3,4]
    atomlist.append(aa)

# archivesection format:
# 0:Enter link
# 1: ?
# 2: host
# 3: calculation type (SP, OPT, etc)
# 4: Functional/method
# 5: Basis
# 6: Formula
# 7: root
# 8: date
# 9,10: blank
# 11: routecard
# 12 blank
# 13: title
# 14: blank
# 15: multiplicity
# 16..n: Atoms
# n: blank
# n+1: version
# n+2: HF energy
# n+3: RMSD
# n+4: dipole
# n+5: quadrupole
# n+6: symm PG=C01 [X(C144H60N24Zn6)]'
# useless stuff and the quote


# In[ ]:

# find line indices which contain 'Isotropic' -- ie shielding data
indices =[ii for ii,x in enumerate(logdata) if "Isotropic" in x]
shieldings=[]
# for a line with 'Isotropic' in it, read ahead 4 lines into a list of lists
for ii in indices:
#    if "Bq" in logdata[ii]:
        
        # the join is to put all 4 lines (list elements) into one. The split to remove whitespace and make list
        rawshield = ''.join(logdata[ii:ii+4]).replace('=',' ').split()

        atomCoords = atomlist[int(rawshield[0])-1]
        # these are the elements of each list (in the rawshield list of lists) that we want, remembering we split() in the last step
        ell = [3,5,7,9,11,13,15,17,19,21,23]
        el2 = [0,2,3,4]
        # so for each of those elements in ell, join (to make a csv line)
        shieldings.append(','.join([rawshield[0],','.join([atomCoords[i] for i in el2]),','.join([rawshield[i] for i in ell])]))



# In[ ]:

# headings for csv file in csv format
headings = 'Num,Type,X,Y,Z,Isotropic,Anisotropic,XX,XY,XZ,YX,YY,YZ,ZX,ZY,ZZ'

# prepare outdata string
outdata = headings + '\n' + '\n'.join(shieldings)

#and write out the file
with open(file_path+'.csv','w') as fo:
    fo.writelines(outdata)

