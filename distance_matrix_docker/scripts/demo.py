#! /usr/bin/python3

from here_connection.here_connection import HereConnector, WayPointParameter


if __name__ == "__main__":
    app_id = "9QUQ9EMEU9Ex8wYShCOu"
    app_code = "0FLZ9442aCDEqBa1Xw3xwQ"

    hc = HereConnector(app_id, app_code)

    starts = list()
    starts.append(WayPointParameter(47.939517, 12.936859, "A"))
    starts.append(WayPointParameter(48.118741, 11.663132, "B"))

    destinations = list()
    destinations.append(WayPointParameter(47.939517, 12.936859, "A"))
    destinations.append(WayPointParameter(48.118741, 11.663132, "B"))

    max_km = 500
    mat = hc.get_distance_matrix(starts, destinations, max_dist_km=max_km)
    if mat:
        print("(-1 for distances above %i km)" % (max_km))
        hc.print_distance_matrix(starts, destinations, mat)
    print("")

