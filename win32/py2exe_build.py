#
"""
Important note:
seeing errors in build with python setup.py py2exe?

move whole directory to a non-networked drive!

"""
##
from distutils.core import setup
# from setuptools import setup
import py2exe
import sys
import os
import shutil
import numpy
import scipy
import matplotlib
import h5py
import Image
import Ifeffit
import wx
import PythonCard
import ctypes
import ctypes.util
from numpy import sort

import scipy.io.netcdf
from scipy.io.netcdf import netcdf_file
import scipy.constants

from tdl.pds import menu

loadlib =  ctypes.windll.LoadLibrary


# larch library bits...
# from larch.larchlib import get_dll
# cllib = get_dll('cldata')

# matplotlib, wxmplot
matplotlib.use('WXAgg')
mpl_data_files = matplotlib.get_py2exe_datafiles()
# import wxmplot

pycard_incs = ['PythonCard', 'PythonCard.model', 'PythonCard.dialog',
               'PythonCard.components.bitmapcanvas',
               'PythonCard.components.button',
               'PythonCard.components.calendar',
               'PythonCard.components.checkbox',
               'PythonCard.components.choice',
               'PythonCard.components.codeeditor',
               'PythonCard.components.combobox',
               'PythonCard.components.container',
               'PythonCard.components.floatcanvas',
               'PythonCard.components.gauge',
               'PythonCard.components.grid',
               'PythonCard.components.htmlwindow',
               'PythonCard.components.iehtmlwindow',
               'PythonCard.components.image',
               'PythonCard.components.imagebutton',
               'PythonCard.components.list',
               'PythonCard.components.multicolumnlist',
               'PythonCard.components.notebook',
               'PythonCard.components.passwordfield',
               'PythonCard.components.radiogroup',
               'PythonCard.components.slider',
               'PythonCard.components.spinner',
               'PythonCard.components.staticbox',
               'PythonCard.components.staticline',
               'PythonCard.components.statictext',
               'PythonCard.components.textarea',
               'PythonCard.components.textfield',
               'PythonCard.components.togglebutton',
               'PythonCard.components.tree']

tdl_incs = ['tdl.modules.ana',
            'tdl.modules.ana_upgrade',
            'tdl.modules.geom',
            'tdl.modules.peak',
            'tdl.modules.specfile',
            'tdl.modules.spectra',
            'tdl.modules.sxrd',
            'tdl.modules.utils',
            'tdl.modules.utils.files',
            'tdl.modules.utils.mpfit',
            'tdl.modules.xrd',
            'tdl.modules.xrf',
            'tdl.modules.xrr',
            'tdl.modules.xtab',
            'tdl.modules.xtal',
            'tdl.pds.pcgui',
            'tdl.pds.menu']



extra_files = ['TDL.ico']
scipy_dlls = ['lib/site-packages/scipy/optimize/minpack2.pyd',
              'lib/site-packages/scipy/interpolate/dftipack.pyd',
              'lib/site-packages/scipy/integrate/_quadpack.pyd',
              'lib/site-packages/numpy/fft/fftpack_lite.pyd']


dlldir = os.path.join(sys.prefix, 'DLLs')
for n in os.listdir(dlldir):
    extra_files.append(os.path.join(dlldir, n))

for n in scipy_dlls:
    extra_files.append(os.path.join(sys.prefix, n))

style_xml = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="PDS"
    type="win32"
  />
  <description>PDS</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
            level="asInvoker"
            uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
            type="win32"
            name="Microsoft.VC90.CRT"
            version="9.0.21022.8"
            processorArchitecture="x86"
            publicKeyToken="1fc8b3b9a1e18e3b">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
  </dependency>
</assembly>
"""

windows_apps = [{'script': 'runpds.py',
                 'icon_resources': [(0, 'TDL.ico')],
                 'other_resources': [(24, 1, style_xml)],
                 },
                ]


py2exe_opts = {'optimize':1,
               'bundle_files':2,
               'includes': ['ConfigParser', 'Image', 'ctypes',
                            'fpformat', 'h5py', 'Ifeffit',
                            'h5py._objects', 'h5py._proxy', 'h5py.defs',
                            'h5py.utils', 'matplotlib', 'numpy', 'scipy',
                            'scipy.constants', 'scipy.fftpack',
                            'scipy.io.matlab.mio5_utils',
                            'scipy.io.matlab.streams', 'scipy.io.netcdf',
                            'scipy.optimize', 'scipy.signal',
                            'sqlite3', 'wx', 'wx._core',
                            'wx.lib', 'wx.lib.agw',
                            'wx.lib.agw.flatnotebook',
                            'wx.lib.colourselect', 'wx.lib.masked',
                            'wx.lib.mixins', 'wx.lib.mixins.inspection',
                            'wx.lib.agw.pycollapsiblepane',
                            'wx.lib.newevent', 'wx.py',
                            'wxversion', 'xdrlib', 'xml.etree',
                            'xml.etree.cElementTree'],
               'packages': ['h5py', 'scipy.optimize', 'scipy.signal', 'scipy.io',
                            'numpy.random', 'xml.etree', 'xml.etree.cElementTree'],
               'excludes': ['Tkinter', '_tkinter', 'Tkconstants', 'tcl',
                            '_imagingtk', 'PIL._imagingtk', 'ImageTk',
                            'PIL.ImageTk', 'FixTk''_gtkagg', '_tkagg',
                            'matplotlib.tests', 'qt', 'PyQt4Gui', 'IPython',
                            'pywin', 'pywin.dialogs', 'pywin.dialogs.list'],
               'dll_excludes': ['w9xpopen.exe',
                                'libgdk-win32-2.0-0.dll',
                                'libgobject-2.0-0.dll', 'libzmq.dll']
               }
py2exe_opts['includes'].extend(pycard_incs)
py2exe_opts['includes'].extend(tdl_incs)
setup(name = "TDL",
      windows = windows_apps,
      options = {'py2exe': py2exe_opts},
      data_files = mpl_data_files)

for fname in extra_files:
    path, name = os.path.split(fname)
    print fname, name
    try:
        shutil.copy(fname, os.path.join('dist', name))
    except:
        pass



def sys(cmd):
    print ' >> ', cmd
    os.system(cmd)

try:
    os.makedirs("dist/tdl/")
    os.makedirs("dist/tdl/modules")
except:
    pass
sys("cp -pr ../modules   dist/tdl/." )
sys("cp -pr ../pds/startup.pds   dist/tdl/." )
sys("cp -pr ../dlls/win32/* dist/.")

if __name__ == '__main__':
    print 'usage:  python py2exe_build.py py2exe'

