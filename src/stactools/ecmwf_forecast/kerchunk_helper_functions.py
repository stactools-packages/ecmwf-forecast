from kerchunk.combine import MultiZarrToZarr
from kerchunk.grib2 import scan_grib


def get_kerchunk_indices(part):
    
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
        
    return mzz.translate()