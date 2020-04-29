#!/bin/bash

fullpath ()
{
  # if argument start with / use it, otherwise use $PWD and strip the ./	
  [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}
