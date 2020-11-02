#!/usr/bin/env python
"""
deepmerge.py - merges multiple directories which may contain similar or
               otherwise overlapping files. In the event of conflicts, the
               newest version of a file gets the name, and older versions
               get copied with their modification times appended to their
               names

Authors:
  Erick Brown <ejtbpublic -at- gmail -dot- com>

Copyright:
  2020, Erick Brown (work for hire; LogMeIn, Inc.)
"""

import os
import sys
import argparse
import shutil
import datetime
import hashlib

dest_hashes = dict()


def ts_str(timestamp):
    """
    ts_str - returns consistently formatted  timestamp string

    :type timestamp: float      Timestamp, seconds since epoch
    :return:                    See description
    :rtype: str
    """

    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d--at--%H-%M-%S')


def assure_dest_hash(path):
    """
    assure_dest_hash - make sure that path is accurately represented in
                       the dest_hash dict

    :type path: str     Path and file name to assure
    :return:            Returns the hash of the file
    :rtype: str
    """

    global dest_hashes

    if path not in dest_hashes:
        dest_hashes[path] = list()

    with open(path, 'rb') as f_handle:
        current_hash = hashlib.md5(f_handle.read()).hexdigest()

    if current_hash not in dest_hashes[path]:
        dest_hashes[path].append(current_hash)

    return current_hash


def recurse_dir(source_dir, sub_dir):
    """
    recurs_dir - recursively walk a source directory

    :type source_dir: str   Source directory
    :type sub_dir: str      Current subdirectory of source directory
    """

    global args
    global dest_hashes

    if sub_dir is None:
        source = source_dir
        dest = args.destination
    else:
        source = os.path.sep.join([source_dir, sub_dir])
        dest = os.path.sep.join([args.destination, sub_dir])

    if not os.path.isdir(dest):
        os.mkdir(dest)

    for f in os.listdir(source):
        if os.path.isdir(os.path.sep.join([source, f])):
            # This is a directory; recurse down into it
            if sub_dir is None:
                recurse_dir(source_dir, f)
            else:
                recurse_dir(source_dir, os.path.sep.join([sub_dir, f]))
        else:
            # This isn't a directory; handle merge
            if not os.path.exists(os.path.sep.join([dest, f])):
                # If the file doesn't exist in the dest, copy it
                shutil.copy2(
                    os.path.sep.join([source, f]),
                    os.path.sep.join([dest, f])
                )
                assure_dest_hash(os.path.sep.join([dest, f]))
            else:
                # The file exists; check to see if it's older than the one in
                # the source directory
                s_mod = os.stat(os.path.sep.join([source, f])).st_mtime
                d_mod = os.stat(os.path.sep.join([dest, f])).st_mtime

                # Take a hash of the file; we'll use this in a few places to
                # make sure that we don't end up spamming
                with open(os.path.sep.join([source, f]), 'rb') as f_handle:
                    s_hash = hashlib.md5(f_handle.read()).hexdigest()
                d_hash = assure_dest_hash(os.path.sep.join([dest, f]))

                if s_mod > d_mod:
                    # Source is newer; save off the dest file and copy in the
                    # newer source file
                    if s_hash == d_hash:
                        print(os.path.sep.join([source, f]) + '; newer but identical; updating modified date')
                        os.utime(os.path.sep.join([source, f]), (s_mod, s_mod))
                    else:
                        print(os.path.sep.join([source, f]) + '; newer and different; save/copy')
                        shutil.move(
                            os.path.sep.join([dest, f]),
                            os.path.sep.join([dest, f]) + '--' + ts_str(d_mod)
                        )
                        shutil.copy2(
                            os.path.sep.join([source, f]),
                            os.path.sep.join([dest, f])
                        )
                        dest_hashes[os.path.sep.join([dest, f])].append(s_hash)
                else:
                    if s_mod != d_mod:
                        # The destination is newer; copy the source, but append
                        # a timestamp to the name

                        if s_hash in dest_hashes[os.path.sep.join([dest, f])]:
                            # If we already have a copy of this, we shouldn't
                            # make another one
                            continue

                        print(os.path.sep.join([source, f]) + '; older but different; saving')
                        shutil.copy2(
                            os.path.sep.join([source, f]),
                            os.path.sep.join([dest, f]) + '--' + ts_str(s_mod)
                        )
                        dest_hashes[os.path.sep.join([dest, f])].append(s_hash)


# Main entry point
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', help='Destination path')
    parser.add_argument('source', nargs='*', help='Source paths')
    args = parser.parse_args()

    # Sanity check the arguments
    if not issubclass(list, type(args.source)):
        print("ERROR: source is not a list")
        sys.exit(-1)

    for src in args.source:
        if not os.path.isdir(src):
            print("ERROR: source path " + src + " does not exist")
            sys.exit(-1)

    # Recursively walk the source directories
    for src in args.source:
        print("####### Processing source " + src + " #######")
        recurse_dir(src, None)

    print("Run complete")
