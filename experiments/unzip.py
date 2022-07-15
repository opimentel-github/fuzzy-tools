#!/usr/bin/env python3
import zipfile
import argparse

if __name__== '__main__':
    parser = argparse.ArgumentParser('unzip')
    parser.add_argument('-fd','--filedir',  type=str, default=None)
    args = parser.parse_args()
    print('unziping: '+args.filedir)
    with zipfile.ZipFile(args.filedir, 'r') as z:
        z.extractall('.')