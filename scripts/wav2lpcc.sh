#!/bin/bash

## \file
## \DONE This file implements a very trivial feature extraction; use it as a template for other front ends.
## 
## Please, read SPTK documentation and some papers in order to implement more advanced front ends.

# Base name for temporary files
base=/tmp/$(basename $0).$$ 

# Ensure cleanup of temporary files on exit
trap cleanup EXIT
cleanup() {
   \rm -f $base.*
}

if [[ $# != 3 ]]; then
   echo "$0 lpcc_order input.wav output.lpcc"
   exit 1
fi

lpcc_order=$1
inputfile=$2
outputfile=$3

if [[ $UBUNTU_SPTK == 1 ]]; then
   # In case you install SPTK using debian package (apt-get)
   X2X="sptk x2x"
   FRAME="sptk frame"
   WINDOW="sptk window"
   LPC="sptk lpc"
   LPC2C="sptk lpc2c"
else
   # or install SPTK building it from its source
   X2X="x2x"
   FRAME="frame"
   WINDOW="window"
   LPC="lpc"
   LPC2C="lpc2c"
fi

# Main command for feature extration
sox $inputfile -t raw -e signed -b 16 - |
    $X2X +sf |
    $FRAME -l 240 -p 80 |
    $WINDOW -l 240 -L 240 |
	$LPC -l 240 -m $lpcc_order |
    $LPC2C -m $lpcc_order -M 13 > $base.lpcc
    # El 13 de la diapositiva 30 de "2c Representation of the speech signal for ASR"

# Our array files need a header with the number of cols and rows:
ncol=$((lpcc_order+1)) # lpcc p =>  (gain a1 a2 ... ap) 
nrow=`$X2X +fa < $base.lpcc | wc -l | perl -ne 'print $_/'$ncol', "\n";'`

# Build fmatrix file by placing nrow and ncol in front, and the data after them
echo $nrow $ncol | $X2X +aI > $outputfile
cat $base.lpcc >> $outputfile

exit
