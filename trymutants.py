
#!python2

# IMPORTANT: Make sure that your tstl file does not find any errors in the original microjson!
# microjson.py can be found here: https://github.com/agroce/tstl/tree/master/examples/microjson

# This microjson does NOT implement the full json feature set, which is why if you test for all json features, microjson will fail.
# You may kill over 90% of mutants this way, but this does not count because even the original microjson does not pass the tests.
# Modify your tstl until it does not find errors in the original microjson, then run this file to test the mutants.

# Where to put this file:
# in the same directory as your .tstl file and the folder of mutants

# How and when to use this script:
# 1. modify and save your .tstl file
# 2. recompile your .tstl and get sut.py
# 3. run this script

# This script will replace microjson.py with a mutant!
# This is because your tstl should import microjson, so this script renames the mutants to microjson
# So if you want to test the original microjson again after you run this script, you will have to overwrite microjson.py with the original.
# Otherwise, you will be testing a mutant.

# change this to "tstl_rt" if you have it installed on your system
# otherwise, change this path to wherever your tstl files are
# python2 ~/tstl/generators/randomtester.py
tstl_rt_command = "tstl_rt"

# this is the number of tests run on each mutant
# more tests is better, but fewer tests make it go faster
MAX_TESTS = 4



# the body of the script

import subprocess
import glob
import os
import sys
import shutil
import random
import time

make_logs = 0

dnull = open(os.devnull,'w')

rlist = glob.glob("mutants/*_mutant_*.py")
random.shuffle(rlist)

tried = 0
killed = 0

attempted = []
try:
    for l in open("attempted.txt"):
        attempted.append(l[:-1])
except IOError:
    pass

attemptf = open("attempted.txt",'a')


time_since_last = time.time()
start_time = time_since_last

num_mutants = len(rlist)

for f in rlist:

    fdir = f.replace("mutants/","faults_").replace(".py","")
    tried += 1

    if os.path.exists(fdir):
        print "ALREADY ANALYZED AND KILLED\n"
        killed += 1
        continue

    if f in attempted:
        print "ALREADY ANALYZED AND NOT KILLED\n",
        continue

    # overwrites microjson.py with a mutant
    shutil.copy(f,"microjson.py")
    if os.path.exists("microjson.pyc"):
        os.remove("microjson.pyc")

    print "MUTANT #" + str(tried) + ":" + f

    tests = glob.glob("*.test")
    for t in tests:
        os.remove(t)

    r = subprocess.call([tstl_rt_command + " --progress --full --maxtests " + str(MAX_TESTS)],shell=True,stderr=dnull,stdout=dnull)
    if r == 152:
        subprocess.call(["cp currtest.test timeout.test"], shell=True)
        print "TIMEOUT (PROBABLE NON-TERMINATING LOOP DUE TO MUTANT)"

    # were there any error logs generated?
    errors = glob.glob("*.test")
    try:
        os.remove("currtest.test")
    except:
        pass

    kill_msg = ""
    kill_token = " O"

    if errors != []:
        kill_msg = "MUTANT KILLED"
        kill_token = "XX"
        if make_logs == True:
            os.mkdir(fdir)
            subprocess.call(["mv *.test " + fdir + "/"],shell=True,stderr=dnull,stdout=dnull)
            shutil.copy(f,fdir+"/")
        killed += 1
    else:
       kill_msg = "Mutant Passed!"
       attemptf.write(f+"\n")
       sys.stdout.flush()
       attemptf.flush()

    try:
        shutil.copy("originalmicrojson.py","microjson.py")
    except:
        pass

    dt = time.time() - time_since_last
    time_since_last = time.time()
    elapsed = time.time() - start_time
    remaining = elapsed * num_mutants / tried

    print " {:20}".format(kill_msg), "Analyzed:", tried
    print "      KILL RATE:", str(100*killed//tried) + "%", "    KILLED:", killed
    print " ", kill_token, " Time elapsed:", "{:6.2f}".format(elapsed) , "This mutant:", "{:6.2f}".format(dt)
    print "      Est. time remaining:", "{:6.2f}".format(remaining-elapsed)
    print "="*50


attemptf.close()
