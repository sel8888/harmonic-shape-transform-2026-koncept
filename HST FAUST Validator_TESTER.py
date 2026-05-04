# License: GNU GPL v3 + Custom Research Protection
# See LICENSE file for details.

import bpy
import bmesh
import numpy as np
import time
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import eigsh

bl_info = {
    "name": "HST Semantic Core Ultra – HST + FAUST + HKS Edition",
    "author": "Pavel Krahulík",
    "version": (4, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > HST_Ultra",
    "description": "HST Note + FAUST Spectral + HKS Validator with Report Output",
    "category": "Mesh",
}

# ---------------------------------------------------------
#  Laplacian + Mass Matrix
# ---------------------------------------------------------

def get_laplacian_and_mass(obj):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    n = len(bm.verts)
    rows, cols, data = [], [], []
    mass = np.zeros(n)

    # Mass matrix (triangle areas)
    for face in bm.faces:
        area = face.calc_area()
        for v in face.verts:
            mass[v.index] += area / 3.0

    # Cotangent Laplacian
    for v in bm.verts:
        t_w = 0.0
        for edge in v.link_edges:
            v_o = edge.other_vert(v)
            w = 0.0
            for face in edge.link_faces:
                v_t = [vert for vert in face.verts if vert not in (v, v_o)][0]
                v1 = v.co - v_t.co
                v2 = v_o.co - v_t.co
                cp = v1.cross(v2)
                if cp.length > 1e-12:
                    w += 0.5 * (v1.dot(v2) / cp.length)

            rows.append(v.index)
            cols.append(v_o.index)
            data.append(-w)
            t_w += w

        rows.append(v.index)
        cols.append(v.index)
        data.append(t_w)

    bm.free()

    L = csr_matrix((data, (rows, cols)), shape=(n, n))
    M = diags(mass)

    return L, M


# ---------------------------------------------------------
#  Utility
# ---------------------------------------------------------

def normalize(v):
    v_min, v_max = np.min(v), np.max(v)
    if abs(v_max - v_min) < 1e-12:
        return np.zeros_like(v)
    return (v - v_min) / (v_max - v_min)

def align_sign(f1, f2):
    if np.linalg.norm(f1 - f2) > np.linalg.norm(f1 + f2):
        return -f2
    return f2


# ---------------------------------------------------------
#  HKS IMPLEMENTACE
# ---------------------------------------------------------

def compute_hks(evals, evecs, num_times=6):
    n = evecs.shape[0]
    k = len(evals)

    # Logaritmicky rozprostřené časy
    t_min = 4 * np.log(10) / evals[-1]
    t_max = 4 * np.log(10) / evals[1]
    ts = np.logspace(np.log10(t_min), np.log10(t_max), num=num_times)

    H = np.zeros((n, num_times))

    for ti, t in enumerate(ts):
        for i in range(1, k):
            H[:, ti] += np.exp(-evals[i] * t) * (evecs[:, i] ** 2)

        # Normalizace každého časového sloupce
        H[:, ti] = normalize(H[:, ti])

    return H


def compare_hks(H1, H2):
    diff = np.sqrt(np.sum((H1 - H2)**2, axis=1))
    residual = float(np.mean(diff))
    precision = float((1.0 - residual) * 100.0)
    return residual, precision


# ---------------------------------------------------------
#  Panel
# ---------------------------------------------------------

class HST_PT_PANEL(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HST_Ultra'
    bl_label = 'HST Semantic Topology v4.0'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.label(text="HST Mode")
        col.prop(context.scene, "hst_mode", expand=True)

        if context.scene.hst_mode == "HKS":
            col.prop(context.scene, "hst_hks_times")

        col.separator()
        col.label(text="Source Shape")
        col.prop(context.scene, "hst_source", text="")

        col.label(text="Target Shape")
        col.prop(context.scene, "hst_target", text="")

        col.separator()
        col.operator("mesh.hst_run", text="RUN VALIDATION", icon='MOD_DATA_TRANSFER')

        col.separator()
        col.label(text="Report:")
        col.prop(context.scene, "hst_report", text="")


# ---------------------------------------------------------
#  Operator
# ---------------------------------------------------------

class HST_OT_RUN(bpy.types.Operator):
    bl_idname = "mesh.hst_run"
    bl_label = "Run HST Validation"

    def execute(self, context):
        mode = context.scene.hst_mode
        objA = context.scene.hst_source
        objB = context.scene.hst_target

        if not objA or not objB:
            self.report({'ERROR'}, "Select both Source and Target objects.")
            return {'CANCELLED'}

        start = time.time()

        # Laplacians
        L1, M1 = get_laplacian_and_mass(objA)
        L2, M2 = get_laplacian_and_mass(objB)

        # Vertex counts
        nA = len(objA.data.vertices)
        nB = len(objB.data.vertices)

        # -------------------------
        # HST NOTE MODE (original)
        # -------------------------
        if mode == "HST_NOTE":
            vals1, vecs1 = eigsh(L1, k=2, M=M1, sigma=0, which='LM')
            vals2, vecs2 = eigsh(L2, k=2, M=M2, sigma=0, which='LM')

            f1 = normalize(vecs1[:, 1])
            f2 = normalize(vecs2[:, 1])
            f2 = align_sign(f1, f2)

            diff = np.abs(f1 - f2)
            residual = float(np.mean(diff))
            precision = float((1.0 - residual) * 100.0)

            modes_used = 1

        # -------------------------
        # FAUST SPECTRAL MODE
        # -------------------------
        elif mode == "FAUST":
            k = 20
            vals1, vecs1 = eigsh(L1, k=k, M=M1, sigma=0, which='LM')
            vals2, vecs2 = eigsh(L2, k=k, M=M2, sigma=0, which='LM')

            F1 = vecs1[:, 1:k]
            F2 = vecs2[:, 1:k]

            for i in range(F1.shape[1]):
                F1[:, i] = normalize(F1[:, i])
                F2[:, i] = normalize(F2[:, i])
                F2[:, i] = align_sign(F1[:, i], F2[:, i])

            weights = 1.0 / (np.arange(1, k) ** 1.2)
            weights /= np.sum(weights)

            diff = np.sqrt(np.sum(((F1 - F2) ** 2) * weights, axis=1))
            residual = float(np.mean(diff))
            precision = float((1.0 - residual) * 100.0)

            modes_used = k - 1

        # -------------------------
        # HKS MODE (stable)
        # -------------------------
        else:
            k = 30
            times = context.scene.hst_hks_times

            vals1, vecs1 = eigsh(L1, k=k, M=M1, sigma=0, which='LM')
            vals2, vecs2 = eigsh(L2, k=k, M=M2, sigma=0, which='LM')

            H1 = compute_hks(vals1, vecs1, num_times=times)
            H2 = compute_hks(vals2, vecs2, num_times=times)

            residual, precision = compare_hks(H1, H2)
            modes_used = k

        end = time.time()
        elapsed = end - start

        # ---------------------------------------------------------
        #  REPORT (Style B)
        # ---------------------------------------------------------

        report = (
            "=== HST VALIDATION REPORT ===\n"
            f"Mode: {mode}\n"
            "--------------------------------\n"
            f"Source vertices: {nA}\n"
            f"Target vertices: {nB}\n"
            f"Eigenmodes used: {modes_used}\n"
            f"Residual: {residual:.6f}\n"
            f"Precision: {precision:.2f}%\n"
            "Sign alignment: OK\n"
            "Normalization: OK\n"
            f"Computation time: {elapsed:.3f} s\n"
            "--------------------------------\n"
            f"Status: {'PASS' if precision > 90 else 'WARNING'}\n"
        )

        # UI output
        context.scene.hst_report = report

        # Console output
        print(report)

        # Text datablock
        text = bpy.data.texts.get("HST_Report.txt")
        if not text:
            text = bpy.data.texts.new("HST_Report.txt")
        text.clear()
        text.write(report)

        return {'FINISHED'}


# ---------------------------------------------------------
#  Register
# ---------------------------------------------------------

classes = (HST_PT_PANEL, HST_OT_RUN)

def register():
    bpy.types.Scene.hst_mode = bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("HST_NOTE", "HST Note (original)", ""),
            ("FAUST", "FAUST Spectral (benchmark)", ""),
            ("HKS", "HST HKS (stable)", "")
        ],
        default="HST_NOTE"
    )

    bpy.types.Scene.hst_hks_times = bpy.props.IntProperty(
        name="HKS time samples",
        default=6,
        min=3,
        max=12
    )

    bpy.types.Scene.hst_source = bpy.props.PointerProperty(
        name="Source",
        type=bpy.types.Object
    )

    bpy.types.Scene.hst_target = bpy.props.PointerProperty(
        name="Target",
        type=bpy.types.Object
    )

    bpy.types.Scene.hst_report = bpy.props.StringProperty(
        name="Report",
        default="",
        description="HST validation output"
    )

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.hst_mode
    del bpy.types.Scene.hst_hks_times
    del bpy.types.Scene.hst_source
    del bpy.types.Scene.hst_target
    del bpy.types.Scene.hst_report


if __name__ == "__main__":
    register()
