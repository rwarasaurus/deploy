# Deploy
Basic deployment runner

## Install

    git clone git@github.com:rwarasaurus/deploy.git /opt/deploy
    chmod +x /opt/deploy/run.py
    ln -s /opt/deploy/run.py /bin/deployer

## Setup

Copy the `config-sample.yml` to `config.yml` and edit for your project.

    cp /opt/deploy/config-sample.yml /my/deployments/myproject/config.yml
    cd /my/deployments/myproject
    mkdir ./release
    mkdir ./static
    ssh-keygen -t rsa -b 4096 -f ./is_rsa
    nano ./config.yml

## Configuration

Parameters that are required in the yaml config file

- `repo_branch` Branch name to clone
- `repo_url` Git repo url
- `deploy_key` Path of private key on the filesystem to use when cloning
- `static_path` Path to a folder where static assets are copied to the release folder
- `release_path` Path to the folder that will contain all the releases
- `symlink` Path to symlink to the release
- `deploy_user` System user account which all files should be changed to
- `deploys_to_keep` Number of releases to keep
- `pre_scripts` List of command to run before the symlink is updated
- `post_scripts` List of commands to run once the symlink has been updated

Variables that can be substituted in `pre_scripts` and `post_scripts`

- `$deploy_path` The current release path
- `$repo_branch` Branch name
- `$repo_url` Git repo url
- `$hostname` The systems hostname

## Running

Using the `run.py` file passing the first argument as the location of the `config.yml` file

    python /opt/deploy/run.py /my/deployments/myproject/config.yml

Or if you have symlinked the `run.py` file to `/bin/deployer`

    deployer /my/deployments/myproject/config.yml

## Rollback

Rollback back to another release, for example `20171221173000`

    deployer /my/deployments/myproject/config.yml 20171221173000
