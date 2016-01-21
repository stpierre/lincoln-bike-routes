#!/usr/bin/env python
"""A simple script to improve geojson.io data.

geojson.io can't produce MultiLineStrings, which makes the raw data
unnecessarily verbose. This script cleans up the data and merges
LineStrings where possible.
"""
from __future__ import print_function

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=argparse.FileType("r"))
    options = parser.parse_args()

    raw_data = json.load(options.input)
    data = {"type": "FeatureCollection", "features": []}

    trails = {}
    for feature in raw_data["features"]:
        props = feature["properties"]
        if "name" in props:
            name = props["name"]
        else:
            print("Feature is missing a name: %s" % props, file=sys.stderr)
            continue

        ttype = props.get("type")

        trails.setdefault(name, {}).setdefault(ttype, []).append(feature)

    for name1 in trails.keys():
        for name2 in trails.keys():
            if name1 != name2 and name1.lower() == name2.lower():
                print("Possible duplicate trails: %s, %s" % (name1, name2),
                      file=sys.stderr)

    for name, types in trails.items():
        if None in types:
            if len(types) == 2:
                all_types = list(types.keys())
                all_types.remove(None)
                default_type = all_types[0]
                types[default_type].extend(types[None])
                del types[None]
            else:
                print("Unknown trail type for %s; candidates: %s" %
                      (name, types.keys()), file=sys.stderr)

        for ttype, features in types.items():
            data["features"].append(
                {"type": "Feature",
                 "properties": {"name": name, "type": ttype},
                 "geometry": {"type": "MultiLineString",
                              "coordinates": [f["geometry"]["coordinates"]
                                              for f in features]}})

    print(json.dumps(data))


if __name__ == "__main__":
    sys.exit(main())
