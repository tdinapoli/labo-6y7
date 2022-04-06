#!/bin/bash
DIR=`dirname "$0"`
echo DIR: $DIR
export LD_LIBRARY_PATH=/opt/KAYA_Instruments/bin:$LD_LIBRARY_PATH
$DIR/VisionPoint "$@" &> /dev/null
exit 0

