from typing import List, Tuple


class Edge(object):
    def __init__(self):
        self.half_edges = []
        self.index = -1  # modelled after source code.


class HalfEdge(object):
    def __init__(self, loc=None):
        self.loc = loc
        self.vtx: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self.next: HalfEdge | None = None
        self.twin: HalfEdge | None = None
        self.edge: Edge | None = None
        self.face: Face | None = None
        self.on_boundary: bool = False

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        else:
            # check faces
            if self.face != other.face:
                return False
            # check next, call to super to not recurse
            elif not super(HalfEdge, self.next).__eq__(other.next):
                return False
            # check twin, call to super to not recurse
            elif not super(HalfEdge, self.twin).__eq__(other.twin):
                return False
            else:
                return True

    def __ne__(self, other):
        return not self == other


class Face:
    def __init__(self):
        self.edge: HalfEdge | None = None
        self.index: int = -1  # modelled after the source code

    def get_half_edges(self) -> List[HalfEdge]:
        outp = []
        if self.edge is not None:
            cur_edge = self.edge
            while True:
                outp.append(cur_edge)
                cur_edge = cur_edge.next
                if cur_edge == self.edge:
                    return outp
        else:
            return outp


class HalfEdgeMesh:
    def __init__(self):
        self.half_edges = []
        self.faces: List[Face] = []
        self.boundary = []  # unsure if needed currently

    @classmethod
    def build_hem(cls, faces: List[List]) -> "HalfEdgeMesh":
        outp = cls()
        edges = {}
        for face in faces:
            outp.faces.append(Face())
            for pos in range(len(face)):
                edge = (face[pos], face[(pos + 1) % len(face)])
                print(edge)
                edges[edge] = HalfEdge(loc=(face[pos], face[(pos + 1) % len(face)]))
                if (edge[1], edge[0]) in edges:
                    edges[edge].twin = edges[(edge[1], edge[0])]
                    edges[(edge[1], edge[0])].twin = edges[edge]
            for pos in range(len(face)):
                edge = (face[pos], face[(pos + 1) % len(face)])
                edge_next = (face[(pos + 1) % len(face)], face[(pos + 2) % len(face)])
                edges[edge].next = edges[edge_next]
            outp.faces[-1].edge = edges[(face[0], face[1])]
        outp.half_edges = [edges[key] for key in edges]
        return outp

if __name__ == "__main__":
    test_input = [[1, 2, 3], [3, 2, 4], [1, 3, 4], [2, 1, 4]]
    test_output = HalfEdgeMesh.build_hem(test_input)
