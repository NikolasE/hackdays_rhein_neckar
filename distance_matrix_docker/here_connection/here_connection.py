#! /usr/bin/python3

import requests
from copy import deepcopy


class WayPointParameter:
    # https://developer.here.com/documentation/routing/topics/resource-param-type-waypoint.html
    def __init__(self, lat, lng, label=''):
        self.latitude = lat
        self.longitude = lng
        self.label = label

    def __str__(self):
        s = "geo!%f,%f" % (self.latitude, self.longitude)
        if self.label:
            s += ';;'+self.label  # empty radius
        return s

    def geo_str(self):
        return "%s,%s" % (self.latitude, self.longitude)


class HereConnector:
    matrix_url = "https://matrix.route.api.here.com/routing/7.2/calculatematrix.json"

    def __init__(self, app_id, app_code):
        self.mode = 'fastest;car;traffic:disabled'
        self.app_data_dict = {"app_id": app_id, "app_code": app_code}

    def get_initial_appdata(self):
        app_data = deepcopy(self.app_data_dict)
        app_data['mode'] = self.mode
        return app_data


    @staticmethod
    def print_distance_matrix(starts, destinations, matrix):
        topline = 'Distance (km)'
        top_len = len(topline)
        for p in destinations:
            assert isinstance(p, WayPointParameter)
            topline += '%15s' % p.label
        print(topline)
        for i, s in enumerate(starts):
            l = s.label + ((top_len - len(s.label)) * ' ')
            for j in range(len(destinations)):
                l += "%15i" % (matrix[i][j] // 1000)
            print(l)
        print("")

    # https://developer.here.com/documentation/routing/topics/resource-calculate-matrix.html
    def get_distance_matrix(self, starts, destinations, max_dist_km=-1):
        app_data = self.get_initial_appdata()
        app_data['summaryAttributes'] = 'distance'  # 'distance, costfactor, traveltime'

        for i, p in enumerate(starts):
            assert isinstance(p, WayPointParameter)
            app_data['start' + str(i)] = str(p)
            # print(str(p))

        # TODO: check if iterable
        if not isinstance(destinations, list):
            destinations = [destinations]

        for i, p in enumerate(destinations):
            assert isinstance(p, WayPointParameter)
            app_data['destination' + str(i)] = str(p)

        if max_dist_km > 0:
            app_data['searchRange'] = max_dist_km * 1000

        r = requests.get(HereConnector.matrix_url, app_data)
        if r.status_code != 200:
            HereConnector.print_error(r)
            return None

        dist_mat = list()
        for i in range(len(starts)):
            dist_mat.append([-1] * len(destinations))

        j = r.json()

        mat = j['response']['matrixEntry']
        for e in mat:

            # catch distances above searchRange
            try:
                status = e['status']
                if status == 'rangeExceeded':
                    val = -1
                else:
                    print("Unhandled status exception: %s" % status)
                    val = -1
            except KeyError:
                summary = e['summary']
                val = summary['distance']
            dist_mat[e['startIndex']][e['destinationIndex']] = val

        return dist_mat

    @staticmethod
    def print_error(response):
        # print(response.json())
        try:
            print(response.json()['Details'])
            print(response.json()['AdditionalData'])
        except KeyError:
            print(response.json()['details'])
            print(response.json()['additionalData'])
