# nymeria code overview - read this first
Note: please be sure to download the data yourself from the nymeria dataset here: explorer.projectaria.com/nymeria (or run autodownload.py on the file nymeria_allmetadata_download_urls.json) and crosscheck the directory before employing this code. for what it's worth, I really do recommend that you run autodownload.py and subjects.py first. 

## non-coding files  
**everything else/notes.html**
notes that i took on the data and analyses i ran. might be nice to see the progression of my thoughts over time, but not much help in understanding the data.

**everything else/nymeria_allmetadata_download_urls.json**
the urls for downloading all 1100 subjects' metadata from nymeria. you can parse through for a specific subject and click the link to download their metadata, or run autodownload.py to download all the data at once. you can also make a subset of the metadata urls and run autodownload.py on that instead. 

**everything else/nymeria_download_urls.json**
all the download links for seth, paul, and kenneth for their simon_says activity. useful for comparisons between the three while they did the same task.


## coding files  
**ageBreakdown.py**
This python file parses through a directory of metadata.json files and grabs the age group then returns a histogram displaying distribution. If using this, be sure to change the directory to the actual folder that holds these metadata files. 

**ageHead.py**
Plots head trajectory across 3 specific subjects. (see also totalAgeHead.py)

**autodownload.py**
Goes through a json file of download urls and downloads them all at once to your laptop's designated download folder. Can be modified to save the downloaded files to a specific directory. 

**averageHeats.py**
Makes a compiled heatmap of gaze by activity/script. That is, for every script given, this will parse through an indicated directory (set to current), download the recording_head data for an activity (a zip file), grab the pitch yaw data from the csv file within, and use that to make a heatmap showing where everyone who did that activity in that dataset is looking. Note: this is a way oversimplified summary. 
Code also includes different displays of the heatmap plots, variance, median, overlapping them on the same plot, etc. Please read carefully to ensure the uncommented code is what you wish to plot. Generated heatmaps are saved to a directory of choice (set to make a heatmaps folder in your current directory and save them there, but modify as needed). 

**subjects.py**
summarises the downloaded data. returns number of unique subjects, activities, etc. useful for confirming that the subset of downloaded data is what you wish to have. perhaps if you only wanted subjects of a specific activity, or you are unsure how many repeats there are (as some subjects did the same script twice), etc.

**totalAgeHead.py**
This looks at head trajectory across age groups by going through a directory, collecting age group and their head trajectory in meters then returning a plot of that data. you will need to have already downloaded the files to use this code. 

**trajRecHead.py**
This plots the head trajectory of a specific subject in the dataset. Assuming you already have the data, you will simply need to change the name of the subject whose data you wish to plot. Options to animate and overlay are included. 

## a whole lotta links
a bunch of links to aria analysis tool docs
https://facebookresearch.github.io/projectaria_tools/docs/data_utilities

https://facebookresearch.github.io/projectaria_tools/docs/data_utilities/getting_started#step-0--check-system-requirements-and-download-codebase

aria docs on vrs: https://facebookresearch.github.io/projectaria_tools/docs/data_formats/aria_vrs/aria_vrs_format

jupyter notebook:http://localhost:8888/doc/tree/dataprovider_quickstart_tutorial.ipynbjupyter notebook

projectaria_tools/core/examples/dataprovider_quickstart_tutorial.ipynb

mps visualisation: https://colab.research.google.com/github/facebookresearch/projectaria_tools/blob/1.6.0/core/examples/mps_quickstart_tutorial.ipynb

vrs repo: https://github.com/facebookresearch/vrs/tree/main

my nymeria repo: https://github.com/betsy-paul/nymeria

some tutorials? idk tbh: https://facebookresearch.github.io/projectaria_tools/docs/data_utilities/getting_started
