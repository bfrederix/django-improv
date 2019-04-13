import datetime

from fabric.api import run, env, local, put, cd

# Directory where the deploys go
DEPLOYS = '/home/django/deploys/'

# virtualenv python version
VIRTUALENV_PYTHON = "/home/django/dumpedit/bin/python"

# the servers where the commands are executed
env.hosts = ['***REMOVED***']

def pack(version_name):
    # Compress the react js
    local("browserify static/js/react_components.js -t reactify -d -p [minifyify --map bundle.js.map --output bundle.js.map --uglify] > static/js/react_components.min.js",
          capture=False)
    tar_path = "/tmp/{0}.tar.gz".format(version_name)
    tar_command = "tar -czf {0} .".format(tar_path)
    # create a new source distribution as tarball
    local(tar_command, capture=False)
    return tar_path

def server_deploy(version_name, tar_path):
    # New deploy directory
    deploy_dir = '{0}{1}'.format(DEPLOYS, version_name)
    # Deploy file plus path
    deploy_tar = '{0}.tar.gz'.format(deploy_dir)
    # upload the source tarball to the deploys folder on the server
    put(tar_path, deploy_tar)

    # Make the new deployment directory
    run('mkdir {0}'.format(deploy_dir))
    # Change directory into the new deploy directory
    with cd(deploy_dir):
        # Unzip the tar in the deploys directory
        run('tar -xvf {0}'.format(deploy_tar))
        # REMOVE ALL THE UNNECESSARY FILES AND DIRECTORIES
        # Remove all pycs
        run('find . -name "*.pyc" -exec rm -rf {} \;')
        # Remove the .git directory
        run('rm -r .git')
        # Remove the node_modules directory
        run('rm -r node_modules')
        # Remove the gae_export directory
        run('rm -r gae_export')
        # Remove the local config directory
        run('rm -r conf/local')
        # Symlink prod to local
        run('ln -s {0}/conf/prod {0}/conf/local'.format(deploy_dir))
        # Update the static files
        run('{0} manage.py collectstatic -v0 --noinput'.format(VIRTUALENV_PYTHON))
    # Delete the deployed tar file
    run('rm {0}'.format(deploy_tar))
    # Remove the old current symlink
    run('rm {0}current'.format(DEPLOYS))
    # Create the new current symlink
    run('ln -s {0} {1}current'.format(deploy_dir, DEPLOYS))
    # Set ownership of the deploy directory to django
    run('chown -R django:django {0}'.format(DEPLOYS))
    # Restart Nginx
    run('service nginx restart')
    # Restart Gunicorn
    run('service gunicorn restart')

def cleanup(tar_path):
    # Remove the temporary tar file
    local("rm {0}".format(tar_path), capture=False)

def deploy():
    # Create the timestamp for the tar file
    now = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
    version_name = "dumpedit-{0}".format(now)
    tar_path = pack(version_name)
    server_deploy(version_name, tar_path)
    cleanup(tar_path)
