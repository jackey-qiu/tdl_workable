"""
Read EMSA detector files

This module is out of data and needs updating...

Authors/Modifications:
----------------------

"""
#########################################################################

import numpy as num
import os

from tdl.modules.spectra.mca import Mca
from tdl.modules.spectra.med import Med

#########################################################################
# Read Files
#########################################################################

##########################################################################
def read_med(file):
    """
    Reads a disk file into an Med object.

    The file contains the information from the Med object
     which it makes sense to store permanently, but does
    not contain all of the internal state information for the Med.

    Parameters:
    -----------
    * file: The name of the disk file to read.
    """
    r = read_ascii_file(file)

    if r == None: return None
    
    n_detectors = r['n_detectors']
    path, fname = os.path.split(file)
    med = Med(n_detectors=n_detectors, name=fname)

    med.mca = []
    for i in range(n_detectors):
        med.mca.append(Mca())
        med.mca[i].set_rois(r['rois'][i])
        med.mca[i].set_data(r['data'][i])
        med.mca[i].set_name(fname + ':' + str(i))
    med.set_elapsed(r['elapsed'])
    med.set_calibration(r['calibration'])
    med.set_environment(r['environment'])

    return med

########################################################################
def read_ascii_file(file):
    """
    Reads a disk file.  The file format is a tagged ASCII format.
    
    The file contains the information from the Mca object which it makes sense
    to store permanently, but does not contain all of the internal state
    information for the Mca.  This procedure reads files written with
    write_ascii_file().

    Parameters:
    -----------
    * file: The name of the disk file to read.
            
    Outputs:
    --------
    * Returns a dictionary of the following type:
      'n_detectors': int,
      'calibration': [McaCalibration()],
      'elapsed':     [McaElapsed()],
      'rois':        [[McaROI()]]
      'data':        [numpy.array]
      'environment': [[McaEnvironment()]]
        
    Example:
    --------
    >>m = read_ascii_file('mca.001')
    >>m['elapsed'][0].real_time
    """
    try:
        fp = open(file, 'r')
    except:
        print "File not found"
        return None
    
    line = ''
    start_time = ''
    xunits = 'kev'
    data = None

    environment = []
    n_detectors = 1  # Assume single element data
    elapsed = [mca.McaElapsed()]
    calibration = [mca.McaCalibration()]
    rois = [[]]
    
    while(1):
        line = fp.readline()
        if (line == ''): break

        # get header info
        if line[0] == '#':
            tmp = line[1:].split(':')
            tag = tmp.pop(0).strip()
            values = []
            for val in tmp:
                values.append(val.strip())
        else:
            print "Error reading file"
            break
        #print 'tag=', tag
        #print 'values =', values
        if (tag == 'FORMAT'):
            pass
        elif (tag == 'VERSION'):  
            pass
        elif (tag == 'TITLE'):
            pass
        elif (tag == 'DATE'):
            pass
        elif (tag == 'TIME'):
            start_time = values[0]
        elif (tag == 'OWNER'):
            start_time = start_time + values[0]
        elif (tag == 'NPOINTS'):
            nchans = int(float(values[0]))
        elif (tag == 'NCOLUMNS'):
            n_detectors  = int(float(values[0]))
            for det in range(1, n_detectors):
                 elapsed.append(mca.McaElapsed())
                 calibration.append(mca.McaCalibration())
                 rois.append([])
        elif (tag == 'REALTIME'):
            for d in range(n_detectors):
                elapsed[d].start_time = start_time
                elapsed[d].real_time = float(values[d])
        elif (tag == 'LIVETIME'):  
            for d in range(n_detectors):
                elapsed[d].live_time = float(values[d])
        elif (tag == 'XUNITS'):
            xunits = values[0]
        elif (tag == 'XPERCHAN'):
            for d in range(n_detectors):
                calibration[d].slope = float(values[d])
        elif (tag == 'OFFSET'):
            for d in range(n_detectors):
                calibration[d].offset = float(values[d])
        elif (tag == 'SPECTRUM'):
            data = []
            for d in range(n_detectors):
                data.append(num.zeros(nchans, 'i'))
            for chan in range(nchans):
                line = fp.readline()
                counts = line.split(',')
                for d in range(n_detectors):
                    data[d][chan]=int(float(counts[d]))
            for d in range(n_detectors):
                elapsed[d].total_counts = sum(data[d])
        else:
            #print 'Unknown tag = '+tag+' in file: ' + file + '.'
            pass

    # Make sure DATA array is defined, else this was not a valid data file
    if (data == None): print 'Not a valid data file: ' + file + '.'
    fp.close()
    # Built dictionary to return
    r = {}
    r['n_detectors'] = n_detectors
    r['calibration'] = calibration
    r['elapsed'] = elapsed
    r['rois'] = rois
    r['data'] = data
    r['environment'] = environment
    return r


