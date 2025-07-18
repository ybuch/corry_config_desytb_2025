#!/bin/bash

#Iteration Chi2 1
./corry_tb -c align_tel_eudet.conf \
  -o number_of_tracks=50000 \
  -o histogram_file=align_tel_id5_it1.root \
  -o detectors_file=../geo/updated_geo/geo_id5_1748.geo \
  -o detectors_file_updated=../geo/updated_geo/geo_id5_align_tel_it1.geo \
  -o Tracking4D.spatial_cut_abs=400um,250um \
  -o AlignmentTrackChi2.iterations=2 \
  -o AlignmentTrackChi2.align_orientation=false

./corry_tb -c align_dut_eudet.conf \
  -o number_of_tracks=50000 \
  -o histogram_file=align_tel_id5_it2.root \
  -o detectors_file=../geo/updated_geo/geo_id5_align_tel_it1.geo \
  -o detectors_file_updated=../geo/updated_geo/geo_id5_align_tel_it2.geo \
  -o DUTAssociation.spatial_cut_abs=150um,150um

#Iteration Millepede
./corry_tb -c align_tel_mille_eudet.conf \
  -o number_of_tracks=5000 \
  -o histogram_file=align_tel_id5_it3.root \
  -o detectors_file=../geo/updated_geo/geo_id5_align_tel_it2.geo \
  -o detectors_file_updated=../geo/updated_geo/geo_id5_align_tel_it3.geo \
  -o Tracking4D.spatial_cut_abs=600um,600um \

#Iteration Millepede
./corry_tb -c align_tel_mille_eudet.conf \
  -o number_of_tracks=5000 \
  -o histogram_file=align_tel_id5_it4.root \
  -o detectors_file=../geo/updated_geo/geo_id5_align_tel_it3.geo \
  -o detectors_file_updated=../geo/updated_geo/geo_id5_align_tel_it4.geo \
  -o Tracking4D.spatial_cut_abs=400um,300um \

#Iteration Millepede
./corry_tb -c align_tel_mille_eudet.conf \
  -o number_of_tracks=50000 \
  -o histogram_file=align_tel_id5_it5.root \
  -o detectors_file=../geo/updated_geo/geo_id5_align_tel_it4.geo \
  -o detectors_file_updated=../geo/updated_geo/geo_id5_align_tel_it5.geo \
  -o Tracking4D.spatial_cut_abs=300um,145um \

#Iteration Chi2 2
./corry_tb -c align_tel_eudet.conf \
  -o number_of_tracks=5000 \
  -o histogram_file=align_tel_id5_it6.root \
  -o detectors_file=../geo/updated_geo/geo_id5_align_tel_it5.geo \
  -o detectors_file_updated=../geo/updated_geo/geo_id5_align_tel_it6.geo \
  -o Tracking4D.spatial_cut_abs=200um,60um \
  -o AlignmentTrackChi2.iterations=1 \
  -o AlignmentTrackChi2.align_orientation=true

 # Coarse DUT alignment (will be repeated at every run)
./corry_tb -c align_dut_eudet.conf \
  -o number_of_tracks=50000 \
  -o histogram_file=align_tel_id5_it7.root \
  -o detectors_file=../geo/updated_geo/geo_id5_align_tel_it6.geo \
  -o detectors_file_updated=../geo/updated_geo/geo_id5_align_tel_it7.geo \
  -o DUTAssociation.spatial_cut_abs=150um,150um