#!/bin/bash
port=$1 #4242
eval "nohup jupyter notebook --port $port &"
