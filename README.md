# nymeria code overview - read this first

Note: please be sure to download the data yourself from the nymeria dataset here: explorer.projectaria.com/nymeria and crosscheck the directory before employing this code. in addition, I recommend that you run autodownload.py and subjects.py first. 


**ageBreakdown.py**
This python file parses through a directory of metadata.json files and grabs the age group then returns a histogram displaying distribution. If using this, be sure to change the directory to the actual folder that holds these metadata files. 

**ageHead.py**
semthnga

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
