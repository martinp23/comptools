#!/usr/bin/env python3

import numpy as np 
import tarfile, re, sys

def getLCindex(line):
    
    # get index (x, y, or z) of a given value in order to construct ...
    # the response tensor
    m = re.search('spin: ([A-Z]{1})',line)
    a = m.group(1)
    
    if a == 'X':
        i = 0
    elif a == 'Y': 
        i = 1
    elif a == 'Z':
        i = 2
    return i


def getFreqs(jobname):
    fin = open(jobname+'.dal','r')

    finlines = fin.readlines()
    fin.close()

    ss = 0
    for i, line in enumerate(finlines):
        if "BFREQ" in line:
            ss = i
            
    nfreq = int(finlines[ss+1])
    freqs = finlines[ss+2].split(' ')
    freqs =[float(i) for i in freqs]

    return nfreq,freqs

def readResults(jobname):
    filename = jobname + '.tar.gz'
    t = tarfile.open(filename,'r')
    fout = t.extractfile('RESULTS.RSP')
    foutlines = fout.readlines()
    foutlines = [i.decode("utf-8") for i in foutlines]
    fout.close()
    t.close()
    return foutlines

def genLeviCivita():
    # stackoverlow 20908754
    # generate Levi-Civita tensor
    eijk = np.zeros((3, 3, 3))
    eijk[0, 1, 2] = eijk[1, 2, 0] = eijk[2, 0, 1] = 1
    eijk[0, 2, 1] = eijk[2, 1, 0] = eijk[1, 0, 2] = -1    
    return eijk

def getC(N=1):
    c = 137 #au
    e = 1 # au
    me = 1 # au
    e0 = 1/(4*np.pi) # au
    #N = 9.89 * 10**-4 # au, for benzene

    C = (1/(6*c))*((2*np.pi*N)/(4*np.pi*e0))*(e/(2*me)) # in au
    return C

def getV_in_au_from_calc_res(res,freq,N=1):
    C = getC(N)
    return res*freq*C

def conv_Vau_to_Vrad(Vau):
    return Vau * 8.039624 * 10**4

def conv_Vrad_to_Vdeg(Vrad):
    return Vrad * (360/(2*np.pi))

def conv_freq_au_to_nm(freq):
    wn = freq * 219474.6305 # nb freqs were in au
    wl = 10**7/wn
    return wl

def main(jobname,N=1):
    nfreq,freqs = getFreqs(jobname)
    foutlines = readResults(jobname)

    outlines = []
    for i,line in enumerate(foutlines):
        if "@ Quadratic response function value in a.u. for" in line:
            outlines.append(i)

    #prepare list of numpy 3x3x3 arrays to describe response tensors for
    # each frequency
    results = []
    for i in range(nfreq):
        results.append(np.zeros((3,3,3)))   

    # read actual data from results file linelist and populate results 
    # tensor(s)
    for l in outlines:
        aline = l+1
        bline = l+2
        cline = l+3
        
        resline = l+5
        
        ai = getLCindex(foutlines[aline])
        bi = getLCindex(foutlines[bline])
        ci = getLCindex(foutlines[cline])
        rx = "omega C, QR value :\s*([-+]?\d+(\.\d+)?)\s*([-+]?\d+(\.\d+)?)\s*([-+]?\d+(\.\d+)?)$"
        m = re.search(rx,foutlines[resline])
        freq = m.group(1)
        fidx = freqs.index(float(freq))
        res = m.group(5)

        res=float(res)
        
        results[fidx][ai,bi,ci] = res    

    # now do arithmetic
    eijk = genLeviCivita()

    summedres = []
    # do einstein summation and Levi-Civita tensor application to get scalar
    # result

    for r in results:
        summedres.append(np.einsum('ijk,ijk->',eijk,r))

    #freqs = np.array(freqs)
    # seems based on lit that this should be minus the value from calc'n
    summedres = -np.array(summedres)

    for i,freq in enumerate(freqs):

        rawVau = getV_in_au_from_calc_res(summedres[i],freq,N)
        Vrad = conv_Vau_to_Vrad(rawVau)
        Vdeg = conv_Vrad_to_Vdeg(Vrad)

        print('Raw V: {} au'.format(rawVau))
        print('V = {} deg/Tm'.format(Vdeg))



if __name__ == '__main__':
    if len(sys.argv) > 2:
        main(sys.argv[1],float(sys.argv[2]))
    else:
        main(sys.argv[1])


