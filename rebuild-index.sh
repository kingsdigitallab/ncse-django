#!/bin/bash

sudo ./manage.py build_solr_schema --configure-directory=/var/solr/data/dev/conf
sudo service solr restart
./manage.py rebuild_index --noinput