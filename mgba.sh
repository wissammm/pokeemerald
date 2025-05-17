#!/bin/bash

(
	sleep 4
	echo "started"
)&

mgba-qt $1 -g