"""
Data / Spec GUI
"""
############################################################################

from PythonCard import model, dialog
import wx
import os
import glob
import types
import copy
import time
import numpy as num
from matplotlib import pyplot

from .wxUtil import wxUtil
from tdl.modules import ana as scandata 

############################################################################

class wxSpecData(model.Background, wxUtil):

    ###########################################################
    # Init and util methods
    ###########################################################
    def on_initialize(self, event):
        # Initialization
        # including sizer setup, do it here
        # self.setupSizers()
        self.startup  = True
        self.dir      = '.'

        # set up shell
        self.shell = None
        self.init_shell()

        # Make sure Scan Data is loaded
        self.exec_line("import ana")

        # init all the menus
        self.init_ShellItems()
        self.init_GUI()
        self.current = True

   ###########################################################

    def init_ShellItems(self,):
        #self.init_Grp()
        self.init_Reader()
        self.init_ScanVar()
        self.init_BadMcas()
        self.init_McaTaus()
        self.init_XrfLines()

    def on_Update_mouseClick(self,event):
        self.init_ShellItems()
        self.init_SpecFile()
    
    ###########################################################
    #   Menu
    ###########################################################

    def on_menuFileExit_select(self,event): 
        self.close()

    def on_menuHelpDocumentation_select(self,event):
        self.exec_line("web 'http://cars9.uchicago.edu/ifeffit/tdl/Pds/SpecGui'")

    ######################################################

    ###########################################################
    #   Group / Reader
    ###########################################################

    ######################################################

    #def init_Grp(self):
    #    " Initialize the menu    "
    #    grp = self.components.Grp.text
    #    tmp = self.shell.interp.symbol_table.list_symbols(tunnel=False)
    #    self.components.Grp.items = tmp['ins']
    #    self.components.Grp.text = grp
    #    return

    #def on_Grp_select(self, event):
    #    "Re-init reader list given the new grp name"
    #    grp = self.components.Grp.stringSelection
    #    self.components.Grp.text = grp
    #    self.init_Model()
    #    return

    #def on_Grp_keyDown(self,event):
    #    "select a variable name and check it out"
    #    keyCode = event.keyCode
    #    if keyCode == wx.WXK_RETURN:
    #        self.init_Model()
    #    else:
    #        event.skip()
    #    return

    def init_Reader(self):
        """
        Initialize the menu. Use the group thats
        selected in the group menu
        """
        #grp = self.components.Grp.text  
        #if len(grp) == 0: grp = None
        reader = self.components.Reader.stringSelection
        #tmp = self.shell.interp.symbol_table.list_symbols(symbol=grp,tunnel=False)
        tmp = self.shell.interp.symbol_table.list_symbols(tunnel=False)
        tmp = tmp['var'] + tmp['ins']
        tmp.sort()
        self.components.Reader.items = tmp
        if reader in tmp:
            self.components.Reader.stringSelection = reader
        else:
            #self.components.Reader.stringSelection = 'reader'
            self.components.Reader.text = 'reader'
        return

    def on_Reader_select(self,event):
        "select a Reader name and check it out"
        self.init_GUI()
        return

    def on_Reader_keyDown(self,event):
        "select a variable name and check it out"
        keyCode = event.keyCode
        if keyCode == wx.WXK_RETURN:
            self.init_GUI()
        else:
            event.skip()
        return

    def get_ReaderName(self,):
        if len(self.components.Reader.stringSelection) > 0:
            self.components.Reader.text = self.components.Reader.stringSelection
        reader = self.components.Reader.text
        if len(reader.strip()) == 0: return None
        name = "%s" % reader.strip()
        return name

    def get_Reader(self):
        name = self.get_ReaderName()
        if name == None:
            print "Please provide a reader name"
            return None
        reader = self.get_data(name)
        if reader == None:
            reader = scandata.Reader()
            self.set_Reader(reader)
        return reader

    def set_Reader(self,reader):
        name = self.get_ReaderName()
        return self.set_data(name,reader)

    def CheckReader(self,):
        try:
            name = self.get_ReaderName()
            r    = self.get_data(name)
            #if type(r) == types.InstanceType:
            #    if hasattr(r,'read_spec'):
            #        self.post_message("Valid reader object: %s" % name)
            #        return True
            #    else:
            #        self.post_message("Invalid reader object: %s" % name)
            #        return False
            if isinstance(r,scandata.Reader):
                return True
            else:
                self.post_message("Invalid reader object")
                return False
        except:
            self.post_message("Invalid reader object")
            return False

    ######################################################
    # here update stuff from reader
    def init_GUI(self):
        if self.startup:
            self.startup = False
            cmap = copy.copy(pyplot.cm.cmapnames)
            cmap.insert(0,'')
            self.components.ColorMap.items = cmap 
            self.components.ColorMap.stringSelection = ''
        check = self.CheckReader()
        if check == False:
            return
        else:
            self.UpdateGuiFromReader()

    def UpdateGuiFromReader(self,):
        """
        update gui from a reader
        """
        reader = self.get_Reader()
        if reader == None: return
        
        self.components.SpecPath.text = reader.spec_path
        #
        fname0 = ''
        items = []
        for j in range(len(reader.spec_files)):
            s = reader.spec_files[j].fname
            if j == 0: fname0 = s
            items.append(s)
        self.components.SpecFile.items = items
        if fname0:
            self.components.SpecFile.stringSelection = fname0
        #
        self.UpdateGuiMedImgPar(reader)
        #
        self.SpecFileSelect()

    ######################################################

    ###########################################################
    #   Path/files
    ###########################################################

    ######################################################
    def init_SpecPath(self):
        self.components.SpecPath.text = ''
        
    def on_SpecPathSel_mouseClick(self,event):        
        cdir = self.eval_line("pwd()")
        result = dialog.directoryDialog(self, 'Open', cdir)
        if result.accepted:
            dir = result.path
            dir = dir.replace("\\","\\\\")
            self.components.SpecPath.text = dir
            self.init_SpecFile()

    def init_SpecFile(self):
        dir = self.components.SpecPath.text
        dir = os.path.join(dir,'*.spc')
        files = glob.glob(dir)
        list = []
        for f in files:
            list.append(os.path.basename(f))
        sfile = self.components.SpecFile.stringSelection
        self.components.SpecFile.items = list
        if sfile in list:
            self.components.SpecFile.stringSelection=sfile
            
    def on_SpecFileSel_mouseClick(self,event):
        sdir = self.components.SpecPath.text
        cdir = self.eval_line("pwd()")
        if len(sdir.strip()) == 0:
            dir = cdir
        else:
            dir = sdir
        #
        result = dialog.fileDialog(self, 'Open', dir, '',"*")
        if result.accepted == False:
            self.post_message("File selection cancelled.")
            return
        #
        files = []
        #print result.paths
        for j in range(len(result.paths)):
            path        = result.paths[j]
            dir,fname   = os.path.split(path)
            if j == 0:
                if os.path.abspath(dir) != os.path.abspath(sdir):
                    self.components.SpecPath.text = dir
                    #self.init_SpecFile()
                    self.components.SpecFile.items = []
                fname0 = fname
            if fname not in files:
                files.append(fname)
        items = self.components.SpecFile.items
        for f in files:
            if f not in items: items.append(f)
        items.sort()
        self.components.SpecFile.items = items
        #
        self.components.SpecFile.stringSelection = fname0
        self.SpecFileSelect()
        #idx = items.index(fname0)
        #self.components.SpecFile.SetSelection(idx)
 
    ######################################################
    def on_SpecFile_select(self,event):
        self.SpecFileSelect()
        
    def SpecFileSelect(self):
        spath = str(self.components.SpecPath.text)
        sfile = str(self.components.SpecFile.stringSelection)
        reader = self.get_Reader()
        if reader == None: return None
        if reader.spec_path != spath:
            reader.spec_path = os.path.abspath(spath)
        reader.read_spec(sfile)
        #
        self.init_ScanVar()
        #
        for s in reader.spec_files:
            if s.fname == sfile:
                s.read()
                min = s.min_scan
                max = s.max_scan
                idx = num.arange(min,max+1,dtype=int)
                idx = map(str,idx)
                self.components.ScanNum.items = idx
                self.components.ScanNum.stringSelection=idx[-1]
                self.ScanNumSelect()

    ######################################################

    ###########################################################
    #   ScanVar/Num
    ###########################################################

    ######################################################

    def on_ScanNum_select(self,event):
        self.ScanNumSelect()

    def on_ScanNum_keyDown(self,event):
        keyCode = event.keyCode
        if keyCode == wx.WXK_RETURN:
            self.ScanNumSelect()
            self.ReadScan()
        else:
            event.skip()
        return

    def ScanNumSelect(self,):
        sfile = str(self.components.SpecFile.stringSelection)
        snum = str(self.components.ScanNum.stringSelection)
        if self.components.AutoCalcVarName.checked:
            if self.components.LongName.checked:
                scan_var = u"%s.s%s" % (sfile,snum)
                scan_var = scan_var.replace('.','_')
            else:
                scan_var = u"s%s" % (snum)
            #
            items = self.components.ScanVar.items
            if scan_var not in items:
                items.append(scan_var)
                items.sort()
                self.components.ScanVar.items = items
            self.components.ScanVar.stringSelection = scan_var
        else:
            scan_var = self.components.ScanVar.stringSelection
            if  len(scan_var) == 0:
                self.components.ScanVar.text = 'tmp'
        if len(self.components.ScanVar.stringSelection) > 0:
            self.components.ScanVar.text = self.components.ScanVar.stringSelection
            
    def init_ScanVar(self,):
        var = self.components.ScanVar.stringSelection
        tmp = self.shell.interp.symbol_table.list_symbols(tunnel=False)
        self.components.ScanVar.items = tmp['var'] + tmp['ins']
        self.components.ScanVar.stringSelection = var
        return

    def on_ScanVar_select(self,event):
        tmp = self.components.ScanVar.text
        if len(self.components.ScanVar.stringSelection) > 0:
            self.components.ScanVar.text = self.components.ScanVar.stringSelection
        var_name = self.components.ScanVar.text
        if len(var_name)>0:
            data = self.get_data(var_name)
            if (data != None) and (hasattr(data,'primary_axis')==True):
                self.UpdateGuiParmsFromData(data)
                if self.components.AutoUpdateCheck.checked==True:
                    self.AutoPlot(var_name=var_name)

    def on_Read_mouseClick(self,event):
        self.ReadScan()

    ######################################################    
    def ReadScan(self):
        ####
        self.UpdateReaderMedImgPar()

        ####
        fname = self.components.SpecFile.stringSelection
        if len(fname.strip())==0: return
        #
        scan_num = self.components.ScanNum.stringSelection
        if len(scan_num.strip())==0: return
        scan_num = int(scan_num)
        #
        var_name = self.components.ScanVar.text
        if len(var_name.strip())==0:
            #var_name = '__tmp__'
            print "Please enter a variable name"
            return 
        ####
        reader = self.get_Reader()
        if reader == None: return
        ###
        data = reader.spec_scan(scan_num,file=fname)
        self.set_data(var_name,data)
        ###
        
        self.UpdateGuiParmsFromData(data)        
        ####
        if self.components.AutoUpdateCheck.checked==True:
            self.AutoPlot(var_name=var_name)

    def UpdateGuiParmsFromData(self,data):
        """
        update fields
        """
        ####
        x = data.positioners.keys()
        x.sort()
        x.insert(0,'')
        scalers = data.scalers.keys()
        scalers.sort()
        scalers.insert(0,'')
        if hasattr(data,'xrf'):
            xrf_lines = data.xrf.lines
        else:
            xrf_lines = []
        ####
        # scaler default
        default = self.components.DefaultScalerAxes.checked
        ####
        # Plot X
        tmp = self.components.XPlot.stringSelection
        self.components.XPlot.items = x + scalers
        if (len(tmp)>0) and (tmp in x or tmp in scalers) and (default==False):
            self.components.XPlot.stringSelection = tmp
        else:
            self.components.XPlot.stringSelection = data.primary_axis[0]
        ####
        # Plot Y
        tmp = self.components.YPlot.stringSelection
        self.components.YPlot.items = scalers + xrf_lines
        if (len(tmp)> 0) and (tmp in scalers) and (default==False):
            self.components.YPlot.stringSelection = tmp
        else:
            self.components.YPlot.stringSelection = data.primary_det
        ####
        # Plot norm
        tmp = self.components.NormPlot.stringSelection
        self.components.NormPlot.items = scalers
        if len(tmp)>0 and (tmp in scalers) and (default==False):
            self.components.NormPlot.stringSelection = tmp
        else:
            self.components.NormPlot.stringSelection = ''
        ####
        # Med Deadtime
        self.components.DTX.items = scalers + x 
        self.components.DTX.stringSelection = 'io'
        self.components.DTNorm.items = scalers
        self.components.DTNorm.stringSelection = 'Seconds'
        ###
        # Med
        npts = data.dims[0]
        pts = num.arange(npts,dtype=int)
        pts = map(str,pts)
        self.components.ScanPnt.items = pts
        self.components.ScanPnt.stringSelection = '0'
        # check bad_idx
        tmp = str(self.components.BadMcas.text).strip()
        #print tmp
        if hasattr(data,'med'):
            if (len(tmp) == 0) and (len(data.med.med)>0):
                if (len(data.med.med[0].bad_mca_idx) > 0):
                    self.components.BadMcas.text = repr(data.med.med[0].bad_mca_idx)
     
    ######################################################

    ###########################################################
    #   Med and Image Params
    ###########################################################

    ######################################################
    def init_XrfLines(self,):
        " Initialize the menu    "
        var = self.components.XrfLines.stringSelection
        tmp = self.shell.interp.symbol_table.list_symbols(tunnel=False)
        self.components.XrfLines.items = tmp['var']+ tmp['ins']
        self.components.XrfLines.stringSelection = var
        return

    def init_BadMcas(self,):
        " Initialize the menu    "
        var = self.components.BadMcas.stringSelection
        tmp = self.shell.interp.symbol_table.list_symbols(tunnel=False)
        self.components.BadMcas.items = tmp['var']+ tmp['ins']
        self.components.BadMcas.stringSelection = var
        return

    def init_McaTaus(self,):
        " Initialize the menu    "
        var = self.components.McaTaus.stringSelection
        tmp = self.shell.interp.symbol_table.list_symbols(tunnel=False)
        self.components.McaTaus.items = tmp['var'] + tmp['ins']
        self.components.McaTaus.stringSelection = var
        return

    def init_ImagePath(self):
        self.components.ImagePath.text = ''
 
    def init_ImageArchivePath(self):
        self.components.ImageArchivePath.text = ''

    def init_ImageROI(self):
        self.components.ImageROI.text = ''

    def init_BadPixelMap(self):
        self.components.BadPixelMap.text = ''

    def on_MedPathSel_mouseClick(self,event):        
        cdir = self.eval_line("pwd()")
        result = dialog.directoryDialog(self, 'Open', cdir)
        if result.accepted:
            dir = result.path
            dir = dir.replace("\\","\\\\")
            self.components.MedPath.text = dir
    
    def on_ImgPathSel_mouseClick(self,event):        
        cdir = self.eval_line("pwd()")
        result = dialog.directoryDialog(self, 'Open', cdir)
        if result.accepted:
            dir = result.path
            dir = dir.replace("\\","\\\\")
            self.components.ImagePath.text = dir
    
    def on_ImgArchivePathSel_mouseClick(self,event):        
        cdir = self.eval_line("pwd()")
        result = dialog.directoryDialog(self, 'Open', cdir)
        if result.accepted:
            dir = result.path
            dir = dir.replace("\\","\\\\")
            self.components.ImageArchivePath.text = dir

    def on_BadPixelMapSel_mouseClick(self,event):        
        cdir = self.eval_line("pwd()")
        result = dialog.fileDialog(self, 'Open', cdir,'',"*")
        if result.accepted:
            file = result.paths[0]
            if len(file) > 0:
                file = file.replace("\\","\\\\")
                self.components.BadPixelMap.text = file
            else:
                self.components.BadPixelMap.text = ''
                
    def UpdateGuiMedImgPar(self,reader):
        """
        update the GUI from reader
        """
        # spectra
        tmp = reader.spectra_path
        if tmp == None:
            self.components.MedPath.text = ''
        else:
            self.components.MedPath.text = str(tmp)
        self.components.ReadMed.checked = reader.spec_params['med']
        self.components.ReadXrf.checked = reader.spec_params['xrf']
        self.components.XrfLines.stringSelection = repr(reader.spectra_params['lines'])
        self.components.BadMcas.stringSelection = repr(reader.spectra_params['bad_mca_idx'])
        self.components.McaTaus.stringSelection = repr(reader.spectra_params['tau'])
        self.components.Emin.text = repr(reader.spectra_params['emin'])
        self.components.Emax.text = repr(reader.spectra_params['emax'])
        self.components.Total.checked = reader.spectra_params['total']
        self.components.Align.checked = reader.spectra_params['align'] 
        self.components.CorrectData.checked = reader.spectra_params['correct']
        # missing fields for det_idx and nfmt       
        
        # Now for images
        #reader.image_params = {'bad_pixel_map': None, 'rois': None,
        # 'fmt': 'tif', 'nfmt': 3, 'archive': None}
        self.components.ReadImg.checked = reader.spec_params['image']
        #
        tmp = reader.image_path
        if tmp == None:
            self.components.ImagePath.text = ''
        else:
            self.components.ImagePath.text = str(tmp)
        #
        tmp = reader.image_params.get('bad_pixel_map')
        if tmp != None:
            self.components.BadPixelMap.text = str(tmp)
        else:
            self.components.BadPixelMap.text = ''
        #
        self.components.ImageROI.text = repr(reader.image_params.get('rois'))
        #
        tmp = reader.image_params.get('archive')
        if tmp != None:
            arch_path = tmp.get('path')
            if arch_path != None:
                self.components.ImageArchivePath.text = str(arch_path)
            else:
                self.components.ImageArchivePath.text = ''
        
    def UpdateReaderMedImgPar(self):
        """
        update reader from GUI
        """
        reader = self.get_Reader()
        if reader == None: return
        #
        med_path = str(self.components.MedPath.text).strip()
        if len(med_path) > 0:
            reader.med_path=med_path
        else:
            reader.med_path=None
        #
        reader.spec_params['med'] = self.components.ReadMed.checked
        reader.spec_params['xrf'] = self.components.ReadXrf.checked
        #
        xrf_lines = str(self.components.XrfLines.stringSelection).strip()
        if len(xrf_lines) > 0:
            reader.spectra_params['lines'] = self.eval_line(xrf_lines)
        else:
            reader.spectra_params['lines'] = None
        #
        #bad_mcas  = str(self.components.BadMcas.stringSelection).strip()
        bad_mcas  = str(self.components.BadMcas.text).strip()
        if len(bad_mcas) > 0:
            reader.spectra_params['bad_mca_idx'] = self.eval_line(bad_mcas)
        else:
            reader.spectra_params['bad_mca_idx'] = []
        #
        mca_taus  = str(self.components.McaTaus.stringSelection).strip()
        if len(mca_taus) > 0:
            reader.spectra_params['tau'] = self.eval_line(mca_taus)
        else:
            reader.spectra_params['tau'] = None
        #
        emin = str(self.components.Emin.text).strip()
        if len(emin) > 0:
            reader.spectra_params['emin'] = self.eval_line(emin)
        else:
            reader.spectra_params['emin'] = -1.
        emax = str(self.components.Emax.text).strip()
        if len(emax) > 0:
            reader.spectra_params['emax'] = self.eval_line(emax)
        else:
            reader.spectra_params['emax'] = -1.
        #
        reader.spectra_params['total'] = self.components.Total.checked
        reader.spectra_params['align'] = self.components.Align.checked
        reader.spectra_params['correct'] = self.components.CorrectData.checked
        # missing fields for det_idx and nfmt
        
        # image stuff
        reader.spec_params['image'] = self.components.ReadImg.checked
        #
        image_path = str(self.components.ImagePath.text).strip()
        if len(image_path) > 0:
            reader.image_path=image_path
        else:
            reader.image_path=None
        #
        pixel_map = str(self.components.BadPixelMap.text).strip()
        if len(pixel_map) > 0:
            reader.image_params['bad_pixel_map']=pixel_map
        else:
            reader.image_params['bad_pixel_map']=None
        #
        rois = str(self.components.ImageROI.text).strip()
        if len(rois) > 0:
            reader.image_params['rois']=self.eval_line(rois)
        else:
            reader.image_params['rois']=None
        #
        arch_path = str(self.components.ImageArchivePath.text).strip()
        if len(arch_path) > 0:
            if reader.image_params['archive'] == None:
                reader.image_params['archive'] = {}
            reader.image_params['archive']['path']=arch_path
        else:
            if type(reader.image_params['archive']) == types.DictType:
                reader.image_params['archive']['path']=None
            
    def on_FitDeadtime_mouseClick(self,event):
        #reader_name = self.get_ReaderName()
        tau_name = str(self.components.McaTaus.text).strip()
        if len(tau_name) == 0:
            print "Please give a 'Tau' variable name"
        var_name = self.components.ScanVar.text
        x = str(self.components.DTX.stringSelection)
        norm = str(self.components.DTNorm.stringSelection)
        #s = "%s.spectra_params['tau'] = scandata.fit_deadtime(%s,"
        #s = s % (reader_name, var_name)
        #s = s + "x='io',y='Med',norm='Seconds')"
        s = "%s = ana.scan_data.fit_deadtime(%s,"  % (tau_name, var_name)
        s = s + "x='%s',y='Med',norm='%s')" % (x, norm)
        #print s
        self.exec_line(s)

    ######################################################

    ###########################################################
    #   Plot
    ###########################################################

    ######################################################
    def on_PlotScaler_mouseClick(self,event):
        var_name = self.components.ScanVar.text
        self._plot_scaler(var_name)
        
    def on_PlotMed_mouseClick(self,event):
        var_name = self.components.ScanVar.text
        self._plot_med(var_name)
        
    def on_PlotImg_mouseClick(self,event):
        var_name = self.components.ScanVar.text
        self._plot_img(var_name)

    def on_ScanPntMore_mouseClick(self,event):
        pts = self.components.ScanPnt.items
        max = int(pts[-1])
        curr = int(self.components.ScanPnt.stringSelection)
        more = curr + 1
        if more <= max:
            self.components.ScanPnt.stringSelection = str(more)
        self.ScanPnt_Click()

    def on_ScanPntLess_mouseClick(self,event):
        pts = self.components.ScanPnt.items
        min = int(pts[0])
        curr = int(self.components.ScanPnt.stringSelection)
        less = curr - 1
        if more >= mim:
            self.components.ScanPnt.stringSelection = str(less)
        self.ScanPnt_Click()

    def on_ScanPnt_keyDown(self,event):
        keyCode = event.keyCode
        if keyCode == wx.WXK_RETURN:
            self.ScanPnt_Click()
        else:
            event.skip()
        return

    def ScanPnt_Click(self):    
        var_name = self.components.ScanVar.text
        self._plot_med(var_name)
        self._plot_img(var_name)

    ######################################################
    def AutoPlot(self,var_name=None):
        if var_name == None:
            var_name = self.components.ScanVar.text
        if len(var_name.strip()) == 0:
            print "Please provide a scan variable name"
            return
        if self.components.ScalerPlot.checked:
            self._plot_scaler(var_name)
        if self.components.ReadMed.checked:
            self._plot_med(var_name)
        if self.components.ReadImg.checked:
            self._plot_img(var_name)

    ######################################################
    def _plot_scaler(self,var_name):
        from matplotlib import pyplot
        pyplot.ioff()
        pyplot.figure(1)
        hold = str(self.components.HoldCheck.checked)
        xlog = str(self.components.XlogCheck.checked)
        ylog = str(self.components.YlogCheck.checked)
        #
        deriv = self.components.ScalerDerivative.checked
        grid  = self.components.ScalerGrid.checked
        #
        x = self.components.XPlot.stringSelection
        y = self.components.YPlot.stringSelection
        norm = self.components.NormPlot.stringSelection
        #
        if len(norm.strip()) > 0:
            if deriv:
                s = "__dy__ = num.diff(%s['%s']/%s['%s'])" % (var_name,y,
                                                              var_name,norm)
                self.exec_line(s)
                s = "plot(%s['%s'][1:],__dy__" % (var_name,x)
            else:
                s = "plot(%s['%s'],%s['%s']/%s['%s']" % (var_name,x,
                                                         var_name,y,
                                                         var_name,norm)
        else:
            if deriv:
                s = "__dy__ = num.diff(%s['%s'])" %  (var_name,y)
                self.exec_line(s)
                s = "plot(%s['%s'][1:],__dy__" % (var_name,x)
            else:
                s = "plot(%s['%s'],%s['%s']" % (var_name,x,
                                                var_name,y)
        #
        s = s + ",xlog=%s,ylog=%s,hold=%s)" % (xlog,ylog,hold)
        #print s
        self.exec_line(s)
        #
        if grid:
            s = "pyplot.grid(True)"
            self.exec_line(s)
        pyplot.draw()
        pyplot.show()
        pyplot.ion()

    ######################################################
    def _plot_med(self,var_name):
        data = self.get_data(var_name)
        if data == None: return
        if hasattr(data,'med') == False: return
        if len(data.med.med) == 0: return
        from matplotlib import pyplot
        pyplot.ioff()
        pyplot.figure(2)
        hold = str(self.components.MedHold.checked)
        ylog = str(self.components.MedYlog.checked)
        pnt = int(self.components.ScanPnt.stringSelection)
        s = "ana.med_data.med_plot(%s.med,scan_pnt=%s,hold=%s,ylog=%s)" % (var_name,
                                                                           str(pnt),
                                                                           hold,
                                                                           ylog)
        #print s
        self.exec_line(s)
        pyplot.draw()
        pyplot.show()
        pyplot.ion()

    ######################################################
    def _plot_img(self,var_name):
        data = self.get_data(var_name)
        if data == None: return
        if hasattr(data,'image') == False: return
        if len(data.image.image) == 0: return
        from matplotlib import pyplot
        pyplot.ioff()
        pyplot.figure(3)
        pyplot.clf()
        pnt = int(self.components.ScanPnt.stringSelection)
        s = "ana.image_data.image_plot(%s.image.image[%s]" % (var_name,str(pnt))
        if self.components.ColorMap.stringSelection.strip()!='':
            cmap = self.components.ColorMap.stringSelection.strip()
            s = "%s,cmap='%s'" % (s,cmap)
        #
        reader = self.get_Reader()
        if reader.image_params.get('rois') != None:
            roi = repr(reader.image_params.get('rois'))
            s = "%s,roi=%s" % (s,roi)
        #
        s = "%s)" % s
        #print s
        self.exec_line(s)
        pyplot.draw()
        pyplot.show()
        pyplot.ion()
        
##################################################
if __name__ == '__main__':
    app = model.Application(wxXrayData)
    app.MainLoop()
