#author: Julien Klaus
#email: julien.klaus@gmx.de

import os
from pathlib import Path
from pprint import pprint

import api as api

from qengine import Query


if __name__ == "__main__":
    manifest = Path(os.path.join("..","examples"))
    api.create_graph_from_path(manifest)
    api.discover_relations()
    print(api.CABOTO_GRAPH)

    query = Query("GET nodes WHERE type=Pod", api.CABOTO_GRAPH)
    result = query.execute()
    print(result)

    # Query time
    pprint(api.exec_query("AllPods"))