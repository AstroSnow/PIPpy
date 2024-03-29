# -*- coding: utf-8 -*-
"""
Module for reading in HDF5 data from the PIP code 
"""

def pipread(fname,tstep=-1,vararrin='all',exrates=0):
    #import h5py
    import numpy as np
    import glob
    confdir=[fname,'config.txt']
    confdir=''.join(confdir) #Get the config for the simulation
    with open(confdir) as fp:
       line = fp.readline()
       cnt = 1
       lend=0
       conf={}
       while lend==0:
           #print("Line {}: {}".format(cnt, line.strip()))
           lar=line.strip()
           lar=lar.split(':',1)
           larn=lar[0].strip()
           larv=lar[1].strip()
           conf[larn]=larv
           line = fp.readline()
           cnt += 1
           if line.strip()=='ENDSETTING':
               lend=1
#        dict(line.split(':', 1) for line in open(''.join(confdir)))
#    print(conf)
    vararr=[]
    varex=[]
    if (vararrin=='all'):
        if (conf['flag_eqs'] == 'MHD'):
            vararr=['ro_p','mx_p','my_p','mz_p','en_p','bx','by','bz','xgrid','ygrid','zgrid']
        if (conf['flag_eqs'] == 'HD'):
            vararr=['ro_n','mx_n','my_n','mz_n','en_n','xgrid','ygrid','zgrid']
        if (conf['flag_eqs'] == 'PIP'):
            vararr=['ac','ro_p','mx_p','my_p','mz_p','en_p','ro_n','mx_n','my_n','mz_n','en_n','bx','by','bz','xgrid','ygrid','zgrid']
    if (vararr!='all'):
        for param in vararrin:
            if param=='ro_p':
                vararr.append('ro_p')
            if param=='ro_n':
                vararr.append('ro_n')
            if param=='vx_p':
                vararr.append('ro_p')
                vararr.append('mx_p')
            if param=='vy_p':
                vararr.append('ro_p')
                vararr.append('my_p')
            if param=='vz_p':
                vararr.append('ro_p')
                vararr.append('mz_p')
            if param=='bx':
                vararr.append('bx')
            if param=='by':
                vararr.append('by')
            if param=='bz':
                vararr.append('bz')
            if param=='pr_p':
                vararr.append('ro_p')
                vararr.append('mx_p')
                vararr.append('my_p')
                vararr.append('mz_p')
                vararr.append('bx')
                vararr.append('by')
                vararr.append('bz')
                vararr.append('en_p')
#        vararr=vararrin
        vararr.append('xgrid')
        vararr.append('ygrid')
        vararr.append('zgrid')
        vararr.append('time')
        if (conf['flag_rad'] == '1') or (conf['flag_rad'] >= '2') and (conf['flag_IR'] == '0'):
            vararr.append('edref_m')
            varex.append('edref_m')
        vararr=set(vararr)
    print(vararr)
    if (tstep != -1): 
        print("loading single time step")
        fname=''.join([fname,'t',"{:0>4d}".format(tstep),'.h5'])
        data=pipreadtimestep(fname,vararr)
    
    if tstep ==-1:
        print("reading in all time steps")
        timeCounter = len(glob.glob1(fname,"*.h5"))
        print(timeCounter)
        itco=0
        for t0 in sorted(glob.glob1(fname,"*.h5")):
            #t0=0
            fnamet=''.join([fname,t0])
            print(fnamet)
            datatemp=pipreadtimestep(fnamet,vararr)
            if itco != 0:
                for param in datatemp:
                    if param != 'xgrid' and param!='ygrid' and param!='zgrid':
                        ref_data = datatemp[param]
#                        print(ref_data.shape,data[param].shape)
#                        data[param]=np.stack((data[param],ref_data),axis=-1)
                        data[param]=np.concatenate([data[param],ref_data[...,np.newaxis]],axis=-1)
#                        data[param]=data[param].append(ref_data)  
            if itco == 0:
                data=datatemp
                for param in datatemp:
                    if param != 'xgrid' and param!='ygrid' and param!='zgrid':
                        data[param]=data[param][...,np.newaxis]
                itco=1 
                    
    
    if (vararrin == 'all'):
        data=cv2pv(data,conf['flag_eqs'],varex)
    if (vararrin != 'all'):
        data=cv2pvvar(data,vararrin)

#Ancillary file reading
#Radiative losses
    if (conf['flag_rad'] == '1') or (conf['flag_rad'] >= '2'):
#        vararr.append('edref_m')
        #if (conf['flag_IR'] == '0'):
            #datatemp=pipreadtimestep(fname,["edref_m"])    
            #data["edref_m"]=datatemp["edref_m"]
        if (conf['flag_IR'] >= '1'):
            datatemp=pipreadtimestep(fname,["ion_rad",'rec_rad'])    
            data["ion_rad"]=datatemp["ion_rad"]
            data["rec_rad"]=datatemp["rec_rad"]
    
#Ionisation and recombination        
    if (conf['flag_IR'] >= '1') and (conf['flag_eqs']=='PIP'):
        vararrtemp=["ion","rec"]
        if (conf['flag_IR_type'] == '0'):
            vararrtemp=["ion","rec","ion_loss","aheat"]
        if (tstep != -1): 
            datatemp=pipreadtimestep(fname,vararrtemp)    
            for param in datatemp:
                data[param]=datatemp[param]
        if tstep ==-1:
            timeCounter = len(glob.glob1(fname,"*.h5"))
            itco=0
            for t0 in sorted(glob.glob1(fname,"*.h5")):
                #t0=0
                fnamet=''.join([fname,t0])
                datatemp=pipreadtimestep(fnamet,vararrtemp)
                if itco != 0:
                    for param in datatemp:
                        if param != 'xgrid' and param!='ygrid' and param!='zgrid':
                            ref_data = datatemp[param]
                            data[param]=np.concatenate([data[param],ref_data[...,np.newaxis]],axis=-1)
                if itco == 0:
                    for param in datatemp:
                        if param != 'xgrid' and param!='ygrid' and param!='zgrid':
                            data[param]=datatemp[param][...,np.newaxis]
                    itco=1 

#Nlevel hydrogen        
    if (conf['flag_IR'] == '4') and (conf['flag_eqs']=='PIP'):
        if (tstep != -1): 
            datatemp=pipreadtimestep(fname,["nexcite1","nexcite2","nexcite3","nexcite4","nexcite5","nexcite6"])    
            for param in datatemp:
                data[param]=datatemp[param]
        if tstep ==-1:
            timeCounter = len(glob.glob1(fname,"*.h5"))
            itco=0
            for t0 in sorted(glob.glob1(fname,"*.h5")):
                #t0=0
                fnamet=''.join([fname,t0])
                datatemp=pipreadtimestep(fnamet,["nexcite1","nexcite2","nexcite3","nexcite4","nexcite5","nexcite6"])
                if itco != 0:
                    for param in datatemp:
                        if param != 'xgrid' and param!='ygrid' and param!='zgrid':
                            ref_data = datatemp[param]
    #                        print(ref_data.shape,data[param].shape)
    #                        data[param]=np.stack((data[param],ref_data),axis=-1)
                            data[param]=np.concatenate([data[param],ref_data[...,np.newaxis]],axis=-1)
    #                        data[param]=data[param].append(ref_data)  
                if itco == 0:
                    for param in datatemp:
                        if param != 'xgrid' and param!='ygrid' and param!='zgrid':
                            data[param]=datatemp[param][...,np.newaxis]
                    itco=1 
        if ((tstep !=-1) and (exrates==1)):
            #Create the array for the excitation rates
            datatemp=pipreadtimestep(fname,['colrat11'])
            data['colrat']=0.0*datatemp['colrat11'][...,np.newaxis,np.newaxis]
            data['colrat']=np.concatenate([data['colrat'],0.0*datatemp['colrat11'][...,np.newaxis,np.newaxis]],axis=1)
            data['colrat']=np.concatenate([data['colrat'],0.0*datatemp['colrat11'][...,np.newaxis,np.newaxis]],axis=1)
            data['colrat']=np.concatenate([data['colrat'],0.0*datatemp['colrat11'][...,np.newaxis,np.newaxis]],axis=1)
            data['colrat']=np.concatenate([data['colrat'],0.0*datatemp['colrat11'][...,np.newaxis,np.newaxis]],axis=1)
            data['colrat']=np.concatenate([data['colrat'],0.0*datatemp['colrat11'][...,np.newaxis,np.newaxis]],axis=1)
            data['colrat']=np.concatenate([data['colrat'],0.0*datatemp['colrat11'][...,np.newaxis,np.newaxis]],axis=1)
            
            data['colrat']=np.concatenate([data['colrat'],data['colrat']],axis=2)
            data['colrat']=np.concatenate([data['colrat'],data['colrat']],axis=2)
            datatemp=data['colrat'][:,:,1]
            data['colrat']=np.concatenate([data['colrat'],datatemp[:,:,np.newaxis]],axis=2)
            data['colrat']=np.concatenate([data['colrat'],datatemp[:,:,np.newaxis]],axis=2)
            data['colrat']=np.concatenate([data['colrat'],datatemp[:,:,np.newaxis]],axis=2)
            
            #print(np.size(data['colrat']))
            for i in range(1,7):
                for j in range(1,7):
                    creadname=''.join(['colrat',"{:0>1d}".format(i),"{:0>1d}".format(j)])
                    #print(creadname)
                    datatemp=pipreadtimestep(fname,[creadname])
                    data['colrat'][:,i,j]=datatemp[creadname]
#                    data['colrat']=np.concatenate([data['colrat'],datatemp[creadname][...,np.newaxis,np.newaxis]],axis=-1)
            if (conf['flag_IR_type'] == '0') and (conf['flag_rad'] >= '2'):
                datatemp=pipreadtimestep(fname,['radrat11'])
                data['radrat']=0.0*datatemp['radrat11'][...,np.newaxis,np.newaxis]
                data['radrat']=np.concatenate([data['radrat'],0.0*datatemp['radrat11'][...,np.newaxis,np.newaxis]],axis=1)
                data['radrat']=np.concatenate([data['radrat'],0.0*datatemp['radrat11'][...,np.newaxis,np.newaxis]],axis=1)
                data['radrat']=np.concatenate([data['radrat'],0.0*datatemp['radrat11'][...,np.newaxis,np.newaxis]],axis=1)
                data['radrat']=np.concatenate([data['radrat'],0.0*datatemp['radrat11'][...,np.newaxis,np.newaxis]],axis=1)
                data['radrat']=np.concatenate([data['radrat'],0.0*datatemp['radrat11'][...,np.newaxis,np.newaxis]],axis=1)
                data['radrat']=np.concatenate([data['radrat'],0.0*datatemp['radrat11'][...,np.newaxis,np.newaxis]],axis=1)
                
                data['radrat']=np.concatenate([data['radrat'],data['radrat']],axis=2)
                data['radrat']=np.concatenate([data['radrat'],data['radrat']],axis=2)
                datatemp=data['radrat'][:,:,1]
                data['radrat']=np.concatenate([data['radrat'],datatemp[:,:,np.newaxis]],axis=2)
                data['radrat']=np.concatenate([data['radrat'],datatemp[:,:,np.newaxis]],axis=2)
                data['radrat']=np.concatenate([data['radrat'],datatemp[:,:,np.newaxis]],axis=2)
                
                #print(np.size(data['colrat']))
                for i in range(1,7):
                    for j in range(1,7):
                        creadname=''.join(['radrat',"{:0>1d}".format(i),"{:0>1d}".format(j)])
                        #print(creadname)
                        datatemp=pipreadtimestep(fname,[creadname])
                        data['radrat'][:,i,j]=datatemp[creadname]
    #                    data['colrat']=np.concatenate([data['colrat'],datatemp[creadname][...,np.newaxis,np.newaxis]],axis=-1)
    return(data)

###############################################################################    
def pipreadtimestep(fname,vararr):
    import h5py
    import numpy as np
    with h5py.File(fname, "r") as f:
        # List all groups
        #print("Keys: %s" % f.keys())

        # Get the data
        data={}
        for param in vararr:
#            print(param)
            ref_data = np.array(f[param])
#            if (param != 'dx') and (param != 'dy') and (param != 'dz') and (param != 'xgrid') and (param != 'ygrid') and (param != 'zgrid'):
#                ref_data=np.transpose(ref_data,(2, 1, 0)) #convert it to x,y,z
            data[param]=np.squeeze(ref_data)
            
        return(data)
            
        
###############################################################################        
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
        ro_p=np.transpose(np.array(f['ro_p']),(2, 1, 0))
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

###############################################################################    
def cv2pv(data,flag_eqs,varex):
    import numpy as np
    gm=5.0/3.0
    xg=data["xgrid"]
    yg=data["ygrid"]
    zg=data["zgrid"]
    time=data["time"]
    if (flag_eqs == 'MHD'):
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
                  'xgrid':xg,'ygrid':yg,'zgrid':zg,'time':time}
    if (flag_eqs == 'HD'):
        ro_n=data["ro_n"]
        vx_n=data["mx_n"]/data["ro_n"]
        vy_n=data["my_n"]/data["ro_n"]
        vz_n=data["mz_n"]/data["ro_n"]
        pr_n=(gm-1.0)*(data["en_n"]-0.5*data["ro_n"]*(np.square(vx_n)+np.square(vy_n)+np.square(vz_n)))
        
        dataout={'ro_n':ro_n,'vx_n':vx_n,'vy_n':vy_n,'vz_n':vz_n,'pr_n':pr_n,
                  'xgrid':xg,'ygrid':yg,'zgrid':zg,'time':time}
        
    if (flag_eqs == 'PIP'):
        ro_p=data["ro_p"]
        vx_p=data["mx_p"]/data["ro_p"]
        vy_p=data["my_p"]/data["ro_p"]
        vz_p=data["mz_p"]/data["ro_p"]
        bx=data["bx"]
        by=data["by"]
        bz=data["bz"]
        pr_p=(gm-1.0)*(data["en_p"]-0.5*data["ro_p"]*(np.square(vx_p)+np.square(vy_p)+np.square(vz_p))
                       -0.5*(np.square(bx)+np.square(by)+np.square(bz)))
        ro_n=data["ro_n"]
        vx_n=data["mx_n"]/data["ro_n"]
        vy_n=data["my_n"]/data["ro_n"]
        vz_n=data["mz_n"]/data["ro_n"]
        pr_n=(gm-1.0)*(data["en_n"]-0.5*data["ro_n"]*(np.square(vx_n)+np.square(vy_n)+np.square(vz_n)))
        
        ac=data["ac"]
        dataout={'ro_p':ro_p,'bx':bx,'by':by,'bz':bz,'vx_p':vx_p,'vy_p':vy_p,'vz_p':vz_p,'pr_p':pr_p,
                 'ro_n':ro_n,'vx_n':vx_n,'vy_n':vy_n,'vz_n':vz_n,'pr_n':pr_n,
                 'xgrid':xg,'ygrid':yg,'zgrid':zg,'time':time,'ac':ac}       
    for param in varex:
        if (param == "edref_m"):
            edref_m=data["edref_m"]
            dataout["edref_m"]=edref_m
    return(dataout)

###############################################################################    
def cv2pvvar(data,vararr):
    import numpy as np
    gm=5.0/3.0
    dataout={}
    xg=data["xgrid"]
    yg=data["ygrid"]
    zg=data["zgrid"]
    time=data["time"]
    dataout={'xgrid':xg,'ygrid':yg,'zgrid':zg,'time':time}
    for param in vararr:
        if param =='xgrid':
            temparr=data['xgrid']
        if param =='ygrid':
            temparr=data['ygrid']
        if param =='zgrid':
            temparr=data['zgrid']
        if param == "ro_p":
            temparr=data["ro_p"]
        if param == "vx_p":
            temparr=data["mx_p"]/data["ro_p"]
        if param == "vy_p":
            temparr=data["my_p"]/data["ro_p"]
        if param == "vz_p":
            temparr=data["mz_p"]/data["ro_p"]
        if param == "bx":
            temparr=data["bx"]
        if param == "by":
            temparr=data["by"]
        if param == "bz":
            temparr=data["bz"]
        if param == "pr_p":
            temparr=(gm-1.0)*(data["en_p"]-0.5/data["ro_p"]*(np.square(data["mx_p"])+np.square(data["my_p"])+np.square(data["mz_p"]))
                   -0.5*(np.square(data["bx"])+np.square(data["by"])+np.square(data["bz"])))
        if param == "ro_n":
            temparr=data["ro_n"]
        if param == "vx_n":
            temparr=data["mx_n"]/data["ro_n"]
        if param == "vy_n":
            temparr=data["my_n"]/data["ro_n"]
        if param == "vz_n":
            temparr=data["mz_n"]/data["ro_n"]
        if param == "pr_n":
            temparr=(gm-1.0)*(data["en_n"]-0.5/data["ro_n"]*(np.square(data["mx_n"])+np.square(data["my_n"])+np.square(data["mz_n"])))
        dataout[param]=temparr
#    dataout={'ro_p':ro_p,'bx':bx,'by':by,'bz':bz,
#              'vx_p':vx_p,'vy_p':vy_p,'vz_p':vz_p,'pr_p':pr_p,
#              'xgrid':xg,'ygrid':yg,'zgrid':zg}
    return(dataout)

###############################################################################

def getTimeSteps(ds):
	import numpy as np
	
	print('Calculate the timesteps in each cell. CURRENTLY MHD ONLY')
	
	ts={} #return variable
	
	#Constants
	print('Assuming usual constants and ignoring Safety')
	gamma=5.0/3.0
	
	##################################
	#MHD CFL condition
	gmin=min(ds['xgrid'][1]-ds['xgrid'][0],ds['ygrid'][1]-ds['ygrid'][0],ds['zgrid'][1]-ds['zgrid'][0])
	cs2=gamma*ds['pr_p']/ds['ro_p']
	va2=(np.square(ds['bx'])+np.square(ds['by'])+np.square(ds['bz']))/ds['ro_p']
	vabs=np.sqrt(np.square(ds['vx_p'])+np.square(ds['vy_p'])+np.square(ds['vz_p']))
	dt_mhd=gmin/(vabs+np.sqrt(cs2+va2))
	ts['dt_mhd']=dt_mhd
	##################################
	#Radiative CFL condition
	try:
		ts_rad=ds['edref_m']*np.square(ds['ro_p'])/(ds['pr_p']/(gamma-1.0))
		dt_rad=1.0/ts_rad
		ts['dt_rad']=dt_rad
	except:
		pass
	
	return(ts)