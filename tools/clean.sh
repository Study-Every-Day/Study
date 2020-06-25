#/bin/bash
# This script is used to clean memory by kill all chrome process.
ps -ef | grep chrome | awk '{print $2}' | xargs kill -9
