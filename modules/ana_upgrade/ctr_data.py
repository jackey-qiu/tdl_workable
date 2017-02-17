"""
Functions/Objects for extracting ctr data from ScanData objects.

Authors / Modifications:
------------------------
* T. Trainor (tptrainor@alaska.edu)
* Frank Heberling (Frank.Heberling@kit.edu)

Notes:
------
The CTR data object takes as an argument ScanData objects
and a bunch of parameters that define how the data is
to be integrated and processed to generate CTR structure
factors.  The key references for how the geometric
corrections are applied include:

* E. Vlieg, J. Appl. Cryst. (1997). 30, 532-543
* C. Schlepuetz et al, Acta Cryst. (2005). A61, 418-425

Todo:
-----
* Averaging/merging and merge statistics
* Integrations/Corrections for rocking scans
* Add normalized F plots  - divide by |Fctr|
  (need to pass delta_H, delta_K for non-rational surfaces)
* Lots of optimization to speed up...  
  
"""
##############################################################################

import types, copy
import numpy as num
from   matplotlib import pyplot
import time

from tdl.modules.utils import plotter
from tdl.modules.utils.mathutil import cosd, sind, tand
from tdl.modules.utils.mathutil import arccosd, arcsind, arctand

#from tdl.modules.ana import image_data
from tdl.modules.geom.active_area import active_area
from tdl.modules.geom import gonio_psic 

DEBUG = False

##############################################################################
def ctr_data(scans,ctr=None,I=None,Inorm=None,Ierr=None,Ibgr=None,
             corr_params=None,scan_type=None):
    """
    create a ctr instance or add scan data to an existing instance
    """
    if ctr == None:
        # check for defaults
        if I==None: I ='I'
        if Inorm==None: Inorm='io'
        if Ierr==None: Inorm='Ierr',
        if Ibgr==None: Ibgr='Ibgr',
        if corr_params==None: corr_params={}
        if scan_type==None:scan_type='image'
        return CtrData(scans=scans,I=I,Inorm=Inorm,Ierr=Ierr,Ibgr=Ibgr,
                       corr_params=corr_params,scan_type=scan_type)
    else:
        ctr.append_scans(scans,I=I,Inorm=Inorm,Ierr=Ierr,Ibgr=Ibgr,
                         corr_params=corr_params,scan_type=scan_type)
    
##############################################################################
class CtrData:
    """
    CTR data

    Attributes:
    -----------
    * bad is a list of index values of points flagged as 'bad'
    * scan is a list holding all the scan data ojects
    * scan_index is a list (possibly of tuples) that give the
      scan index corresponding to a data point. see the get_scan method
    * labels is a dictionary of lists of the string labels
      for 'I','Inorm','Ierr','Ibgr'
    * corr_params = list of correction parameter dictionaries
    * scan_type list of string flags for scan type
    * H     = array of H values
    * K     = array of K values
    * L     = array of L values
    * I     = array of integrated intensities
    * Inorm = array of normalization values
    * Ierr  = array of intensity errors
    * Ibgr  = array of intensity backgrounds
    * ctot  = array of total correction factors
    * F     = array of structure factor magnitudes
    * Ferr  = array of structure factor error bars
    """
    ##########################################################################
    def __init__(self,scans=[],I='I',Inorm='io',Ierr='Ierr',
                 Ibgr='Ibgr',corr_params={},scan_type='image'):
        """
        Initialize the object.

        Parameters:
        -----------
        * scans = list of scan data instances

        * I = string label corresponding to the intensity array, ie
          let y be the intensity, then y = scan[I]

        * Inorm=string label corresponding to the normalization intensity array, 
          ie, norm = scan[Inorm], where the normalized intensity is taken as
          ynorm= y/norm

        * Ierr = string label corresponding to the intensity error array, ie
          y_err = scan[Ierr].  We assume these are standard deviations 
          of the intensities (y).
        
          Note when the data are normalized we assume the statistics of norm 
          go as norm_err = sqrt(norm).  Therefore the error of normalized
          data is
            ynorm_err = ynorm * sqrt( (y_err/y)^2 + (norm_err/(norm))^2 )
                      = ynorm * sqrt( (y_err/y)^2 + 1/norm )
          If its assumed that y_err = sqrt(y) then the expression could be
          simplified futher, but we wont make that assumption since there
          may be other factors that determine how yerr was calculated.  

        * Ibgr = string label corresponding to background intensity array

        * corr_params = a dictionary containing the necessary information for
          data corrections.
          corr_params['geom'] = Type of goniometer geometry ('psic' is default)
          corr_params['beam_slits'] = dictionary describing the beam slits,e.g.
                                      {'horz':.6,'vert':.8}
          corr_params['det_slits'] = dictionary describing the beam slits,e.g.
                                     {'horz':.6,'vert':.8}
          corr_params['sample'] = a dictionary describing the sample shape.
                                  {'dia':0,'angles':{},'polygon':[]}
                                  if dia >=0 then assume a round sample.
                                  Otherwise use polygon/angles
                                  If all are None, then no sample correction is
                                  computed
          corr_params['scale'] = scale factor to multiply by all the intensity
                                 values. e.g.  if Io ~ 1million cps
                                 then using 1e6 as the scale makes the normalized
                                 intensity close to cps.  ie y = scale*y/norm

          See the Correction class for more info...

        * scan_type = Type of scans (e.g. 'image', 'phi', etc..)
        
        """
        self.fig    = None
        self.cursor = None
        self.hklist = None
        self.bad    = []
        self.scan   = []
        self.scan_index  = []
        #
        self.labels      = {'I':[],'Inorm':[],'Ierr':[],'Ibgr':[]}
        self.corr_params = []
        self.scan_type   = []
        #
        self.H     = num.array([],dtype=float)
        self.K     = num.array([],dtype=float)
        self.L     = num.array([],dtype=float)
        self.I     = num.array([],dtype=float)
        self.Inorm = num.array([],dtype=float)
        self.Ierr  = num.array([],dtype=float)
        self.Ibgr  = num.array([],dtype=float)
        self.ctot  = num.array([],dtype=float)
        self.F     = num.array([],dtype=float)
        self.Ferr  = num.array([],dtype=float)
        #
        self.append_scans(scans,I=I,Inorm=Inorm,Ierr=Ierr,Ibgr=Ibgr,
                          corr_params=corr_params,
                          scan_type=scan_type)

    ##########################################################################
    def __repr__(self,):
        """ display """
        lout = "CTR DATA\n"
        lout = "%sNumber of scans = %i\n" % (lout,len(self.scan))
        lout = "%sNumber of structure factors = %i\n" % (lout,len(self.L))
        return lout

    ##########################################################################
    def __save__(self,):
        """
        this is called by the pickler so we can delete stuff
        we dont want to pickle
        """
        try:
            del self.cursor
            self.cursor = None
        except:
            self.cursor = None

    ##########################################################################
    def append_scans(self,scans,I=None,Inorm=None,Ierr=None,Ibgr=None,
                     corr_params=None,scan_type=None):
        """
        Append new scan data

        Parameters:
        -----------
        * scans is a list of scan data objects.

        * The rest of the arguments (defined in __init__)
          should be the same for each scan in the list.

        For any argument with None passed we use previous defined
        values - based on the last exisiting data point.  
        """
        if type(scans) != types.ListType:
            scans = [scans]
        
        # if None passed use the last values
        if I == None:           I = self.labels['I'][-1]
        if Inorm == None:       Inorm = self.labels['Inorm'][-1]
        if Ierr == None:        Ierr = self.labels['Ierr'][-1]
        if Ibgr == None:        Ibgr = self.labels['Ibgr'][-1]
        if corr_params == None: corr_params = self.corr_params[-1]
        if scan_type == None:   scan_type = self.scan_type[-1]

        # get all the data parsed out of each scan and append
        for scan in scans:
            data = self._scan_data(scan,I,Inorm,Ierr,Ibgr,corr_params,scan_type)
            if data == None: return

            #self.scan.append([])
            self.scan.append(scan)
            #
            self.scan_index.extend(data['scan_index'])
            self.labels['I'].extend(data['I_lbl'])
            self.labels['Inorm'].extend(data['Inorm_lbl'])
            self.labels['Ierr'].extend(data['Ierr_lbl'])
            self.labels['Ibgr'].extend(data['Ibgr_lbl'])
            self.corr_params.extend(data['corr_params'])
            self.scan_type.extend(data['scan_type'])
            #
            self.H     = num.append(self.H,data['H'])
            self.K     = num.append(self.K,data['K'])
            self.L     = num.append(self.L,data['L'])
            self.I     = num.append(self.I,data['I'])
            self.Inorm = num.append(self.Inorm,data['Inorm'])
            self.Ierr  = num.append(self.Ierr,data['Ierr'])
            self.Ibgr  = num.append(self.Ibgr,data['Ibgr'])
            self.ctot  = num.append(self.ctot,data['ctot'])
            self.F     = num.append(self.F,data['F'])
            self.Ferr  = num.append(self.Ferr,data['Ferr'])
        # make a list of stored hk's
        self.hklist = find_HKs(self)
        
    ##########################################################################
    def _scan_data(self,scan,I,Inorm,Ierr,Ibgr,corr_params,scan_type):
        """
        Parse scan into data...
        """
        data = {'scan_index':[],'I_lbl':[],'Inorm_lbl':[],
                'Ierr_lbl':[],'Ibgr_lbl':[],'corr_params':[],'scan_type':[],
                'H':[],'K':[],'L':[],'I':[],'Inorm':[],'Ierr':[],'Ibgr':[],
                'ctot':[],'F':[],'Ferr':[]}

        # compute a scan index
        scan_idx = len(self.scan)
        
        # image scan -> each scan point is a unique HKL
        if scan_type == 'image':
            if scan.image._is_integrated == False:
                scan.image.integrate()
            npts = int(scan.dims[0])
            for j in range(npts):
                data['scan_index'].append((scan_idx,j))
                data['I_lbl'].append(I)
                data['Inorm_lbl'].append(Inorm)
                data['Ierr_lbl'].append(Ierr)
                data['Ibgr_lbl'].append(Ibgr)
                data['corr_params'].append(corr_params)
                data['scan_type'].append(scan_type)
                #
                data['H'].append(scan['H'][j])
                data['K'].append(scan['K'][j])
                data['L'].append(scan['L'][j])
                # get F
                d = image_point_F(scan,j,I=I,Inorm=Inorm,
                                  Ierr=Ierr,Ibgr=Ibgr,
                                  corr_params=corr_params)
                data['I'].append(d['I'])
                data['Inorm'].append(d['Inorm'])
                data['Ierr'].append(d['Ierr'])
                data['Ibgr'].append(d['Ibgr'])
                data['ctot'].append(d['ctot'])
                data['F'].append(d['F'])
                data['Ferr'].append(d['Ferr'])
        return data

    ##########################################################################
    def integrate_point(self,idx,**kw):
        """
        (Re)-integrate an individual structure factor point.

        Parameters:
        -----------
        * idx is the index number of the structure factor (data point)

        If scan type is image use the following kw arguments
        (if the argument is not passed the existing value is used,
        ie just use these to update/change parameters)
        
        * bad        = True/False flags point as bad or not
        * roi        = image roi
        * rotangle   = image rotation angle
        * bgr_params = image background parameters
        * plot       = True/False to show integration plot 
        * fig        = Fig number for plot
        * I          = Intensity label
        * Inorm      = Intensity norm label
        * Ierr       = Intensity error label
        * Ibgr       = Intensity background label
        * corr_params = CTR correction parameters
        
        """
        if DEBUG: tm = time.time()
        if idx not in range(len(self.L)): return

        bad = kw.get('bad')
        if bad != None:
            if bad == True:
                if idx not in self.bad:
                    self.bad.append(idx)
            elif bad == False:
                if idx in self.bad:
                    self.bad.remove(idx)
            else:
                print "Warning: bad should be True/False"

        # Image Data
        if self.scan_type[idx]=="image":
            (scan_idx,point) = self.scan_index[idx]
            scan = self.scan[scan_idx]
            if scan.image._is_init() == False:
                scan.image._init_image()
            
            # parse integration parameters
            roi        = kw.get('roi')
            rotangle   = kw.get('rotangle')
            bgr_params = kw.get('bgr_params')
            #
            plot       = kw.get('plot',False)
            fig        = kw.get('fig')
            
            if idx in self.bad:
                bad = [point]
            else:
                bad = []
            # integrate the scan.  
            scan.image.integrate(idx=[point],roi=roi,rotangle=rotangle,
                                 bgr_params=bgr_params,bad_points=bad,
                                 plot=plot,fig=fig)
            
            # parse all the correction info and re-compute 
            I           = kw.get('I',self.labels['I'][idx])
            Inorm       = kw.get('Inorm',self.labels['Inorm'][idx])
            Ierr        = kw.get('Ierr', self.labels['Ierr'][idx])
            Ibgr        = kw.get('Ibgr', self.labels['Ibgr'][idx])
            corr_params = kw.get('corr_params',self.corr_params[idx])
            d = image_point_F(scan,point,I=I,Inorm=Inorm,
                              Ierr=Ierr,Ibgr=Ibgr,
                              corr_params=corr_params)
            
            # store results
            self.labels['I'][idx]     = I
            self.labels['Inorm'][idx] = Inorm
            self.labels['Ierr'][idx]  = Ierr
            self.corr_params[idx]     = corr_params
            self.H[idx]               = scan['H'][point]
            self.K[idx]               = scan['K'][point]
            self.L[idx]               = scan['L'][point]
            self.I[idx]               = d['I']
            self.Inorm[idx]           = d['Inorm']
            self.Ierr[idx]            = d['Ierr']
            self.Ibgr[idx]            = d['Ibgr']
            self.ctot[idx]            = d['ctot']
            self.F[idx]               = d['F']
            self.Ferr[idx]            = d['Ferr']
        # Rocking scan data
        else:
            # note if rocking scans are implemented
            # make sure to compute corrections using the
            # correct angles, e.g. the angles from the
            # center of the scan (or at the start)
            print "No other scan types implemented"
        if DEBUG: print "Integration time(s)=",time.time()-tm
        return 

    ##########################################################################
    def hk_plot(self,H,K,fig=None,cursor=True,verbose=True,spnt=None):
        """
        Plot structure factors for select HK vs L (simple/fast plot)

        Parameters:
        -----------
        * H and K are HK vals
        * fig is the figure number to plot to
        * cursor is a flag to indicate cursor updates
        * verbose is a flag to indicate if cursor clicks
          should also print info
        * spnt is point index to plot in red
        """
        if DEBUG: tm1 = time.time()
        pyplot.figure(fig)
        pyplot.clf()
        idx = HK_idx(self,H,K)
        if len(idx[0])==0:
            print "No matching values"
            return
        pyplot.plot(self.L[idx],self.F[idx],'bo')
        if spnt != None:
            if spnt in idx[0]:
                sidx = num.where(idx[0]==spnt)
                pyplot.plot(self.L[sidx],self.F[sidx],'ro')
        pyplot.semilogy()
        #
        fig = pyplot.gcf()
        self.fig = fig.number
        if self.cursor != None:
            self.cursor._disconnect()
            del self.cursor
            self.cursor = None
        if cursor == True:
            self.cursor = plotter.cursor(fig=self.fig,verbose=verbose)
        if DEBUG: print "Rod Plot Time(s) =" , time.time()-tm1

    ##########################################################################
    def hk_plot_I(self,H,K,fig=None,cursor=True,verbose=True,spnt=None):
        """
        Plot intensities for select HK vs L (simple/fast plot)

        Parameters:
        -----------
        * H and K are HK vals
        * fig is the figure number to plot to
        * cursor is a flag to indicate cursor updates
        * verbose is a flag to indicate if cursor clicks
          should also print info
        * spnt is point index to plot in red
        """
        if DEBUG: tm1 = time.time()
        pyplot.figure(fig)
        pyplot.clf()
        idx = HK_idx(self,H,K)
        if len(idx[0])==0:
            print "No matching values"
            return
        I  = self.I[idx]
        In = self.Inorm[idx]
        Ib = self.Ibgr[idx]
        #Ie = self.Ierr[idx]
        y  = I/In
        yb = Ib/In
        #ye = Ie/In
        pyplot.plot(self.L[idx],y,'bo')
        pyplot.plot(self.L[idx],yb,'m.')
        if spnt != None:
            if spnt in idx[0]:
                sidx = num.where(idx[0]==spnt)
                pyplot.plot(self.L[sidx],y[sidx],'ro')
        pyplot.semilogy()
        #
        fig = pyplot.gcf()
        self.fig = fig.number
        if self.cursor != None:
            self.cursor._disconnect()
            del self.cursor
            self.cursor = None
        if cursor == True:
            self.cursor = plotter.cursor(fig=self.fig,verbose=verbose)
        if DEBUG: print "Rod Plot Time(s) =" , time.time()-tm1

    ##########################################################################
    def plot(self,fig=None,num_col=2,cursor=True,verbose=True,spnt=None):
        """
        Plot the structure factor data vs L

        Parameters:
        -----------
        * fig is the figure number to plot to
        * num_col is the number of plot columns
        * cursor is a flag to indicate cursor updates
        * verbose is a flag to indicate if cursor clicks
          should also print info
        * spnt is point index to plot in red
        """
        if DEBUG: tm1 = time.time()
        hksets  = sort_data(self)
        nset    = len(hksets)
        num_col = float(num_col)
        num_row = num.ceil(nset/num_col)
        pyplot.figure(fig)
        pyplot.clf()
        for j in range(nset):
            if DEBUG: tm2 = time.time()
            pyplot.subplot(num_row,num_col,j+1)
            if DEBUG: tm3 = time.time()
            title = 'H=%2.3f,K=%2.3f' % (hksets[j]['H'][0],hksets[j]['K'][0])
            pyplot.title(title, fontsize = 12)
            pyplot.plot(hksets[j]['L'],hksets[j]['F'],'b.')
            pyplot.errorbar(hksets[j]['L'],hksets[j]['F'],hksets[j]['Ferr'], fmt ='o')
            if spnt != None:
                if spnt in hksets[j]['point_idx']:
                    idx = num.where(hksets[j]['point_idx']==spnt)
                    pyplot.plot(hksets[j]['L'][idx],hksets[j]['F'][idx],'ro')
            pyplot.semilogy()
            #
            min_L = num.floor(num.min(hksets[j]['L']))
            max_L = num.ceil(num.max(hksets[j]['L']))
            idx   = num.where(hksets[j]['F'] > 0.)
            min_F = num.min(hksets[j]['F'][idx])
            min_F = 10.**(num.round(num.log10(min_F)) - 1)
            max_F = num.max(hksets[j]['F'][idx])
            max_F = 10.**(num.round(num.log10(max_F)) + 1)
            pyplot.axis([min_L,max_L,min_F,max_F])
            if DEBUG: print " -- Plot Time(s) =" , time.time()-tm2, time.time()-tm3
            #
            #pyplot.xlabel('L')
            #pyplot.ylabel('|F|')
        #
        fig = pyplot.gcf()
        self.fig = fig.number
        if self.cursor != None:
            self.cursor._disconnect()
            del self.cursor
            self.cursor = None
        if cursor == True:
            self.cursor = plotter.cursor(fig=self.fig,verbose=verbose)
        if DEBUG: print "Rod Plot Time(s) =" , time.time()-tm1

    ##########################################################################
    def plot_I(self,fig=None,num_col=2,cursor=True,verbose=True,spnt=None):
        """
        Plot the raw intensities vs L

        Parameters:
        -----------
        * fig is the figure number to plot to
        * num_col is the number of plot columns
        * cursor is a flag to indicate cursor updates
        * verbose is a flag to indicate if cursor clicks
          should also print info
        * spnt is point index to plot in red
        
        """
        hksets  = sort_data(self)
        nset    = len(hksets)
        num_col = float(num_col)
        num_row = num.ceil(nset/num_col)

        pyplot.figure(fig)
        pyplot.clf()
        for j in range(nset):
            pyplot.subplot(num_row,num_col,j+1)
            title = 'H=%2.3f,K=%2.3f' % (hksets[j]['H'][0],hksets[j]['K'][0])
            pyplot.title(title, fontsize = 12)
            I  = hksets[j]['I']
            In = hksets[j]['Inorm']
            Ib = hksets[j]['Ibgr']
            Ie = hksets[j]['Ierr']
            y  = I/In
            yb = Ib/In
            ye = Ie/In
            #
            pyplot.plot(hksets[j]['L'],y,'b.',label='I/Inorm')
            pyplot.errorbar(hksets[j]['L'],y,ye, fmt ='o')
            pyplot.plot(hksets[j]['L'],yb,'m.',label='Ibgr/Inorm')
            #
            min_L = num.floor(num.min(hksets[j]['L']))
            max_L = num.ceil(num.max(hksets[j]['L']))
            #
            idx   = num.where(y > 0.)
            min_I = num.min(y[idx])
            min_I = 10.**(num.round(num.log10(min_I)) - 1)
            idxb  = num.where(yb > 0.)
            if len(idxb[0]) == 0:
                min_Ibgr = min_I
            else:
                min_Ibgr = num.min(yb[idxb])
                min_Ibgr = 10.**(num.round(num.log10(min_Ibgr)) - 1)
            min_I = min(min_I,min_Ibgr)
            #
            max_I = num.max(y[idx])
            max_I = 10.**(num.round(num.log10(max_I)) + 1)
            if len(idxb[0]) == 0:
                max_Ibgr = max_I
            else:
                max_Ibgr = num.max(yb[idxb])
                max_Ibgr = 10.**(num.round(num.log10(max_Ibgr)) + 1)
            max_I = max(max_I,max_Ibgr)
            #
            idx  = num.where(I <= 0.)
            tmp  = I[idx] * 0.0 + 1.1*min_I 
            pyplot.plot(hksets[j]['L'][idx],tmp,'bo')
            #
            if spnt != None:
                if spnt in hksets[j]['point_idx']:
                    idx = num.where(hksets[j]['point_idx']==spnt)
                    if I[idx] <= 0.:
                        pyplot.plot(hksets[j]['L'][idx],[1.1*min_I],'ro')
                    else:
                        pyplot.plot(hksets[j]['L'][idx],y[idx],'ro')
            #
            pyplot.semilogy()
            pyplot.axis([min_L,max_L,min_I,max_I])
            #pyplot.xlabel('L')
            #pyplot.ylabel('Intensity')
            pyplot.legend()
        #
        fig = pyplot.gcf()
        self.fig = fig.number
        if self.cursor != None:
            self.cursor._disconnect()
            del self.cursor
            self.cursor = None
        if cursor == True:
            self.cursor = plotter.cursor(fig=self.fig,verbose=verbose)

    ##########################################################################
    def plot_point(self,idx=None,fig=None,show_int=False,cmap=None):
        """
        Plot the raw data for a selected point

        Parameters:
        -----------
        * idx is the index number of the structure factor (data point)
          if idx = None, then uses last cursor click
        * fig = fig number
        * show_int is a flag for showing integration plot for images
        * cmap is the color map for images
        """
        if idx == None:
            idx = self.get_idx()
        if self.scan_type[idx] == 'image':
            if show_int:
                self.integrate_point(idx,plot=True,fig=fig)
            else:
                (scan_idx,point) = self.scan_index[idx]
                self.scan[scan_idx].image.plot(idx=point,fig=fig,cmap=cmap)
        else:
            # plot scan data
            pass

    ##########################################################################
    def get_idx(self):
        """
        Get point index from last plot selection

        Example:
        -------
        >>idx = ctr.get_idx()
        >>L = ctr.L[idx]
        """
        if self.cursor == None:
            return None
        if self.cursor.clicked == False:
            #self.cursor.get_click(msg="Select a data point")
            return None
        L = self.cursor.x
        subplot = self.cursor.subplot
        if subplot < 0:
            return None
        hksets  = sort_data(self)
        return self._get_idx(subplot,L,hksets)
    
    def _get_idx(self,subplot,L,hksets):
        d   = hksets[subplot]
        tmp = num.fabs(d['L']-L)
        idx = num.where(tmp==min(tmp))
        if len(idx) > 0:
            idx = idx[0]
        point_idx = d['point_idx'][idx]
        return point_idx

    ##########################################################################
    def get_scan(self,idx=None):
        """
        Get scan from point index (idx)

        Parameters
        ----------
        * idx is the index number of the structure factor (data point)
          If idx is None it uses the last plot selection        

        Returns:
        --------
        * tuple of (scan,point) where scan is the
          scan data object and point is the point
          in the scan (for image/stationary scans)
        """
        if idx == None:
            idx = self.get_idx()
            if idx == None: return None
        scan_idx = self.scan_index[idx]
        if len(scan_idx) > 1:
            point = scan_idx[1]
            idx = scan_idx[0]
        else:
            idx = scan_idx
            point = 0
        scan = self.scan[idx]
        return (scan,point)

    ##########################################################################
    def get_scan_name(self,idx=None):
        """
        Get the scan name from point index (idx)

        Parameters
        ----------
        * idx is the index number of the structure factor (data point)
          If idx is None it uses the last plot selection        

        Returns:
        --------
        * string with scan information
        """
        if idx == None:
            idx = self.get_idx()
            if idx == None: return None
        scan_idx = self.scan_index[idx]
        if len(scan_idx) > 1:
            point = scan_idx[1]
            idx = scan_idx[0]
        else:
            idx = scan_idx
            point = 0
        name = self.scan[idx].name
        return name
        
    ##########################################################################
    def get_corr(self,idx=None):
        """
        Get scan the correction instance (which includes the
        gonio instance) from point index (idx)

        Parameters
        ----------
        * idx is the index number of the structure factor (data point)
          If idx is None it uses the last plot selection        

        Returns:
        --------
        * CtrCorrection instance
        """
        if self.scan_type[idx]=="image":
            (scan,spnt) = self.get_scan(idx)
            corr_params = self.corr_params[idx]
            corr = _get_corr(scan,spnt,corr_params)
        else:
            # need the scan point within the rocking scan
            # or the values at the start??
            print "Not implemented for non image scans"
        return corr
    
    ##########################################################################
    def get_points(self,fig=None):
        """
        get index value of points from the plot zoom
        """
        if self.cursor == None:
            return None
        if self.cursor.clicked == False:
            #self.cursor.get_click(msg="Zoom on plot")
            return None
        self.cursor._zoom()
        z = self.cursor.zoom
        z = (z[0][0],z[1][0])
        Lmin = min(z)
        Lmax = max(z)
        subplot = self.cursor.subplot
        if subplot < 0:
            return None
        hksets  = sort_data(self)
        return self._get_idx_range(subplot,Lmin,Lmax,hksets)
        
    def _get_idx_range(self,subplot,Lmin,Lmax,hksets):
        d    = hksets[subplot]
        tmp  = d['L']
        idx1 = num.where(tmp<Lmin)
        idx2 = num.where(tmp>Lmax)
        tmp  = num.fabs(tmp)
        tmp[idx1] = 0.0
        tmp[idx2] = 0.0
        idx = num.where(tmp > 0 )
        point_idx = d['point_idx'][idx]
        return (point_idx)
    
    ##########################################################################
    def write_HKL(self,fname = 'ctr.lst'):
        """
        Dump data file
        
        Note should use the sort fcn to write in order
        """
        f = open(fname, 'w')
        header = "#idx %5s %5s %5s %7s %7s\n" % ('H','K','L','F','Ferr')
        f.write(header)
        for i in range(len(self.L)):
            if self.I[i] > 0:
                line = "%4i %3.2f %3.2f %6.3f %6.6g %6.6g\n" % (i,round(self.H[i]),
                                                                round(self.K[i]),
                                                                self.L[i],self.F[i],
                                                                self.Ferr[i])
                f.write(line)
        f.close()

##########################################################################
def find_HKs(ctr,hkdecimal=3):
    """
    find all the unique HK pairs in the data set
    """
    hkvals = []
    npts = len(ctr.L)
    H = num.around(ctr.H,decimals=hkdecimal)
    K = num.around(ctr.K,decimals=hkdecimal)
    s = []
    for j in range(npts):
        s = (H[j],K[j]) 
        if s not in hkvals:
            hkvals.append(s)
    # sort the hkvals
    hkvals.sort()
    return hkvals

##########################################################################
def HK_idx(ctr,H,K,hkdecimal=3):
    """
    Get the index numbers for all the data matching H,K

    Example:
    -------
    idx = HK_idx(ctr,1,0)
    Hset = ctr.H[idx]
    Kset = ctr.K[idx]
    Lset = ctr.K[idx]
    Fset = ctr.F[idx]
    """
    Hrnd = num.around(ctr.H,decimals=hkdecimal)
    Krnd = num.around(ctr.K,decimals=hkdecimal)
    idx1 = num.where(Hrnd==H)
    if len(idx1) == 0:
        return idx1
    idx2 = num.where(Krnd[idx1]==K)
    idx = (idx1[0][idx2],)
    return idx

##########################################################################
def sort_data(ctr,hkdecimal=3):
    """
    Return a dict of sorted data

    Assume H,K define a set with a range of L values
    All arrays should be of len npts. 

    Parameters:
    -----------
    * ctr is a ctr data object
    * hkdecimal is the number of precision to round H and K
      values to for sorting.  

    """
    scan_idx = ctr.scan_index
    npts = len(ctr.F)

    #find all unique sets
    hkvals = find_HKs(ctr,hkdecimal=hkdecimal)

    # put data in correct set
    nsets = len(hkvals)
    hkset = []
    for j in range(nsets):
        hkset.append({'H':[],'K':[],'L':[],'F':[],'Ferr':[],
                      'I':[],'Inorm':[],'Ierr':[],'Ibgr':[],
                      'point_idx':[]})
    for j in range(nsets):
        s = hkvals[j]
        idx = HK_idx(ctr,s[0],s[1],hkdecimal=hkdecimal)
        hkset[j]['H']     = num.around(ctr.H[idx],decimals=hkdecimal)
        hkset[j]['K']     = num.around(ctr.K[idx],decimals=hkdecimal)
        hkset[j]['L']     = ctr.L[idx]
        hkset[j]['F']     = ctr.F[idx]
        hkset[j]['Ferr']  = ctr.Ferr[idx]
        hkset[j]['I']     = ctr.I[idx]
        hkset[j]['Inorm'] = ctr.Inorm[idx]
        hkset[j]['Ierr']  = ctr.Ierr[idx]
        hkset[j]['Ibgr']  = ctr.Ibgr[idx]
        hkset[j]['point_idx'] = idx[0]

    # now sort each set by L
    for j in range(nsets):
        lidx = num.argsort(hkset[j]['L'])
        hkset[j]['H'] = hkset[j]['H'][lidx]
        hkset[j]['K'] = hkset[j]['K'][lidx]
        hkset[j]['L'] = hkset[j]['L'][lidx]
        hkset[j]['F'] = hkset[j]['F'][lidx]
        hkset[j]['Ferr'] = hkset[j]['Ferr'][lidx]
        hkset[j]['I'] = hkset[j]['I'][lidx]
        hkset[j]['Inorm'] = hkset[j]['Inorm'][lidx]
        hkset[j]['Ierr'] = hkset[j]['Ierr'][lidx]
        hkset[j]['Ibgr'] = hkset[j]['Ibgr'][lidx]
        hkset[j]['point_idx'] = hkset[j]['point_idx'][lidx]

    return hkset

##############################################################################
def image_point_F(scan,point,I='I',Inorm='io',Ierr='Ierr',Ibgr='Ibgr',
                  corr_params={}, preparsed=False):
    """
    compute F for a single scan point in an image scan
    """
    d = {'I':0.0,'Inorm':0.0,'Ierr':0.0,'Ibgr':0.0,'F':0.0,'Ferr':0.0,
         'ctot':1.0,'alpha':0.0,'beta':0.0}
    d['I']     = scan[I][point]
    d['Inorm'] = scan[Inorm][point]
    d['Ierr']  = scan[Ierr][point]
    d['Ibgr']  = scan[Ibgr][point]
    if corr_params == None:
        d['ctot'] = 1.0
        scale = 1.0
    else:
        # compute correction factors
        scale  = corr_params.get('scale')
        if scale == None: scale = 1.
        scale  = float(scale)
        corr = _get_corr(scan,point,corr_params, preparsed)
        if corr == None:
            d['ctot'] = 1.0
        else:
            d['ctot']  = corr.ctot_stationary()
            d['alpha'] = corr.gonio.pangles['alpha']
            d['beta']  = corr.gonio.pangles['beta']

    # compute F
    if d['I'] <= 0.0 or d['Inorm'] <= 0.:
        d['F']    = 0.0
        d['Ferr'] = 0.0
    else:
        scale = scale * d['ctot']/d['Inorm']
        d['F']    = num.sqrt(scale*d['I'])
        d['Ferr'] = 0.5 * scale**0.5 * d['Ierr']/d['I']**0.5
    return d

##############################################################################
def _get_corr(scan,point,corr_params,preparsed=False):
    """
    get CtrCorrection instance
    """
    geom   = corr_params.get('geom','psic')
    beam   = corr_params.get('beam_slits',{})
    det    = corr_params.get('det_slits')
    sample = corr_params.get('sample')
    # get gonio instance for corrections
    if geom == 'psic':
        gonio = gonio_psic.psic_from_spec(scan['G'],preparsed=preparsed)
        _update_psic_angles(gonio,scan,point)
        corr  = CtrCorrectionPsic(gonio=gonio,beam_slits=beam,
                                  det_slits=det,sample=sample)
    else:
        print "Geometry %s not implemented" % geom
        corr = None
    return corr

##############################################################################
def get_params(ctr,point):
    """
    Return relevant parameters from a specified point
    of a ctr object.  ie use to copy parameters...
    """
    intpar = {}
    corrpar = {}
    (scan,spnt) = ctr.get_scan(point)
    #
    intpar['I']     = ctr.labels['I'][point]
    intpar['Inorm'] = ctr.labels['Inorm'][point]
    intpar['Ierr']  = ctr.labels['Ierr'][point]
    intpar['Ibgr']  = ctr.labels['Ibgr'][point]
    if ctr.scan_type[point] == 'image':
        intpar['image roi']      = scan.image.rois[spnt]
        intpar['image rotangle'] = scan.image.rotangle[spnt]
        intpar['bgr flag']       = scan.image.bgrpar[spnt]['bgrflag']
        intpar['bgr col nbgr']   = scan.image.bgrpar[spnt]['cnbgr']
        intpar['bgr col width']  = scan.image.bgrpar[spnt]['cwidth']
        intpar['bgr col power']  = scan.image.bgrpar[spnt]['cpow']
        intpar['bgr col tan']    = scan.image.bgrpar[spnt]['ctan']
        intpar['bgr row nbgr']   = scan.image.bgrpar[spnt]['rnbgr']
        intpar['bgr row width']  = scan.image.bgrpar[spnt]['rwidth']
        intpar['bgr row power']  = scan.image.bgrpar[spnt]['rpow']
        intpar['bgr row tan']    = scan.image.bgrpar[spnt]['rtan']
        intpar['bgr nline']      = scan.image.bgrpar[spnt]['nline']
        intpar['bgr filter']     = scan.image.bgrpar[spnt]['filter']
        intpar['bgr compress']   = scan.image.bgrpar[spnt]['compress']
    else:
        pass
    #
    corrpar['beam_slits'] = ctr.corr_params[point].get('beam_slits')
    corrpar['det_slits'] = ctr.corr_params[point].get('det_slits')
    corrpar['geom'] = ctr.corr_params[point].get('geom')
    corrpar['scale'] = ctr.corr_params[point].get('scale')
    #
    sample  = ctr.corr_params[point].get('sample')
    if sample == None:
        corrpar['sample dia']     = None
        corrpar['sample polygon'] = None
        corrpar['sample angles']  = None
    elif type(sample) == types.DictType:
        corrpar['sample dia']     = ctr.corr_params[point]['sample'].get('dia')
        corrpar['sample polygon'] = ctr.corr_params[point]['sample'].get('polygon')
        corrpar['sample angles']  = ctr.corr_params[point]['sample'].get('angles')
    else:
        try:
            corrpar['sample dia'] = float(sample)
        except:
            corrpar['sample dia'] = None
        corrpar['sample polygon'] = None
        corrpar['sample angles']  = None

    return (intpar,corrpar)

##############################################################################
def set_params(ctr,point,intpar={},corrpar={}):
    """
    Set ctr parameters.

    The intpar and corrpar arguments should be from get_param fcn above
    ie that sets the correct format...
    """
    (scan,spnt) = ctr.get_scan(point)
    #
    def _getpar(x):
        if x == None: return None
        if type(x) == types.StringType:
            x = eval(x)
        return x
    #
    if len(intpar) > 0:
        if intpar.get('I')!=None:
            ctr.labels['I'][point] = intpar['I']
        if intpar.get('Inorm')!=None:
            ctr.labels['Inorm'][point] = intpar['Inorm']
        if intpar.get('Ierr')!=None:
            ctr.labels['Ierr'][point]  = intpar['Ierr']
        if intpar.get('Ibgr')!=None:
            ctr.labels['Ibgr'][point]  = intpar['Ibgr']
        if ctr.scan_type[point] == 'image':
            if intpar.get('image roi')!=None:
                scan.image.rois[spnt] = _getpar(intpar['image roi'])
            if intpar.get('image rotangle')!=None:
                scan.image.rotangle[spnt] = _getpar(intpar['image rotangle'])
            if intpar.get('bgr flag')!=None:
                scan.image.bgrpar[spnt]['bgrflag'] = _getpar(intpar['bgr flag'])
            if intpar.get('bgr col nbgr')!=None:
                scan.image.bgrpar[spnt]['cnbgr'] = _getpar(intpar['bgr col nbgr'])
            if intpar.get('bgr col width')!=None:
                scan.image.bgrpar[spnt]['cwidth'] = _getpar(intpar['bgr col width'])
            if intpar.get('bgr col power')!=None:
                scan.image.bgrpar[spnt]['cpow'] = _getpar(intpar['bgr col power'])
            if intpar.get('bgr col tan')!=None:
                scan.image.bgrpar[spnt]['ctan'] = _getpar(intpar['bgr col tan'])
            if intpar.get('bgr row nbgr')!=None:
                scan.image.bgrpar[spnt]['rnbgr'] = _getpar(intpar['bgr row nbgr'])
            if intpar.get('bgr row width')!=None:
                scan.image.bgrpar[spnt]['rwidth'] = _getpar(intpar['bgr row width'])
            if intpar.get('bgr row power')!=None:
                scan.image.bgrpar[spnt]['rpow'] = _getpar(intpar['bgr row power'])
            if intpar.get('bgr row tan')!=None:
                scan.image.bgrpar[spnt]['rtan'] = _getpar(intpar['bgr row tan'])
            if intpar.get('bgr nline')!=None:
                scan.image.bgrpar[spnt]['nline'] = _getpar(intpar['bgr nline'])
            if intpar.get('bgr filter')!=None:
                scan.image.bgrpar[spnt]['filter'] = _getpar(intpar['bgr filter'])
            if intpar.get('bgr compress')!=None:
                scan.image.bgrpar[spnt]['compress'] = _getpar(intpar['bgr compress'])
    if len(corrpar) > 0:
        if corrpar.get('beam_slits')!=None:
            ctr.corr_params[point]['beam_slits'] = _getpar(corrpar['beam_slits'])
        if corrpar.get('det_slits')!=None:
            ctr.corr_params[point]['det_slits'] = _getpar(corrpar['det_slits'])
        if corrpar.get('geom')!=None:
            ctr.corr_params[point]['geom'] = corrpar['geom']
        if corrpar.get('scale')!=None:
            ctr.corr_params[point]['scale'] = _getpar(corrpar['scale'])
        #
        sample = ctr.corr_params[point].get('sample') 
        if sample ==None:
            ctr.corr_params[point]['sample']={}
        elif type(sample) != types.DictType:
            ctr.corr_params[point]['sample']={}
            try:
                ctr.corr_params[point]['sample']['dia'] = float(sample)
            except:
                print 'Cant convert original sample descr.'
        #
        if corrpar.get('sample dia')!=None:
            ctr.corr_params[point]['sample']['dia'] = _getpar(corrpar.get('sample dia'))
        if corrpar.get('sample polygon')!=None:
            ctr.corr_params[point]['sample']['polygon'] = _getpar(corrpar.get('sample polygon'))
        if corrpar.get('sample angles')!=None:
            ctr.corr_params[point]['sample']['angles'] = _getpar(corrpar.get('sample angles'))
    
##############################################################################
def _update_psic_angles(gonio,scan,point,verbose=True):
    """
    given a psic gonio instance, a scandata object
    and a scan point, update the gonio angles...
    """
    try:
        npts = int(scan.dims[0])
    except:
        npts = scan.get('dims', (1,0))[0]
    try: 
        scan_name = scan.name
    except: 
        scan_name = ''
    #
    try:
      if type(scan['phi']) == types.FloatType:
          phi=scan['phi']
      elif len(scan['phi']) == npts:
          phi=scan['phi'][point]
    except:
        phi=None
    if phi == None and verbose==True:
        print "Warning no phi angle:", scan_name
    #
    try:
        if type(scan['chi']) == types.FloatType:
            chi=scan['chi']
        elif len(scan['chi']) == npts:
            chi=scan['chi'][point]
    except:
        chi = None
    if chi == None and verbose==True:
        print "Warning no chi angle", scan_name
    #
    try:
        if type(scan['eta']) == types.FloatType:
            eta=scan['eta']
        elif len(scan['eta']) == npts:
            eta=scan['eta'][point]
    except:
        eta = None
    if eta == None and verbose==True:
        print "Warning no eta angle", scan_name
    #
    try:
        if type(scan['mu']) == types.FloatType:
            mu=scan['mu']
        elif len(scan['mu']) == npts:
            mu=scan['mu'][point]
    except:
        mu = None
    if mu == None and verbose==True:
        print "Warning no mu angle", scan_name
    #
    try:
        if type(scan['nu']) == types.FloatType:
            nu=scan['nu']
        elif len(scan['nu']) == npts:
            nu=scan['nu'][point]
    except:
        nu = None
    if nu == None and verbose==True:
        print "Warning no nu angle", scan_name
    #
    try:
        if type(scan['del']) == types.FloatType:
            delta=scan['del']
        elif len(scan['del']) == npts:
            delta=scan['del'][point]
    except:
        delta = None
    if delta == None and verbose==True:
        print "Warning no del angle", scan_name
    #
    gonio.set_angles(phi=phi,chi=chi,eta=eta,
                     mu=mu,nu=nu,delta=delta)

##############################################################################
class CtrCorrectionPsic:
    """
    Data point operations / corrections for Psic geometry

    Notes:
    ------
    All correction factors are defined such that the
    measured data is corrected by multiplying times
    the correction: 
      Ic  = Im*ct
    where
      Im = Idet/Io = uncorrected (measured) intensity

    In other words we use the following formalism:
      Im = (|F|**2)* prod_i(Xi)
    where Xi are various (geometric) factors that 
    influence the measured intensity.  To get the
    structure factor:
      |F| = sqrt(Im/prod_i(Xi)) = sqrt(Im* ct)
    and
      ct = prod_i(1/Xi) = prod_i(ci)
      ci = 1/Xi
      
    If there is an error or problem in the routine for a specific
    correction factor, (e.g. divide by zero), the routine should
    return a zero.  This way the corrected data is zero'd....

    * The correction factors depend on the goniometer geometry
      gonio = gonio_psic.Psic instance

    * The slits settings are needed.  Note if using a large area detector
      you may pass det_slits = None and just spill off will be computed
        beam_slits = {'horz':.6,'vert':.8}
        det_slits = {'horz':20.0,'vert':10.5}
      these are defined wrt psic phi-frame:
        horz = beam/detector horz width (total slit width in lab-z,
               or the horizontal scattering plane)
        vert = detector vert hieght (total slit width in lab-x,
               or the vertical scattering plane)

    * A sample description is needed.
      sample = {}
        sample['dia'] = is taken as the diameter of a round sample
                        mounted on center. if dia<=0 then we either use
                        the polygon description or ignore the sample.
        sample['polygon'] = [[1.,1.], [.5,1.5], [-1.,1.],
                             [-1.,-1.],[0.,.5],[1.,-1.]]
        sample['angles']  = {'phi':108.0007,'chi':0.4831}

        polygon = [[x,y,z],[x,y,z],[x,y,z],....]
                  is a list of vectors that describe the shape of
                  the sample.  They should be given in general lab
                  frame coordinates.

        angles = {'phi':0.,'chi':0.,'eta':0.,'mu':0.}
                 are the instrument angles at which the sample
                 vectors were determined.

    Note: the lab frame coordinate systems is defined such that:
    x is vertical (perpendicular, pointing to the ceiling of the hutch)
    y is directed along the incident beam path
    z make the system right handed and lies in the horizontal scattering plane
    (i.e. z is parallel to the phi axis)

    The center (0,0,0) of the lab frame is the rotation center of the instrument.

    If the sample vectors are given at the flat phi and chi values and with
    the correct sample hieght (sample Z set so the sample surface is on the
    rotation center), then the z values of the sample vectors will be zero.
    If 2D vectors are passed we therefore assume these are [x,y,0].  If this
    is the case then make sure:
    angles = {'phi':flatphi,'chi':flatchi,'eta':0.,'mu':0.}

    The easiest way to determine the sample coordinate vectors is to take a picture
    of the sample with a camera mounted such that is looks directly down the omega
    axis and the gonio angles set at the sample flat phi and chi values and
    eta = mu = 0. Then find the sample rotation center and measure the position
    of each corner (in mm) with up being the +x direction, and downstream
    being the +y direction.  

    Note this routine does not correct for attenuation factors.  
    
    """
    def __init__(self,gonio=None,beam_slits={},det_slits=None,sample={}):
        """
        Initialize

        Parameters:
        -----------
        * gonio is a goniometer instance used for computing reciprocal
          lattice indicies and psuedo angles from motor angles
        * beam_slits are dictionary defining the incident beam aperature
        * det_slits are a dictionary defining the detector aperature
        * sample is a dictionary describing the sample geometry
        (see the instance documentation for more details)
        """
        self.gonio      = gonio
        if self.gonio.calc_psuedo == False:
            self.gonio.calc_psuedo = True
            self.gonio._update_psuedo()
        self.beam_slits = beam_slits
        self.det_slits  = det_slits
        self.sample     = sample
        # fraction horz polarization
        self.fh         = 1.0

    ##########################################################################
    def ctot_stationary(self,plot=False,fig=None):
        """
        correction factors for stationary measurements (e.g. images)
        """
        cp = self.polarization()
        cl = self.lorentz_stationary()
        ca = self.active_area(plot=plot,fig=fig)
        ct = (cp)*(cl)*(ca)
        if plot == True:
            print "Correction factors (mult by I)" 
            print "   Polarization=%f" % cp
            print "   Lorentz=%f" % cl
            print "   Area=%f" % ca
            print "   Total=%f" % ct
        return ct

    ##########################################################################
    def lorentz_stationary(self):
        """
        Compute the Lorentz factor for a stationary (image)
        measurement.  See Vlieg 1997

        Measured data is corrected for Lorentz factor as: 
          Ic  = Im * cl
        """
        beta  = self.gonio.pangles['beta']
        cl = sind(beta)
        return cl

    ##########################################################################
    def lorentz_scan(self):
        """
        Compute the Lorentz factor for a generic scan
        
        Note this is approximate. In general for bulk xrd
        with single crystals lorentz factor is defined as:
          L = 1/sin(2theta)
        We need L for specific scan types, e.g. phi, omega, etc..
        See Vlieg 1997

        Measured data is corrected for Lorentz factor as: 
          Ic  = Im * cl = Im/L
        """
        tth  = self.gonio.pangles['tth']
        cl = sind(tth)
        return cl

    ##########################################################################
    def rod_intercept(self,):
        """
        Compute the dl of the rod intercepted by the detector.
        (this correction only applies for rocking scans)
        
        This can be (roughly) approximated from:
          dl = dl_o * cos(beta)
          where dl_o is the detector acceptance at beta = 0

        Note this is an approximation for all but simple specular scans,
        Should use the detector acceptance polygon and determine
        the range of dl for the specific scan axis used.
        
        Measured data is corrected for the intercept as: 
          Ic  = Im * cr = Im/dl
        """
        beta  = self.gonio.pangles['beta']
        cr   = cosd(beta)
        return cr
    
    ##########################################################################
    def polarization(self,):
        """
        Compute polarization correction factor.
        
        For a horizontally polarized beam (polarization vector
        parrallel to the lab-frame z direction) the polarization
        factor is normally defined as:
           p = 1-(cos(del)*sin(nu))^2
        For a beam with mixed horizontal and vertical polarization:
           p = fh( 1-(cos(del)*sin(nu))^2 ) + (1-fh)(1-sin(del)^2)
        where fh is the fraction of horizontal polarization.

        Measured data is corrected for polarization as: 
          Ic  = Im * cp = Im/p
        """
        fh    = self.fh
        delta = self.gonio.angles['delta']
        nu    = self.gonio.angles['nu']
        p = 1. - ( cosd(delta) * sind(nu) )**2.
        if fh != 1.0:
            p = fh * c_p + (1.-fh)*(1.0 - (sind(delta))**2.)
        if p == 0.:
            cp = 0.
        else:
            cp = 1./p

        return cp

    ##########################################################################
    def active_area(self,plot=False,fig=None):
        """
        Compute active area correction (c_a = A_beam/A_int**2)
        
        Use to correct scattering data for area effects,
        including spilloff, A_int/A_beam and normailization 
        to unit surface area (1/A_beam), i.e.
            Ic = Im * ca = Im/A_ratio 
            A_ratio = A_int/(A_beam**2) 
        where
            A_int = intersection area (area of beam on sample
                    viewed by detector)
            A_beam = total beam area
        """
        if self.beam_slits == {} or self.beam_slits == None:
            print "Warning beam slits not specified"
            return 1.0
        alpha = self.gonio.pangles['alpha']
        beta  = self.gonio.pangles['beta']
        if plot == True:
            print 'Alpha = ', alpha, ', Beta = ', beta
        if alpha < 0.0:
            print 'alpha is less than 0.0'
            return 0.0
        elif beta < 0.0:
            print 'beta is less than 0.0'
            return 0.0

        # get beam vectors
        bh = self.beam_slits['horz']
        bv = self.beam_slits['vert']
        beam = gonio_psic.beam_vectors(h=bh,v=bv)

        # get det vectors
        if self.det_slits == None:
            det = None
        else:
            dh = self.det_slits['horz']
            dv = self.det_slits['vert']
            det  = gonio_psic.det_vectors(h=dh,v=dv,
                                          nu=self.gonio.angles['nu'],
                                          delta=self.gonio.angles['delta'])
        # get sample poly
        if type(self.sample) == types.DictType:
            sample_dia    = self.sample.get('dia',0.)
            sample_vecs   = self.sample.get('polygon',None)
            sample_angles = self.sample.get('angles',{})
            #
            if sample_vecs != None and sample_dia <= 0.:
                sample = gonio_psic.sample_vectors(sample_vecs,
                                                   angles=sample_angles,
                                                   gonio=self.gonio)
            elif sample_dia > 0.:
                sample = sample_dia
            else:
                sample = None
        else:
            sample = self.sample

        # compute active_area
        (A_beam,A_int) = active_area(self.gonio.nm,ki=self.gonio.ki,
                                     kr=self.gonio.kr,beam=beam,det=det,
                                     sample=sample,plot=plot,fig=fig)
        if A_int == 0.:
            ca = 0.
        else:
            ca = A_beam/(A_int**2)
            
        return ca

##############################################################################
##############################################################################
def test1():
    #psic = psic_from_spec(G,angles={})
    psic = gonio_psic.test2(show=False)
    psic.set_angles(phi=12.,chi=30.,eta=20.,
                    mu=25.,nu=75.,delta=20.)
    beam_slits = {'horz':.6,'vert':.8}
    det_slits = {'horz':20.0,'vert':10.5}
    sample = {}
    sample['polygon'] = [[1.,1.], [.5,1.5], [-1.,1.], [-1.,-1.],[0.,.5],[1.,-1.]]
    sample['angles']  = {'phi':108.0007,'chi':0.4831}
    cor = CtrCorrectionPsic(gonio=psic,beam_slits=beam_slits,
                            det_slits=det_slits,sample=sample)
    ct = cor.ctot_stationary(plot=True)

##############################################################################
if __name__ == "__main__":
    """
    test 
    """
    test1()



