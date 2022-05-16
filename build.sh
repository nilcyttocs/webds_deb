#!/bin/bash
set -e

rm -fr *.deb
cp control pinormos-webds/webds-deb/DEBIAN/.
cp wheelhouse/* pinormos-webds/webds-deb/var/spool/syna/webds/wheels/.
cp requirements.txt pinormos-webds/webds-deb/var/spool/syna/webds/wheels/.
pinormos-webds/gen-deb.sh
rm -fr pinormos-webds/webds-deb/var/spool/syna/webds/wheels/*
