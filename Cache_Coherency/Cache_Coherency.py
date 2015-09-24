#!/usr/bin/python

import getopt
import sys
import os
import subprocess
import re
import shlex
import logging
import threading
import filecmp
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )   

def getpath(argv):
    runcmd = ''
    tracepath = ''
    outputpath = ''
    inputpath = ''
    try:
        opts, args = getopt.getopt(argv,"hr:t:i:o:",["rcmd=", "tpath=","ipath=","opath="])
    except getopt.GetoptError:
        print 'Cache_Coherency.py -r <runcmd> -t <tracepath> -i <inputpath> -o <outputpath>'
        sys.exit(2)
    if len(opts) == 0:
        print 'ERROR: Cache_Coherency.py -r <runcmd> -t <tracepath> -i <inputpath> -o <outputpath>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'Cache_Coherency.py -r <runcmd> -t <tracepath> -i <inputpath> -o <outputpath>'
            sys.exit()
        elif opt in ("-r", "--rcmd"):
            runcmd = arg
        elif opt in ("-t", "--tpath"):
            tracepath = arg
        elif opt in ("-i", "--ipath"):
            inputpath = arg
        elif opt in ("-o", "--opath"):
            outputpath = arg
    print 'Run command is :', runcmd
    print 'Trace path is :', tracepath
    print 'Input path is :', inputpath
    print 'Output path is :', outputpath,'\n\n'
    return (runcmd,tracepath,inputpath,outputpath)

class run(object):
    def __init__(self,tname,rcmd,ipath,output):
        self.tname =tname
        #print self.tname
        self.rcmd =rcmd
        #print self.rcmd
        self.ipath = ipath
        #print self.ipath
        self.log = open(output,'w')
        self.process1= None
        
    def runprocess(self,timeout):
        def target():
            args = shlex.split(self.rcmd)
            logging.debug('****Starting****')
            self.process1 = subprocess.Popen(args,stderr=self.log,cwd=self.ipath)
            self.log.flush()
            self.log.close()
            self.process1.communicate()
            logging.debug('****Exiting****\n')
            
        thread = threading.Thread(name=self.tname,target=target)
        thread.start()  
        thread.join(timeout)
        if thread.is_alive():
            print '****Protocol: ',self.tname,'is Terminated ****'
            self.process1.terminate()
            thread.join()
            self.log.close()
            return(False)
        else:
            return(True)
            
        

if __name__ == "__main__":
    rcmd,tpath, ipath, opath = getpath(sys.argv[1:])
    
    finalcommand = "./"+rcmd + " -t "
    clean_process = subprocess.Popen("rm -rf *", cwd=opath, shell=True)
    clean_process.communicate()
    clean_process.wait()
    
    '''
    MI protocol
    '''
    MI_opath = opath + "/MI"
    os.mkdir(MI_opath)
    
    '''Proc Run'''
    proc_no =2
    runwasok=True
    comparewasok = False
    dontrunexperiments = False
    while((proc_no<9) and (runwasok == True)):
        proc_no = proc_no*2
        run1cmd = finalcommand + tpath + "/"+str(proc_no)+"proc_validation -p MI"
        ofile = MI_opath + "/My_MI_"+str(proc_no)+"proc.txt"
        temp_tname = "MI_"+str(proc_no)+"proc"
        MIrun = run(temp_tname,run1cmd,ipath,ofile)
        runwasok=MIrun.runprocess(10)
        val_file = tpath+"/"+str(proc_no)+"proc_validation/MI_validation.txt"
        print "Comparing the Outputs...."
        comparewasok = filecmp.cmp(ofile,val_file, shallow=False)
        if(comparewasok):
            print "*****Results match!!!******\n"
        else:
            dontrunexperiments = True
            print "*****Compare FAILED!!!****\n"

    if dontrunexperiments ==False and runwasok==True:
        '''Experiments'''
        for expno in range(1,9):
            run1cmd = finalcommand + tpath + "/experiment"+str(expno)+" -p MI"
            ofile = MI_opath + "/My_MI_experiment"+str(expno)+".txt"
            temp_tname = "MI_experiment"+str(expno)
            MIrun = run(temp_tname,run1cmd,ipath,ofile)
            MIrun.runprocess(10)
    elif dontrunexperiments == True:
        print "\n\n****Not Running Experiments: Results did not match****\n\n"
    else:
        print "\n\n****Not Running Experiments: One of validation runs failed****\n\n"
    
    MIworkedfine = False
    if dontrunexperiments == False and runwasok == True:
        MIworkedfine = True
    '''
    MSI protocol
    '''
    MSI_opath = opath + "/MSI"
    os.mkdir(MSI_opath)
    
    '''Proc Run'''
    proc_no =2
    runwasok=True
    comparewasok = False
    dontrunexperiments = False
    
    while((proc_no<9) and (runwasok == True)):
        proc_no = proc_no*2
        run1cmd = finalcommand + tpath + "/"+str(proc_no)+"proc_validation -p MSI"
        ofile = MSI_opath + "/My_MSI_"+str(proc_no)+"proc.txt"
        temp_tname = "MSI_"+str(proc_no)+"proc"
        MSIrun = run(temp_tname,run1cmd,ipath,ofile)
        runwasok = MSIrun.runprocess(10)
        val_file = tpath+"/"+str(proc_no)+"proc_validation/MSI_validation.txt"
        print "Comparing the Outputs...."
        comparewasok = filecmp.cmp(ofile,val_file, shallow=False)
        if(comparewasok):
            print "*****Results match!!!******\n"
        else:
            dontrunexperiments = True
            print "*****Compare FAILED!!!*****\n"

    '''Experiments'''
    if dontrunexperiments ==False and runwasok==True:
        for expno in range(1,9):
            run1cmd = finalcommand + tpath + "/experiment"+str(expno)+" -p MSI"
            ofile = MSI_opath + "/My_MSI_experiment"+str(expno)+".txt"
            temp_tname = "MSI_experiment"+str(expno)
            MSIrun = run(temp_tname,run1cmd,ipath,ofile)
            MSIrun.runprocess(10)
    elif dontrunexperiments == True:
        print "\n\n****Not Running Experiments: Results did not match****\n\n"
    else:
        print "\n\n****Not Running Experiments: One of validation runs failed****\n]n"
        
        
    MSIworkedfine = False
    if dontrunexperiments == False and runwasok == True:
        MSIworkedfine = True
    '''
    MESI protocol
    '''
    MESI_opath = opath + "/MESI"
    os.mkdir(MESI_opath)
    
    '''Proc Run'''
    proc_no =2
    runwasok=True
    comparewasok = False
    dontrunexperiments = False
    while((proc_no<9) and (runwasok == True)):
        proc_no = proc_no*2
        run1cmd = finalcommand + tpath + "/"+str(proc_no)+"proc_validation -p MESI"
        ofile = MESI_opath + "/My_MESI_"+str(proc_no)+"proc.txt"
        temp_tname = "MESI_"+str(proc_no)+"proc"
        MESIrun = run(temp_tname,run1cmd,ipath,ofile)
        runwasok = MESIrun.runprocess(10)
        val_file = tpath+"/"+str(proc_no)+"proc_validation/MESI_validation.txt"
        print "Comparing the Outputs...."
        comparewasok = filecmp.cmp(ofile,val_file, shallow=False)
        if(comparewasok):
            print "*****Results match!!!******\n"
        else:
            dontrunexperiments = True
            print "*****Compare FAILED!!!*****\n"

    '''Experiments'''
    if dontrunexperiments ==False and runwasok==True:
        for expno in range(1,9):
            run1cmd = finalcommand + tpath + "/experiment"+str(expno)+" -p MESI"
            ofile = MESI_opath + "/My_MESI_experiment"+str(expno)+".txt"
            temp_tname = "MESI_experiment"+str(expno)
            MESIrun = run(temp_tname,run1cmd,ipath,ofile)
            MESIrun.runprocess(10)
    elif dontrunexperiments == True:
        print "\n\n****Not Running Experiments: Results did not match****\n\n"
    else:
        print "\n\n****Not Running Experiments: One of validation runs failed****\n]n"  
        
    MESIworkedfine = False
    if dontrunexperiments == False and runwasok == True:
        MESIworkedfine = True
    
    '''
    MOSI protocol
    '''
    MOSI_opath = opath + "/MOSI"
    os.mkdir(MOSI_opath)
    
    '''Proc Run'''
    proc_no =2
    runwasok=True
    comparewasok = False
    dontrunexperiments = False
    
    while((proc_no<9) and (runwasok == True)):
        proc_no = proc_no*2
        run1cmd = finalcommand + tpath + "/"+str(proc_no)+"proc_validation -p MOSI"
        ofile = MOSI_opath + "/My_MOSI_"+str(proc_no)+"proc.txt"
        temp_tname = "MOSI_"+str(proc_no)+"proc"
        MOSIrun = run(temp_tname,run1cmd,ipath,ofile)
        runwasok = MOSIrun.runprocess(10)
        val_file = tpath+"/"+str(proc_no)+"proc_validation/MOSI_validation.txt"
        print "Comparing the Outputs...."
        comparewasok = filecmp.cmp(ofile,val_file, shallow=False)
        if(comparewasok):
            print "*****Results match!!!******\n"
        else:
            dontrunexperiments = True
            print "*****Compare FAILED!!!*****\n"

    '''Experiments'''
    if dontrunexperiments ==False and runwasok==True:
        for expno in range(1,9):
            run1cmd = finalcommand + tpath + "/experiment"+str(expno)+" -p MOSI"
            ofile = MOSI_opath + "/My_MOSI_experiment"+str(expno)+".txt"
            temp_tname = "MOSI_experiment"+str(expno)
            MOSIrun = run(temp_tname,run1cmd,ipath,ofile)
            MOSIrun.runprocess(10)
    elif dontrunexperiments == True:
        print "\n\n****Not Running Experiments: Results did not match****\n\n"
    else:
        print "\n\n****Not Running Experiments: One of validation runs failed****\n]n"
        
    MOSIworkedfine = False
    if dontrunexperiments == False and runwasok == True:
        MOSIworkedfine = True
        
    '''
    MOESI protocol
    '''
    MOESI_opath = opath + "/MOESI"
    os.mkdir(MOESI_opath)
    
    '''Proc Run'''
    proc_no =2
    runwasok=True
    comparewasok = False
    dontrunexperiments = False
    
    while((proc_no<9) and (runwasok == True)):
        proc_no = proc_no*2
        run1cmd = finalcommand + tpath + "/"+str(proc_no)+"proc_validation -p MOESI"
        ofile = MOESI_opath + "/My_MOESI_"+str(proc_no)+"proc.txt"
        temp_tname = "MOESI_"+str(proc_no)+"proc"
        MOESIrun = run(temp_tname,run1cmd,ipath,ofile)
        runwasok = MOESIrun.runprocess(10)
        val_file = tpath+"/"+str(proc_no)+"proc_validation/MOESI_validation.txt"
        print "Comparing the Outputs...."
        comparewasok = filecmp.cmp(ofile,val_file, shallow=False)
        if(comparewasok):
            print "*****Results match!!!******\n"
        else:
            dontrunexperiments = True
            print "*****Compare FAILED!!!*****\n"

    '''Experiments'''
    if dontrunexperiments ==False and runwasok==True:
        for expno in range(1,9):
            run1cmd = finalcommand + tpath + "/experiment"+str(expno)+" -p MOESI"
            ofile = MOESI_opath + "/My_MOESI_experiment"+str(expno)+".txt"
            temp_tname = "MOESI_experiment"+str(expno)
            MOESIrun = run(temp_tname,run1cmd,ipath,ofile)
            MOESIrun.runprocess(10)
    elif dontrunexperiments == True:
        print "\n\n****Not Running Experiments: Results did not match****\n\n"
    else:
        print "\n\n****Not Running Experiments: One of validation runs failed****\n]n"
    
    MOESIworkedfine = False
    if dontrunexperiments == False and runwasok == True:
        MOESIworkedfine = True
    
    '''
    MOESIF protocol
    '''
    MOESIF_opath = opath + "/MOESIF"
    os.mkdir(MOESIF_opath)
    
    '''Proc Run'''
    proc_no =2
    runwasok=True
    comparewasok = False
    dontrunexperiments = False
    
    while((proc_no<9) and (runwasok == True)):
        proc_no = proc_no*2
        run1cmd = finalcommand + tpath + "/"+str(proc_no)+"proc_validation -p MOESIF"
        ofile = MOESIF_opath + "/My_MOESIF_"+str(proc_no)+"proc.txt"
        temp_tname = "MOESIF_"+str(proc_no)+"proc"
        MOESIFrun = run(temp_tname,run1cmd,ipath,ofile)
        runwasok = MOESIFrun.runprocess(10)
        val_file = tpath+"/"+str(proc_no)+"proc_validation/MOESIF_validation.txt"
        print "Comparing the Outputs...."
        comparewasok = filecmp.cmp(ofile,val_file, shallow=False)
        if(comparewasok):
            print "*****Results match!!!******\n"
        else:
            dontrunexperiments = True
            print "*****Compare FAILED!!!*****\n"

    '''Experiments'''
    if dontrunexperiments ==False and runwasok==True:
        for expno in range(1,9):
            run1cmd = finalcommand + tpath + "/experiment"+str(expno)+" -p MOESIF"
            ofile = MOESIF_opath + "/My_MOESIF_experiment"+str(expno)+".txt"
            temp_tname = "MOESIF_experiment"+str(expno)
            MOESIFrun = run(temp_tname,run1cmd,ipath,ofile)
            MOESIFrun.runprocess(10)
    elif dontrunexperiments == True:
        print "\n\n****Not Running Experiments: Results did not match****\n\n"
    else:
        print "\n\n****Not Running Experiments: One of validation runs failed****\n]n"
    
    MOESIFworkedfine = False
    if dontrunexperiments == False and runwasok == True:
        MOESIFworkedfine = True
        
    '''Making graphs'''
    MI_statdict = {}
    if MIworkedfine:
        for expno in range(1,9):
            ofile = MI_opath + "/My_MI_experiment"+str(expno)+".txt"
            fp = open(ofile)
            lines = fp.readlines()
            fp.close()
            tempdict = {}
            for line in lines:
                line =line.strip()
                if "run time" in line.lower():
                    words = line.split(' ')
                    tempdict['RunTime'] = words[-2]
                elif "cache misses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheMisses'] = words[-2]
                elif "cache accesses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheAccesses'] = words[-2]
                elif "silent upgrades" in line.lower():
                    words = line.split(' ')
                    tempdict['SilentUpgrades'] = words[-2]
                elif "transfers" in line.lower():
                    words = line.split(' ')
                    tempdict['$-$Transfers'] = words[-2]
            expname = "Experiment"+str(expno)
            MI_statdict[expname] = tempdict
        
    MSI_statdict = {}
    if MSIworkedfine:
        for expno in range(1,9):
            ofile = MSI_opath + "/My_MSI_experiment"+str(expno)+".txt"
            fp = open(ofile)
            lines = fp.readlines()
            fp.close()
            tempdict = {}
            for line in lines:
                line =line.strip()
                if "run time" in line.lower():
                    words = line.split(' ')
                    tempdict['RunTime'] = words[-2]
                elif "cache misses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheMisses'] = words[-2]
                elif "cache accesses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheAccesses'] = words[-2]
                elif "silent upgrades" in line.lower():
                    words = line.split(' ')
                    tempdict['SilentUpgrades'] = words[-2]
                elif "transfers" in line.lower():
                    words = line.split(' ')
                    tempdict['$-$Transfers'] = words[-2]
            expname = "Experiment"+str(expno)
            MSI_statdict[expname] = tempdict
            
    MESI_statdict = {}
    if MESIworkedfine:
        for expno in range(1,9):
            ofile = MESI_opath + "/My_MESI_experiment"+str(expno)+".txt"
            fp = open(ofile)
            lines = fp.readlines()
            fp.close()
            tempdict = {}
            for line in lines:
                line =line.strip()
                if "run time" in line.lower():
                    words = line.split(' ')
                    tempdict['RunTime'] = words[-2]
                elif "cache misses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheMisses'] = words[-2]
                elif "cache accesses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheAccesses'] = words[-2]
                elif "silent upgrades" in line.lower():
                    words = line.split(' ')
                    tempdict['SilentUpgrades'] = words[-2]
                elif "transfers" in line.lower():
                    words = line.split(' ')
                    tempdict['$-$Transfers'] = words[-2]
            expname = "Experiment"+str(expno)
            MESI_statdict[expname] = tempdict
    
    MOSI_statdict = {}
    if MOSIworkedfine:
        for expno in range(1,9):
            ofile = MOSI_opath + "/My_MOSI_experiment"+str(expno)+".txt"
            fp = open(ofile)
            lines = fp.readlines()
            fp.close()
            tempdict = {}
            for line in lines:
                line =line.strip()
                if "run time" in line.lower():
                    words = line.split(' ')
                    tempdict['RunTime'] = words[-2]
                elif "cache misses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheMisses'] = words[-2]
                elif "cache accesses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheAccesses'] = words[-2]
                elif "silent upgrades" in line.lower():
                    words = line.split(' ')
                    tempdict['SilentUpgrades'] = words[-2]
                elif "transfers" in line.lower():
                    words = line.split(' ')
                    tempdict['$-$Transfers'] = words[-2]
            expname = "Experiment"+str(expno)
            MOSI_statdict[expname] = tempdict
    
    MOESI_statdict = {}
    if MOESIworkedfine:
        for expno in range(1,9):
            ofile = MOESI_opath + "/My_MOESI_experiment"+str(expno)+".txt"
            fp = open(ofile)
            lines = fp.readlines()
            fp.close()
            tempdict = {}
            for line in lines:
                line =line.strip()
                if "run time" in line.lower():
                    words = line.split(' ')
                    tempdict['RunTime'] = words[-2]
                elif "cache misses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheMisses'] = words[-2]
                elif "cache accesses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheAccesses'] = words[-2]
                elif "silent upgrades" in line.lower():
                    words = line.split(' ')
                    tempdict['SilentUpgrades'] = words[-2]
                elif "transfers" in line.lower():
                    words = line.split(' ')
                    tempdict['$-$Transfers'] = words[-2]
            expname = "Experiment"+str(expno)
            MOESI_statdict[expname] = tempdict
            
    MOESIF_statdict = {}
    if MOESIFworkedfine:
        for expno in range(1,9):
            ofile = MOESIF_opath + "/My_MOESIF_experiment"+str(expno)+".txt"
            fp = open(ofile)
            lines = fp.readlines()
            fp.close()
            tempdict = {}
            for line in lines:
                line =line.strip()
                if "run time" in line.lower():
                    words = line.split(' ')
                    tempdict['RunTime'] = words[-2]
                elif "cache misses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheMisses'] = words[-2]
                elif "cache accesses" in line.lower():
                    words = line.split(' ')
                    tempdict['CacheAccesses'] = words[-2]
                elif "silent upgrades" in line.lower():
                    words = line.split(' ') 
                    tempdict['SilentUpgrades'] = words[-2]
                elif "transfers" in line.lower():
                    words = line.split(' ')
                    tempdict['$-$Transfers'] = words[-2]
            expname = "Experiment"+str(expno)
            MOESIF_statdict[expname] = tempdict

    '''Making Graphs for run time'''
    if MIworkedfine and MSIworkedfine and MESIworkedfine and MOSIworkedfine and MOESIworkedfine and MOESIFworkedfine:
        for expno in range(1,9):
            expname = "Experiment" + str(expno)
            runtimelist = ( int(MI_statdict[expname]['RunTime']), int(MSI_statdict[expname]['RunTime']), int(MESI_statdict[expname]['RunTime']), int(MOSI_statdict[expname]['RunTime']), int(MOESI_statdict[expname]['RunTime']), int(MOESIF_statdict[expname]['RunTime']))
            protocol = ('MI', 'MSI', 'MESI', 'MOSI', 'MOESI', 'MOESIF')
            N = 6
            ind = np.arange(N)    # the x locations for the groups
            width = 0.35       # the width of the bars: can also be len(x) sequence 
            p1 = plt.bar(ind, runtimelist,  width, color='b')
            plt.xlabel('Cache Coherency Protocols')
            plt.ylabel('Clock Cycles')
            title = "Run Time for " + expname
            plt.title(title)
            plt.xticks(ind+width/2.,protocol)
            yspots = max(runtimelist) - max(runtimelist)%100
            yspots //= 10
            plt.yticks(np.arange(0,(max(runtimelist)+yspots), yspots))
            #plt.legend(p1[0],'Protocols')
            graphname = "Experiment" + str(expno) +  ".png"
            plt.savefig(graphname)
            plt.clf()
            
            expname = "Experiment" + str(expno)
            runtimelist = ( int(MI_statdict[expname]['SilentUpgrades']), int(MSI_statdict[expname]['SilentUpgrades']), int(MESI_statdict[expname]['SilentUpgrades']), int(MOSI_statdict[expname]['SilentUpgrades']), int(MOESI_statdict[expname]['SilentUpgrades']), int(MOESIF_statdict[expname]['SilentUpgrades']))
            protocol = ('MI', 'MSI', 'MESI', 'MOSI', 'MOESI', 'MOESIF')
            N = 6
            ind = np.arange(N)    # the x locations for the groups
            width = 0.35       # the width of the bars: can also be len(x) sequence 
            p1 = plt.bar(ind, runtimelist,  width, color='b')
            plt.xlabel('Cache Coherency Protocols')
            plt.ylabel('No. of Silent Upgrades')
            title = "Silent Upgrades for " + expname
            plt.title(title)
            plt.xticks(ind+width/2.,protocol)
            yspots = max(runtimelist) - max(runtimelist)%100
            yspots //= 1
            plt.yticks(np.arange(0,(max(runtimelist)+1), 1))
            #plt.legend(p1[0],'Protocols')
            graphname = "Silent_Upgrades_Experiment" + str(expno) +  ".png"
            plt.savefig(graphname)
            plt.clf()
            
            expname = "Experiment" + str(expno)
            runtimelist = ( int(MI_statdict[expname]['$-$Transfers']), int(MSI_statdict[expname]['$-$Transfers']), int(MESI_statdict[expname]['$-$Transfers']), int(MOSI_statdict[expname]['$-$Transfers']), int(MOESI_statdict[expname]['$-$Transfers']), int(MOESIF_statdict[expname]['$-$Transfers']))
            protocol = ('MI', 'MSI', 'MESI', 'MOSI', 'MOESI', 'MOESIF')
            N = 6
            ind = np.arange(N)    # the x locations for the groups
            width = 0.35       # the width of the bars: can also be len(x) sequence 
            p1 = plt.bar(ind, runtimelist,  width, color='b')
            plt.xlabel('Cache Coherency Protocols')
            plt.ylabel("No. of \$-\$ Transfers")
            title = "\$-\$ Transfers for " + expname
            plt.title(title)
            plt.xticks(ind+width/2.,protocol)
            yspots = max(runtimelist) - max(runtimelist)%100
            yspots //= 1
            plt.yticks(np.arange(0,(max(runtimelist)+1), 5))
            #plt.legend(p1[0],'Protocols')
            graphname = "C-C_Transfers_Experiment" + str(expno) +  ".png"
            plt.savefig(graphname)
            plt.clf()