### Corry with docker 

## Mount Cloud data (optional)

`$ conda create -y -n s3 python=3.10`

`$ conda activate s3`

`$ pip install s3cmd`

`$ conda install -y -c conda-forge s3fs-fuse s3fs pyyaml`

`$ mkdir $HOME/s3_cloud`

If you need the passwd_file, write me at yannik.buch@stud.uni-goettingen.de

Copy both password files in your home folder and remove any characters before the dot, so that they are hidden files

Change permissions of key files with

`$ sudo chmod 600 .passwd-s3fs`

`$ sudo chmod 600 .s3cfg`

`$ s3fs tjmonopix2-desy-tb-2024 $HOME/s3_cloud/ -o url=https://s3.gwdg.de -o passwd_file=$HOME/.passwd-s3fs -o allow_root`

**Hints if the previous line does not work**: 	

To use -o allow_root you will have to uncomment “user_allow_other” in /etc/fuse.conf



The network folder will appear in  $HOME/s3_cloud/

**Alternative**: You can also copy any beam data in any local folder 

## Docker
Install docker for your OS https://docs.docker.com/engine/install/
This manual assumes that you added docker to your sudo group like is described here https://docs.docker.com/engine/install/linux-postinstall/

Clone repo

`$ git clone https://github.com/ybuch/corry_config_desytb_2024.git`

`$ cd corry_config_desytb_2024/docker`

You can pull the image from Docker Hub using `ybuch/belle-ii-tb:2024_2x2inpix_hdf5` in the subsequent calls instead of the name defined by `corry:tb2024` in the previous line. 

Alternatively you can also build the image from source by executing the following line in the folder with dockerfile_corry execute

`$ docker build -t corry:tb2024 -f dockerfile_corry .`

This will take some time as root, eudaq and corry will be built from source.

Choose option with or without graphics:

Option 1: Run container without graphics (use this if you are running on servers):

`$ docker run --name corry_container -i -t --mount type=bind,source=$HOME/corry_config_desytb_2024/,target=/corry_config_desytb_2024 --mount type=bind,source=$HOME/s3_cloud/,target=/s3_cloud,readonly corry:tb2024`

Option 2: Run container with graphics (use this if you want to use root inside the docker container for TBrowser to inspect root files):

Allow docker to connect to X11 socket

`$ xhost +local:docker`

`$ docker run --name corry_container -i -t --mount type=bind,source=/home/bgnet2/corry_config_desytb_2024/,target=/corry_config_desytb_2024 --mount type=bind,source=/home/bgnet2/s3_cloud/,target=/s3_cloud,readonly -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix corry:tb2024`

Help in case you need to change the docker run command, e.g. if your setup requires different paths:

**--name** 	    Give a name to your container. This is optional and an arbitrary choice.

**-i -t** 		Start container in interactive mode → You get a persistent console in your 
                container to execute scripts via command line

**--mount type=bind,source=/path/to/folder/in/your/system,target=/path/to/folder/in/container(,readonly)**
		        This will make folders available to your docker container. 
                First: We want to mount the analysis git repo to get access scripts and save
                analysis output files, since we want to access results outside of the docker
                container
                Second: We want to mount the folder with the beam data. This might be a local folder or the network shared folder. This folder also has “readonly” attached just in case.

**corry:tb2024**
Defines the container you want to run. In this case it is the same name you just defined with the -t flag when you used the docker build command


## Update paths

Once inside the docker container

`$ vim corry_config_desytb_2024/conf/analyze.py`

And change **corry_bin** path:

**corry_bin = '/src/corryvreckan/bin/corry'**

and data_folder to the data folder you mounted when running the container:

**data_folder = '/s3_cloud/beam_data/desy'**

`$ vim corry_config_desytb_2024/conf/full_align.sh`

**RAW_DIR="/s3_cloud/beam_data/desy"**

## Do the analysis

Start alignment by ./full_align.sh run_number geo_id

`$ cd corry_config_desytb_2024/conf/`

`$ chmod +x full_align.sh`

`$ ./full_align.sh run_number geo_id`

Example: `$ ./full_align.sh 1535 7`

Start analysis with

`$ cd corry_config_desytb_2024/conf/`

`$ python3 analyze.py --start 1535 --stop 1535`

Analysis files (as well as any output files for that matter) are to be found in the mounted analysis git repository. Analysis files can be found in /analysis 

Inspecting analysis files can be done with a root TBrowser from either the host system or, if configured during the startup of the docker container, with the root version inside docker. 

`$ cd corry_config_desytb_2024/analysis`

`$ root`

`$ new TBrowser`

Select respective analysis file for a specific run and browse through the available hitmaps/histograms/plots 
