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

`$ git clone https://github.com/ybuch/corry_config_desytb_2025.git`

`$ cd corry_config_desytb_2025/docker`

You can pull the image from Docker Hub using `ybuch/belle-ii-tb:2025v5` in the subsequent calls.
If oyu buil dthe image locally instead you will need to use the name of your local image defined by `corry:tb2025` in the following line. 

Alternatively you can also build the image from source by executing the following line in the folder with dockerfile_corry, however you need a folder with the telepix dataformat that is currently not publicly available and has too be there locally, but I am hesitant to upload other peoples code here, (if you plan to compile the container yourself please ask me for the appropriate files), execute

`$ docker build -t corry:tb2025 -f dockerfile_corry .`

This will take some time as root, eudaq and corry will be built from source.

Choose option with or without graphics:

Option 1: Run container without graphics (use this if you are running on servers):

`$ docker run --name corry_container -i -t --mount type=bind,source=$HOME/corry_config_desytb_2025/,target=/corry_config_desytb_2025 --mount type=bind,source=$HOME/s3_cloud/,target=/s3_cloud,readonly corry:tb2025`

Option 2: Run container with graphics (use this if you want to use root inside the docker container for TBrowser to inspect root files):

Allow docker to connect to X11 socket

`$ xhost +local:docker`

`$ docker run --name corry_container -i -t --mount type=bind,source=/home/bgnet2/corry_config_desytb_2025/,target=/corry_config_desytb_2025 --mount type=bind,source=/home/bgnet2/s3_cloud/,target=/s3_cloud,readonly -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix corry:tb2025`

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

`$ vim corry_config_desytb_2025/conf/analyze.py`

And change **data_path** path:

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


