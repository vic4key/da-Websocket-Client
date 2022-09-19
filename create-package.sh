#!/bin/sh

if [ -d "bin" ]
then
  echo "Creating package ..."
  cp -a preferences/. bin/preferences/
  cp -a plugins/. bin/plugins/
  tar -czvf bin.tar.gz bin/
  echo "Finished"
else
  echo "ERROR: Missing 'bin' folder. See the instruction to build project first."
fi
