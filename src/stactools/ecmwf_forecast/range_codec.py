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
        diffs = array[1:] - array[0:-1]
        delta = np.mean(diffs)
        max_diff = np.max(np.abs(delta-diffs))
        if max_diff > 1e-10:
            print("Delta may not be accurate:", delta, max_diff)
        return start, stop+delta, delta
    
    def encode(self,buf):
        info = self._get_start_stop_inc(np.frombuffer(buf,dtype=self.dtype))
        info = np.array([*info], dtype=self.dtype)
        return info.tobytes()
    
    def decode(self,buf):
        new_arr = np.arange(*[i for i in np.frombuffer(buf, dtype=self.dtype)], dtype=self.dtype)
        return new_arr   
