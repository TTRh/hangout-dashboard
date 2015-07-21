#!/bin/bash

SCRIPT_DIR=$(dirname $(readlink -f $0))
BOWER_DIR=$SCRIPT_DIR/web/public/bower_components

function check_bower_dep {
  test -d $1 && echo "[INFO] $1 OK" || echo "[WARNING] run 'bower install $1' in $(dirname $BOWER_DIR)"
}

echo "[INFO] : check web compoments ..."
mkdir -p $BOWER_DIR
pushd $BOWER_DIR >/dev/null
check_bower_dep jquery
check_bower_dep fontawesome
check_bower_dep bootstrap
check_bower_dep ihover
check_bower_dep jquery.sparkline
popd >/dev/null
