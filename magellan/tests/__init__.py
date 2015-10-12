import sys
#sys.path.append('/Users/pradap/Documents/Research/Python-Package/enrique')
sys.path.append('/scratch/pradap/python-work/enrqiue')
import os
import magellan as mg
import jpype
p = mg.get_install_path()
path_for_A = os.sep.join([p, 'datasets', 'table_A.csv'])
path_for_B = os.sep.join([p, 'datasets', 'table_B.csv'])
# mg.init_jvm('/Library/Java/JavaVirtualMachines/jdk1.8.0_45.jdk/Contents/Home/jre/lib/server/libjvm.dylib')
jvm_path = jpype.get_default_jvm_path()
if os.path.isfile(jvm_path):
    mg.init_jvm(jvm_path)
    #mg.init_jvm('/Library/Java/JavaVirtualMachines/jdk1.8.0_45.jdk/Contents/Home/jre/lib/server/libjvm.dylib')
else:
    x = []
    for t in jvm_path.split(os.sep):
        if t == 'client':
            t = 'server'
        elif t == 'server':
            r = 'client'
        x.append(t)
    jp = os.sep.join(x)
    if os.path.isfile(jp):
        mg.init_jvm(jp)
    else:
        jp = raw_input('Give path to jvm library (i.e libjvm.so in linux) : ')
        if os.path.isfile(jp):
            mg.init_jvm(jp)
        else:
            print 'Invalid path; cannot run tests; exiting'




