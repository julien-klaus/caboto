
import os
from pathlib import Path

import api
from qengine import Query


def test(api, query_string, query_file):
    # query the engine
    query = Query(query_string, api.CABOTO_GRAPH)
    result_qe = query.execute()
    # query the file
    result_qf = api.exec_query(query_file)
    print(query_string)
    print(result_qe)
    print(result_qf)
    print()
    # check for equality
    return set(result_qe) == set(result_qf)


def test_all(api):
    assert test(api, "get nodes n where n.type=Application", "AllApplications")
    assert test(api, "get nodes n where n.type=Ingress", "AllIngress")
    assert test(api, "get nodes n where n.type=Pod", "AllPods")
    assert test(api, "get nodes n where n.type=Service", "AllServices")
    assert test(api, "get edges (m,n) where (m,n).label=hosts", "IngressToHost")
    assert test(api, "get nodes n where n.type=ConfigMap", "AllConfigMaps")
    assert test(api, "get edges (m,n) where m.label=serves and n.type=Pod", "IngressToContainerImage")
    assert test(api, "get edges (m,n) where n.type=Pod and m.type=Service and m.name=admin", "ServiceToPod")
    return True

if __name__ == "__main__":
    # create graph from mainfest
    manifest = Path(os.path.join("examples"))
    api.create_graph_from_path(manifest)
    api.discover_relations()
    graph = api.CABOTO_GRAPH

    # run tests    
    print(f"Test {'passed' if test_all(api) else 'failed'}")


