"""
Methods for fitting a collection of xrf data

Authors/Modifications:
-----------------------
* T. Trainor (tptainor@alaska.edu)

Todo:
----
* Improve documentation
* Test!

"""
########################################################################

import sys
import types
import string
import copy
import numpy as num

from  tdl.modules.spectra import medfile_cars
from  tdl.modules.spectra import medfile_emsa
from  tdl.modules.spectra import calibration as calib
from  tdl.modules.xrf.xrf_model import Xrf
from  tdl.modules.ana.med_data import read, read_files   

##############################################################################
def read(file,bad_mca_idx=[],total=True,align=True,correct=True,
         tau=None,det_idx=0,emin=-1.0,emax=-1.0,
         xrf_params={},lines=None,fmt='CARS'):
    """
    Read detector files

    Examples:
    ---------
    >>m = xrf.read(file="file_name",bad_mca_idx=[],
                   total=True,align=True,tau=None)

    Notes:
    ------
    * xrf_params should have the same format as returned
      by Xrf.get_params
    
    * if xrf_params == None: returns a list of med objects
      otherwise: returns a list of xrf objects (default)

    """
    med = read(file,bad_mca_idx=bad_mca_idx,total=total,
               align=align,correct=correct,tau=tau,fmt=fmt)
    if med == None: return None
    xrf = med2xrf(med,xrf_params=xrf_params,lines=lines,
                  det_idx=det_idx,emin=emin,emax=emax)
    return xrf

##############################################################################
def read_files(prefix,start=0,end=100,nfmt=3,bad_mca_idx=[],
               total=True,align=True,correct=True,tau=None,det_idx=0,
               emin=-1.0,emax=-1.0,xrf_params={},lines=None,fmt='CARS'):
    """
    Read multiple detector files

    Notes:
    ------
    * xrf_params should have the same format as returned
      by Xrf.get_params
    
    * if xrf_params == None: returns a list of med objects
      otherwise: returns a list of xrf objects (default)
    """
    med = read_files(prefix,start=start,end=end,nfmt=nfmt,
                     bad_mca_idx=bad_mca_idx,total=total,
                     align=align,correct=correct,tau=tau,fmt=fmt)
    if med == None: return None
    
    xrf = med2xrf(med,xrf_params=xrf_params,lines=lines,
                  det_idx=det_idx,emin=emin,emax=emax)
    return xrf

##############################################################################
def med2xrf(med,xrf_params={},lines=None,det_idx=0,emin=-1.,emax=-1.):
    """
    Given an med object (or list of med objects) return a
    new xrf object (or list of xrf objects).
    
    Notes:
    ------
    * xrf_params should have the same format as returned
      by Xrf.get_params
    """
    if type(med) == types.ListType:
        xrf = []
        for m in med:
            tmp = _med2xrf(m,xrf_params=xrf_params,lines=lines,
                           det_idx=det_idx,emin=emin,emax=emax)
            xrf.append(tmp)
    else:
        xrf = _med2xrf(med,xrf_params=xrf_params,lines=lines,
                       det_idx=det_idx,emin=emin,emax=emax)
    return xrf

def _med2xrf(med,xrf_params={},lines=None,det_idx=0,emin=-1.,emax=-1.):
    """
    med2xrf
    """
    # Xrf just fits one data/energy array    
    if med.total == True:
        det_idx=0
    if (det_idx < 0) or (det_idx > med.n_detectors -1):
        det_idx=0
    # med will always ret data, energy and cal as arrays
    data = med.get_data()[det_idx]
    en   = med.get_energy()[det_idx]
    cal  = med.get_calib_params()[det_idx]
    # if energy range specified, truncate
    if ((emin + emax) > 0.) and (emin != emax):
        idx  = calib.energy_idx(en,emin=emin,emax=emax)
        data = data[idx]
        en   = en[idx]
    # Make sure we have energy calib params.
    # use those passed in if given, otherwise
    # use those from med.  
    if not xrf_params.has_key('fit'):
        xrf_params['fit'] = {}

    keys = xrf_params['fit'].keys()
    if 'energy_offset' not in keys:
        xrf_params['fit']['energy_offset'] = cal['offset']
    if 'energy_slope' not in keys:
        xrf_params['fit']['energy_slope'] = cal['slope']

    # convert energy back to chans
    chans = calib.energy_to_channel(en,
                                    offset=xrf_params['fit']['energy_offset'],
                                    slope=xrf_params['fit']['energy_slope'])
    # Create an XrfSpectrum object
    x =  Xrf(data=data,chans=chans,params=xrf_params)
    #Add bgr    
    if xrf_params.has_key('bgr'):
        x.init_bgr(params=xrf_params['bgr'])
    else:
        x.init_bgr()
    # if lines add lines
    if lines:
        x.init_lines(lines)
    return x

#################################################################################
def fit(xrf,xrf_params={},use_prev_fit=False,fit_init=-1,guess=False,verbose=True):
    """
    Given a (list of) xrf objects fit them all

    Parameters:
    -----------
    * xrf_params should have the same format as returned
      by Xrf.get_params
    * fit_init: the index of the first scan in the list to fit
      it will be used as the seed value for fitting
      all the xrf objects restarting at index zero.
    * use_prev_fit: if True then use index-1 as seed parameters
    * If fit_init >-1 and use_prev_fit=True then fit_init will only
      be used as the seed for fitting the first index only.
    * if guess is true the initial amplitudes will be guessed from the data
    """
    if type(xrf) != types.ListType:
        xrf = [xrf]

    if fit_init >=0:
        if verbose: sys.__stdout__.write("Fitting index = %d\n" % fit_init)
        xrf[fit_init].fit()
        params = xrf[fit_init].get_params()
        init = True
    elif len(xrf_params) > 0:
        params = xrf_params
        init = True
    else:
        init = False
    
    for j in range(len(xrf)):
        if verbose: sys.__stdout__.write("Fitting index = %d\n" % j)
        if (j > 0) and (use_prev_fit == True):
            params = xrf[j-1].get_params()
            xrf[j].init(params=params)
        elif init:
            xrf[j].init(params=params,guess=guess)
        xrf[j].fit()
    return

#################################################################################
def peak_areas(xrf,line):
    """
    get peak areas for given line
    """
    if type(xrf) != types.ListType:
        xrf = [xrf]
    results = []
    for x in xrf:
        for pk in x.peaks:
            if string.lower(pk.label) == string.lower(line):
                results.append(pk.area)
                break
    return num.array(results)

#################################################################################
def xrf_plot(xrf,d='Data',f='Fit',p=None,ylog=True,xlog=False,hold=False):
    """
    Plot data
    
    Parameters:
    -----------
    * d = 'Data', 'Data-Bgr'
    * f = 'Fit', 'Bgr', 'Fit-Bgr', 'Fit and Bgr'
    * p = 'Peaks', 'Peaks+Bgr'
    """
    tiny = 1.e-6

    try:
        from matplotlib import pyplot
    except:
        return
    if hold == False: pyplot.clf()
    
    en  = xrf.get_energy() + tiny
    da  = xrf.get_data() + tiny
    fit = copy.copy(xrf.predicted)
    fit = num.array(fit) + tiny
    bgr = copy.copy(xrf.bgr.bgr)
    bgr = num.array(bgr)  + tiny  

    if d == 'Data':
        pyplot.plot(en,da,'k.-',label='Data')
    if d == 'Data-Bgr':
        if len(bgr) == len(da):
            pyplot.plot(en,da-bgr,'k.-',label='Data')
        else:
            pyplot.plot(en,da,'k.-',label='Data')

    if f == 'Fit':
        pyplot.plot(en,fit,'r-',label='Fit')
    elif f == 'Bgr':
        pyplot.plot(en,bgr,'r-',label='Bgr')
    elif f == 'Fit-Bgr':
        if len(bgr) == len(da):
            pyplot.plot(en,fit-bgr,'r-',label='Fit-Bgr')
        else:
            pyplot.plot(en,fit,'r-',label='Fit')
    elif f == 'Fit and Bgr':
        pyplot.plot(en,fit,'r-',label='Fit')
        pyplot.plot(en,bgr,'g-',label='Bgr')

    if p == 'Peaks':
        npks = len(xrf.peaks)
        lbls = []
        for pk in xrf.peaks:
            lbls.append(pk.label)
        pk_fit = xrf.calc_peaks()
        for j in range(npks):
            pyplot.plot(en,pk_fit[j],label=lbls[j])
    elif p == 'Peaks+Bgr':
        npks = len(xrf.peaks)
        lbls = []
        for pk in xrf.peaks:
            lbls.append(pk.label)
        pk_fit = xrf.calc_peaks()
        for j in range(npks):
            if len(bgr) == len(pk_fit[j]):
                pyplot.plot(en,pk_fit[j]+bgr,label=lbls[j])
            else:
                pyplot.plot(en,pk_fit[j],label=lbls[j])
    if ylog:
        pyplot.semilogy()
        pyplot.ylim(ymin=1.)
    if xlog:
        pyplot.semilogx()

    # annotation
    pyplot.legend()
    pyplot.xlabel('keV')
    pyplot.ylabel('counts')

##############################################################################
class XrfScan:
    """
    Class to hold a collection of xrf's associated with a scan
    ie one xrf spectrum per scan point
    """
    def __init__(self,xrf=[],lines=None):
        """
        Initialize

        Parameters:
        -----------
        * xrf is a list of xrf objects
        * lines is list of xrf lines to fit
        """
        if type(xrf) != types.ListType: xrf = [xrf]
        self.xrf   = xrf
        self.lines = []
        self.peaks = {}
        if lines == None:
            self._update_lines()
        else:
            self.init_lines(lines)
            
    ################################################################
    def get_xrf(self,pnt=0):
        """
        get xrf for a given point
        """
        pnt = int(pnt)
        if self.xrf == []:
            return None
        if pnt not in range(len(self.xrf)):
            return None
        return self.xrf[pnt]

    ################################################################
    def init_lines(self,lines=None):
        """
        init xrf lines
        """
        if lines == None:
            self._update_lines()
        elif type(lines) != types.ListType:
            self.lines = [lines]
            self.lines = lines
        else:
            self.lines = lines
        for x in self.xrf:
            x.init_lines(self.lines)

    def _update_lines(self):
        """
        update self.lines from peaks
        """
        lines = []
        for pk in self.xrf[0].peaks:
            lines.append(pk.label)
        self.lines = lines

    ################################################################
    def calc(self):
        """
        calc xrf
        """
        for x in self.xrf:
            x.calc()
        self._update_peaks()

    ################################################################
    def fit(self,xrf_params={},use_prev_fit=False,fit_init=-1,
            guess=False,verbose=True):
        """
        fit xrf
        """
        fit(self.xrf,xrf_params=xrf_params,use_prev_fit=use_prev_fit,
            fit_init=fit_init,guess=guess,verbose=verbose)
        self._update_peaks()

    ################################################################
    def _update_peaks(self,):
        """
        update xrf peaks
        """
        lines = []
        for pk in self.xrf[0].peaks:
            lines.append(pk.label)
        self.lines = lines
        self.peaks = {}
        for l in lines:
            p = peak_areas(self.xrf,l)
            self.peaks[l] = p

##############################################################################
##############################################################################
if __name__ == "__main__":
    from matplotlib import pyplot
    xrf = read(file='_test.xrf',bad_mca_idx=[0,2,13],emin=4.,emax=9.)
    pyplot.plot(xrf.get_energy(),xrf.get_data(),'-k')
    #pyplot.show()
    #
    xrf.init_lines(['Fe ka',7.12])
    #xrf.init_bgr()
    #
    xrf.calc()
    pyplot.plot(xrf.get_energy(),xrf.predicted,'-r')
    #
    xrf.fit()
    en = xrf.get_energy()
    pyplot.plot(en,xrf.predicted,'-b')
    #
    #for peak in xrf.peaks:
    #    pyplot.plot(en,1+peak.calc(en),'.')
    #
    cnts = xrf.calc_peaks()
    for j in range(len(xrf.peaks)):
        pyplot.plot(en,cnts[j],'.')
    #
    print xrf
    pyplot.semilogy()
    pyplot.show()
