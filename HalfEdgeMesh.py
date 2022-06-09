from typing import List, Tuple



class Edge(object):
    def __init__(self):
        self.half_edges = []
        self.index = -1  # modelled after source code.


class HalfEdge(object):
    def __init__(self, loc=None):
        self.loc = loc  # really for testing - stores the endpoint of the edges
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
        self.edges = []  # Edges of our mesh
        self.half_edges = []  # Half Edges of our mesh
        self.faces: List[Face] = []  # Faces of our mesh
        self.boundary = []  # unsure if needed currently

    @classmethod
    def build_hem(cls, faces: List[List]) -> "HalfEdgeMesh":
        outp = cls()
        h_edges = {}
        for face in faces:
            # add new face to output
            f = Face()
            f.index = len(outp.faces)
            outp.faces.append(f)
            for pos in range(len(face)):
                h_edge = (face[pos], face[(pos + 1) % len(face)])
                print(h_edge)
                h_edges[h_edge] = HalfEdge(loc=(face[pos], face[(pos + 1) % len(face)]))
                if (h_edge[1], h_edge[0]) in h_edges:
                    # updating correct edge.
                    h_edges[h_edge].edge = h_edges[(h_edge[1], h_edge[0])].edge
                    h_edges[h_edge].edge.half_edges.append(h_edges[h_edge])
                    # updating twin
                    h_edges[h_edge].twin = h_edges[(h_edge[1], h_edge[0])]
                    h_edges[(h_edge[1], h_edge[0])].twin = h_edges[h_edge]
                else:
                    # create new edge if one does not exit
                    edge = Edge()
                    edge.index = len(outp.edges) # corresponds to next index
                    h_edges[h_edge].edge = edge
                    edge.half_edges.append(h_edges[h_edge])
                    outp.edges.append(edge)
            # updating next
            for pos in range(len(face)):
                h_edge = (face[pos], face[(pos + 1) % len(face)])
                h_edge_next = (face[(pos + 1) % len(face)], face[(pos + 2) % len(face)])
                h_edges[h_edge].next = h_edges[h_edge_next]
            outp.faces[-1].edge = h_edges[(face[0], face[1])]
        outp.half_edges = [h_edges[key] for key in h_edges]
        return outp

    @classmethod
    def from_loaded_obj(cls, vtx: List[Tuple[float, float, float]], faces: List[Tuple[int, ...]]):
        """
        Precondition: the surface is orientable
        :param vtx: position of the vertices
        :param faces: the faces as describe in terms of vertices
        :return: half edge mesh on the vertices
        """
        outp = cls()
        h_edges = {}
        for face in faces:
            f = Face()
            f.index = len(outp.faces)
            outp.faces.append(f)
            # determine oriented direction of face
            for pos in range(len(face)):
                h_edge = (face[pos], face[(pos + 1) % len(face)])
                if h_edge in h_edges:
                    # reverse the face
                    face = list(face)
                    face.reverse()
                    break
            for pos in range(len(face)):
                h_edge = (face[pos], face[(pos + 1) % len(face)])
                print(h_edge)
                h_edges[h_edge] = HalfEdge(loc=(face[pos], face[(pos + 1) % len(face)]))
                h_edges[h_edge].vtx = vtx[face[pos]]
                if (h_edge[1], h_edge[0]) in h_edges:
                    # updating correct edge.
                    h_edges[h_edge].edge = h_edges[(h_edge[1], h_edge[0])].edge
                    h_edges[h_edge].edge.half_edges.append(h_edges[h_edge])
                    # updating twin
                    h_edges[h_edge].twin = h_edges[(h_edge[1], h_edge[0])]
                    h_edges[(h_edge[1], h_edge[0])].twin = h_edges[h_edge]
                else:
                    # create new edge if one does not exit
                    edge = Edge()
                    edge.index = len(outp.edges) # corresponds to next index
                    h_edges[h_edge].edge = edge
                    edge.half_edges.append(h_edges[h_edge])
                    outp.edges.append(edge)
            # updating next
            for pos in range(len(face)):
                h_edge = (face[pos], face[(pos + 1) % len(face)])
                h_edge_next = (face[(pos + 1) % len(face)], face[(pos + 2) % len(face)])
                print(h_edges)
                h_edges[h_edge].next = h_edges[h_edge_next]
            # set a reference edge for the face.
            outp.faces[-1].edge = h_edges[(face[0], face[1])]
        outp.half_edges = [h_edges[key] for key in h_edges]
        return outp

    @classmethod
    def form_file(cls, path):
        vtxs = []
        faces = []
        with open(path, 'r') as f_i:
            for line in f_i.readlines():
                splt = line.split()
                if splt[0] == "#":
                    continue
                elif splt[0] == "v":
                    print(splt)
                    print(line)
                    pos = (float(splt[1]), float(splt[2]), float(splt[3]))
                    vtxs.append(pos)
                elif splt[0] == 'f':
                    face = tuple([int(pos.split('/')[0]) - 1 for pos in splt[1:]])
                    faces.append(face)
        return cls.from_loaded_obj(vtxs, faces)


if __name__ == "__main__":
    test_input = [[0, 1, 2], [2, 1, 3], [0, 2, 3], [1, 0, 3]]
    test_output1 = HalfEdgeMesh.build_hem(test_input)
    test_output2 = HalfEdgeMesh.form_file('test.obj')


