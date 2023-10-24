from numcodecs.abc import Codec
import numpy as np

class Range(Codec):
    """Codec providing range compression
    
    Parameters
    ----------
    """
    codec_id='range'
    
    def __init__(self, dtype=float):
        self.dtype = np.dtype(dtype)
        if self.dtype == object:
            raise ValueError('object arrays are not supported')
    
    def _get_start_stop_inc(self, array):
        start = array[0]
        stop = array[-1]
        delta = np.mean(array[1:] - array[0:-1])
        deltap = np.round(delta,2)
        if np.abs(delta-deltap) > 1e-10:
            print("Delta may not be accurate:", delta, deltap)
        return start, np.round(stop+deltap,2), deltap
    
    def encode(self,buf):
        info = self._get_start_stop_inc(np.frombuffer(buf,dtype=self.dtype))
        info = np.array([*info], dtype=self.dtype)
        return info.tobytes()
    
    def decode(self,buf):
        new_arr = np.arange(*[i for i in np.frombuffer(buf, dtype=self.dtype)], dtype=self.dtype)
        return new_arr    
