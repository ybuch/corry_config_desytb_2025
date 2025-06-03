## Alignment and analysis procedure

Local alignemnt:

Edit `align_tel.sh`

Change `histogram_file`, `detectors_file` and `detectors_file_updated` with appropriate names.

Currently we use names of the form `geo_id10_align_tel_it1`

So only the config ID `id10` needs to be changed to something appropriate to your alignment like `id7` for an alignment of config 7.

Make sure the correct corry binary is used. 

In `align_tel.conf`, `align_tel_mille.conf`, `align_dut.conf` change the run number in the file names to the run you want to use. Just find and replace the run number. 

Then run with 

`$ ./align_tel.sh`

You may need to change permissions using 

`$ chmod +x align_tel.sh`

Local analysis

Check binaries and paths in `analyze.py` 

Change **data_path** path:

**data_path = '.'**

And create a link to your data folder using 

`$ ln -s /path/to/data data/`.

Similarly, create a link to the corry binary 

`$ ln -s /path/to/corryvreckan/bin/corry corry`.

If you decide to do so then change

**cmd = './corry ...'**

or if you have it in $PATH you can use

**cmd = 'corry ...'**

And change **repo_path** path:

**repo_path = '/corry_config_desytb_2025'**

to the root of this git repo.

Run with 

`$ python3 analyze.py 1000-1200 ../geo/updated_geo/geo_idXX_align_tel_it4.geo`
