<<<<<<< HEAD
##ACA Project3: Advanced Computer Architecture ECE 6100- Fall 2014 (Dr. Conte)
==========
-------------------------------------------------------------------------

###Implementing the MSI, MESI, MOSI, MOESI, and MOESIF protocols for a bus-based broadcast system.
===================

####Speicifactions of given architecture and simulator:

1. A simulator in C++, capable of simulating a 4, 8, and 16 core CMP system.  With a memory traace reader.
2. Each core in the CMP has one level of cache.  The cache is fully associative, has infinite size, and has a single cycle lookup time. The CMP has a single memory controller which can access the off chip memory. 

####Regarding simulator Framework:

1. /lib folder contains libraries for protocols.
2. /sim folder contains trace reader source code aling with a basic cache simulator for CMP system.
3. /protocols folder contains source code for implement coherence protocols.

####Adding protocol methods:

1. Required methods were added to necessary protocol classes in the given simulator.
2. Respective outputs were compared to given outputs.

####Automation Work:

1. Created a python script to automate the simulation run for 4,8,16 core configuration, comparing the outputs and plotting necesaary graphs so as to compare performace of the system.
2. Source code: /Cache_Coherence folder contains Cache_Coherence.py 

####Compiling and Runnign the Code:

1. Compile using provided makefile
2. Running the script: python Cache_Coherence.py -r \<runcmd\> -t \<tracepath\> -i \<inputpath\> -o \<outputpath\>
=======
# ACA_Project3
>>>>>>> 09816887717c65da6a329e989621275a756535d2
