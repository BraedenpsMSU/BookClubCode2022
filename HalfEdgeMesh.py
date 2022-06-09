from typing import List, Tuple, Any
# TODO refactor and add vtx class


def min_arg(arr: list) -> Tuple[Any, int]:
    _min = arr[0]
    pos = 0
    for new_pos in range(len(arr)):
        if arr[new_pos] < _min:
            _min = arr[new_pos]
            pos = new_pos
    return _min, pos


def rotate_to_min(arr: list) -> list:
    _, pos = min_arg(arr)
    return [arr[(pos+i) % len(arr)] for i in range(len(arr))]


class SparseMatrix:
    def __init__(self, c_num, r_num):
        self.c_num = c_num
        self.r_num = r_num
        self.__col_data = {i: dict() for i in range(c_num)}
        self.__row_data = {i: dict() for i in range(r_num)}

    def __setitem__(self, key: Tuple[int, int], value):
        self.__col_data[key[1]][key[0]] = value
        self.__row_data[key[0]][key[1]] = value

    def __getitem__(self, item: Tuple[int, int]):
        return self.__col_data[item[1]][item[0]]

    def get_sparse_col(self, col):
        return self.__col_data[col].copy()

    def get_sparse_row(self, row):
        return self.__row_data[row].copy()

    def get_col_vect(self, col):
        outp = [0 for _ in range(self.r_num)]
        for key in self.__col_data[col]:
            outp[key] = self.__col_data[col][key]
        return outp

    def get_row_vect(self, row):
        outp = [0 for _ in range(self.c_num)]
        for key in self.__row_data[row]:
            outp[key] = self.__row_data[row][key]
        return outp

    def get_full_mat(self):
        return [self.get_row_vect(i) for i in range(self.r_num)]

    def display(self):
        outp = ""
        for i in range(self.r_num):
            outp += str(self.get_row_vect(i))
            outp += "\n"
        print(outp)


class Edge:
    def __init__(self):
        self.half_edges = []
        self.index = -1  # modelled after source code.


class HalfEdge:
    def __init__(self, endpoints=None):
        self.endpoints = endpoints
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
            # # check next, call to super to not recurse
            # elif not super(HalfEdge, self.next).__eq__(other.next):
            #     return False
            # # check twin, call to super to not recurse
            # elif not super(HalfEdge, self.twin).__eq__(other.twin):
            #     return False
            # else:
            #     return True
            return self.endpoints == other.endpoints

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

    def get_vertices(self) -> List[int]:
        hedges = self.get_half_edges()
        return [hedge.endpoints[0] for hedge in hedges]

    def get_edges(self) -> List[int]:
        outp = []
        if self.edge is not None:
            cur_edge = self.edge
            while True:
                outp.append(cur_edge.edge.index)
                cur_edge = cur_edge.next
                if cur_edge == self.edge:
                    return outp
        else:
            return outp


class HalfEdgeMesh:
    def __init__(self):
        self.vertices = []  # vertices for mesh
        self.edges = []  # Edges of our mesh
        self.half_edges = []  # Half Edges of our mesh
        self.faces: List[Face] = []  # Faces of our mesh
        self.boundary = []  # unsure if needed currently
        self.index_built = False
        self.index = dict()

    def build_index(self):
        for vtx in self.vertices:
            self.index[(vtx,)] = vtx
        for edge in self.edges:
            self.index[tuple(edge.half_edges[0].endpoints)] = edge.index
            self.index[tuple(edge.half_edges[1].endpoints)] = edge.index
        for face in self.faces:
            face_index = face.get_vertices()
            face_index_rev = face_index.copy()
            face_index_rev.reverse()
            face_index = rotate_to_min(face_index)
            face_index_rev = rotate_to_min(face_index_rev)
            self.index[tuple(face_index)] = face.index
            self.index[tuple(face_index_rev)] = face.index

    def build_vtx_vector(self, vtx_simplices: List[Tuple[int]]):
        if not self.index_built:
            self.build_index()
        vect = [0 for _ in range(len(self.vertices))]
        non_zero = [self.index[smplx] for smplx in vtx_simplices]
        for value in non_zero:
            vect[value] = 1
        return vect

    def build_edge_vector(self, edge_simplices: List[Tuple[int, int]]):
        if not self.index_built:
            self.build_index()
        vect = [0 for _ in range(len(self.edges))]
        non_zero = [self.index[smplx] for smplx in edge_simplices]
        for value in non_zero:
            vect[value] = 1
        return vect

    def build_face_vector(self, face_simplices: List[Tuple[int, ...]]):
        if not self.index_built:
            self.build_index()
        vect = [0 for _ in range(len(self.faces))]
        non_zero = [self.index[tuple(rotate_to_min(list(smplx)))] for smplx in face_simplices]
        for value in non_zero:
            vect[value] = 1
        return vect

    def build_vtx_edge_matrix(self):
        outp = SparseMatrix(c_num=len(self.edges), r_num=len(self.vertices))
        for edge in self.edges:
            for vtx in edge.half_edges[0].endpoints:
                outp[vtx, edge.index] = 1
        return outp

    def build_edge_face_matrix(self):
        outp = SparseMatrix(c_num=len(self.faces), r_num=len(self.edges))
        for face in self.faces:
            for edge in face.get_edges():
                outp[edge, face.index] = 1
        return outp

    # @classmethod
    # def build_hem(cls, faces: List[List]) -> "HalfEdgeMesh":
    #     outp = cls()
    #     h_edges = {}
    #     for face in faces:
    #         # add new face to output
    #         f = Face()
    #         f.index = len(outp.faces)
    #         outp.faces.append(f)
    #         for pos in range(len(face)):
    #             h_edge = (face[pos], face[(pos + 1) % len(face)])
    #             h_edges[h_edge] = HalfEdge(endpoints=(face[pos], face[(pos + 1) % len(face)]))
    #             if h_edge[0] not in outp.vertices:
    #                 outp.vertices.append(h_edge[0])
    #             if h_edge[1] not in outp.vertices:
    #                 outp.vertices.append(h_edge[1])
    #             if (h_edge[1], h_edge[0]) in h_edges:
    #                 # updating correct edge.
    #                 h_edges[h_edge].edge = h_edges[(h_edge[1], h_edge[0])].edge
    #                 h_edges[h_edge].edge.half_edges.append(h_edges[h_edge])
    #                 # updating twin
    #                 h_edges[h_edge].twin = h_edges[(h_edge[1], h_edge[0])]
    #                 h_edges[(h_edge[1], h_edge[0])].twin = h_edges[h_edge]
    #             else:
    #                 # create new edge if one does not exit
    #                 edge = Edge()
    #                 edge.index = len(outp.edges)  # corresponds to next index
    #                 h_edges[h_edge].edge = edge
    #                 edge.half_edges.append(h_edges[h_edge])
    #                 outp.edges.append(edge)
    #         # updating next
    #         for pos in range(len(face)):
    #             h_edge = (face[pos], face[(pos + 1) % len(face)])
    #             h_edge_next = (face[(pos + 1) % len(face)], face[(pos + 2) % len(face)])
    #             h_edges[h_edge].next = h_edges[h_edge_next]
    #         outp.faces[-1].edge = h_edges[(face[0], face[1])]
    #     outp.half_edges = [h_edges[key] for key in h_edges]
    #     return outp

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
                if h_edge in h_edges:
                    # reverse the face
                    raise Exception
            for pos in range(len(face)):
                h_edge = (face[pos], face[(pos + 1) % len(face)])
                h_edges[h_edge] = HalfEdge(endpoints=(face[pos], face[(pos + 1) % len(face)]))
                h_edges[h_edge].vtx = vtx[face[pos]]
                if h_edge[0] not in outp.vertices:
                    outp.vertices.append(h_edge[0])
                if h_edge[1] not in outp.vertices:
                    outp.vertices.append(h_edge[1])
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
                    edge.index = len(outp.edges)  # corresponds to next index
                    h_edges[h_edge].edge = edge
                    edge.half_edges.append(h_edges[h_edge])
                    outp.edges.append(edge)
            # updating next
            for pos in range(len(face)):
                h_edge = (face[pos], face[(pos + 1) % len(face)])
                h_edge_next = (face[(pos + 1) % len(face)], face[(pos + 2) % len(face)])
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
                    pos = (float(splt[1]), float(splt[2]), float(splt[3]))
                    vtxs.append(pos)
                elif splt[0] == 'f':
                    face = tuple([int(pos.split('/')[0]) - 1 for pos in splt[1:]])
                    faces.append(face)
        return cls.from_loaded_obj(vtxs, faces)


if __name__ == "__main__":
    to2 = HalfEdgeMesh.form_file('test.obj')
    to3 = HalfEdgeMesh.form_file("torus.obj")
    sp_mat = SparseMatrix(2, 4)
    test = to2.build_vtx_edge_matrix()
    test2 = to2.build_edge_face_matrix()
    test3 = to2.build_vtx_vector([(0,), (1,), (3,)])
    test4 = to2.build_edge_vector([(0, 1), (2, 3), (3, 2)])
    test5 = to2.build_face_vector([(3, 2, 1), (2, 0, 1)])
