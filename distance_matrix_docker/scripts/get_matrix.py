#! /usr/bin/python3

import os

from here_connection.here_connection import HereConnector, WayPointParameter
import yaml


if __name__ == "__main__":

    in_docker = os.environ.get('IN_DOCKER', False)

    prefix = "" if in_docker else ".."

    debug = True

    key_file = prefix + "/data/keys.yaml"
    data_file = prefix + "/data/positions.txt"
    out_file = prefix + "/data/result.txt"

    # Read access codes for Here API
    try:
        with open(key_file, 'r') as stream:
            keys = yaml.load(stream)
    except FileNotFoundError:
        print("No key file at %s" % (key_file))
        exit(1)

    try:
        app_id = keys['app_id']
        app_code = keys['app_code']
    except KeyError:
        print("Could not find app_id and app_code in keyfile at %s" % (key_file))
        exit(2)

    hc = HereConnector(app_id, app_code)

    # Load positions:
    try:
        f = open(data_file, 'r')
    except FileNotFoundError:
        print("no data file at %s" % (data_file))
        exit(3)

    positions = list()

    for l in f.readlines():
        spl = l.strip().split(',')
        if not len(spl) == 3:
            print("Invalid line '%s'" % (l))
            exit(4)
        positions.append(WayPointParameter(float(spl[1]), float(spl[2]), spl[0]))

    print("Found %i positions in '%s'" % (len(positions), data_file))

    # maximal size of distance matrix
    max_start_cnt = 15
    max_dest_cnt = 100

    cnt_pos = len(positions)

    start_ndx = 0

    off = open(out_file, 'w')
    print("Writing distances to '%s'" % (out_file))

    distance_count = 0

    while start_ndx < cnt_pos:
        dest_ndx = start_ndx  # symmetric distances
        last_start = min(start_ndx+max_start_cnt, cnt_pos)
        while dest_ndx < cnt_pos:
            last_dest = min(dest_ndx + max_dest_cnt, cnt_pos)
            print("Processing")
            print(start_ndx, last_start, dest_ndx, last_dest)

            starts = positions[start_ndx:last_start]
            destinations = positions[dest_ndx:last_dest]
            distance_count += len(starts)*len(destinations)

            if debug:
                for i in range(len(starts)):
                    for j in range(len(destinations)):
                        off.write("%s, %s, %i\n" % (starts[i].label,
                                                    destinations[j].label,
                                                    i*j))
            else:
                mat = hc.get_distance_matrix(starts, destinations, max_dist_km=-1)
                for i in range(len(starts)):
                    for j in range(len(destinations)):
                        off.write("%s, %s, %i\n" % (starts[i].label,
                                                    destinations[j].label,
                                                    mat[i][j]))

            dest_ndx = last_dest
        start_ndx = last_start

    print("Wrote %i distances to '%s'" % (distance_count, out_file))