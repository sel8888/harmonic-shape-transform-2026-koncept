# HST ZoomOut Benchmark Addon v1.0
# Porovnání HST Note vs ZoomOut vs HST+ZoomOut přímo v Blenderu
#
# Author: Pavel Krahulík
# License: GNU GPL v3
#
# Instalace: Edit -> Preferences -> Add-ons -> Install -> vybrat tento soubor
# Použití: View3D -> Sidebar -> HST_Benchmark

import bpy
import bmesh
import numpy as np
import time
import os
import csv
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import eigsh

bl_info = {
    "name": "HST ZoomOut Benchmark v1.0",
    "author": "Pavel Krahulík",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > HST_Benchmark",
    "description": "HST Note vs ZoomOut vs HST+ZoomOut benchmark na FAUST datech",
    "category": "Mesh",
}


# ─────────────────────────────────────────────
# MATEMATICKÉ JÁDRO
# ─────────────────────────────────────────────

def get_laplacian_and_mass(obj):
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    n = len(bm.verts)
    rows, cols, data = [], [], []
    mass = np.zeros(n)
    for face in bm.faces:
        area = face.calc_area()
        for v in face.verts:
            mass[v.index] += area / 3.0
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
    M = diags(np.maximum(mass, 1e-12))
    return L, M


def get_vertices(obj):
    return np.array([v.co[:] for v in obj.data.vertices])


def norm01(v):
    vmin, vmax = np.min(v), np.max(v)
    return (v - vmin) / (vmax - vmin + 1e-12)


def bbox_diag(verts):
    return np.linalg.norm(verts.max(axis=0) - verts.min(axis=0))


def geo_error_normalized(verts_b, mapped, bb):
    """Standardní normalizovaná geodetická chyba."""
    errors = [
        np.linalg.norm(verts_b[mapped[i]] - verts_b[min(i, len(verts_b)-1)])
        for i in range(len(mapped))
    ]
    return np.mean(errors) / (bb + 1e-10)


def hst_map(note_a, note_b):
    """HST Note mapování přes level sety."""
    return np.array([np.argmin(np.abs(note_b - v)) for v in note_a])


def zoomout_refine(evecs_a, evecs_b, T12_init, k_init=10, k_step=5, k_final=40):
    """
    ZoomOut: iterativní zpřesňování functional map.
    T12_init: počáteční pointwise mapa (indexy z A do B)
    """
    n_a = evecs_a.shape[0]
    T12 = T12_init.copy()
    k = k_init
    while k <= min(k_final, evecs_a.shape[1], evecs_b.shape[1]):
        Phi_a = evecs_a[:, :k]
        Phi_b = evecs_b[:, :k]
        Phi_b_pulled = Phi_b[T12, :]
        C = np.linalg.lstsq(Phi_b_pulled, Phi_a, rcond=None)[0].T
        mapped_coords = Phi_a @ C.T
        target_coords = Phi_b
        new_T12 = np.zeros(n_a, dtype=int)
        batch = 500
        for start in range(0, n_a, batch):
            end = min(start + batch, n_a)
            diffs = (mapped_coords[start:end, np.newaxis, :] -
                     target_coords[np.newaxis, :, :])
            dists = np.sum(diffs**2, axis=2)
            new_T12[start:end] = np.argmin(dists, axis=1)
        T12 = new_T12
        k += k_step
    return T12


def apply_vertex_colors(obj, values, colormap, layer_name):
    mesh = obj.data
    if layer_name in mesh.vertex_colors:
        mesh.vertex_colors.remove(mesh.vertex_colors[layer_name])
    color_layer = mesh.vertex_colors.new(name=layer_name)
    for poly in mesh.polygons:
        for loop_idx, vert_idx in zip(poly.loop_indices, poly.vertices):
            val = float(np.clip(values[vert_idx], 0, 1)) if vert_idx < len(values) else 0.0
            color_layer.data[loop_idx].color = colormap(val)
    mesh.vertex_colors.active = color_layer


def coolwarm(t):
    t = np.clip(t, 0, 1)
    if t < 0.5:
        s = t * 2
        return (0.1 + s*0.3, 0.1 + s*0.3, 0.9 - s*0.4, 1.0)
    else:
        s = (t - 0.5) * 2
        return (0.4 + s*0.6, 0.4 - s*0.4, 0.5 - s*0.5, 1.0)


def error_color(t):
    t = np.clip(t, 0, 1)
    return (float(t), float(1.0-t), 0.0, 1.0)


# ─────────────────────────────────────────────
# PANEL
# ─────────────────────────────────────────────

class HST_BENCH_PT_PANEL(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HST_Benchmark'
    bl_label = 'HST ZoomOut Benchmark v1.0'

    def draw(self, context):
        layout = self.layout
        sc = context.scene

        col = layout.column(align=True)
        col.label(text="Objects")
        col.prop(sc, "hstb_source", text="Source (A)")
        col.prop(sc, "hstb_target", text="Target (B)")

        col.separator()
        col.label(text="ZoomOut Settings")
        col.prop(sc, "hstb_k_eigen")
        col.prop(sc, "hstb_k_init")
        col.prop(sc, "hstb_k_step")
        col.prop(sc, "hstb_k_final")

        col.separator()
        col.label(text="Vizualization")
        col.prop(sc, "hstb_show_notes")
        col.prop(sc, "hstb_show_errors")

        col.separator()
        col.operator("mesh.hstb_run_all", text="RUN BENCHMARK", icon='MOD_DATA_TRANSFER')
        col.operator("mesh.hstb_run_hst", text="Jen HST Note", icon='FORCE_MAGNETIC')
        col.operator("mesh.hstb_run_zoom", text="Jen ZoomOut", icon='MOD_SMOOTH')

        col.separator()
        col.prop(sc, "hstb_csv_path", text="CSV export")
        col.operator("mesh.hstb_export_csv", text="Export CSV", icon='EXPORT')

        col.separator()
        col.label(text="Results:")
        box = col.box()
        for line in sc.hstb_report.split('\n'):
            box.label(text=line)


# ─────────────────────────────────────────────
# OPERÁTORY
# ─────────────────────────────────────────────

class HST_BENCH_OT_RUN_ALL(bpy.types.Operator):
    bl_idname = "mesh.hstb_run_all"
    bl_label = "Run Full Benchmark"

    def execute(self, context):
        sc = context.scene
        objA = sc.hstb_source
        objB = sc.hstb_target

        if not objA or not objB:
            self.report({'ERROR'}, "Select Source and Target object.")
            return {'CANCELLED'}

        verts_a = get_vertices(objA)
        verts_b = get_vertices(objB)
        bb = bbox_diag(verts_b)

        # Eigenfunkce
        self.report({'INFO'}, "Počítám eigenfunkce...")
        La, Ma = get_laplacian_and_mass(objA)
        Lb, Mb = get_laplacian_and_mass(objB)

        t0 = time.time()
        k = sc.hstb_k_eigen
        evals_a, evecs_a = eigsh(La, k=k, M=Ma, sigma=0, which='LM', tol=1e-5, maxiter=8000)
        evals_b, evecs_b = eigsh(Lb, k=k, M=Mb, sigma=0, which='LM', tol=1e-5, maxiter=8000)
        idx_a = np.argsort(evals_a); evecs_a = evecs_a[:, idx_a]
        idx_b = np.argsort(evals_b); evecs_b = evecs_b[:, idx_b]
        t_eigen = time.time() - t0

        results = {}

        # TEST 1: HST Note
        t0 = time.time()
        note_a = norm01(evecs_a[:, 1])
        note_b = norm01(evecs_b[:, 1])
        T_hst = hst_map(note_a, note_b)
        t_hst = time.time() - t0
        geo_hst = geo_error_normalized(verts_b, T_hst, bb)
        results['hst'] = {'geo': geo_hst, 'time': t_hst, 'map': T_hst}

        # TEST 2: Náhodná → ZoomOut
        t0 = time.time()
        np.random.seed(42)
        T_rand = np.random.randint(0, len(verts_b), len(verts_a))
        T_zoom_rand = zoomout_refine(evecs_a, evecs_b, T_rand,
                                     sc.hstb_k_init, sc.hstb_k_step, sc.hstb_k_final)
        t_zoom_rand = time.time() - t0
        geo_zoom_rand = geo_error_normalized(verts_b, T_zoom_rand, bb)
        results['zoom_rand'] = {'geo': geo_zoom_rand, 'time': t_zoom_rand, 'map': T_zoom_rand}

        # TEST 3: HST → ZoomOut
        t0 = time.time()
        T_zoom_hst = zoomout_refine(evecs_a, evecs_b, T_hst,
                                    sc.hstb_k_init, sc.hstb_k_step, sc.hstb_k_final)
        t_zoom_hst = time.time() - t0
        geo_zoom_hst = geo_error_normalized(verts_b, T_zoom_hst, bb)
        results['zoom_hst'] = {'geo': geo_zoom_hst, 'time': t_hst + t_zoom_hst, 'map': T_zoom_hst}

        # Vizualizace
        if sc.hstb_show_notes:
            apply_vertex_colors(objA, note_a, coolwarm, "HST_Note_A")
            apply_vertex_colors(objB, note_b, coolwarm, "HST_Note_B")

        if sc.hstb_show_errors:
            err_vals = np.array([
                np.linalg.norm(verts_b[T_hst[i]] - verts_b[min(i, len(verts_b)-1)])
                for i in range(len(verts_a))
            ])
            err_norm = norm01(err_vals)
            apply_vertex_colors(objA, err_norm, error_color, "HST_Error")

        # Report
        imp = (geo_zoom_rand - geo_zoom_hst) / (geo_zoom_rand + 1e-10) * 100
        winner = "HST Note" if geo_hst < geo_zoom_rand and geo_hst < geo_zoom_hst else \
                 "HST+ZoomOut" if geo_zoom_hst < geo_zoom_rand else "Random+ZoomOut"

        report = (
            f"=== BENCHMARK REPORT ===\n"
            f"Vrcholy A/B: {len(verts_a)} / {len(verts_b)}\n"
            f"Eigenfunktion (k={k}): {t_eigen:.2f}s\n"
            f"------------------------\n"
            f"HST Note:      geo={geo_hst:.4f}  t={t_hst:.3f}s\n"
            f"Rand->ZoomOut: geo={geo_zoom_rand:.4f}  t={t_zoom_rand:.2f}s\n"
            f"HST->ZoomOut:  geo={geo_zoom_hst:.4f}  t={t_hst+t_zoom_hst:.2f}s\n"
            f"------------------------\n"
            f"Improvements init: {imp:.1f}%\n"
            f"Winner:         {winner}\n"
        )

        sc.hstb_report = report
        sc.hstb_last_results = repr(results)
        print(report)

        text = bpy.data.texts.get("HST_Benchmark.txt") or bpy.data.texts.new("HST_Benchmark.txt")
        text.clear()
        text.write(report)

        return {'FINISHED'}


class HST_BENCH_OT_RUN_HST(bpy.types.Operator):
    bl_idname = "mesh.hstb_run_hst"
    bl_label = "Run HST Note Only"

    def execute(self, context):
        sc = context.scene
        objA = sc.hstb_source
        objB = sc.hstb_target
        if not objA or not objB:
            self.report({'ERROR'}, "Vyber Source a Target.")
            return {'CANCELLED'}

        verts_b = get_vertices(objB)
        bb = bbox_diag(verts_b)
        La, Ma = get_laplacian_and_mass(objA)
        Lb, Mb = get_laplacian_and_mass(objB)

        t0 = time.time()
        _, evecs_a = eigsh(La, k=2, M=Ma, sigma=0, which='LM', tol=1e-5, maxiter=8000)
        _, evecs_b = eigsh(Lb, k=2, M=Mb, sigma=0, which='LM', tol=1e-5, maxiter=8000)
        note_a = norm01(evecs_a[:, 1])
        note_b = norm01(evecs_b[:, 1])
        T_hst = hst_map(note_a, note_b)
        t_total = time.time() - t0
        geo = geo_error_normalized(verts_b, T_hst, bb)

        if sc.hstb_show_notes:
            apply_vertex_colors(objA, note_a, coolwarm, "HST_Note_A")
            apply_vertex_colors(objB, note_b, coolwarm, "HST_Note_B")

        report = (
            f"=== HST NOTE ===\n"
            f"Geo error: {geo:.5f}\n"
            f"Cas: {t_total:.3f}s\n"
        )
        sc.hstb_report = report
        print(report)
        return {'FINISHED'}


class HST_BENCH_OT_RUN_ZOOM(bpy.types.Operator):
    bl_idname = "mesh.hstb_run_zoom"
    bl_label = "Run ZoomOut Only"

    def execute(self, context):
        sc = context.scene
        objA = sc.hstb_source
        objB = sc.hstb_target
        if not objA or not objB:
            self.report({'ERROR'}, "Vyber Source a Target.")
            return {'CANCELLED'}

        verts_a = get_vertices(objA)
        verts_b = get_vertices(objB)
        bb = bbox_diag(verts_b)
        La, Ma = get_laplacian_and_mass(objA)
        Lb, Mb = get_laplacian_and_mass(objB)

        t0 = time.time()
        k = sc.hstb_k_eigen
        _, evecs_a = eigsh(La, k=k, M=Ma, sigma=0, which='LM', tol=1e-5, maxiter=8000)
        _, evecs_b = eigsh(Lb, k=k, M=Mb, sigma=0, which='LM', tol=1e-5, maxiter=8000)
        np.random.seed(42)
        T_rand = np.random.randint(0, len(verts_b), len(verts_a))
        T_zoom = zoomout_refine(evecs_a, evecs_b, T_rand,
                                sc.hstb_k_init, sc.hstb_k_step, sc.hstb_k_final)
        t_total = time.time() - t0
        geo = geo_error_normalized(verts_b, T_zoom, bb)

        report = (
            f"=== ZOOMOUT (Random init) ===\n"
            f"Geo error: {geo:.5f}\n"
            f"Cas: {t_total:.2f}s\n"
        )
        sc.hstb_report = report
        print(report)
        return {'FINISHED'}


class HST_BENCH_OT_EXPORT_CSV(bpy.types.Operator):
    bl_idname = "mesh.hstb_export_csv"
    bl_label = "Export CSV"

    def execute(self, context):
        sc = context.scene
        csv_path = bpy.path.abspath(sc.hstb_csv_path)

        try:
            results = eval(sc.hstb_last_results)
        except Exception:
            self.report({'ERROR'}, "No results are available. Run the benchmark.")
            return {'CANCELLED'}

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['method', 'geo_error_norm', 'time_s'])
            for method, r in results.items():
                writer.writerow([method, f"{r['geo']:.6f}", f"{r['time']:.3f}"])

        self.report({'INFO'}, f"CSV uloženo: {csv_path}")
        return {'FINISHED'}


# ─────────────────────────────────────────────
# REGISTRACE
# ─────────────────────────────────────────────

classes = (
    HST_BENCH_PT_PANEL,
    HST_BENCH_OT_RUN_ALL,
    HST_BENCH_OT_RUN_HST,
    HST_BENCH_OT_RUN_ZOOM,
    HST_BENCH_OT_EXPORT_CSV,
)


def register():
    bpy.types.Scene.hstb_source = bpy.props.PointerProperty(
        name="Source", type=bpy.types.Object)
    bpy.types.Scene.hstb_target = bpy.props.PointerProperty(
        name="Target", type=bpy.types.Object)
    bpy.types.Scene.hstb_k_eigen = bpy.props.IntProperty(
        name="Eigenmódů celkem", default=50, min=10, max=100)
    bpy.types.Scene.hstb_k_init = bpy.props.IntProperty(
        name="ZoomOut k_init", default=10, min=5, max=30)
    bpy.types.Scene.hstb_k_step = bpy.props.IntProperty(
        name="ZoomOut k_step", default=5, min=1, max=10)
    bpy.types.Scene.hstb_k_final = bpy.props.IntProperty(
        name="ZoomOut k_final", default=40, min=20, max=100)
    bpy.types.Scene.hstb_show_notes = bpy.props.BoolProperty(
        name="Zobrazit harmonické nóty", default=True)
    bpy.types.Scene.hstb_show_errors = bpy.props.BoolProperty(
        name="Zobrazit chyby mapování", default=True)
    bpy.types.Scene.hstb_csv_path = bpy.props.StringProperty(
        name="CSV", default="//hst_benchmark.csv", subtype='FILE_PATH')
    bpy.types.Scene.hstb_report = bpy.props.StringProperty(
        name="Report", default="Spusť benchmark...")
    bpy.types.Scene.hstb_last_results = bpy.props.StringProperty(
        name="Results", default="{}")

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    props = ['hstb_source', 'hstb_target', 'hstb_k_eigen', 'hstb_k_init',
             'hstb_k_step', 'hstb_k_final', 'hstb_show_notes', 'hstb_show_errors',
             'hstb_csv_path', 'hstb_report', 'hstb_last_results']
    for p in props:
        if hasattr(bpy.types.Scene, p):
            delattr(bpy.types.Scene, p)


if __name__ == "__main__":
    register()
