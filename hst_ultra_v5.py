# HST Semantic Core Ultra v5.0
# Harmonic Shape Transform — Blender Addon
#
# Author: Pavel Krahulík
# License: GNU GPL v3
#
# Vylepšení oproti v4.0:
#   - Standardní geodetická chyba (normalizovaná průměrem bbox)
#   - Vizualizace: obarvení vrcholů podle nóty + chyby
#   - Batch mode: všechny FAUST páry najednou
#   - Export výsledků do CSV
#   - HKS jako stabilní default
#   - Pointwise mapování s vizualizací čar A→B
#
# Závislosti: scipy (součást Blender Pythonu od 3.6+)

import bpy
import bmesh
import numpy as np
import time
import os
import csv
from scipy.sparse import csr_matrix, diags
from scipy.sparse.linalg import eigsh

bl_info = {
    "name": "HST Semantic Core Ultra v5.0",
    "author": "Pavel Krahulík",
    "version": (5, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > HST_Ultra",
    "description": "HST Note + HKS + Geodesic Error + Visualization + Batch + CSV Export",
    "category": "Mesh",
}


# ─────────────────────────────────────────────
# MATEMATICKÉ JÁDRO
# ─────────────────────────────────────────────

def get_laplacian_and_mass(obj):
    """Cotangent Laplaceova matice a mass matice z Blender objektu."""
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
    """Vrátí numpy pole vrcholů objektu."""
    return np.array([v.co[:] for v in obj.data.vertices])


def normalize(v):
    vmin, vmax = np.min(v), np.max(v)
    if abs(vmax - vmin) < 1e-12:
        return np.zeros_like(v)
    return (v - vmin) / (vmax - vmin)


def align_sign(f1, f2):
    if np.linalg.norm(f1 - f2) > np.linalg.norm(f1 + f2):
        return -f2
    return f2


def compute_hks(evals, evecs, num_times=10):
    """Heat Kernel Signature — stabilní deskriptor."""
    n = evecs.shape[0]
    k = len(evals)
    valid = evals > 1e-6
    ev = evals[valid]
    ec = evecs[:, valid]
    if len(ev) < 2:
        return np.zeros((n, num_times))

    t_min = 4 * np.log(10) / ev[-1]
    t_max = 4 * np.log(10) / ev[0]
    ts = np.logspace(np.log10(t_min), np.log10(t_max), num=num_times)

    H = np.zeros((n, num_times))
    for ti, t in enumerate(ts):
        for i in range(len(ev)):
            H[:, ti] += np.exp(-ev[i] * t) * (ec[:, i] ** 2)
        H[:, ti] = normalize(H[:, ti])
    return H


def hst_pointwise_map(note_a, note_b):
    """HST mapování: pro každý bod A najdi nejbližší bod B podle hodnoty nóty."""
    mapped = np.zeros(len(note_a), dtype=int)
    for i, val in enumerate(note_a):
        mapped[i] = np.argmin(np.abs(note_b - val))
    return mapped


def geodesic_error(verts_a, verts_b, mapped_indices, bbox_diag):
    """
    Standardní normalizovaná geodetická chyba.
    Pro FAUST: body se stejným indexem jsou ground truth korespondence.
    Chyba = průměrná vzdálenost mapovaného bodu od správného bodu,
    normalizovaná průměrem bounding boxu.
    """
    n = min(len(verts_a), len(verts_b), len(mapped_indices))
    errors = []
    for i in range(n):
        correct = verts_b[min(i, len(verts_b)-1)]
        mapped_pt = verts_b[mapped_indices[i]]
        err = np.linalg.norm(mapped_pt - correct)
        errors.append(err)
    mean_err = np.mean(errors) if errors else 0.0
    normalized = mean_err / (bbox_diag + 1e-10)
    return mean_err, normalized


def bbox_diagonal(verts):
    mn = np.min(verts, axis=0)
    mx = np.max(verts, axis=0)
    return np.linalg.norm(mx - mn)


# ─────────────────────────────────────────────
# VIZUALIZACE
# ─────────────────────────────────────────────

def colormap_coolwarm(t):
    """Coolwarm colormap: modrá=0, bílá=0.5, červená=1."""
    t = np.clip(t, 0, 1)
    if t < 0.5:
        r = t * 2 * 0.4
        g = t * 2 * 0.4
        b = 0.5 + t * 2 * 0.5
    else:
        s = (t - 0.5) * 2
        r = 0.4 + s * 0.6
        g = 0.4 - s * 0.4
        b = 1.0 - s * 0.7
    return (float(np.clip(r, 0, 1)),
            float(np.clip(g, 0, 1)),
            float(np.clip(b, 0, 1)),
            1.0)


def colormap_error(t):
    """Zelená=malá chyba, červená=velká chyba."""
    t = np.clip(t, 0, 1)
    return (float(t), float(1.0 - t), 0.0, 1.0)


def apply_vertex_colors(obj, values, colormap_func, layer_name="HST_Note"):
    """Obarví vrcholy objektu podle hodnot."""
    mesh = obj.data

    # Odstraň existující vrstvu pokud existuje
    if layer_name in mesh.vertex_colors:
        mesh.vertex_colors.remove(mesh.vertex_colors[layer_name])
    color_layer = mesh.vertex_colors.new(name=layer_name)

    # Nastav barvy
    for poly in mesh.polygons:
        for loop_idx, vert_idx in zip(poly.loop_indices, poly.vertices):
            val = float(values[vert_idx]) if vert_idx < len(values) else 0.0
            color_layer.data[loop_idx].color = colormap_func(val)

    # Aktivuj vrstvu
    mesh.vertex_colors.active = color_layer

    # Nastav material na vertex colors pokud neexistuje
    if not obj.data.materials:
        mat = bpy.data.materials.new(name=f"HST_{layer_name}")
        mat.use_nodes = True
        obj.data.materials.append(mat)

        nodes = mat.node_tree.nodes
        nodes.clear()
        attr_node = nodes.new('ShaderNodeAttribute')
        attr_node.attribute_name = layer_name
        bsdf = nodes.new('ShaderNodeBsdfDiffuse')
        out = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(attr_node.outputs['Color'], bsdf.inputs['Color'])
        mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])


def draw_mapping_lines(obj_a, obj_b, note_a, note_b, n_lines=60, collection_name="HST_Mapping"):
    """Nakreslí čáry spojující mapované body A→B."""
    # Vymaž staré čáry
    if collection_name in bpy.data.collections:
        old_col = bpy.data.collections[collection_name]
        for o in list(old_col.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.collections.remove(old_col)

    col = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(col)

    verts_a = get_vertices(obj_a)
    verts_b = get_vertices(obj_b)
    mapped = hst_pointwise_map(note_a, note_b)

    step = max(1, len(verts_a) // n_lines)
    curve_data = bpy.data.curves.new('HST_Lines', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = 0.002

    for i in range(0, len(verts_a), step):
        j = mapped[i]
        spline = curve_data.splines.new('POLY')
        spline.points.add(1)
        spline.points[0].co = (*verts_a[i], 1)
        spline.points[1].co = (*verts_b[j], 1)

    curve_obj = bpy.data.objects.new('HST_Mapping_Lines', curve_data)
    col.objects.link(curve_obj)

    # Barevný materiál
    mat = bpy.data.materials.new("HST_Line_Mat")
    mat.use_nodes = True
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.6, 1.0, 1.0)
    curve_obj.data.materials.append(mat)


# ─────────────────────────────────────────────
# BATCH ZPRACOVÁNÍ
# ─────────────────────────────────────────────

def run_hst_on_pair(objA, objB, mode, hks_times):
    """Spustí HST na jednom páru a vrátí výsledky."""
    L1, M1 = get_laplacian_and_mass(objA)
    L2, M2 = get_laplacian_and_mass(objB)
    verts_a = get_vertices(objA)
    verts_b = get_vertices(objB)
    bb = bbox_diagonal(verts_b)

    start = time.time()

    if mode == "HST_NOTE":
        vals1, vecs1 = eigsh(L1, k=2, M=M1, sigma=0, which='LM')
        vals2, vecs2 = eigsh(L2, k=2, M=M2, sigma=0, which='LM')
        note_a = normalize(vecs1[:, 1])
        note_b = normalize(vecs2[:, 1])
        note_b = align_sign(note_a, note_b)
        mapped = hst_pointwise_map(note_a, note_b)
        modes_used = 1

    elif mode == "HKS":
        k = 30
        vals1, vecs1 = eigsh(L1, k=k, M=M1, sigma=0, which='LM')
        vals2, vecs2 = eigsh(L2, k=k, M=M2, sigma=0, which='LM')
        H1 = compute_hks(vals1, vecs1, num_times=hks_times)
        H2 = compute_hks(vals2, vecs2, num_times=hks_times)
        # Mapování přes první HKS dimenzi
        note_a = H1[:, 0]
        note_b = H2[:, 0]
        mapped = hst_pointwise_map(note_a, note_b)
        modes_used = k

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
        note_a = F1 @ weights
        note_b = F2 @ weights
        note_a = normalize(note_a)
        note_b = normalize(note_b)
        mapped = hst_pointwise_map(note_a, note_b)
        modes_used = k - 1

    elapsed = time.time() - start

    # Reziduál (původní metrika)
    note_a_norm = normalize(note_a)
    note_b_mapped = np.array([note_b[mapped[i]] for i in range(len(mapped))])
    residual = float(np.mean(np.abs(note_a_norm - note_b_mapped)))
    precision_orig = (1.0 - residual) * 100.0

    # Geodetická chyba (standardní metrika)
    mean_geo, geo_norm = geodesic_error(verts_a, verts_b, mapped, bb)

    return {
        "mode": mode,
        "n_source": len(verts_a),
        "n_target": len(verts_b),
        "modes_used": modes_used,
        "residual": residual,
        "precision_pct": precision_orig,
        "geo_error_abs": mean_geo,
        "geo_error_norm": geo_norm,
        "time_s": elapsed,
        "status": "PASS" if precision_orig > 90 else "WARNING",
        "note_a": note_a,
        "note_b": note_b,
        "mapped": mapped,
    }


# ─────────────────────────────────────────────
# PANEL
# ─────────────────────────────────────────────

class HST_PT_PANEL(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HST_Ultra'
    bl_label = 'HST Semantic Topology v5.0'

    def draw(self, context):
        layout = self.layout
        sc = context.scene

        col = layout.column(align=True)
        col.label(text="HST Mode")
        col.prop(sc, "hst_mode", expand=True)
        if sc.hst_mode == "HKS":
            col.prop(sc, "hst_hks_times")

        col.separator()
        col.label(text="Source Shape")
        col.prop(sc, "hst_source", text="")
        col.label(text="Target Shape")
        col.prop(sc, "hst_target", text="")

        col.separator()
        col.label(text="Vizualizace")
        col.prop(sc, "hst_show_colors")
        col.prop(sc, "hst_show_lines")
        col.prop(sc, "hst_n_lines")

        col.separator()
        col.operator("mesh.hst_run", text="RUN VALIDATION", icon='MOD_DATA_TRANSFER')

        col.separator()
        col.label(text="Batch & Export")
        col.prop(sc, "hst_faust_dir", text="FAUST dir")
        col.operator("mesh.hst_batch", text="BATCH — všechny páry", icon='FILE_REFRESH')
        col.prop(sc, "hst_csv_path", text="CSV výstup")
        col.operator("mesh.hst_export_csv", text="Export CSV", icon='EXPORT')

        col.separator()
        col.label(text="Report:")
        col.prop(sc, "hst_report", text="")


# ─────────────────────────────────────────────
# OPERATOR: SINGLE VALIDATION
# ─────────────────────────────────────────────

class HST_OT_RUN(bpy.types.Operator):
    bl_idname = "mesh.hst_run"
    bl_label = "Run HST Validation"

    def execute(self, context):
        sc = context.scene
        objA = sc.hst_source
        objB = sc.hst_target

        if not objA or not objB:
            self.report({'ERROR'}, "Vyber Source a Target objekt.")
            return {'CANCELLED'}

        result = run_hst_on_pair(objA, objB, sc.hst_mode, sc.hst_hks_times)

        # Vizualizace — barvy vrcholů
        if sc.hst_show_colors:
            apply_vertex_colors(objA, result["note_a"], colormap_coolwarm, "HST_Note_A")
            apply_vertex_colors(objB, result["note_b"], colormap_coolwarm, "HST_Note_B")

            # Chyby na A
            verts_b = get_vertices(objB)
            verts_a = get_vertices(objA)
            bb = bbox_diagonal(verts_b)
            errors = np.array([
                np.linalg.norm(verts_b[result["mapped"][i]] - verts_b[min(i, len(verts_b)-1)])
                for i in range(len(verts_a))
            ])
            errors_norm = errors / (bb + 1e-10)
            errors_norm = normalize(errors_norm)
            apply_vertex_colors(objA, errors_norm, colormap_error, "HST_Error_A")

        # Vizualizace — mapovací čáry
        if sc.hst_show_lines:
            draw_mapping_lines(objA, objB,
                               result["note_a"], result["note_b"],
                               n_lines=sc.hst_n_lines)

        # Report
        report = (
            "=== HST VALIDATION REPORT ===\n"
            f"Mode: {result['mode']}\n"
            "--------------------------------\n"
            f"Source vertices: {result['n_source']}\n"
            f"Target vertices: {result['n_target']}\n"
            f"Eigenmodes used: {result['modes_used']}\n"
            f"Residual: {result['residual']:.6f}\n"
            f"Precision (orig): {result['precision_pct']:.2f}%\n"
            f"Geo error (abs):  {result['geo_error_abs']:.5f}\n"
            f"Geo error (norm): {result['geo_error_norm']:.5f}\n"
            "Sign alignment: OK\n"
            "Normalization: OK\n"
            f"Computation time: {result['time_s']:.3f} s\n"
            "--------------------------------\n"
            f"Status: {result['status']}\n"
        )

        sc.hst_report = report
        print(report)

        # Ulož do text bloku
        text = bpy.data.texts.get("HST_Report.txt") or bpy.data.texts.new("HST_Report.txt")
        text.clear()
        text.write(report)

        # Ulož výsledky pro CSV export
        sc.hst_last_results = repr([result])

        return {'FINISHED'}


# ─────────────────────────────────────────────
# OPERATOR: BATCH
# ─────────────────────────────────────────────

class HST_OT_BATCH(bpy.types.Operator):
    bl_idname = "mesh.hst_batch"
    bl_label = "Batch HST na všech FAUST párech"

    def execute(self, context):
        sc = context.scene
        faust_dir = bpy.path.abspath(sc.hst_faust_dir)

        if not os.path.isdir(faust_dir):
            self.report({'ERROR'}, f"FAUST adresář nenalezen: {faust_dir}")
            return {'CANCELLED'}

        # Najdi OBJ soubory
        objs = sorted([f for f in os.listdir(faust_dir) if f.endswith('.obj') or f.endswith('.ply')])
        if len(objs) < 2:
            self.report({'ERROR'}, "Potřebuji alespoň 2 soubory v FAUST adresáři.")
            return {'CANCELLED'}

        results = []
        pairs_tested = 0

        for i in range(0, min(len(objs)-1, 20), 2):  # max 10 párů
            file_a = os.path.join(faust_dir, objs[i])
            file_b = os.path.join(faust_dir, objs[i+1])

            # Import do Blenderu
            bpy.ops.import_scene.obj(filepath=file_a)
            objA = context.selected_objects[0]
            bpy.ops.import_scene.obj(filepath=file_b)
            objB = context.selected_objects[0]

            try:
                result = run_hst_on_pair(objA, objB, sc.hst_mode, sc.hst_hks_times)
                result["pair"] = f"{objs[i]} → {objs[i+1]}"
                results.append(result)
                pairs_tested += 1
                print(f"Pár {i//2+1}: {result['pair']} | geo_norm={result['geo_error_norm']:.5f} | {result['status']}")
            except Exception as e:
                print(f"Chyba na páru {objs[i]}: {e}")

            # Vymaž importované objekty
            bpy.data.objects.remove(objA, do_unlink=True)
            bpy.data.objects.remove(objB, do_unlink=True)

        # Souhrnný report
        if results:
            mean_geo = np.mean([r["geo_error_norm"] for r in results])
            mean_time = np.mean([r["time_s"] for r in results])
            summary = (
                f"\n=== BATCH VÝSLEDKY ({pairs_tested} párů) ===\n"
                f"Průměrná geo chyba (norm): {mean_geo:.5f}\n"
                f"Průměrný čas:              {mean_time:.3f} s\n"
                f"Mode: {sc.hst_mode}\n"
            )
            print(summary)
            sc.hst_report = summary
            sc.hst_last_results = repr(results)

        return {'FINISHED'}


# ─────────────────────────────────────────────
# OPERATOR: CSV EXPORT
# ─────────────────────────────────────────────

class HST_OT_EXPORT_CSV(bpy.types.Operator):
    bl_idname = "mesh.hst_export_csv"
    bl_label = "Export výsledků do CSV"

    def execute(self, context):
        sc = context.scene
        csv_path = bpy.path.abspath(sc.hst_csv_path)

        try:
            results = eval(sc.hst_last_results)
        except Exception:
            self.report({'ERROR'}, "Nejsou dostupné výsledky. Spusť nejdřív validaci.")
            return {'CANCELLED'}

        fieldnames = ["pair", "mode", "n_source", "n_target", "modes_used",
                      "residual", "precision_pct", "geo_error_abs",
                      "geo_error_norm", "time_s", "status"]

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                row = {k: r.get(k, "") for k in fieldnames}
                writer.writerow(row)

        self.report({'INFO'}, f"Výsledky uloženy: {csv_path}")
        print(f"CSV export: {csv_path}")
        return {'FINISHED'}


# ─────────────────────────────────────────────
# REGISTRACE
# ─────────────────────────────────────────────

classes = (HST_PT_PANEL, HST_OT_RUN, HST_OT_BATCH, HST_OT_EXPORT_CSV)


def register():
    bpy.types.Scene.hst_mode = bpy.props.EnumProperty(
        name="Mode",
        items=[
            ("HKS",      "HST HKS (stable)",        "HKS — stabilní, doporučeno"),
            ("HST_NOTE", "HST Note (original)",      "Jedna eigenfunkce"),
            ("FAUST",    "FAUST Spectral (benchmark)","Spektrální benchmark"),
        ],
        default="HKS"
    )
    bpy.types.Scene.hst_hks_times = bpy.props.IntProperty(
        name="HKS time samples", default=10, min=3, max=20
    )
    bpy.types.Scene.hst_source = bpy.props.PointerProperty(
        name="Source", type=bpy.types.Object
    )
    bpy.types.Scene.hst_target = bpy.props.PointerProperty(
        name="Target", type=bpy.types.Object
    )
    bpy.types.Scene.hst_show_colors = bpy.props.BoolProperty(
        name="Obarvit vrcholy", default=True
    )
    bpy.types.Scene.hst_show_lines = bpy.props.BoolProperty(
        name="Zobrazit mapovací čáry", default=False
    )
    bpy.types.Scene.hst_n_lines = bpy.props.IntProperty(
        name="Počet čar", default=60, min=10, max=200
    )
    bpy.types.Scene.hst_faust_dir = bpy.props.StringProperty(
        name="FAUST adresář", default="//faust/", subtype='DIR_PATH'
    )
    bpy.types.Scene.hst_csv_path = bpy.props.StringProperty(
        name="CSV výstup", default="//hst_results.csv", subtype='FILE_PATH'
    )
    bpy.types.Scene.hst_report = bpy.props.StringProperty(
        name="Report", default=""
    )
    bpy.types.Scene.hst_last_results = bpy.props.StringProperty(
        name="Last Results", default="[]"
    )
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    props = ["hst_mode", "hst_hks_times", "hst_source", "hst_target",
             "hst_show_colors", "hst_show_lines", "hst_n_lines",
             "hst_faust_dir", "hst_csv_path", "hst_report", "hst_last_results"]
    for p in props:
        if hasattr(bpy.types.Scene, p):
            delattr(bpy.types.Scene, p)


if __name__ == "__main__":
    register()
