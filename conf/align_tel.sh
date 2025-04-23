#!/bin/bash

# Iteration Chi2 1
./corry -c align_tel.conf \
  -o number_of_tracks=25000 \
  -o histogram_file=align_tel_id12_it1.root \
  -o detectors_file=../geo/updated_geo/geo_id11_align_tel_it3.geo \
  -o detectors_file_updated=../geo/updated_geo/geo_id12_align_tel_it1.geo \
  -o Tracking4D.spatial_cut_abs=400um,250um \
  -o AlignmentTrackChi2.iterations=2 \
  -o AlignmentTrackChi2.align_orientation=false

# Iteration Millepede
./corry -c align_tel_mille.conf \
  -o number_of_tracks=25000 \
  -o histogram_file=align_tel_id12_it2.root \
  -o detectors_file=../geo/updated_geo/geo_id12_align_tel_it1.geo \
  -o detectors_file_updated=../geo/updated_geo/geo_id12_align_tel_it2.geo \
  -o Tracking4D.spatial_cut_abs=300um,145um \

# Iteration Chi2 2
./corry -c align_tel.conf \
  -o number_of_tracks=25000 \
  -o histogram_file=align_tel_id12_it3.root \
  -o detectors_file=../geo/updated_geo/geo_id12_align_tel_it2.geo \
  -o detectors_file_updated=../geo/updated_geo/geo_id12_align_tel_it3.geo \
  -o Tracking4D.spatial_cut_abs=200um,60um \
  -o AlignmentTrackChi2.iterations=1 \
  -o AlignmentTrackChi2.align_orientation=true

# # Coarse DUT alignment (will be repeated at every run)
# ./corry -c align_dut.conf \
#   -o number_of_tracks=50000 \
#   -o histogram_file=align_tel_id12_it4.root \
#   -o detectors_file=../geo/updated_geo/geo_id12_align_tel_it3.geo \
#   -o detectors_file_updated=../geo/updated_geo/geo_id12_align_tel_it4.geo \
#   -o DUTAssociation.spatial_cut_abs=150um,150um