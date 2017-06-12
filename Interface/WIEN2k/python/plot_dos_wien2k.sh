#!/bin/bash
export case=`basename "$PWD"`

# Assuming you have got the converged electron density
# You may want to change to denser k-points for DOS plot
x kgen
# Then have one-shot run
run_lapw -so -s lapw0 -e lapw2
# It goes through x lapw0; x lapw1; x lapwso; x lapw2 -so

# Edit case.inq 
cat <<EOF > ./${case}.inq
-9.0   3.0           Emin  Emax
   1                 number of atoms selected for calculations
   1   0  1  0       iatom,qsplit,symmetrize,locrot
1  3                 nL, l-values
EOF 
vi ./${case}.inq
# run qtl to genete <psi_band | Ylm_atom>
x qtl -so
# run configure_int_lapw and/or edit case.int to set up for the dos plot

#configure_int_lapw  # In consistent with ${case}.inq
 
# Or edit from the follwing case.int
cat <<EOF > ./${case}.int
${case}                              #Title
 -1.000   0.00250   1.200  0.000     #Emin, DE, Emax, Gauss-Broad
     5                               #Number of DOS
     0 1 total-DOS
     1 1 tot-Ce
     1 2 f-Ce
     1 3 f5/2-Ce
     1 4 f7/2-Ce
EOF
vi ./${case}.int

# Generate the plot
x tetra -so

# view the plot
xmgrace -nxy ${case}.dos1ev
# Check DOS at fermi level
vi ${case}.outputt

# modify case.int to get fine plot
vi ./${case}.int
# Generate the plot
x tetra -so

# continue if necessary