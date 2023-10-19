from kerchunk.combine import MultiZarrToZarr
from kerchunk.grib2 import scan_grib
from numcodecs.registry import register_codec
from range_codec import Range

import base64
import fsspec
import numpy as np

register_codec(Range)

def get_kerchunk_indices(part):

    #clear instance cache, prevents memory leak
    fs = fsspec.filesystem('')
    fs.clear_instance_cache()

    out = scan_grib(part.filename)

    if (((part.stream=='scda')|(part.stream=='oper')) & (part.type=='fc')):
        messages_iso = [out[i] for i in range(len(out)) if 'isobaricInhPa/.zarray' in list(out[i]['refs'].keys())]
        mzz = MultiZarrToZarr(messages_iso,
                              concat_dims = ['time','isobaricInhPa'])
        d1 = mzz.translate()

        messages_not_iso = [out[i] for i in range(len(out)) if 'isobaricInhPa/.zarray' not in list(out[i]['refs'].keys())]
        mzz = MultiZarrToZarr(messages_not_iso,
                              identical_dims = ['depthBelowLandLayer','entireAtmosphere','heightAboveGround','meanSea','surface'],
                              concat_dims = ['time'])
        d2 = mzz.translate()
        mzz = MultiZarrToZarr([d1,d2],
                              identical_dims = ['depthBelowLandLayer','entireAtmosphere','heightAboveGround','meanSea','surface'],
                              concat_dims = ['time'])
        
    elif ((part.stream=='enfo') & (part.type=='ep')):
        mzz = MultiZarrToZarr(out,
                              identical_dims = ['heightAboveGround','isobaricInhPa','surface','meanSea'],
                              concat_dims = ['step','time'])
    
    elif ((part.stream=='waef') & (part.type=='ef')):
        mzz = MultiZarrToZarr(out,
                              concat_dims = ['number','time'])
        
    elif ((part.stream=='waef') & (part.type=='ep')):
        mzz = MultiZarrToZarr(out,
                              identical_dims = ['meanSea'],
                              concat_dims = ['step','time'])
    
    elif (((part.stream=='scwv')|(part.stream=='wave')) & (part.type=='fc')):
        mzz = MultiZarrToZarr(out,
                              concat_dims = ['time'])
        
    return compress_lat_lon(mzz.translate())

def compress_lat_lon(d):
    d['refs']['latitude/0'] = 'base64:' + base64.b64encode(Range().encode(base64.b64decode(d['refs']['latitude/0'][7:]))).decode()
    d['refs']['longitude/0'] = 'base64:' + base64.b64encode(Range().encode(base64.b64decode(d['refs']['longitude/0'][7:]))).decode()
    d['refs']['latitude/.zarray'] = ','.join([':'.join([i.split(':')[0],'[{"id": "range"}]']) if 'filter' in i else i for i in d['refs']['latitude/.zarray'].split(',')])
    d['refs']['longitude/.zarray'] = ','.join([':'.join([i.split(':')[0], '[{"id": "range"}]']) if 'filter' in i else i for i in d['refs']['longitude/.zarray'].split(',')])
    
    return d

def get_start_stop_inc(array):
    start = array[0]
    stop = array[-1]
    delta = np.mean(array[1:] - array[0:-1])
    deltap = np.round(delta,2)
    if np.abs(delta-deltap) > 1e-10:
        print("Delta may not be accurate:", delta, deltap)
    return start, np.round(stop+deltap,2), deltap
