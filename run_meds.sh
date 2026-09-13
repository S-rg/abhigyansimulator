#!/bin/bash
cd /home/arnav/Desktop/abhigyansimulator || exit
/usr/bin/python3 -m main meds check >>logfile.log 2>&1
