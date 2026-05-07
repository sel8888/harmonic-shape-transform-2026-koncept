# HST Dual Note Benchmark v1.0
# Two-eigenfunction shape correspondence with symmetry disambiguation
#
# Key idea: instead of mapping via one normalized eigenfunction (HST Note),
# use TWO eigenfunctions simultaneously in 2D spectral space.
# φ₁ captures global structure (top/bottom), φ₂ breaks left/right symmetry.
#
# Author: Pavel Krahulík
# License: GPL-3.0
#
# Usage: View3D -> Sidebar -> HST_Dual
# Compares: HST Single Note vs HST Dual Note vs ZoomOut vs FMaps

import bpy
import bmesh
import numpy as np
import os
import sys
import time
import csv
import struct
import datetime
from scipy.sparse import csr_matrix, coo_matrix, diags
from scipy.sparse.linalg import eigsh

bl_info = {
    "name": "HST Dual Note Benchmark v1.0",
    "author": "Pavel Krahulík",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > HST_Dual",
    "description": "HST Single vs Dual Note — symmetry disambiguation benchmark",
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
        v = cp.cuda.runtime.runtimeGetVersion()
        return ('cuda',
                f"cuda | CUDA {v//1000}.{(v%1000)//10} | "
                f"{mem[0]/1024**2:.0f} MB free")
    except Exception as e:
        return 'cpu', f'cpu — {str(e)[:40]}'


# ─────────────────────────────────────────────
# PLY LOADER
# ─────────────────────────────────────────────

def load_ply(path):
    with open(path, 'rb') as f:
        header_lines = []
        while True:
            line = f.readline().decode('ascii', errors='ignore').strip()
            header_lines.append(line)
            if line == 'end_header':
                break

        fmt_line = next((l for l in header_lines if l.startswith('format')), '')
        is_binary_le = 'binary_little_endian' in fmt_line
        is_ascii = not is_binary_le and 'binary_big_endian' not in fmt_line

        n_verts = 0; n_faces = 0
        for l in header_lines:
            if l.startswith('element vertex'): n_verts = int(l.split()[-1])
            elif l.startswith('element face'): n_faces = int(l.split()[-1])

        vert_props = []
        in_vertex = False
        for l in header_lines:
            if l.startswith('element vertex'): in_vertex = True
            elif l.startswith('element') and 'vertex' not in l: in_vertex = False
            elif in_vertex and l.startswith('property'):
                parts = l.split()
                vert_props.append((parts[1], parts[2]))

        type_map = {
            'float': ('f4',4), 'float32': ('f4',4),
            'double': ('f8',8), 'float64': ('f8',8),
            'int': ('i4',4), 'uint': ('u4',4),
            'uchar': ('u1',1), 'char': ('i1',1),
        }

        if is_ascii:
            verts = np.array([list(map(float,
                f.readline().decode().split()))[:3]
                for _ in range(n_verts)], dtype=np.float64)
            faces = []
            for _ in range(n_faces):
                parts = list(map(int, f.readline().decode().split()))
                n = parts[0]; idx = parts[1:n+1]
                if n == 3: faces.append(idx)
                elif n == 4:
                    faces += [[idx[0],idx[1],idx[2]],[idx[0],idx[2],idx[3]]]
        else:
            endian = '<' if is_binary_le else '>'
            np_fields = [(pname, endian + type_map.get(ptype,('f4',4))[0])
                         for ptype, pname in vert_props]
            vert_dtype = np.dtype(np_fields)
            raw = f.read(n_verts * vert_dtype.itemsize)
            vs = np.frombuffer(raw, dtype=vert_dtype)
            verts = np.column_stack([vs['x'].astype(np.float64),
                                     vs['y'].astype(np.float64),
                                     vs['z'].astype(np.float64)])
            faces = []
            for _ in range(n_faces):
                n_raw = f.read(1)
                if not n_raw: break
                n = struct.unpack('B', n_raw)[0]
                idx = struct.unpack(endian + f'{n}i', f.read(n*4))
                if n == 3: faces.append(list(idx))
                elif n == 4:
                    faces += [[idx[0],idx[1],idx[2]],[idx[0],idx[2],idx[3]]]

    return verts, np.array(faces, dtype=np.int32)


# ─────────────────────────────────────────────
# LAPLACIAN
# ─────────────────────────────────────────────

def build_laplacian(verts, faces):
    n = len(verts)
    rows, cols, data = [], [], []
    mass = np.zeros(n)

    for tri in faces:
        i, j, k = tri
        vi, vj, vk = verts[i], verts[j], verts[k]
        area = 0.5 * np.linalg.norm(np.cross(vj-vi, vk-vi))
        if area < 1e-12: continue
        mass[i] += area/3; mass[j] += area/3; mass[k] += area/3

        def cot(a, b):
            return np.dot(a,b) / (np.linalg.norm(np.cross(a,b)) + 1e-12)

        ci = cot(vj-vi, vk-vi); cj = cot(vi-vj, vk-vj); ck = cot(vi-vk, vj-vk)
        for (a,b,w) in [(i,j,ck),(j,k,ci),(i,k,cj)]:
            wh = w*0.5
            rows+=[a,b,a,b]; cols+=[b,a,a,b]; data+=[-wh,-wh,wh,wh]

    L = csr_matrix((data,(rows,cols)), shape=(n,n))
    M = diags(np.maximum(mass, 1e-12))
    return L, M


def compute_eigenvectors(L, M, k, seed=42):
    n = L.shape[0]
    rng = np.random.RandomState(seed)
    v0 = rng.randn(n); v0 /= np.linalg.norm(v0)
    evals, evecs = eigsh(L, k=k, M=M, sigma=0.0, which='LM',
                         tol=1e-6, maxiter=10000, v0=v0)
    idx = np.argsort(evals)
    return evals[idx], evecs[:, idx]


# ─────────────────────────────────────────────
# CORE MATH
# ─────────────────────────────────────────────

def norm01(v):
    vmin, vmax = v.min(), v.max()
    return (v - vmin) / (vmax - vmin + 1e-12)


def bbox_diag(verts):
    return np.linalg.norm(verts.max(axis=0) - verts.min(axis=0))


def geo_error(verts_b, mapped, bb):
    errors = [np.linalg.norm(verts_b[mapped[i]] - verts_b[min(i,len(verts_b)-1)])
              for i in range(len(mapped))]
    return float(np.mean(errors)) / (bb + 1e-10)


# ─────────────────────────────────────────────
# HST SINGLE NOTE (classic)
# ─────────────────────────────────────────────

def select_best_single_note(evecs_a, evecs_b, k_cands=5, tol=0.001):
    """Original HST Note — 1D nearest neighbor in spectral space."""
    candidates = []
    for k in range(1, min(k_cands+1, evecs_a.shape[1])):
        na = norm01(evecs_a[:,k])
        if np.mean(na) < 0.5: na = 1.0 - na
        nb = norm01(evecs_b[:,k])
        best_res = np.inf; best_nb = nb
        for nb_c in [nb, 1.0-nb]:
            mapped = np.array([np.argmin(np.abs(nb_c - v)) for v in na])
            res = float(np.mean(np.abs(na - nb_c[mapped])))
            if res < best_res: best_res = res; best_nb = nb_c.copy()
        candidates.append((best_res, k, na.copy(), best_nb))
    candidates.sort(key=lambda x: (round(x[0]/tol), x[1]))
    return candidates[0][2], candidates[0][3], candidates[0][1]


def hst_map_single(note_a, note_b):
    """1D mapping: for each point in A find closest value in B."""
    return np.array([np.argmin(np.abs(note_b - v)) for v in note_a])


# ─────────────────────────────────────────────
# HST DUAL NOTE (new)
# ─────────────────────────────────────────────

def select_best_dual_note(evecs_a, evecs_b, k1=1, k2=2):
    """
    HST Dual Note — uses two eigenfunctions simultaneously.
    φ₁: global structure (top/bottom axis)
    φ₂: lateral structure (left/right symmetry breaking)

    Maps in 2D spectral space: (φ₁, φ₂) → 2D coordinate per vertex.
    Resolves the left/right symmetry ambiguity of single-note HST.
    """
    # Get both eigenfunctions
    na1 = norm01(evecs_a[:, k1])
    na2 = norm01(evecs_a[:, k2])
    nb1 = norm01(evecs_b[:, k1])
    nb2 = norm01(evecs_b[:, k2])

    # Sign alignment for each eigenfunction independently
    if np.mean(na1) < 0.5: na1 = 1.0 - na1
    if np.mean(na2) < 0.5: na2 = 1.0 - na2

    # Try all 4 sign combinations for target (both orientations of both notes)
    best_res = np.inf
    best_nb1, best_nb2 = nb1, nb2

    for s1 in [nb1, 1.0-nb1]:
        for s2 in [nb2, 1.0-nb2]:
            # Build 2D coordinates
            coords_a = np.column_stack([na1, na2])   # (n, 2)
            coords_b = np.column_stack([s1, s2])     # (n, 2)

            # Quick residual: mean distance after nearest-neighbor
            batch = 500
            total_res = 0.0
            n_a = len(na1)
            for start in range(0, n_a, batch):
                end = min(start+batch, n_a)
                diff = coords_a[start:end, np.newaxis, :] - coords_b[np.newaxis, :, :]
                dists = np.sum(diff**2, axis=2)
                nn = np.argmin(dists, axis=1)
                total_res += np.sum(np.linalg.norm(
                    coords_a[start:end] - coords_b[nn], axis=1))
            res = total_res / n_a

            if res < best_res:
                best_res = res
                best_nb1, best_nb2 = s1.copy(), s2.copy()

    return na1, na2, best_nb1, best_nb2, best_res


def hst_map_dual(na1, na2, nb1, nb2, backend='cpu'):
    """
    2D mapping: for each point in A find nearest point in B
    in the 2D space (φ₁, φ₂).

    This resolves left/right symmetry: points with same φ₁ but
    different φ₂ are now distinguishable.
    """
    coords_a = np.column_stack([na1, na2]).astype(np.float32)  # (n_a, 2)
    coords_b = np.column_stack([nb1, nb2]).astype(np.float32)  # (n_b, 2)

    if backend == 'cuda':
        try:
            import cupy as cp
            _register_nvidia_dlls()
            ca_gpu = cp.array(coords_a)
            cb_gpu = cp.array(coords_b)
            n_a = len(coords_a)
            mapped = np.zeros(n_a, dtype=int)
            batch = 1000
            for s in range(0, n_a, batch):
                e = min(s+batch, n_a)
                diff = ca_gpu[s:e, None, :] - cb_gpu[None, :, :]
                dists = cp.sum(diff**2, axis=2)
                mapped[s:e] = cp.asnumpy(cp.argmin(dists, axis=1))
            return mapped
        except Exception as e:
            print(f"GPU Dual Note failed ({e}), using CPU")

    # CPU
    n_a = len(coords_a)
    mapped = np.zeros(n_a, dtype=int)
    batch = 500
    for s in range(0, n_a, batch):
        e = min(s+batch, n_a)
        diff = coords_a[s:e, np.newaxis, :] - coords_b[np.newaxis, :, :]
        dists = np.sum(diff**2, axis=2)
        mapped[s:e] = np.argmin(dists, axis=1)
    return mapped


# ─────────────────────────────────────────────
# ZOOMOUT
# ─────────────────────────────────────────────

def zoomout_refine(evecs_a, evecs_b, T_init,
                   k_init=10, k_step=5, k_final=40, backend='cpu'):
    n_a = evecs_a.shape[0]
    T = T_init.copy(); k = k_init

    if backend == 'cuda':
        try:
            import cupy as cp
            _register_nvidia_dlls()
            evecs_b_gpu = cp.array(evecs_b, dtype=cp.float64)
            while k <= min(k_final, evecs_a.shape[1], evecs_b.shape[1]):
                Phi_a = evecs_a[:,:k]; Phi_b = evecs_b[:,:k]
                C = np.linalg.lstsq(Phi_b[T,:], Phi_a, rcond=None)[0].T
                mc = cp.array(Phi_a @ C.T, dtype=cp.float64)
                Pb = evecs_b_gpu[:,:k]
                new_T = np.zeros(n_a, dtype=int)
                for s in range(0, n_a, 500):
                    e = min(s+500, n_a)
                    diff = mc[s:e,None,:] - Pb[None,:,:]
                    new_T[s:e] = cp.asnumpy(cp.argmin(cp.sum(diff**2,axis=2),axis=1))
                T = new_T; k += k_step
            return T
        except Exception as e:
            print(f"GPU ZoomOut failed ({e}), using CPU")
            T = T_init.copy(); k = k_init

    while k <= min(k_final, evecs_a.shape[1], evecs_b.shape[1]):
        Phi_a = evecs_a[:,:k]; Phi_b = evecs_b[:,:k]
        C = np.linalg.lstsq(Phi_b[T,:], Phi_a, rcond=None)[0].T
        mc = Phi_a @ C.T
        new_T = np.zeros(n_a, dtype=int)
        for s in range(0, n_a, 200):
            e = min(s+200, n_a)
            d = np.sum((mc[s:e,None,:]-Phi_b[None,:,:])**2, axis=2)
            new_T[s:e] = np.argmin(d, axis=1)
        T = new_T; k += k_step
    return T


# ─────────────────────────────────────────────
# FUNCTIONAL MAPS
# ─────────────────────────────────────────────

def functional_maps(evecs_a, evecs_b, T_init, k=30, backend='cpu'):
    n_a = evecs_a.shape[0]
    Phi_a = evecs_a[:,:k]; Phi_b = evecs_b[:,:k]
    C = np.linalg.lstsq(Phi_b[T_init,:], Phi_a, rcond=None)[0].T
    mc = Phi_a @ C.T

    if backend == 'cuda':
        try:
            import cupy as cp
            _register_nvidia_dlls()
            mc_gpu = cp.array(mc, dtype=cp.float64)
            Pb_gpu = cp.array(Phi_b, dtype=cp.float64)
            new_T = np.zeros(n_a, dtype=int)
            for s in range(0, n_a, 500):
                e = min(s+500, n_a)
                diff = mc_gpu[s:e,None,:] - Pb_gpu[None,:,:]
                new_T[s:e] = cp.asnumpy(cp.argmin(cp.sum(diff**2,axis=2),axis=1))
            return new_T
        except Exception as e:
            print(f"GPU FMaps failed ({e}), using CPU")

    new_T = np.zeros(n_a, dtype=int)
    for s in range(0, n_a, 200):
        e = min(s+200, n_a)
        d = np.sum((mc[s:e,None,:]-Phi_b[None,:,:])**2, axis=2)
        new_T[s:e] = np.argmin(d, axis=1)
    return new_T


# ─────────────────────────────────────────────
# VISUALIZATION
# ─────────────────────────────────────────────

def apply_vertex_colors(obj, values, layer_name):
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


def apply_dual_colors(obj, na1, na2, layer_name):
    """Visualize dual note as 2D colormap: φ₁→red, φ₂→green."""
    mesh = obj.data
    if layer_name in mesh.vertex_colors:
        mesh.vertex_colors.remove(mesh.vertex_colors[layer_name])
    color_layer = mesh.vertex_colors.new(name=layer_name)
    n_loops = len(mesh.loops)
    loop_verts = np.zeros(n_loops, dtype=np.int32)
    mesh.loops.foreach_get('vertex_index', loop_verts)
    r = np.clip(na1[loop_verts], 0, 1).astype(np.float32)
    g = np.clip(na2[loop_verts], 0, 1).astype(np.float32)
    colors = np.column_stack([r, g, np.zeros(n_loops, np.float32),
                              np.ones(n_loops, np.float32)])
    color_layer.data.foreach_set('color', colors.ravel())
    mesh.vertex_colors.active = color_layer


# ─────────────────────────────────────────────
# FULL PAIR BENCHMARK
# ─────────────────────────────────────────────

def run_pair(verts_a, faces_a, verts_b, faces_b, sc, backend='cpu'):
    bb = bbox_diag(verts_b)
    rng = np.random.RandomState(sc.hstd_rand_seed)
    T_rand = rng.randint(0, len(verts_b), len(verts_a))

    # Eigenvectors
    La, Ma = build_laplacian(verts_a, faces_a)
    Lb, Mb = build_laplacian(verts_b, faces_b)
    evals_a, evecs_a = compute_eigenvectors(La, Ma, sc.hstd_k_eigen,
                                             sc.hstd_eigen_seed)
    evals_b, evecs_b = compute_eigenvectors(Lb, Mb, sc.hstd_k_eigen,
                                             sc.hstd_eigen_seed)

    # ── HST Single Note ──
    t0 = time.time()
    na1, nb1, note_k = select_best_single_note(
        evecs_a, evecs_b, sc.hstd_k_note_cands)
    T_single = hst_map_single(na1, nb1)
    t_single = time.time() - t0
    geo_single = geo_error(verts_b, T_single, bb)

    # ── HST Dual Note ──
    t0 = time.time()
    k1 = note_k
    k2 = note_k + 1 if note_k + 1 < evecs_a.shape[1] else note_k - 1
    k2 = max(1, k2)
    dna1, dna2, dnb1, dnb2, dual_res = select_best_dual_note(
        evecs_a, evecs_b, k1=k1, k2=k2)
    T_dual = hst_map_dual(dna1, dna2, dnb1, dnb2, backend=backend)
    t_dual = time.time() - t0
    geo_dual = geo_error(verts_b, T_dual, bb)

    result = {
        'note_k': note_k,
        'k1': k1, 'k2': k2,
        'geo_single': geo_single, 't_single': t_single,
        'geo_dual': geo_dual, 't_dual': t_dual,
        'dual_res': dual_res,
        'na1': na1, 'dna1': dna1, 'dna2': dna2,
        'T_single': T_single, 'T_dual': T_dual,
        'evecs_a': evecs_a, 'evecs_b': evecs_b,
    }

    # ── ZoomOut variants ──
    if sc.hstd_run_zoomout:
        # Random → ZoomOut
        t0 = time.time()
        T_zo_rand = zoomout_refine(evecs_a, evecs_b, T_rand,
                                    sc.hstd_k_init, sc.hstd_k_step,
                                    sc.hstd_k_final, backend)
        result['t_zo_rand'] = time.time() - t0
        result['geo_zo_rand'] = geo_error(verts_b, T_zo_rand, bb)

        # Single HST → ZoomOut
        t0 = time.time()
        T_zo_single = zoomout_refine(evecs_a, evecs_b, T_single,
                                      sc.hstd_k_init, sc.hstd_k_step,
                                      sc.hstd_k_final, backend)
        result['t_zo_single'] = t_single + (time.time() - t0)
        result['geo_zo_single'] = geo_error(verts_b, T_zo_single, bb)
        result['imp_zo_single'] = ((result['geo_zo_rand'] - result['geo_zo_single']) /
                                    (result['geo_zo_rand'] + 1e-10) * 100)

        # Dual HST → ZoomOut
        t0 = time.time()
        T_zo_dual = zoomout_refine(evecs_a, evecs_b, T_dual,
                                    sc.hstd_k_init, sc.hstd_k_step,
                                    sc.hstd_k_final, backend)
        result['t_zo_dual'] = t_dual + (time.time() - t0)
        result['geo_zo_dual'] = geo_error(verts_b, T_zo_dual, bb)
        result['imp_zo_dual'] = ((result['geo_zo_rand'] - result['geo_zo_dual']) /
                                  (result['geo_zo_rand'] + 1e-10) * 100)

    # ── Functional Maps variants ──
    if sc.hstd_run_fmaps:
        k_fm = min(sc.hstd_k_fmaps, sc.hstd_k_eigen)

        t0 = time.time()
        T_fm_rand = functional_maps(evecs_a, evecs_b, T_rand, k_fm, backend)
        result['t_fm_rand'] = time.time() - t0
        result['geo_fm_rand'] = geo_error(verts_b, T_fm_rand, bb)

        t0 = time.time()
        T_fm_single = functional_maps(evecs_a, evecs_b, T_single, k_fm, backend)
        result['t_fm_single'] = t_single + (time.time() - t0)
        result['geo_fm_single'] = geo_error(verts_b, T_fm_single, bb)
        result['imp_fm_single'] = ((result['geo_fm_rand'] - result['geo_fm_single']) /
                                    (result['geo_fm_rand'] + 1e-10) * 100)

        t0 = time.time()
        T_fm_dual = functional_maps(evecs_a, evecs_b, T_dual, k_fm, backend)
        result['t_fm_dual'] = t_dual + (time.time() - t0)
        result['geo_fm_dual'] = geo_error(verts_b, T_fm_dual, bb)
        result['imp_fm_dual'] = ((result['geo_fm_rand'] - result['geo_fm_dual']) /
                                  (result['geo_fm_rand'] + 1e-10) * 100)

    return result


# ─────────────────────────────────────────────
# PANEL
# ─────────────────────────────────────────────

class HST_DUAL_PT_PANEL(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HST_Dual'
    bl_label = 'HST Dual Note v1.0'

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        col = layout.column(align=True)

        box = col.box()
        box.label(text=f"Backend: {sc.hstd_backend}")
        col.operator("mesh.hstd_detect", text="🔍 Detect GPU", icon='VIEWZOOM')
        col.prop(sc, "hstd_force_cpu", text="Force CPU")

        col.separator()
        col.label(text="Quick Test (single pair)")
        col.prop(sc, "hstd_source", text="Source (A)")
        col.prop(sc, "hstd_target", text="Target (B)")
        col.operator("mesh.hstd_run_single",
                     text="▶ Test Single Pair", icon='FORCE_MAGNETIC')

        col.separator()
        col.label(text="Full FAUST Benchmark")
        col.prop(sc, "hstd_faust_dir", text="")
        col.prop(sc, "hstd_pair_start")
        col.prop(sc, "hstd_pair_end")
        col.prop(sc, "hstd_pair_step")

        col.separator()
        col.label(text="Settings")
        col.prop(sc, "hstd_k_eigen")
        col.prop(sc, "hstd_eigen_seed")
        col.prop(sc, "hstd_k_note_cands")
        col.prop(sc, "hstd_rand_seed")

        col.separator()
        col.label(text="Methods")
        col.prop(sc, "hstd_run_zoomout")
        if sc.hstd_run_zoomout:
            col.prop(sc, "hstd_k_init")
            col.prop(sc, "hstd_k_step")
            col.prop(sc, "hstd_k_final")
        col.prop(sc, "hstd_run_fmaps")
        if sc.hstd_run_fmaps:
            col.prop(sc, "hstd_k_fmaps")

        col.separator()
        col.prop(sc, "hstd_csv_path", text="CSV")
        col.operator("mesh.hstd_run_all",
                     text="▶ RUN FULL BENCHMARK", icon='MOD_DATA_TRANSFER')
        col.operator("mesh.hstd_stop", text="■ STOP", icon='X')

        col.separator()
        col.label(text="Results:")
        box = col.box()
        for line in sc.hstd_report.split('\n'):
            if line.strip():
                box.label(text=line)


# ─────────────────────────────────────────────
# OPERATORS
# ─────────────────────────────────────────────

_STOP_REQUESTED = False


class HST_DUAL_OT_DETECT(bpy.types.Operator):
    bl_idname = "mesh.hstd_detect"
    bl_label = "Detect GPU"

    def execute(self, context):
        backend, info = detect_gpu()
        context.scene.hstd_backend = info
        self.report({'INFO'}, f"Backend: {backend}")
        return {'FINISHED'}


class HST_DUAL_OT_STOP(bpy.types.Operator):
    bl_idname = "mesh.hstd_stop"
    bl_label = "Stop"

    def execute(self, context):
        global _STOP_REQUESTED
        _STOP_REQUESTED = True
        self.report({'INFO'}, "Stop requested.")
        return {'FINISHED'}


class HST_DUAL_OT_RUN_SINGLE(bpy.types.Operator):
    bl_idname = "mesh.hstd_run_single"
    bl_label = "Test Single Pair"

    def execute(self, context):
        sc = context.scene
        objA, objB = sc.hstd_source, sc.hstd_target
        if not objA or not objB:
            self.report({'ERROR'}, "Select Source and Target.")
            return {'CANCELLED'}

        backend = 'cpu'
        if not sc.hstd_force_cpu and 'cuda' in sc.hstd_backend:
            backend = 'cuda'

        verts_a = np.array([v.co[:] for v in objA.data.vertices])
        verts_b = np.array([v.co[:] for v in objB.data.vertices])
        faces_a = np.array([[v for v in p.vertices] for p in objA.data.polygons
                            if len(p.vertices)==3])
        faces_b = np.array([[v for v in p.vertices] for p in objB.data.polygons
                            if len(p.vertices)==3])

        self.report({'INFO'}, "Computing...")
        r = run_pair(verts_a, faces_a, verts_b, faces_b, sc, backend)

        # Visualize
        apply_vertex_colors(objA, r['na1'], "HST_Single_A")
        apply_dual_colors(objA, r['dna1'], r['dna2'], "HST_Dual_A")

        imp_dual = ((r['geo_single'] - r['geo_dual']) /
                    (r['geo_single'] + 1e-10) * 100) if r['geo_single'] > 0 else 0

        report = (
            f"=== HST DUAL NOTE TEST ===\n"
            f"Eigenmodes: k1={r['k1']} k2={r['k2']}\n"
            f"{'─'*30}\n"
            f"HST Single:  geo={r['geo_single']:.5f}  t={r['t_single']:.3f}s\n"
            f"HST Dual:    geo={r['geo_dual']:.5f}  t={r['t_dual']:.3f}s\n"
            f"Dual improvement: {imp_dual:.1f}%\n"
        )

        if 'geo_zo_rand' in r:
            report += (
                f"{'─'*30}\n"
                f"ZoomOut rand:   geo={r['geo_zo_rand']:.5f}\n"
                f"ZoomOut single: geo={r['geo_zo_single']:.5f}  imp={r['imp_zo_single']:.1f}%\n"
                f"ZoomOut dual:   geo={r['geo_zo_dual']:.5f}  imp={r['imp_zo_dual']:.1f}%\n"
            )

        if 'geo_fm_rand' in r:
            report += (
                f"FMaps rand:     geo={r['geo_fm_rand']:.5f}\n"
                f"FMaps single:   geo={r['geo_fm_single']:.5f}  imp={r['imp_fm_single']:.1f}%\n"
                f"FMaps dual:     geo={r['geo_fm_dual']:.5f}  imp={r['imp_fm_dual']:.1f}%\n"
            )

        sc.hstd_report = report
        print(report)
        return {'FINISHED'}


class HST_DUAL_OT_RUN_ALL(bpy.types.Operator):
    bl_idname = "mesh.hstd_run_all"
    bl_label = "Run Full Dual Benchmark"

    def execute(self, context):
        global _STOP_REQUESTED
        _STOP_REQUESTED = False

        sc = context.scene
        faust_dir = bpy.path.abspath(sc.hstd_faust_dir)
        csv_path  = bpy.path.abspath(sc.hstd_csv_path)

        if not os.path.isdir(faust_dir):
            self.report({'ERROR'}, f"Directory not found: {faust_dir}")
            return {'CANCELLED'}

        backend = 'cpu'
        if not sc.hstd_force_cpu and 'cuda' in sc.hstd_backend:
            backend = 'cuda'

        ply_files = sorted([f for f in os.listdir(faust_dir)
                            if f.endswith('.ply') and 'tr_reg' in f.lower()])
        if not ply_files:
            ply_files = sorted([f for f in os.listdir(faust_dir)
                                if f.endswith('.ply')])

        pairs = [(ply_files[i], ply_files[i+1])
                 for i in range(sc.hstd_pair_start,
                                min(sc.hstd_pair_end, len(ply_files)-1),
                                sc.hstd_pair_step)
                 if i+1 < len(ply_files)]

        if not pairs:
            self.report({'ERROR'}, "No pairs found.")
            return {'CANCELLED'}

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        fields = ['pair_idx', 'source', 'target', 'n_verts',
                  'k1', 'k2', 'dual_res',
                  'geo_single', 't_single',
                  'geo_dual', 't_dual', 'imp_dual']
        if sc.hstd_run_zoomout:
            fields += ['geo_zo_rand', 't_zo_rand',
                       'geo_zo_single', 't_zo_single', 'imp_zo_single',
                       'geo_zo_dual', 't_zo_dual', 'imp_zo_dual']
        if sc.hstd_run_fmaps:
            fields += ['geo_fm_rand', 't_fm_rand',
                       'geo_fm_single', 't_fm_single', 'imp_fm_single',
                       'geo_fm_dual', 't_fm_dual', 'imp_fm_dual']
        fields += ['backend', 'status']

        all_results = []
        t_total = time.time()

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()

            for pair_idx, (file_a, file_b) in enumerate(pairs):
                if _STOP_REQUESTED:
                    sc.hstd_report += "\n⚠ Stopped."
                    break

                sc.hstd_report = (f"Pair {pair_idx+1}/{len(pairs)}: "
                                   f"{file_a} → {file_b}")
                print(sc.hstd_report)

                try:
                    verts_a, faces_a = load_ply(os.path.join(faust_dir, file_a))
                    verts_b, faces_b = load_ply(os.path.join(faust_dir, file_b))

                    r = run_pair(verts_a, faces_a, verts_b, faces_b, sc, backend)

                    imp_dual = ((r['geo_single'] - r['geo_dual']) /
                                (r['geo_single'] + 1e-10) * 100)

                    row = {
                        'pair_idx': pair_idx,
                        'source': file_a, 'target': file_b,
                        'n_verts': len(verts_a),
                        'k1': r['k1'], 'k2': r['k2'],
                        'dual_res': f"{r['dual_res']:.6f}",
                        'geo_single': f"{r['geo_single']:.6f}",
                        't_single': f"{r['t_single']:.3f}",
                        'geo_dual': f"{r['geo_dual']:.6f}",
                        't_dual': f"{r['t_dual']:.3f}",
                        'imp_dual': f"{imp_dual:.2f}",
                        'backend': backend,
                        'status': 'OK',
                    }

                    line = (f"  ✓ single={r['geo_single']:.4f}"
                            f"  dual={r['geo_dual']:.4f}"
                            f"  imp_dual={imp_dual:.1f}%")

                    for key in ['geo_zo_rand', 't_zo_rand',
                                'geo_zo_single', 't_zo_single', 'imp_zo_single',
                                'geo_zo_dual', 't_zo_dual', 'imp_zo_dual',
                                'geo_fm_rand', 't_fm_rand',
                                'geo_fm_single', 't_fm_single', 'imp_fm_single',
                                'geo_fm_dual', 't_fm_dual', 'imp_fm_dual']:
                        if key in r and key in fields:
                            row[key] = f"{r[key]:.4f}"
                            if 'imp' in key:
                                line += f"  {key}={r[key]:.1f}%"

                    writer.writerow(row)
                    csvfile.flush()
                    all_results.append({**r, 'imp_dual': imp_dual})
                    print(line)

                except Exception as e:
                    err = str(e)[:80]
                    print(f"  ✗ ERROR: {err}")
                    row = {f: 'N/A' for f in fields}
                    row.update({'pair_idx': pair_idx, 'source': file_a,
                                'target': file_b, 'backend': backend,
                                'status': f'ERROR: {err}'})
                    writer.writerow(row)
                    csvfile.flush()

        # Summary
        elapsed = time.time() - t_total
        ok = all_results
        lines = [f"=== DUAL NOTE BENCHMARK: {len(ok)}/{len(pairs)} pairs ===",
                 f"Time: {elapsed/60:.1f} min  Backend: {backend}"]

        if ok:
            g_single = [r['geo_single'] for r in ok]
            g_dual   = [r['geo_dual'] for r in ok]
            imp_d    = [r['imp_dual'] for r in ok]
            lines += [
                f"HST Single: mean={np.mean(g_single):.4f}",
                f"HST Dual:   mean={np.mean(g_dual):.4f}",
                f"Dual improvement over Single: {np.mean(imp_d):.1f}%",
                f"Dual better: {np.sum(np.array(g_dual) < np.array(g_single))}/99",
            ]

            if sc.hstd_run_zoomout and 'geo_zo_rand' in ok[0]:
                g_zr = [r['geo_zo_rand'] for r in ok]
                g_zs = [r['geo_zo_single'] for r in ok]
                g_zd = [r['geo_zo_dual'] for r in ok]
                lines += [
                    f"ZoomOut rand:   {np.mean(g_zr):.4f}",
                    f"ZoomOut single: {np.mean(g_zs):.4f}",
                    f"ZoomOut dual:   {np.mean(g_zd):.4f}",
                ]

            if sc.hstd_run_fmaps and 'geo_fm_rand' in ok[0]:
                g_fr = [r['geo_fm_rand'] for r in ok]
                g_fs = [r['geo_fm_single'] for r in ok]
                g_fd = [r['geo_fm_dual'] for r in ok]
                lines += [
                    f"FMaps rand:   {np.mean(g_fr):.4f}",
                    f"FMaps single: {np.mean(g_fs):.4f}",
                    f"FMaps dual:   {np.mean(g_fd):.4f}",
                ]

        summary = '\n'.join(lines)
        sc.hstd_report = summary
        print(summary)

        text = (bpy.data.texts.get("HST_Dual_Results.txt") or
                bpy.data.texts.new("HST_Dual_Results.txt"))
        text.clear(); text.write(summary)
        return {'FINISHED'}


# ─────────────────────────────────────────────
# REGISTRATION
# ─────────────────────────────────────────────

classes = (HST_DUAL_PT_PANEL, HST_DUAL_OT_DETECT, HST_DUAL_OT_STOP,
           HST_DUAL_OT_RUN_SINGLE, HST_DUAL_OT_RUN_ALL)


def register():
    bpy.types.Scene.hstd_backend = bpy.props.StringProperty(
        name="Backend", default="cpu — click Detect GPU")
    bpy.types.Scene.hstd_force_cpu = bpy.props.BoolProperty(
        name="Force CPU", default=False)
    bpy.types.Scene.hstd_source = bpy.props.PointerProperty(
        name="Source", type=bpy.types.Object)
    bpy.types.Scene.hstd_target = bpy.props.PointerProperty(
        name="Target", type=bpy.types.Object)
    bpy.types.Scene.hstd_faust_dir = bpy.props.StringProperty(
        name="FAUST Directory", default="//faust/", subtype='DIR_PATH')
    bpy.types.Scene.hstd_pair_start = bpy.props.IntProperty(
        name="First pair", default=0, min=0, max=99)
    bpy.types.Scene.hstd_pair_end = bpy.props.IntProperty(
        name="Last pair", default=99, min=1, max=199)
    bpy.types.Scene.hstd_pair_step = bpy.props.IntProperty(
        name="Step", default=1, min=1, max=10)
    bpy.types.Scene.hstd_k_eigen = bpy.props.IntProperty(
        name="Eigenmodes (k)", default=50, min=10, max=100)
    bpy.types.Scene.hstd_eigen_seed = bpy.props.IntProperty(
        name="Eigen seed", default=42, min=0, max=9999)
    bpy.types.Scene.hstd_k_note_cands = bpy.props.IntProperty(
        name="Note candidates", default=5, min=1, max=10)
    bpy.types.Scene.hstd_rand_seed = bpy.props.IntProperty(
        name="Random seed", default=42, min=0, max=9999)
    bpy.types.Scene.hstd_run_zoomout = bpy.props.BoolProperty(
        name="Test ZoomOut", default=True)
    bpy.types.Scene.hstd_k_init = bpy.props.IntProperty(
        name="ZoomOut k_init", default=10, min=5, max=30)
    bpy.types.Scene.hstd_k_step = bpy.props.IntProperty(
        name="ZoomOut k_step", default=5, min=1, max=10)
    bpy.types.Scene.hstd_k_final = bpy.props.IntProperty(
        name="ZoomOut k_final", default=40, min=20, max=100)
    bpy.types.Scene.hstd_run_fmaps = bpy.props.BoolProperty(
        name="Test Functional Maps", default=True)
    bpy.types.Scene.hstd_k_fmaps = bpy.props.IntProperty(
        name="FMaps k", default=30, min=10, max=100)
    bpy.types.Scene.hstd_csv_path = bpy.props.StringProperty(
        name="CSV output", default="//hst_dual_benchmark.csv",
        subtype='FILE_PATH')
    bpy.types.Scene.hstd_report = bpy.props.StringProperty(
        name="Report", default="Detect GPU and click RUN.")

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    props = ['hstd_backend', 'hstd_force_cpu', 'hstd_source', 'hstd_target',
             'hstd_faust_dir', 'hstd_pair_start', 'hstd_pair_end',
             'hstd_pair_step', 'hstd_k_eigen', 'hstd_eigen_seed',
             'hstd_k_note_cands', 'hstd_rand_seed', 'hstd_run_zoomout',
             'hstd_k_init', 'hstd_k_step', 'hstd_k_final',
             'hstd_run_fmaps', 'hstd_k_fmaps', 'hstd_csv_path', 'hstd_report']
    for p in props:
        if hasattr(bpy.types.Scene, p):
            delattr(bpy.types.Scene, p)


if __name__ == "__main__":
    register()
