# HST Volumetric GPU v2.0
# Interior (tetrahedral Laplacian) + Exterior (SDF) harmonic notes
# GPU accelerated via CuPy (automatic CPU fallback)
#
# Author: Pavel Krahulík
# License: GPL-3.0
#
# GPU acceleration:
#   - SDF computation: fully parallelized on GPU
#   - Volumetric Laplacian eigenvectors: GPU eigh for dense matrices
#   - Surface eigenvectors: CPU ARPACK (faster for sparse k)
#
# Usage: View3D -> Sidebar -> HST_VolGPU

import bpy
import bmesh
import numpy as np
import os
import time
from scipy.sparse import csr_matrix, diags, lil_matrix
from scipy.sparse.linalg import eigsh


bl_info = {
    "name": "HST Volumetric GPU v2.0",
    "author": "Pavel Krahulík",
    "version": (2, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > HST_VolGPU",
    "description": "HST: surface + interior + exterior notes — CPU + GPU",
    "category": "Mesh",
}


# ─────────────────────────────────────────────
# GPU SETUP
# ─────────────────────────────────────────────

def _register_nvidia_dlls():
    try:
        import site
        for sp in site.getsitepackages():
            for sub in ['cublas', 'cusolver', 'cusparse',
                        'cuda_runtime', 'nvjitlink', 'cuda_nvrtc']:
                path = os.path.join(sp, 'nvidia', sub, 'bin')
                if os.path.isdir(path):
                    try:
                        os.add_dll_directory(path)
                    except Exception:
                        pass
    except Exception:
        pass

_register_nvidia_dlls()


def detect_gpu():
    try:
        _register_nvidia_dlls()
        import cupy as cp
        dev = cp.cuda.Device(0)
        mem = dev.mem_info
        cc = dev.compute_capability
        v = cp.cuda.runtime.runtimeGetVersion()
        info = (f"cuda | CUDA {v//1000}.{(v%1000)//10} "
                f"| CC {cc} | {mem[0]/1024**2:.0f}/{mem[1]/1024**2:.0f} MB")
        return 'cuda', info
    except Exception as e:
        return 'cpu', f'No GPU — {str(e)[:40]}'


# ─────────────────────────────────────────────
# SURFACE LAPLACIAN
# ─────────────────────────────────────────────

def get_surface_laplacian(obj):
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
                v_t = [vert for vert in face.verts
                       if vert not in (v, v_o)][0]
                v1 = v.co - v_t.co
                v2 = v_o.co - v_t.co
                cp_vec = v1.cross(v2)
                if cp_vec.length > 1e-12:
                    w += 0.5 * (v1.dot(v2) / cp_vec.length)
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


def get_vertices_faces(obj):
    verts = np.array([v.co[:] for v in obj.data.vertices])
    faces = np.array([[v for v in p.vertices] for p in obj.data.polygons
                      if len(p.vertices) == 3])
    return verts, faces


# ─────────────────────────────────────────────
# SDF — CPU + GPU
# ─────────────────────────────────────────────

def compute_sdf_grid_cpu(points, verts, faces):
    """CPU SDF computation — sequential."""
    sdf = np.zeros(len(points))
    for pi, p in enumerate(points):
        min_dist = np.inf
        sign = 1.0
        for face in faces:
            v0, v1, v2 = verts[face[0]], verts[face[1]], verts[face[2]]
            edge0 = v1 - v0
            edge1 = v2 - v0
            w = p - v0
            a = np.dot(edge0, edge0)
            b = np.dot(edge0, edge1)
            c = np.dot(edge1, edge1)
            d = np.dot(edge0, w)
            e = np.dot(edge1, w)
            det = a*c - b*b
            s = b*e - c*d
            t = b*d - a*e
            if s + t <= det:
                if s < 0:
                    if t < 0:
                        if d < 0: s = np.clip(-d/a, 0, 1); t = 0
                        else: s = 0; t = np.clip(-e/c, 0, 1)
                    else: s = 0; t = np.clip(-e/c, 0, 1)
                elif t < 0: s = np.clip(-d/a, 0, 1); t = 0
            else:
                inv_det = 1.0/det; s *= inv_det; t *= inv_det
            closest = v0 + s*edge0 + t*edge1
            dist = np.linalg.norm(p - closest)
            if dist < min_dist:
                min_dist = dist
                normal = np.cross(edge0, edge1)
                nl = np.linalg.norm(normal)
                if nl > 1e-10:
                    normal /= nl
                    sign = -1.0 if np.dot(normal, p - v0) < 0 else 1.0
        sdf[pi] = sign * min_dist
    return sdf


def compute_sdf_grid_gpu(points, verts, faces):
    """
    GPU SDF computation — fully vectorized.
    Computes distances from all points to all triangles in parallel.
    Massive speedup for large grids.
    """
    import cupy as cp
    _register_nvidia_dlls()

    pts_gpu = cp.array(points, dtype=cp.float32)      # (P, 3)
    v0_gpu  = cp.array(verts[faces[:, 0]], dtype=cp.float32)  # (F, 3)
    v1_gpu  = cp.array(verts[faces[:, 1]], dtype=cp.float32)
    v2_gpu  = cp.array(verts[faces[:, 2]], dtype=cp.float32)

    edge0 = v1_gpu - v0_gpu   # (F, 3)
    edge1 = v2_gpu - v0_gpu   # (F, 3)

    P = len(points)
    F = len(faces)
    batch = 500  # process points in batches to avoid OOM

    sdf = np.zeros(P)

    for start in range(0, P, batch):
        end = min(start + batch, P)
        p_batch = pts_gpu[start:end, cp.newaxis, :]  # (B, 1, 3)

        w = p_batch - v0_gpu[cp.newaxis, :, :]  # (B, F, 3)

        a = cp.sum(edge0 * edge0, axis=1)  # (F,)
        b = cp.sum(edge0 * edge1, axis=1)  # (F,)
        c = cp.sum(edge1 * edge1, axis=1)  # (F,)
        d = cp.sum(w * edge0[cp.newaxis], axis=2)  # (B, F)
        e = cp.sum(w * edge1[cp.newaxis], axis=2)  # (B, F)

        det = a * c - b * b  # (F,)

        s = b[cp.newaxis] * e - c[cp.newaxis] * d  # (B, F)
        t = b[cp.newaxis] * d - a[cp.newaxis] * e  # (B, F)

        # Clamp to triangle
        mask1 = (s + t) <= det[cp.newaxis]
        s_out = cp.where(mask1, s, cp.clip(s / (det[cp.newaxis] + 1e-10), 0, 1))
        t_out = cp.where(mask1, t, cp.clip(t / (det[cp.newaxis] + 1e-10), 0, 1))
        s_out = cp.clip(s_out, 0, 1)
        t_out = cp.clip(t_out, 0, 1)

        # Closest point
        closest = (v0_gpu[cp.newaxis] +
                   s_out[:, :, cp.newaxis] * edge0[cp.newaxis] +
                   t_out[:, :, cp.newaxis] * edge1[cp.newaxis])  # (B, F, 3)

        diff = p_batch - closest  # (B, F, 3)
        dists = cp.sqrt(cp.sum(diff**2, axis=2))  # (B, F)

        # Closest face per point
        closest_face = cp.argmin(dists, axis=1)  # (B,)
        min_dist = dists[cp.arange(end-start), closest_face]  # (B,)

        # Sign from normal
        normals = cp.cross(edge0, edge1)  # (F, 3)
        norms_len = cp.linalg.norm(normals, axis=1, keepdims=True)
        normals = normals / (norms_len + 1e-10)

        sel_normals = normals[closest_face]  # (B, 3)
        sel_v0 = v0_gpu[closest_face]        # (B, 3)
        dot = cp.sum(sel_normals * (pts_gpu[start:end] - sel_v0), axis=1)
        sign = cp.where(dot < 0, -1.0, 1.0)

        sdf[start:end] = cp.asnumpy(sign * min_dist)

    return sdf


def compute_sdf_grid(points, verts, faces, backend='cpu'):
    if backend == 'cuda':
        try:
            return compute_sdf_grid_gpu(points, verts, faces)
        except Exception as e:
            print(f"GPU SDF failed ({e}), using CPU")
    return compute_sdf_grid_cpu(points, verts, faces)


# ─────────────────────────────────────────────
# TETRAHEDRALIZATION
# ─────────────────────────────────────────────

def tetrahedralize_object(obj, resolution=8, backend='cpu'):
    from scipy.spatial import Delaunay
    import time

    verts_surface, faces_surface = get_vertices_faces(obj)
    mn = verts_surface.min(axis=0)
    mx = verts_surface.max(axis=0)
    pad = (mx - mn) * 0.05
    mn -= pad; mx += pad

    xs = np.linspace(mn[0], mx[0], resolution)
    ys = np.linspace(mn[1], mx[1], resolution)
    zs = np.linspace(mn[2], mx[2], resolution)
    grid = np.array([[x, y, z] for x in xs for y in ys for z in zs])
    print(f"  Grid points: {len(grid)}, faces: {len(faces_surface)}")

    t0 = time.time()
    sdf_vals = compute_sdf_grid(grid, verts_surface, faces_surface, backend)
    print(f"  SDF grid ({backend}): {time.time()-t0:.3f}s")

    interior = grid[sdf_vals < 0]

    if len(interior) < 10:
        raise ValueError(f"Too few interior points ({len(interior)}). "
                         "Try increasing resolution or check mesh is watertight.")

    all_verts = np.vstack([verts_surface, interior])

    t0 = time.time()
    tri = Delaunay(all_verts)
    print(f"  Delaunay: {time.time()-t0:.3f}s")

    return all_verts, tri.simplices, len(verts_surface)


# ─────────────────────────────────────────────
# VOLUMETRIC LAPLACIAN
# ─────────────────────────────────────────────

def build_volumetric_laplacian(verts, tets):
    """
    Fully vectorized volumetric Laplacian using scipy COO matrix.
    Fast even for 50k+ tetrahedra.
    """
    from scipy.sparse import coo_matrix

    n = len(verts)

    vi = verts[tets[:, 0]]
    vj = verts[tets[:, 1]]
    vk = verts[tets[:, 2]]
    vl = verts[tets[:, 3]]

    # Volume
    vol = np.abs(np.sum((vj - vi) * np.cross(vk - vi, vl - vi), axis=1)) / 6.0
    valid = vol > 1e-15

    # Mass matrix
    M_diag = np.zeros(n)
    for ci in range(4):
        np.add.at(M_diag, tets[:, ci], vol / 4.0)

    # Stiffness — all 6 edge pairs vectorized
    edge_pairs = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
    all_rows, all_cols, all_data = [], [], []

    for a, b in edge_pairs:
        na = tets[:, a]
        nb = tets[:, b]
        edge_len = np.linalg.norm(verts[na] - verts[nb], axis=1)
        w = np.where(valid, vol / (edge_len**2 + 1e-12), 0.0)

        # Off-diagonal
        all_rows.append(na);  all_cols.append(nb);  all_data.append(-w)
        all_rows.append(nb);  all_cols.append(na);  all_data.append(-w)
        # Diagonal
        all_rows.append(na);  all_cols.append(na);  all_data.append(w)
        all_rows.append(nb);  all_cols.append(nb);  all_data.append(w)

    rows = np.concatenate(all_rows)
    cols = np.concatenate(all_cols)
    data = np.concatenate(all_data)

    # COO → CSR (fast duplicate summation)
    L = coo_matrix((data, (rows, cols)), shape=(n, n)).tocsr()
    M = diags(np.maximum(M_diag, 1e-12))
    return L, M


# ─────────────────────────────────────────────
# EIGENFUNCTION COMPUTATION — CPU + GPU
# ─────────────────────────────────────────────

def compute_note_cpu(L, M, k=2, seed=42):
    """CPU sparse eigensolver — best for surface mesh (sparse k)."""
    n = L.shape[0]
    rng = np.random.RandomState(seed)
    v0 = rng.randn(n); v0 /= np.linalg.norm(v0)
    evals, evecs = eigsh(L, k=k+1, M=M, sigma=0.0, which='LM',
                         tol=1e-5, maxiter=5000, v0=v0)
    idx = np.argsort(evals)
    evec = evecs[:, idx[k]]
    vmin, vmax = evec.min(), evec.max()
    return (evec - vmin) / (vmax - vmin + 1e-12)


def compute_note_gpu(L, M, k=2, seed=42):
    """
    GPU dense eigensolver — best for volumetric mesh (dense, many nodes).
    Uses cp.linalg.eigh which is faster than ARPACK for large dense matrices.
    """
    import cupy as cp
    _register_nvidia_dlls()

    M_diag = cp.array(M.diagonal(), dtype=cp.float32)
    L_arr  = cp.array(L.toarray(), dtype=cp.float32)

    M_invsqrt = 1.0 / cp.sqrt(M_diag)
    L_sym = L_arr * M_invsqrt[:, None] * M_invsqrt[None, :]
    L_sym = (L_sym + L_sym.T) * 0.5

    evals_gpu, evecs_gpu = cp.linalg.eigh(L_sym)
    evecs_gpu = evecs_gpu * M_invsqrt[:, None]

    evec = cp.asnumpy(evecs_gpu[:, k]).astype(np.float64)
    vmin, vmax = evec.min(), evec.max()
    return (evec - vmin) / (vmax - vmin + 1e-12)


def compute_note(L, M, k=2, seed=42, backend='cpu', label=''):
    """Dispatch to CPU or GPU eigensolver."""
    n = L.shape[0]
    t0 = time.time()

    if backend == 'cuda':
        try:
            note = compute_note_gpu(L, M, k, seed)
            print(f"  {label} GPU eigh ({n} nodes): {time.time()-t0:.3f}s")
            return note
        except Exception as e:
            print(f"  {label} GPU failed ({e}), using CPU")

    note = compute_note_cpu(L, M, k, seed)
    print(f"  {label} CPU eigsh ({n} nodes): {time.time()-t0:.3f}s")
    return note


# ─────────────────────────────────────────────
# EXTERIOR SDF
# ─────────────────────────────────────────────

def compute_exterior_sdf(obj, n_exterior=500, seed=42, backend='cpu'):
    verts, faces = get_vertices_faces(obj)
    mn, mx = verts.min(axis=0), verts.max(axis=0)
    center = (mn + mx) / 2
    radius = np.linalg.norm(mx - mn) * 0.8

    rng = np.random.RandomState(seed)
    theta = rng.uniform(0, np.pi, n_exterior)
    phi   = rng.uniform(0, 2*np.pi, n_exterior)
    r     = rng.uniform(radius*0.5, radius*1.5, n_exterior)

    ext_pts = np.column_stack([
        center[0] + r * np.sin(theta) * np.cos(phi),
        center[1] + r * np.sin(theta) * np.sin(phi),
        center[2] + r * np.cos(theta),
    ])

    sdf_vals = compute_sdf_grid(ext_pts, verts, faces, backend)
    exterior_mask = sdf_vals > 0
    return ext_pts[exterior_mask], sdf_vals[exterior_mask]


# ─────────────────────────────────────────────
# VISUALIZATION
# ─────────────────────────────────────────────

def apply_vertex_colors(obj, values, layer_name="HST_Note"):
    """Fast vertex color assignment using numpy vectorization."""
    mesh = obj.data
    if layer_name in mesh.vertex_colors:
        mesh.vertex_colors.remove(mesh.vertex_colors[layer_name])
    color_layer = mesh.vertex_colors.new(name=layer_name)
    n_loops = len(mesh.loops)
    loop_verts = np.zeros(n_loops, dtype=np.int32)
    mesh.loops.foreach_get('vertex_index', loop_verts)
    vals = np.clip(values[loop_verts], 0, 1).astype(np.float32)
    colors = np.zeros((n_loops, 4), dtype=np.float32)
    colors[:, 3] = 1.0
    low = vals < 0.5
    s_low = vals[low] * 2
    colors[low, 0] = 0.1 + s_low * 0.3
    colors[low, 1] = 0.1 + s_low * 0.3
    colors[low, 2] = 0.9 - s_low * 0.4
    high = ~low
    s_high = (vals[high] - 0.5) * 2
    colors[high, 0] = 0.4 + s_high * 0.6
    colors[high, 1] = 0.4 - s_high * 0.4
    colors[high, 2] = 0.5 - s_high * 0.5
    color_layer.data.foreach_set('color', colors.ravel())
    mesh.vertex_colors.active = color_layer

def create_point_cloud(name, points, values):
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    mesh = bpy.data.meshes.new(name)
    obj  = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    mesh.from_pydata(points.tolist(), [], [])
    mesh.update()
    color_layer = mesh.vertex_colors.new(name="SDF")
    norm_vals = (values - values.min()) / (values.max() - values.min() + 1e-12)
    for i, val in enumerate(norm_vals):
        if i < len(color_layer.data):
            t = float(val)
            color_layer.data[i].color = (t, 1.0-t, 0.0, 1.0)
    return obj


# ─────────────────────────────────────────────
# PANEL
# ─────────────────────────────────────────────

class HST_VOLGPU_PT_PANEL(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HST_VolGPU'
    bl_label = 'HST Volumetric GPU v2.0'

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        col = layout.column(align=True)

        box = col.box()
        box.label(text=f"Backend: {sc.hstvg_backend}")
        col.operator("mesh.hstvg_detect", text="🔍 Detect GPU", icon='VIEWZOOM')
        col.prop(sc, "hstvg_force_cpu", text="Force CPU")

        col.separator()
        col.prop(sc, "hstvg_object", text="Object")

        col.separator()
        col.label(text="Compute")
        col.prop(sc, "hstvg_surface")
        col.prop(sc, "hstvg_interior")
        col.prop(sc, "hstvg_exterior")

        col.separator()
        col.label(text="Settings")
        col.prop(sc, "hstvg_tet_res")
        col.prop(sc, "hstvg_n_exterior")
        col.prop(sc, "hstvg_eigen_k")
        col.prop(sc, "hstvg_eigen_seed")

        col.separator()
        col.operator("mesh.hstvg_run",
                     text="▶ COMPUTE", icon='MOD_DATA_TRANSFER')

        col.separator()
        col.label(text="Results:")
        box = col.box()
        for line in sc.hstvg_report.split('\n'):
            if line.strip():
                box.label(text=line)


# ─────────────────────────────────────────────
# OPERATORS
# ─────────────────────────────────────────────

class HST_VOLGPU_OT_DETECT(bpy.types.Operator):
    bl_idname = "mesh.hstvg_detect"
    bl_label = "Detect GPU"

    def execute(self, context):
        backend, info = detect_gpu()
        context.scene.hstvg_backend = info if backend == 'cuda' else 'cpu — no GPU'
        self.report({'INFO'}, f"Backend: {backend}")
        return {'FINISHED'}


class HST_VOLGPU_OT_RUN(bpy.types.Operator):
    bl_idname = "mesh.hstvg_run"
    bl_label = "Compute Volumetric HST"

    def execute(self, context):
        sc = context.scene
        obj = sc.hstvg_object
        if not obj:
            self.report({'ERROR'}, "Select an object.")
            return {'CANCELLED'}

        backend = 'cpu'
        if not sc.hstvg_force_cpu and 'cuda' in sc.hstvg_backend:
            backend = 'cuda'

        report_lines = [f"=== HST VOLUMETRIC GPU v2.0 ===",
                        f"Backend: {backend.upper()}"]
        t_total = time.time()

        # ── Surface Note ──
        if sc.hstvg_surface:
            self.report({'INFO'}, "Computing surface note (CPU ARPACK)...")
            try:
                L, M = get_surface_laplacian(obj)
                note = compute_note(L, M, k=sc.hstvg_eigen_k,
                                    seed=sc.hstvg_eigen_seed,
                                    backend='cpu',  # always CPU for surface
                                    label='Surface')
                apply_vertex_colors(obj, note, "HST_Surface_Note")
                report_lines.append(
                    f"Surface note: {L.shape[0]} vertices → 'HST_Surface_Note'")
            except Exception as e:
                report_lines.append(f"Surface ERROR: {str(e)[:60]}")

        # ── Interior Note (tetrahedral) ──
        if sc.hstvg_interior:
            self.report({'INFO'}, f"Tetrahedralizing (res={sc.hstvg_tet_res})...")
            try:
                t0 = time.time()
                all_verts, tets, n_surface = tetrahedralize_object(
                    obj, resolution=sc.hstvg_tet_res, backend=backend)
                n_interior = len(all_verts) - n_surface
                t_tet = time.time() - t0
                report_lines.append(
                    f"Tetrahedralization: {n_surface} surf + "
                    f"{n_interior} interior = {len(tets)} tets  ({t_tet:.2f}s)")

                self.report({'INFO'}, "Building volumetric Laplacian...")
                t0 = time.time()
                L_vol, M_vol = build_volumetric_laplacian(all_verts, tets)
                t_lap = time.time() - t0
                n_vol = len(all_verts)

                # CPU ARPACK for volumetric (sparse k, faster than GPU eigh)
                note_vol = compute_note(L_vol, M_vol,
                                        k=sc.hstvg_eigen_k,
                                        seed=sc.hstvg_eigen_seed,
                                        backend='cpu',
                                        label='Volumetric')

                # Apply surface portion to mesh
                note_surf = note_vol[:n_surface]
                vmin, vmax = note_surf.min(), note_surf.max()
                note_surf_norm = (note_surf - vmin) / (vmax - vmin + 1e-12)
                apply_vertex_colors(obj, note_surf_norm, "HST_Interior_Note")
                report_lines.append(
                    f"Laplacian build: {t_lap:.3f}s  "
                    f"Interior note: {n_vol} nodes → 'HST_Interior_Note'")

            except Exception as e:
                report_lines.append(f"Interior ERROR: {str(e)[:80]}")

        # ── Exterior SDF ──
        if sc.hstvg_exterior:
            self.report({'INFO'}, f"Computing exterior SDF ({backend.upper()})...")
            try:
                t0 = time.time()
                ext_pts, sdf_vals = compute_exterior_sdf(
                    obj, n_exterior=sc.hstvg_n_exterior,
                    seed=sc.hstvg_eigen_seed, backend=backend)
                t_sdf = time.time() - t0
                create_point_cloud(
                    f"HST_Exterior_SDF_{obj.name}", ext_pts, sdf_vals)
                report_lines.append(
                    f"Exterior SDF: {len(ext_pts)} points  "
                    f"({t_sdf:.3f}s) → point cloud")
            except Exception as e:
                report_lines.append(f"Exterior ERROR: {str(e)[:80]}")

        t_elapsed = time.time() - t_total
        report_lines.append(f"{'─'*32}")
        report_lines.append(f"Total: {t_elapsed:.2f}s")

        report = '\n'.join(report_lines)
        sc.hstvg_report = report
        print(report)

        text = (bpy.data.texts.get("HST_Vol_GPU.txt") or
                bpy.data.texts.new("HST_Vol_GPU.txt"))
        text.clear(); text.write(report)

        return {'FINISHED'}


# ─────────────────────────────────────────────
# REGISTRATION
# ─────────────────────────────────────────────

classes = (HST_VOLGPU_PT_PANEL, HST_VOLGPU_OT_DETECT, HST_VOLGPU_OT_RUN)


def register():
    bpy.types.Scene.hstvg_backend = bpy.props.StringProperty(
        name="Backend", default="cpu — click Detect GPU")
    bpy.types.Scene.hstvg_force_cpu = bpy.props.BoolProperty(
        name="Force CPU", default=False)
    bpy.types.Scene.hstvg_object = bpy.props.PointerProperty(
        name="Object", type=bpy.types.Object)
    bpy.types.Scene.hstvg_surface = bpy.props.BoolProperty(
        name="Surface note (classic HST)", default=True)
    bpy.types.Scene.hstvg_interior = bpy.props.BoolProperty(
        name="Interior note (tetrahedral)", default=True)
    bpy.types.Scene.hstvg_exterior = bpy.props.BoolProperty(
        name="Exterior note (SDF)", default=True)
    bpy.types.Scene.hstvg_tet_res = bpy.props.IntProperty(
        name="Tet resolution", default=8, min=4, max=24,
        description="Grid density for tetrahedralization")
    bpy.types.Scene.hstvg_n_exterior = bpy.props.IntProperty(
        name="Exterior points", default=300, min=50, max=2000)
    bpy.types.Scene.hstvg_eigen_k = bpy.props.IntProperty(
        name="Eigenmode k", default=1, min=1, max=10)
    bpy.types.Scene.hstvg_eigen_seed = bpy.props.IntProperty(
        name="Seed", default=42, min=0, max=9999)
    bpy.types.Scene.hstvg_report = bpy.props.StringProperty(
        name="Report", default="Detect GPU, select object, click COMPUTE.")

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    props = ['hstvg_backend', 'hstvg_force_cpu', 'hstvg_object',
             'hstvg_surface', 'hstvg_interior', 'hstvg_exterior',
             'hstvg_tet_res', 'hstvg_n_exterior', 'hstvg_eigen_k',
             'hstvg_eigen_seed', 'hstvg_report']
    for p in props:
        if hasattr(bpy.types.Scene, p):
            delattr(bpy.types.Scene, p)


if __name__ == "__main__":
    register()
