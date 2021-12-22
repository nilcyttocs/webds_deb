#!/bin/bash
set -e

rm -fr *.deb
cp control pinormos-webds/webds-deb/DEBIAN/.
cp wheelhouse/* pinormos-webds/webds-deb/var/spool/syna/jupyterlab_webds/.
cp requirements.txt pinormos-webds/webds-deb/var/spool/syna/jupyterlab_webds/.
pinormos-webds/gen-deb.sh
rm -fr pinormos-webds/webds-deb/var/spool/syna/jupyterlab_webds/*
rm -fr webds_deb.tar.gz
tar -zcf webds_deb.tar.gz *
