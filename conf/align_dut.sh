#!/bin/bash

# Same process as telescope alignment. If the DUT is heavily
# misaligned, a looser spatial cut could be necessary.
# The number of associated tracks versus total tracks in the
# terminal output is a good indicator to check.

# Iteration 1
corry -c align_dut.conf \
  -o number_of_tracks=50000 \
  -o detectors_file=geometry/geometry_tel_aligned.geo \
  -o detectors_file_updated=geometry/geometry_aligned_dut_pre.geo \
  -o DUTAssociation.spatial_cut_abs=150um,150um

# Iteration 2
corry -c align_dut.conf \
  -o number_of_tracks=75000 \
  -o detectors_file=geometry/geometry_aligned_dut_pre.geo \
  -o detectors_file_updated=geometry/geometry_aligned_dut.geo \
  -o DUTAssociation.spatial_cut_abs=50um,50um
