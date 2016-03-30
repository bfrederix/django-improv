##### How to Export from Google ############
http://gbayer.com/big-data/app-engine-datastore-how-to-efficiently-export-your-data/

gsutil cp -R gs://adventureprovbackup/ ./

##### Activating virtualenv (work mac) #########
pyenv activate gae_export


#### Run the management command ############
python manage.py data_export /Users/freddy/projects/django-voteprov/gae_export/adventureprovbackup/ Medal