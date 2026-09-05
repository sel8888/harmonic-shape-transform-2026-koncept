# HST Volumetric Full FAUST Benchmark v1.0
# Tests Surface + Interior + Exterior HST notes as initializers
# for ZoomOut and Functional Maps on all FAUST pairs
#
# Author: Pavel Krahulík
# License: GPL-3.0
#
# Usage: View3D -> Sidebar -> HST_VolBench
# Set FAUST directory, click RUN FULL BENCHMARK
# Results saved to CSV automatically

import bpy
import bmesh
import numpy as np
import os
import sys
import time
import csv
import struct
import datetime
from scipy.sparse import csr_matrix, coo_matrix, diags, lil_matrix
from scipy.sparse.linalg import eigsh
from scipy.spatial import Delaunay

bl_info = {
    "name": "HST Volumetric FAUST Benchmark v1.0",
    "author": "Pavel Krahulík",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > HST_VolBench",
    "description": "Full FAUST benchmark: Surface + Interior + Exterior HST vs ZoomOut vs FMaps",
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
        cp.cuda.Device(0).compute_capability
        return 'cuda'
    except Exception:
        return 'cpu'


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
            'float': ('f4', 4), 'float32': ('f4', 4),
            'double': ('f8', 8), 'float64': ('f8', 8),
            'int': ('i4', 4), 'uint': ('u4', 4),
            'uchar': ('u1', 1), 'char': ('i1', 1),
        }

        if is_ascii:
            vert_data = []
            for _ in range(n_verts):
                row = list(map(float, f.readline().decode().split()))
                vert_data.append(row[:3])
            verts = np.array(vert_data, dtype=np.float64)
            faces = []
            for _ in range(n_faces):
                parts = list(map(int, f.readline().decode().split()))
                n = parts[0]; idx = parts[1:n+1]
                if n == 3: faces.append(idx)
                elif n == 4:
                    faces.append([idx[0],idx[1],idx[2]])
                    faces.append([idx[0],idx[2],idx[3]])
        else:
            endian = '<' if is_binary_le else '>'
            np_fields = []
            for ptype, pname in vert_props:
                dt, _ = type_map.get(ptype, ('f4', 4))
                np_fields.append((pname, endian + dt))
            vert_dtype = np.dtype(np_fields)
            raw = f.read(n_verts * vert_dtype.itemsize)
            vert_struct = np.frombuffer(raw, dtype=vert_dtype)
            verts = np.column_stack([
                vert_struct['x'].astype(np.float64),
                vert_struct['y'].astype(np.float64),
                vert_struct['z'].astype(np.float64),
            ])
            faces = []
            for _ in range(n_faces):
                n_raw = f.read(1)
                if not n_raw: break
                n = struct.unpack('B', n_raw)[0]
                idx = struct.unpack(endian + f'{n}i', f.read(n * 4))
                if n == 3: faces.append(list(idx))
                elif n == 4:
                    faces.append([idx[0],idx[1],idx[2]])
                    faces.append([idx[0],idx[2],idx[3]])

    return verts, np.array(faces, dtype=np.int32)


# ─────────────────────────────────────────────
# SURFACE LAPLACIAN
# ─────────────────────────────────────────────

def build_surface_laplacian(verts, faces):
    n = len(verts)
    rows, cols, data = [], [], []
    mass = np.zeros(n)

    for tri in faces:
        i, j, k = tri
        vi, vj, vk = verts[i], verts[j], verts[k]
        area = 0.5 * np.linalg.norm(np.cross(vj - vi, vk - vi))
        if area < 1e-12: continue
        mass[i] += area/3.0; mass[j] += area/3.0; mass[k] += area/3.0

        def cot(a, b):
            c = np.dot(a, b); s = np.linalg.norm(np.cross(a, b))
            return c / (s + 1e-12)

        ci = cot(vj-vi, vk-vi); cj = cot(vi-vj, vk-vj); ck = cot(vi-vk, vj-vk)
        for (a, b, w) in [(i,j,ck),(j,k,ci),(i,k,cj)]:
            wh = w * 0.5
            rows += [a,b,a,b]; cols += [b,a,a,b]; data += [-wh,-wh,wh,wh]

    L = csr_matrix((data, (rows, cols)), shape=(n, n))
    M = diags(np.maximum(mass, 1e-12))
    return L, M


# ─────────────────────────────────────────────
# SDF
# ─────────────────────────────────────────────

def compute_sdf_cpu(points, verts, faces):
    sdf = np.zeros(len(points))
    for pi, p in enumerate(points):
        min_dist = np.inf; sign = 1.0
        for face in faces:
            v0, v1, v2 = verts[face[0]], verts[face[1]], verts[face[2]]
            e0 = v1-v0; e1 = v2-v0; w = p-v0
            a = np.dot(e0,e0); b = np.dot(e0,e1); c = np.dot(e1,e1)
            d = np.dot(e0,w); e = np.dot(e1,w); det = a*c-b*b
            s = b*e-c*d; t = b*d-a*e
            if s+t <= det:
                if s < 0:
                    if t < 0:
                        if d < 0: s=np.clip(-d/a,0,1); t=0
                        else: s=0; t=np.clip(-e/c,0,1)
                    else: s=0; t=np.clip(-e/c,0,1)
                elif t < 0: s=np.clip(-d/a,0,1); t=0
            else:
                inv = 1.0/det; s*=inv; t*=inv
            closest = v0+s*e0+t*e1
            dist = np.linalg.norm(p-closest)
            if dist < min_dist:
                min_dist = dist
                normal = np.cross(e0, e1); nl = np.linalg.norm(normal)
                if nl > 1e-10:
                    normal /= nl
                    sign = -1.0 if np.dot(normal, p-v0) < 0 else 1.0
        sdf[pi] = sign * min_dist
    return sdf


def compute_sdf_gpu(points, verts, faces):
    import cupy as cp
    _register_nvidia_dlls()
    pts_gpu = cp.array(points, dtype=cp.float32)
    v0_gpu  = cp.array(verts[faces[:,0]], dtype=cp.float32)
    v1_gpu  = cp.array(verts[faces[:,1]], dtype=cp.float32)
    v2_gpu  = cp.array(verts[faces[:,2]], dtype=cp.float32)
    e0 = v1_gpu - v0_gpu; e1 = v2_gpu - v0_gpu
    P = len(points); sdf = np.zeros(P); batch = 500

    for start in range(0, P, batch):
        end = min(start+batch, P)
        p_b = pts_gpu[start:end, cp.newaxis, :]
        w = p_b - v0_gpu[cp.newaxis]
        a = cp.sum(e0*e0, axis=1); b = cp.sum(e0*e1, axis=1)
        c = cp.sum(e1*e1, axis=1)
        d = cp.sum(w*e0[cp.newaxis], axis=2)
        e = cp.sum(w*e1[cp.newaxis], axis=2)
        det = a*c - b*b
        s = b[cp.newaxis]*e - c[cp.newaxis]*d
        t = b[cp.newaxis]*d - a[cp.newaxis]*e
        mask1 = (s+t) <= det[cp.newaxis]
        s_out = cp.where(mask1, s, cp.clip(s/(det[cp.newaxis]+1e-10),0,1))
        t_out = cp.where(mask1, t, cp.clip(t/(det[cp.newaxis]+1e-10),0,1))
        s_out = cp.clip(s_out,0,1); t_out = cp.clip(t_out,0,1)
        closest = (v0_gpu[cp.newaxis] +
                   s_out[:,:,cp.newaxis]*e0[cp.newaxis] +
                   t_out[:,:,cp.newaxis]*e1[cp.newaxis])
        diff = p_b - closest
        dists = cp.sqrt(cp.sum(diff**2, axis=2))
        cf = cp.argmin(dists, axis=1)
        min_dist = dists[cp.arange(end-start), cf]
        normals = cp.cross(e0, e1)
        normals = normals / (cp.linalg.norm(normals,axis=1,keepdims=True)+1e-10)
        sel_n = normals[cf]; sel_v0 = v0_gpu[cf]
        dot = cp.sum(sel_n*(pts_gpu[start:end]-sel_v0), axis=1)
        sign = cp.where(dot < 0, -1.0, 1.0)
        sdf[start:end] = cp.asnumpy(sign * min_dist)
    return sdf


def compute_sdf(points, verts, faces, backend='cpu'):
    if backend == 'cuda':
        try: return compute_sdf_gpu(points, verts, faces)
        except Exception as e: print(f"GPU SDF failed ({e}), using CPU")
    return compute_sdf_cpu(points, verts, faces)


# ─────────────────────────────────────────────
# TETRAHEDRALIZATION
# ─────────────────────────────────────────────

def tetrahedralize(verts, faces, resolution=8, backend='cpu'):
    mn = verts.min(axis=0); mx = verts.max(axis=0)
    pad = (mx-mn)*0.05; mn -= pad; mx += pad
    xs = np.linspace(mn[0],mx[0],resolution)
    ys = np.linspace(mn[1],mx[1],resolution)
    zs = np.linspace(mn[2],mx[2],resolution)
    grid = np.array([[x,y,z] for x in xs for y in ys for z in zs])
    sdf_vals = compute_sdf(grid, verts, faces, backend)
    interior = grid[sdf_vals < 0]
    if len(interior) < 5:
        return None, None, 0
    all_verts = np.vstack([verts, interior])
    tri = Delaunay(all_verts)
    return all_verts, tri.simplices, len(verts)


# ─────────────────────────────────────────────
# VOLUMETRIC LAPLACIAN
# ─────────────────────────────────────────────

def build_volumetric_laplacian(verts, tets):
    n = len(verts)
    vi = verts[tets[:,0]]; vj = verts[tets[:,1]]
    vk = verts[tets[:,2]]; vl = verts[tets[:,3]]
    vol = np.abs(np.sum((vj-vi)*np.cross(vk-vi,vl-vi),axis=1))/6.0
    valid = vol > 1e-15
    M_diag = np.zeros(n)
    for ci in range(4): np.add.at(M_diag, tets[:,ci], vol/4.0)
    edge_pairs = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
    all_rows, all_cols, all_data = [], [], []
    for a, b in edge_pairs:
        na = tets[:,a]; nb = tets[:,b]
        el = np.linalg.norm(verts[na]-verts[nb],axis=1)
        w = np.where(valid, vol/(el**2+1e-12), 0.0)
        all_rows += [na,nb,na,nb]; all_cols += [nb,na,na,nb]
        all_data += [-w,-w,w,w]
    rows = np.concatenate(all_rows); cols = np.concatenate(all_cols)
    data = np.concatenate(all_data)
    L = coo_matrix((data,(rows,cols)),shape=(n,n)).tocsr()
    return L, diags(np.maximum(M_diag,1e-12))


# ─────────────────────────────────────────────
# EIGENVECTORS
# ─────────────────────────────────────────────

def compute_eigenvectors(L, M, k, seed=42):
    n = L.shape[0]
    rng = np.random.RandomState(seed)
    v0 = rng.randn(n); v0 /= np.linalg.norm(v0)
    evals, evecs = eigsh(L, k=k, M=M, sigma=0.0, which='LM',
                         tol=1e-6, maxiter=10000, v0=v0)
    idx = np.argsort(evals)
    return evals[idx], evecs[:, idx]


def norm01(v):
    vmin, vmax = v.min(), v.max()
    return (v - vmin) / (vmax - vmin + 1e-12)


def bbox_diag(verts):
    return np.linalg.norm(verts.max(axis=0) - verts.min(axis=0))


def geo_error(verts_b, mapped, bb):
    errors = [np.linalg.norm(verts_b[mapped[i]] - verts_b[min(i,len(verts_b)-1)])
              for i in range(len(mapped))]
    return float(np.mean(errors)) / (bb + 1e-10)


def select_best_note(evecs_a, evecs_b, k_cands=5, tol=0.001):
    candidates = []
    for k in range(1, min(k_cands+1, evecs_a.shape[1])):
        na = norm01(evecs_a[:,k])
        if np.mean(na) < 0.5: na = 1.0 - na
        nb = norm01(evecs_b[:,k])
        best_res = np.inf; best_nb = nb
        for nb_c in [nb, 1.0-nb]:
            mapped = np.array([np.argmin(np.abs(nb_c-v)) for v in na])
            res = float(np.mean(np.abs(na - nb_c[mapped])))
            if res < best_res: best_res = res; best_nb = nb_c.copy()
        candidates.append((best_res, k, na.copy(), best_nb))
    candidates.sort(key=lambda x: (round(x[0]/tol), x[1]))
    return candidates[0][2], candidates[0][3], candidates[0][1], candidates[0][0]


def hst_map(note_a, note_b):
    return np.array([np.argmin(np.abs(note_b-v)) for v in note_a])


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
            print(f"GPU ZoomOut failed ({e}), using CPU"); T = T_init.copy(); k = k_init

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
# FULL PAIR BENCHMARK
# ─────────────────────────────────────────────

def run_pair(verts_a, faces_a, verts_b, faces_b, sc, backend='cpu'):
    bb = bbox_diag(verts_b)
    rng = np.random.RandomState(sc.hstvb_rand_seed)
    T_rand = rng.randint(0, len(verts_b), len(verts_a))

    # ── Surface eigenvectors ──
    La, Ma = build_surface_laplacian(verts_a, faces_a)
    Lb, Mb = build_surface_laplacian(verts_b, faces_b)
    evals_a, evecs_a = compute_eigenvectors(La, Ma, sc.hstvb_k_eigen,
                                             sc.hstvb_eigen_seed)
    evals_b, evecs_b = compute_eigenvectors(Lb, Mb, sc.hstvb_k_eigen,
                                             sc.hstvb_eigen_seed)

    # ── Surface HST Note ──
    t0 = time.time()
    note_a, note_b, note_k, note_res = select_best_note(
        evecs_a, evecs_b, sc.hstvb_k_note_cands)
    T_hst_surf = hst_map(note_a, note_b)
    t_hst = time.time() - t0
    geo_hst_surf = geo_error(verts_b, T_hst_surf, bb)

    result = {
        'note_k': note_k,
        'geo_hst_surf': geo_hst_surf,
        't_hst_surf': t_hst,
    }

    # ── Interior HST Note ──
    if sc.hstvb_use_interior:
        try:
            t0 = time.time()
            all_va, tets_a, n_sa = tetrahedralize(
                verts_a, faces_a, sc.hstvb_tet_res, backend)
            all_vb, tets_b, n_sb = tetrahedralize(
                verts_b, faces_b, sc.hstvb_tet_res, backend)

            if all_va is not None and all_vb is not None:
                Lva, Mva = build_volumetric_laplacian(all_va, tets_a)
                Lvb, Mvb = build_volumetric_laplacian(all_vb, tets_b)
                evals_va, evecs_va = compute_eigenvectors(
                    Lva, Mva, sc.hstvb_k_eigen, sc.hstvb_eigen_seed)
                evals_vb, evecs_vb = compute_eigenvectors(
                    Lvb, Mvb, sc.hstvb_k_eigen, sc.hstvb_eigen_seed)

                note_va, note_vb, note_vk, _ = select_best_note(
                    evecs_va, evecs_vb, sc.hstvb_k_note_cands)
                T_hst_vol = hst_map(note_va[:n_sa], note_vb[:n_sb])
                t_vol = time.time() - t0
                result['geo_hst_vol'] = geo_error(verts_b, T_hst_vol, bb)
                result['t_hst_vol'] = t_vol
                result['T_hst_vol'] = T_hst_vol
            else:
                result['geo_hst_vol'] = float('nan')
                result['t_hst_vol'] = float('nan')
                result['T_hst_vol'] = T_hst_surf
        except Exception as e:
            print(f"Interior note failed: {e}")
            result['geo_hst_vol'] = float('nan')
            result['t_hst_vol'] = float('nan')
            result['T_hst_vol'] = T_hst_surf
    else:
        result['T_hst_vol'] = T_hst_surf

    # ── ZoomOut variants ──
    if sc.hstvb_run_zoomout:
        # Random → ZoomOut
        t0 = time.time()
        T_zo_rand = zoomout_refine(evecs_a, evecs_b, T_rand,
                                    sc.hstvb_k_init, sc.hstvb_k_step,
                                    sc.hstvb_k_final, backend)
        result['t_zo_rand'] = time.time() - t0
        result['geo_zo_rand'] = geo_error(verts_b, T_zo_rand, bb)

        # Surface HST → ZoomOut
        t0 = time.time()
        T_zo_surf = zoomout_refine(evecs_a, evecs_b, T_hst_surf,
                                    sc.hstvb_k_init, sc.hstvb_k_step,
                                    sc.hstvb_k_final, backend)
        result['t_zo_surf'] = t_hst + (time.time() - t0)
        result['geo_zo_surf'] = geo_error(verts_b, T_zo_surf, bb)
        result['imp_zo_surf'] = ((result['geo_zo_rand'] - result['geo_zo_surf']) /
                                  (result['geo_zo_rand'] + 1e-10) * 100)

        # Interior HST → ZoomOut (if available)
        if sc.hstvb_use_interior and not np.isnan(result.get('geo_hst_vol', float('nan'))):
            t0 = time.time()
            T_zo_vol = zoomout_refine(evecs_a, evecs_b, result['T_hst_vol'],
                                       sc.hstvb_k_init, sc.hstvb_k_step,
                                       sc.hstvb_k_final, backend)
            result['t_zo_vol'] = result['t_hst_vol'] + (time.time() - t0)
            result['geo_zo_vol'] = geo_error(verts_b, T_zo_vol, bb)
            result['imp_zo_vol'] = ((result['geo_zo_rand'] - result['geo_zo_vol']) /
                                     (result['geo_zo_rand'] + 1e-10) * 100)

    # ── Functional Maps variants ──
    if sc.hstvb_run_fmaps:
        k_fm = min(sc.hstvb_k_fmaps, sc.hstvb_k_eigen)

        # Random → FMaps
        t0 = time.time()
        T_fm_rand = functional_maps(evecs_a, evecs_b, T_rand, k_fm, backend)
        result['t_fm_rand'] = time.time() - t0
        result['geo_fm_rand'] = geo_error(verts_b, T_fm_rand, bb)

        # Surface HST → FMaps
        t0 = time.time()
        T_fm_surf = functional_maps(evecs_a, evecs_b, T_hst_surf, k_fm, backend)
        result['t_fm_surf'] = t_hst + (time.time() - t0)
        result['geo_fm_surf'] = geo_error(verts_b, T_fm_surf, bb)
        result['imp_fm_surf'] = ((result['geo_fm_rand'] - result['geo_fm_surf']) /
                                  (result['geo_fm_rand'] + 1e-10) * 100)

    return result


# ─────────────────────────────────────────────
# PANEL
# ─────────────────────────────────────────────

class HST_VOLBENCH_PT_PANEL(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'HST_VolBench'
    bl_label = 'HST Volumetric FAUST Benchmark v1.0'

    def draw(self, context):
        layout = self.layout
        sc = context.scene
        col = layout.column(align=True)

        box = col.box()
        box.label(text=f"Backend: {sc.hstvb_backend}")
        col.operator("mesh.hstvb_detect", text="🔍 Detect GPU", icon='VIEWZOOM')
        col.prop(sc, "hstvb_force_cpu", text="Force CPU")

        col.separator()
        col.label(text="FAUST Directory")
        col.prop(sc, "hstvb_faust_dir", text="")
        col.prop(sc, "hstvb_pair_start")
        col.prop(sc, "hstvb_pair_end")
        col.prop(sc, "hstvb_pair_step")

        col.separator()
        col.label(text="HST Settings")
        col.prop(sc, "hstvb_k_eigen")
        col.prop(sc, "hstvb_eigen_seed")
        col.prop(sc, "hstvb_k_note_cands")
        col.prop(sc, "hstvb_rand_seed")

        col.separator()
        col.label(text="Volumetric")
        col.prop(sc, "hstvb_use_interior")
        if sc.hstvb_use_interior:
            col.prop(sc, "hstvb_tet_res")

        col.separator()
        col.label(text="Methods")
        col.prop(sc, "hstvb_run_zoomout")
        if sc.hstvb_run_zoomout:
            col.prop(sc, "hstvb_k_init")
            col.prop(sc, "hstvb_k_step")
            col.prop(sc, "hstvb_k_final")
        col.prop(sc, "hstvb_run_fmaps")
        if sc.hstvb_run_fmaps:
            col.prop(sc, "hstvb_k_fmaps")

        col.separator()
        col.prop(sc, "hstvb_csv_path", text="CSV")
        col.operator("mesh.hstvb_run", text="▶ RUN BENCHMARK",
                     icon='MOD_DATA_TRANSFER')
        col.operator("mesh.hstvb_stop", text="■ STOP", icon='X')

        col.separator()
        col.label(text="Progress:")
        box = col.box()
        for line in sc.hstvb_progress.split('\n'):
            if line.strip():
                box.label(text=line)


# ─────────────────────────────────────────────
# OPERATORS
# ─────────────────────────────────────────────

_STOP_REQUESTED = False


class HST_VOLBENCH_OT_DETECT(bpy.types.Operator):
    bl_idname = "mesh.hstvb_detect"
    bl_label = "Detect GPU"

    def execute(self, context):
        backend = detect_gpu()
        if backend == 'cuda':
            try:
                import cupy as cp
                mem = cp.cuda.Device(0).mem_info
                v = cp.cuda.runtime.runtimeGetVersion()
                context.scene.hstvb_backend = (
                    f"cuda | CUDA {v//1000}.{(v%1000)//10} | "
                    f"{mem[0]/1024**2:.0f} MB free")
            except Exception:
                context.scene.hstvb_backend = 'cuda'
            self.report({'INFO'}, "GPU detected")
        else:
            context.scene.hstvb_backend = 'cpu — no GPU'
            self.report({'INFO'}, "No GPU — using CPU")
        return {'FINISHED'}


class HST_VOLBENCH_OT_STOP(bpy.types.Operator):
    bl_idname = "mesh.hstvb_stop"
    bl_label = "Stop"

    def execute(self, context):
        global _STOP_REQUESTED
        _STOP_REQUESTED = True
        self.report({'INFO'}, "Stop requested.")
        return {'FINISHED'}


class HST_VOLBENCH_OT_RUN(bpy.types.Operator):
    bl_idname = "mesh.hstvb_run"
    bl_label = "Run Volumetric FAUST Benchmark"

    def execute(self, context):
        global _STOP_REQUESTED
        _STOP_REQUESTED = False

        sc = context.scene
        faust_dir = bpy.path.abspath(sc.hstvb_faust_dir)
        csv_path  = bpy.path.abspath(sc.hstvb_csv_path)

        if not os.path.isdir(faust_dir):
            self.report({'ERROR'}, f"Directory not found: {faust_dir}")
            return {'CANCELLED'}

        backend = 'cpu'
        if not sc.hstvb_force_cpu and 'cuda' in sc.hstvb_backend:
            backend = 'cuda'

        ply_files = sorted([f for f in os.listdir(faust_dir)
                            if f.endswith('.ply') and 'tr_reg' in f.lower()])
        if not ply_files:
            ply_files = sorted([f for f in os.listdir(faust_dir)
                                if f.endswith('.ply')])

        pairs = [(ply_files[i], ply_files[i+1])
                 for i in range(sc.hstvb_pair_start,
                                min(sc.hstvb_pair_end, len(ply_files)-1),
                                sc.hstvb_pair_step)
                 if i+1 < len(ply_files)]

        if not pairs:
            self.report({'ERROR'}, "No pairs found.")
            return {'CANCELLED'}

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Dynamic CSV fields
        fields = ['pair_idx', 'source', 'target', 'n_verts', 'note_k',
                  'geo_hst_surf', 't_hst_surf']
        if sc.hstvb_use_interior:
            fields += ['geo_hst_vol', 't_hst_vol']
        if sc.hstvb_run_zoomout:
            fields += ['geo_zo_rand', 't_zo_rand',
                       'geo_zo_surf', 't_zo_surf', 'imp_zo_surf']
            if sc.hstvb_use_interior:
                fields += ['geo_zo_vol', 't_zo_vol', 'imp_zo_vol']
        if sc.hstvb_run_fmaps:
            fields += ['geo_fm_rand', 't_fm_rand',
                       'geo_fm_surf', 't_fm_surf', 'imp_fm_surf']
        fields += ['backend', 'status']

        all_results = []
        t_total = time.time()

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()

            for pair_idx, (file_a, file_b) in enumerate(pairs):
                if _STOP_REQUESTED:
                    sc.hstvb_progress += "\n⚠ Stopped."
                    break

                sc.hstvb_progress = (f"Pair {pair_idx+1}/{len(pairs)}: "
                                     f"{file_a} → {file_b}")
                print(sc.hstvb_progress)

                try:
                    verts_a, faces_a = load_ply(
                        os.path.join(faust_dir, file_a))
                    verts_b, faces_b = load_ply(
                        os.path.join(faust_dir, file_b))

                    r = run_pair(verts_a, faces_a, verts_b, faces_b,
                                 sc, backend=backend)

                    row = {
                        'pair_idx': pair_idx,
                        'source': file_a, 'target': file_b,
                        'n_verts': len(verts_a),
                        'note_k': r['note_k'],
                        'geo_hst_surf': f"{r['geo_hst_surf']:.6f}",
                        't_hst_surf': f"{r['t_hst_surf']:.3f}",
                        'backend': backend,
                        'status': 'OK',
                    }

                    line = f"  ✓ hst_surf={r['geo_hst_surf']:.4f}"

                    for key in ['geo_hst_vol', 't_hst_vol',
                                'geo_zo_rand', 't_zo_rand',
                                'geo_zo_surf', 't_zo_surf', 'imp_zo_surf',
                                'geo_zo_vol', 't_zo_vol', 'imp_zo_vol',
                                'geo_fm_rand', 't_fm_rand',
                                'geo_fm_surf', 't_fm_surf', 'imp_fm_surf']:
                        if key in r and key in fields:
                            val = r[key]
                            if isinstance(val, float) and not np.isnan(val):
                                row[key] = f"{val:.4f}"
                                if 'geo' in key or 'imp' in key:
                                    line += f"  {key}={val:.4f}"
                            else:
                                row[key] = 'N/A'

                    writer.writerow(row)
                    csvfile.flush()
                    all_results.append(r)
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
        ok = [r for r in all_results]
        lines = [f"=== DONE: {len(ok)}/{len(pairs)} pairs ===",
                 f"Time: {elapsed/60:.1f} min  Backend: {backend}"]

        if ok:
            g_surf = [r['geo_hst_surf'] for r in ok]
            lines.append(f"HST Surface: mean={np.mean(g_surf):.4f}")

            if sc.hstvb_use_interior:
                g_vol = [r['geo_hst_vol'] for r in ok
                         if not np.isnan(r.get('geo_hst_vol', float('nan')))]
                if g_vol:
                    lines.append(f"HST Interior: mean={np.mean(g_vol):.4f}")

            if sc.hstvb_run_zoomout and 'geo_zo_rand' in ok[0]:
                g_rand = [r['geo_zo_rand'] for r in ok]
                g_zo   = [r['geo_zo_surf'] for r in ok]
                imp    = [r['imp_zo_surf'] for r in ok]
                lines += [f"ZoomOut rand: mean={np.mean(g_rand):.4f}",
                          f"ZoomOut surf HST: mean={np.mean(g_zo):.4f}  imp={np.mean(imp):.1f}%"]

            if sc.hstvb_run_fmaps and 'geo_fm_rand' in ok[0]:
                g_fm_r = [r['geo_fm_rand'] for r in ok]
                g_fm   = [r['geo_fm_surf'] for r in ok]
                imp_fm = [r['imp_fm_surf'] for r in ok]
                lines += [f"FMaps rand: mean={np.mean(g_fm_r):.4f}",
                          f"FMaps surf HST: mean={np.mean(g_fm):.4f}  imp={np.mean(imp_fm):.1f}%"]

        summary = '\n'.join(lines)
        sc.hstvb_progress = summary
        print(summary)

        text = (bpy.data.texts.get("HST_VolBench.txt") or
                bpy.data.texts.new("HST_VolBench.txt"))
        text.clear(); text.write(summary)

        return {'FINISHED'}


# ─────────────────────────────────────────────
# REGISTRATION
# ─────────────────────────────────────────────

classes = (HST_VOLBENCH_PT_PANEL, HST_VOLBENCH_OT_DETECT,
           HST_VOLBENCH_OT_RUN, HST_VOLBENCH_OT_STOP)


def register():
    bpy.types.Scene.hstvb_backend = bpy.props.StringProperty(
        name="Backend", default="cpu — click Detect GPU")
    bpy.types.Scene.hstvb_force_cpu = bpy.props.BoolProperty(
        name="Force CPU", default=False)
    bpy.types.Scene.hstvb_faust_dir = bpy.props.StringProperty(
        name="FAUST Directory", default="//faust/", subtype='DIR_PATH')
    bpy.types.Scene.hstvb_pair_start = bpy.props.IntProperty(
        name="First pair", default=0, min=0, max=99)
    bpy.types.Scene.hstvb_pair_end = bpy.props.IntProperty(
        name="Last pair", default=99, min=1, max=199)
    bpy.types.Scene.hstvb_pair_step = bpy.props.IntProperty(
        name="Step", default=1, min=1, max=10)
    bpy.types.Scene.hstvb_k_eigen = bpy.props.IntProperty(
        name="Eigenmodes (k)", default=50, min=10, max=100)
    bpy.types.Scene.hstvb_eigen_seed = bpy.props.IntProperty(
        name="Eigen seed", default=42, min=0, max=9999)
    bpy.types.Scene.hstvb_k_note_cands = bpy.props.IntProperty(
        name="Note candidates", default=5, min=1, max=10)
    bpy.types.Scene.hstvb_rand_seed = bpy.props.IntProperty(
        name="Random seed", default=42, min=0, max=9999)
    bpy.types.Scene.hstvb_use_interior = bpy.props.BoolProperty(
        name="Interior note (tetrahedral)", default=False,
        description="Slower — tetrahedralization per pair")
    bpy.types.Scene.hstvb_tet_res = bpy.props.IntProperty(
        name="Tet resolution", default=6, min=4, max=16)
    bpy.types.Scene.hstvb_run_zoomout = bpy.props.BoolProperty(
        name="Test ZoomOut", default=True)
    bpy.types.Scene.hstvb_k_init = bpy.props.IntProperty(
        name="ZoomOut k_init", default=10, min=5, max=30)
    bpy.types.Scene.hstvb_k_step = bpy.props.IntProperty(
        name="ZoomOut k_step", default=5, min=1, max=10)
    bpy.types.Scene.hstvb_k_final = bpy.props.IntProperty(
        name="ZoomOut k_final", default=40, min=20, max=100)
    bpy.types.Scene.hstvb_run_fmaps = bpy.props.BoolProperty(
        name="Test Functional Maps", default=True)
    bpy.types.Scene.hstvb_k_fmaps = bpy.props.IntProperty(
        name="FMaps k", default=30, min=10, max=100)
    bpy.types.Scene.hstvb_csv_path = bpy.props.StringProperty(
        name="CSV output", default="//hst_volumetric_benchmark.csv",
        subtype='FILE_PATH')
    bpy.types.Scene.hstvb_progress = bpy.props.StringProperty(
        name="Progress", default="Set FAUST dir and click RUN.")

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    props = ['hstvb_backend', 'hstvb_force_cpu', 'hstvb_faust_dir',
             'hstvb_pair_start', 'hstvb_pair_end', 'hstvb_pair_step',
             'hstvb_k_eigen', 'hstvb_eigen_seed', 'hstvb_k_note_cands',
             'hstvb_rand_seed', 'hstvb_use_interior', 'hstvb_tet_res',
             'hstvb_run_zoomout', 'hstvb_k_init', 'hstvb_k_step',
             'hstvb_k_final', 'hstvb_run_fmaps', 'hstvb_k_fmaps',
             'hstvb_csv_path', 'hstvb_progress']
    for p in props:
        if hasattr(bpy.types.Scene, p):
            delattr(bpy.types.Scene, p)


if __name__ == "__main__":
    register()
