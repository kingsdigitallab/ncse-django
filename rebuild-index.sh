#!/bin/bash
sudo su root << EOF
source /home/vagrant/venv/bin/activate
./manage.py build_solr_schema --configure-directory=/var/solr/data/dev/conf
service solr restart
EOF
./manage.py rebuild_index --noinput