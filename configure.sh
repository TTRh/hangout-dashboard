#!/bin/bash

SCRIPT_DIR=$(dirname $(readlink -f $0))
BOWER_DIR=$SCRIPT_DIR/web/public

function check_bower_dep {
  test -d $1 || echo "[WARNING] run 'bower install $1' in $BOWER_DIR"
}

echo "[INFO] : check bower compoments ..."
pushd $BOWER_DIR
check_bower_dep jquery
check_bower_dep fontawsome
check_bower_dep bootstrap
check_bower_dep ihover
check_bower_dep jquery.sparkline
popd
