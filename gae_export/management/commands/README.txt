##### STANDARD NEEDED SQL #######

ALTER DEFAULT PRIVILEGES GRANT ALL ON TABLES TO voteprovprod;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bfrederix;

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO voteprovprod;
GRANT ALL ON SCHEMA public TO public;
COMMENT ON SCHEMA public IS 'standard public schema';


##### Activating virtualenv (work mac) #########
pyenv activate gae_export


#### Run the management command ############
python manage.py data_export /Users/brandon.fredericks/home_projects/django-voteprov/gae_export/adventureprovbackup/ Medal



### Digital Ocean Droplet postgres access ###
/etc/postgresql/9.3/main/pg_hba.conf
# ALLOW CONNECTIONS FROM ALL IPs
host    all         all         0.0.0.0/0       md5

/etc/postgresql/9.3/main/postgresql.conf
# Switch from localhost to * to allow connection on all addresses
listen_addresses = '*'

# Restart postgres
service postgresql restart