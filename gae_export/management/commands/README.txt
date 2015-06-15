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