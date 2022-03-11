# -*- coding: utf-8 -*-
"""
Module for reading in HDF5 data from the PIP code 
"""

def pipread(fname):
    import h5py
    import numpy as np
    with h5py.File(fname, "r") as f:
        # List all groups
        print("Keys: %s" % f.keys())

        # Get the data
        data={}
        for param in f:
            ref_data = np.array(f[param])
            data[param]=ref_data
            
        data=cv2pv(data)
        
        return(data)
    
def pipread2(fname):
    #Old version for testing
    #Not used
    import h5py
    import numpy as np
    with h5py.File(fname, "r") as f:
        # List all groups
        print("Keys: %s" % f.keys())

        # Get the data
        #data = list(f[a_group_key])
        ro_p=np.array(f['ro_p'])
        bx=np.array(f['bx'])
        by=np.array(f['by'])
        bz=np.array(f['bz'])
        mx_p=np.array(f['mx_p'])
        my_p=np.array(f['my_p'])
        mz_p=np.array(f['mz_p'])
        en_p=np.array(f['en_p'])
        
        xg=list(f['xgrid'])
        yg=list(f['ygrid'])
        zg=list(f['zgrid'])
        
        data={'ro_p':ro_p,'bx':bx,'by':by,'bz':bz,
              'mx_p':mx_p,'my_p':my_p,'mz_p':mz_p,'en_p':en_p,
              'x':xg,'y':yg,'z':zg}
        
        return(data)
    
def cv2pv(data):
    import numpy as np
    gm=5.0/3.0
    xg=data["xgrid"]
    yg=data["ygrid"]
    zg=data["zgrid"]
    ro_p=data["ro_p"]
    vx_p=data["mx_p"]/data["ro_p"]
    vy_p=data["my_p"]/data["ro_p"]
    vz_p=data["mz_p"]/data["ro_p"]
    bx=data["bx"]
    by=data["by"]
    bz=data["bz"]
    pr_p=(gm-1.0)*(data["en_p"]-0.5*data["ro_p"]*(np.square(vx_p)+np.square(vy_p)+np.square(vz_p))
                   -0.5*(np.square(bx)+np.square(by)+np.square(bz)))
    
    dataout={'ro_p':ro_p,'bx':bx,'by':by,'bz':bz,
              'vx_p':vx_p,'vy_p':vy_p,'vz_p':vz_p,'pr_p':pr_p,
              'xgrid':xg,'ygrid':yg,'zgrid':zg}
    return(dataout)