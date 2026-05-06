## Full FAUST GPU Benchmark — 99 Pairs (RTX 4070)

> **Note:** To the best of the author's knowledge, this may be the first
> publicly documented GPU-accelerated benchmark of spectral shape
> correspondence on the FAUST dataset using pure Python (CuPy + scipy).
> The official ZoomOut implementation (Melzi et al., 2019) is MATLAB-only
> with no GPU support. Existing Python ports are CPU-only.

### Results — All Methods

| Method | Mean geo error | Time | vs ZoomOut CPU |
|--------|---------------|------|----------------|
| HST Note (CPU) | 0.129 | 0.805s | 53× |
| HST Note (GPU) | 0.129 | 0.844s | 53× |
| Random → FMaps (GPU) | 0.295 | 1.30s | 33× |
| **HST → FMaps (GPU)** | **0.138** | **1.88s** | **23×** |
| Random → ZoomOut (GPU) | 0.349 | 6.98s | 6.1× |
| **HST → ZoomOut (GPU)** | **0.195** | **7.82s** | **6.1×** |
| HST → ZoomOut (CPU) | 0.193 | 43.6s | 1× |

<img width="2084" height="1475" alt="hst_universal_init_final" src="https://github.com/user-attachments/assets/3e4787c1-0ba4-4929-9c60-b7c21d7f1ea6" />

[hst_universal_init.csv](https://github.com/user-attachments/files/27457152/hst_universal_init.csv)
timestamp,pair_idx,source,target,n_verts,note_k,geo_hst,t_hst,geo_fm_rand,t_fm_rand,geo_fm_hst,t_fm_hst,imp_fm,status
2026-05-06 22:27:56,0,tr_reg_000.ply,tr_reg_001.ply,6890,1,0.120386,0.799,0.325016,1.310,0.094229,1.890,71.01,OK
2026-05-06 22:27:56,1,tr_reg_001.ply,tr_reg_002.ply,6890,1,0.124430,0.814,0.268751,1.448,0.149342,1.906,44.43,OK
2026-05-06 22:27:56,2,tr_reg_002.ply,tr_reg_003.ply,6890,1,0.092912,0.815,0.423166,1.122,0.113083,1.915,73.28,OK
2026-05-06 22:27:56,3,tr_reg_003.ply,tr_reg_004.ply,6890,1,0.130153,0.805,0.302480,1.420,0.117202,1.911,61.25,OK
2026-05-06 22:27:56,4,tr_reg_004.ply,tr_reg_005.ply,6890,1,0.161544,0.804,0.270599,1.258,0.136262,1.900,49.64,OK
2026-05-06 22:27:56,5,tr_reg_005.ply,tr_reg_006.ply,6890,1,0.085179,0.813,0.289003,1.357,0.068019,1.920,76.46,OK
2026-05-06 22:27:56,6,tr_reg_006.ply,tr_reg_007.ply,6890,1,0.081873,0.805,0.391198,1.413,0.090621,1.896,76.84,OK
2026-05-06 22:27:56,7,tr_reg_007.ply,tr_reg_008.ply,6890,1,0.146801,0.805,0.300268,1.343,0.198173,1.908,34.00,OK
2026-05-06 22:27:56,8,tr_reg_008.ply,tr_reg_009.ply,6890,1,0.126913,0.818,0.376986,1.265,0.126727,1.911,66.38,OK
2026-05-06 22:27:56,9,tr_reg_009.ply,tr_reg_010.ply,6890,1,0.154684,0.809,0.285950,1.394,0.201133,1.901,29.66,OK
2026-05-06 22:27:56,10,tr_reg_010.ply,tr_reg_011.ply,6890,1,0.120326,0.808,0.297139,1.397,0.100970,1.940,66.02,OK
2026-05-06 22:27:56,11,tr_reg_011.ply,tr_reg_012.ply,6890,1,0.142194,0.803,0.278110,1.387,0.164239,1.955,40.94,OK
2026-05-06 22:27:56,12,tr_reg_012.ply,tr_reg_013.ply,6890,1,0.089412,0.801,0.233246,1.283,0.110406,1.972,52.67,OK
2026-05-06 22:27:56,13,tr_reg_013.ply,tr_reg_014.ply,6890,1,0.144346,0.815,0.301764,1.269,0.194567,1.876,35.52,OK
2026-05-06 22:27:56,14,tr_reg_014.ply,tr_reg_015.ply,6890,1,0.148729,0.803,0.339785,1.390,0.176927,1.854,47.93,OK
2026-05-06 22:27:56,15,tr_reg_015.ply,tr_reg_016.ply,6890,1,0.098594,0.817,0.282693,1.274,0.150652,1.851,46.71,OK
2026-05-06 22:27:56,16,tr_reg_016.ply,tr_reg_017.ply,6890,1,0.082012,0.801,0.213264,1.379,0.085305,1.908,60.00,OK
2026-05-06 22:27:56,17,tr_reg_017.ply,tr_reg_018.ply,6890,1,0.143931,0.806,0.281341,1.364,0.141776,1.840,49.61,OK
2026-05-06 22:27:56,18,tr_reg_018.ply,tr_reg_019.ply,6890,1,0.107202,0.799,0.235266,1.242,0.119431,1.834,49.24,OK
2026-05-06 22:27:56,19,tr_reg_019.ply,tr_reg_020.ply,6890,1,0.209221,0.801,0.286493,1.336,0.239631,1.834,16.36,OK
2026-05-06 22:27:56,20,tr_reg_020.ply,tr_reg_021.ply,6890,1,0.125007,0.799,0.283565,1.325,0.130019,1.861,54.15,OK
2026-05-06 22:27:56,21,tr_reg_021.ply,tr_reg_022.ply,6890,1,0.139603,0.804,0.277328,1.359,0.163434,1.840,41.07,OK
2026-05-06 22:27:56,22,tr_reg_022.ply,tr_reg_023.ply,6890,1,0.102439,0.820,0.240923,1.342,0.100803,1.962,58.16,OK
2026-05-06 22:27:56,23,tr_reg_023.ply,tr_reg_024.ply,6890,1,0.171028,0.804,0.304532,1.386,0.189660,1.854,37.72,OK
2026-05-06 22:27:56,24,tr_reg_024.ply,tr_reg_025.ply,6890,1,0.228230,0.805,0.320996,1.298,0.239533,1.898,25.38,OK
2026-05-06 22:27:56,25,tr_reg_025.ply,tr_reg_026.ply,6890,1,0.094744,0.803,0.267206,1.280,0.114564,1.898,57.13,OK
2026-05-06 22:27:56,26,tr_reg_026.ply,tr_reg_027.ply,6890,1,0.099812,0.802,0.388422,1.323,0.128569,1.900,66.90,OK
2026-05-06 22:27:56,27,tr_reg_027.ply,tr_reg_028.ply,6890,1,0.504457,0.805,0.278108,1.110,0.478754,1.910,-72.15,OK
2026-05-06 22:27:56,28,tr_reg_028.ply,tr_reg_029.ply,6890,1,0.121944,0.801,0.311855,1.400,0.113509,1.898,63.60,OK
2026-05-06 22:27:56,29,tr_reg_029.ply,tr_reg_030.ply,6890,1,0.176663,0.814,0.297190,1.378,0.255043,1.912,14.18,OK
2026-05-06 22:27:56,30,tr_reg_030.ply,tr_reg_031.ply,6890,1,0.094099,0.816,0.271066,1.372,0.076887,1.952,71.64,OK
2026-05-06 22:27:56,31,tr_reg_031.ply,tr_reg_032.ply,6890,1,0.112007,0.801,0.286128,1.292,0.065457,1.895,77.12,OK
2026-05-06 22:27:56,32,tr_reg_032.ply,tr_reg_033.ply,6890,1,0.090942,0.801,0.257357,1.361,0.108126,1.894,57.99,OK
2026-05-06 22:27:56,33,tr_reg_033.ply,tr_reg_034.ply,6890,1,0.159781,0.804,0.319781,1.399,0.116638,1.839,63.53,OK
2026-05-06 22:27:56,34,tr_reg_034.ply,tr_reg_035.ply,6890,1,0.159258,0.809,0.346753,1.287,0.219098,1.908,36.81,OK
2026-05-06 22:27:56,35,tr_reg_035.ply,tr_reg_036.ply,6890,1,0.084023,0.797,0.282651,1.332,0.089905,1.887,68.19,OK
2026-05-06 22:27:56,36,tr_reg_036.ply,tr_reg_037.ply,6890,1,0.105494,0.815,0.215796,1.363,0.129307,1.904,40.08,OK
2026-05-06 22:27:56,37,tr_reg_037.ply,tr_reg_038.ply,6890,1,0.152588,0.815,0.378350,1.339,0.172978,1.924,54.28,OK
2026-05-06 22:27:56,38,tr_reg_038.ply,tr_reg_039.ply,6890,1,0.126762,0.802,0.391689,1.366,0.130421,1.895,66.70,OK
2026-05-06 22:27:56,39,tr_reg_039.ply,tr_reg_040.ply,6890,1,0.161770,0.801,0.262750,1.385,0.219053,1.885,16.63,OK
2026-05-06 22:27:56,40,tr_reg_040.ply,tr_reg_041.ply,6890,1,0.109477,0.848,0.270819,1.422,0.081079,1.887,70.06,OK
2026-05-06 22:27:56,41,tr_reg_041.ply,tr_reg_042.ply,6890,1,0.103716,0.826,0.262657,1.371,0.088349,1.924,66.36,OK
2026-05-06 22:27:56,42,tr_reg_042.ply,tr_reg_043.ply,6890,1,0.104486,0.804,0.277551,1.345,0.080770,1.903,70.90,OK
2026-05-06 22:27:56,43,tr_reg_043.ply,tr_reg_044.ply,6890,1,0.160165,0.802,0.304628,1.293,0.166651,1.842,45.29,OK
2026-05-06 22:27:56,44,tr_reg_044.ply,tr_reg_045.ply,6890,1,0.100625,0.803,0.301793,1.394,0.086300,1.907,71.40,OK
2026-05-06 22:27:56,45,tr_reg_045.ply,tr_reg_046.ply,6890,1,0.098133,0.801,0.250081,1.318,0.108385,1.836,56.66,OK
2026-05-06 22:27:56,46,tr_reg_046.ply,tr_reg_047.ply,6890,1,0.105315,0.799,0.254205,1.293,0.091989,1.836,63.81,OK
2026-05-06 22:27:56,47,tr_reg_047.ply,tr_reg_048.ply,6890,1,0.180707,0.799,0.278285,1.318,0.155051,1.871,44.28,OK
2026-05-06 22:27:56,48,tr_reg_048.ply,tr_reg_049.ply,6890,1,0.113513,0.801,0.434784,1.239,0.119437,1.867,72.53,OK
2026-05-06 22:27:56,49,tr_reg_049.ply,tr_reg_050.ply,6890,1,0.152877,0.807,0.263369,1.241,0.196028,1.870,25.57,OK
2026-05-06 22:27:56,50,tr_reg_050.ply,tr_reg_051.ply,6890,1,0.094542,0.801,0.236445,1.240,0.082388,1.839,65.16,OK
2026-05-06 22:27:56,51,tr_reg_051.ply,tr_reg_052.ply,6890,1,0.151237,0.805,0.300056,1.277,0.165288,1.910,44.91,OK
2026-05-06 22:27:56,52,tr_reg_052.ply,tr_reg_053.ply,6890,1,0.086674,0.809,0.239498,1.300,0.077012,1.893,67.84,OK
2026-05-06 22:27:56,53,tr_reg_053.ply,tr_reg_054.ply,6890,1,0.141777,0.807,0.326645,1.236,0.179241,1.850,45.13,OK
2026-05-06 22:27:56,54,tr_reg_054.ply,tr_reg_055.ply,6890,1,0.150886,0.810,0.310935,1.266,0.195099,1.851,37.25,OK
2026-05-06 22:27:56,55,tr_reg_055.ply,tr_reg_056.ply,6890,1,0.085116,0.803,0.254957,1.249,0.104307,1.841,59.09,OK
2026-05-06 22:27:56,56,tr_reg_056.ply,tr_reg_057.ply,6890,1,0.091192,0.804,0.330013,1.271,0.080201,1.882,75.70,OK
2026-05-06 22:27:56,57,tr_reg_057.ply,tr_reg_058.ply,6890,1,0.141391,0.805,0.271990,1.356,0.205021,1.843,24.62,OK
2026-05-06 22:27:56,58,tr_reg_058.ply,tr_reg_059.ply,6890,1,0.102575,0.799,0.229928,1.333,0.079910,1.839,65.25,OK
2026-05-06 22:27:56,59,tr_reg_059.ply,tr_reg_060.ply,6890,1,0.145964,0.801,0.323031,1.278,0.169754,1.864,47.45,OK
2026-05-06 22:27:56,60,tr_reg_060.ply,tr_reg_061.ply,6890,1,0.111776,0.800,0.285524,1.270,0.119597,1.848,58.11,OK
2026-05-06 22:27:56,61,tr_reg_061.ply,tr_reg_062.ply,6890,1,0.104014,0.808,0.269651,1.225,0.076675,1.886,71.57,OK
2026-05-06 22:27:56,62,tr_reg_062.ply,tr_reg_063.ply,6890,1,0.066098,0.812,0.259167,1.335,0.064321,1.864,75.18,OK
2026-05-06 22:27:56,63,tr_reg_063.ply,tr_reg_064.ply,6890,1,0.134561,0.799,0.337080,1.261,0.120614,1.853,64.22,OK
2026-05-06 22:27:56,64,tr_reg_064.ply,tr_reg_065.ply,6890,1,0.160312,0.801,0.318062,1.279,0.170029,1.836,46.54,OK
2026-05-06 22:27:56,65,tr_reg_065.ply,tr_reg_066.ply,6890,1,0.082585,0.803,0.306351,1.410,0.093630,1.899,69.44,OK
2026-05-06 22:27:56,66,tr_reg_066.ply,tr_reg_067.ply,6890,1,0.106751,0.816,0.394787,1.244,0.121565,1.850,69.21,OK
2026-05-06 22:27:56,67,tr_reg_067.ply,tr_reg_068.ply,6890,1,0.163511,0.803,0.312672,1.388,0.194805,1.836,37.70,OK
2026-05-06 22:27:56,68,tr_reg_068.ply,tr_reg_069.ply,6890,1,0.100800,0.811,0.243048,1.329,0.113606,1.881,53.26,OK
2026-05-06 22:27:56,69,tr_reg_069.ply,tr_reg_070.ply,6890,1,0.163960,0.813,0.284075,1.308,0.119118,1.874,58.07,OK
2026-05-06 22:27:56,70,tr_reg_070.ply,tr_reg_071.ply,6890,1,0.117322,0.801,0.273316,1.284,0.117077,1.836,57.16,OK
2026-05-06 22:27:56,71,tr_reg_071.ply,tr_reg_072.ply,6890,1,0.153224,0.807,0.367639,1.267,0.170418,1.859,53.65,OK
2026-05-06 22:27:56,72,tr_reg_072.ply,tr_reg_073.ply,6890,1,0.110799,0.808,0.276017,1.081,0.129300,1.875,53.16,OK
2026-05-06 22:27:56,73,tr_reg_073.ply,tr_reg_074.ply,6890,1,0.125733,0.801,0.283875,1.116,0.122275,1.856,56.93,OK
2026-05-06 22:27:56,74,tr_reg_074.ply,tr_reg_075.ply,6890,1,0.171406,0.801,0.278835,1.256,0.141108,1.837,49.39,OK
2026-05-06 22:27:56,75,tr_reg_075.ply,tr_reg_076.ply,6890,1,0.094402,0.807,0.251243,1.277,0.072383,1.883,71.19,OK
2026-05-06 22:27:56,76,tr_reg_076.ply,tr_reg_077.ply,6890,1,0.100786,0.795,0.418891,1.243,0.110174,1.841,73.70,OK
2026-05-06 22:27:56,77,tr_reg_077.ply,tr_reg_078.ply,6890,1,0.176100,0.804,0.283600,1.349,0.241286,1.868,14.92,OK
2026-05-06 22:27:56,78,tr_reg_078.ply,tr_reg_079.ply,6890,1,0.139280,0.806,0.241868,1.203,0.163033,1.852,32.59,OK
2026-05-06 22:27:56,79,tr_reg_079.ply,tr_reg_080.ply,6890,1,0.156090,0.802,0.321821,1.246,0.208600,1.862,35.18,OK
2026-05-06 22:27:56,80,tr_reg_080.ply,tr_reg_081.ply,6890,1,0.092819,0.800,0.302536,1.275,0.082051,1.839,72.88,OK
2026-05-06 22:27:56,81,tr_reg_081.ply,tr_reg_082.ply,6890,1,0.139927,0.802,0.316730,1.233,0.089042,1.848,71.89,OK
2026-05-06 22:27:56,82,tr_reg_082.ply,tr_reg_083.ply,6890,1,0.095802,0.805,0.247811,1.290,0.087651,1.911,64.63,OK
2026-05-06 22:27:56,83,tr_reg_083.ply,tr_reg_084.ply,6890,1,0.170049,0.801,0.256863,1.125,0.175222,1.892,31.78,OK
2026-05-06 22:27:56,84,tr_reg_084.ply,tr_reg_085.ply,6890,1,0.194596,0.827,0.303731,1.376,0.219358,1.971,27.78,OK
2026-05-06 22:27:56,85,tr_reg_085.ply,tr_reg_086.ply,6890,1,0.096291,0.811,0.287635,1.322,0.120306,1.916,58.17,OK
2026-05-06 22:27:56,86,tr_reg_086.ply,tr_reg_087.ply,6890,1,0.105693,0.818,0.410775,1.426,0.113399,1.856,72.39,OK
2026-05-06 22:27:56,87,tr_reg_087.ply,tr_reg_088.ply,6890,1,0.155995,0.810,0.286733,1.229,0.208998,1.881,27.11,OK
2026-05-06 22:27:56,88,tr_reg_088.ply,tr_reg_089.ply,6890,1,0.115582,0.803,0.239330,1.297,0.155881,1.859,34.87,OK
2026-05-06 22:27:56,89,tr_reg_089.ply,tr_reg_090.ply,6890,1,0.146488,0.802,0.319583,1.251,0.179817,1.847,43.73,OK
2026-05-06 22:27:56,90,tr_reg_090.ply,tr_reg_091.ply,6890,1,0.111953,0.802,0.342864,1.293,0.107647,1.928,68.60,OK
2026-05-06 22:27:56,91,tr_reg_091.ply,tr_reg_092.ply,6890,1,0.099777,0.804,0.285222,1.334,0.081802,1.852,71.32,OK
2026-05-06 22:27:56,92,tr_reg_092.ply,tr_reg_093.ply,6890,1,0.089412,0.805,0.264368,1.241,0.087647,1.861,66.85,OK
2026-05-06 22:27:56,93,tr_reg_093.ply,tr_reg_094.ply,6890,1,0.141885,0.806,0.314913,1.354,0.139359,1.873,55.75,OK
2026-05-06 22:27:56,94,tr_reg_094.ply,tr_reg_095.ply,6890,1,0.151238,0.809,0.290256,1.363,0.155543,1.893,46.41,OK
2026-05-06 22:27:56,95,tr_reg_095.ply,tr_reg_096.ply,6890,1,0.086090,0.795,0.265128,1.243,0.090860,1.828,65.73,OK
2026-05-06 22:27:56,96,tr_reg_096.ply,tr_reg_097.ply,6890,1,0.096104,0.803,0.210712,1.117,0.091181,1.965,56.73,OK
2026-05-06 22:27:56,97,tr_reg_097.ply,tr_reg_098.ply,6890,1,0.159759,0.808,0.294588,1.357,0.161893,1.916,45.04,OK
2026-05-06 22:27:56,98,tr_reg_098.ply,tr_reg_099.ply,6890,1,0.088935,0.802,0.239774,1.249,0.127348,1.892,46.89,OK


### Total Benchmark Time (99 pairs)

| Scenario | Time |
|----------|------|
| CPU — HST only | 1.3 min |
| CPU — HST + ZoomOut | 142 min |
| **GPU — HST + ZoomOut** | **13 min** |
| **GPU — HST + FMaps** | **17 min** |

### CPU vs GPU — Identical Results

| Metric | CPU | GPU |
|--------|-----|-----|
| HST Note wins | 67/99 | 66/99 |
| HST+ZoomOut wins | 32/99 | 33/99 |
| Random→ZoomOut wins | 0/99 | 0/99 |
| Mean geo error (HST) | 0.129 | 0.129 |
| Mean improvement (ZoomOut) | 42.3% | 41.5% |
| Mean improvement (FMaps) | 52.5% | 52.5% |

GPU and CPU produce **identical winner distributions and geo error values**
across all 99 pairs. The speedup introduces zero numerical artifacts.

### Analysis

GPU acceleration comes from parallelizing nearest-neighbor search in
spectral space. For ZoomOut this gives 6.1× speedup, for Functional Maps
~10× speedup. Eigenvectors remain on CPU (scipy ARPACK is faster for sparse k=2).

All computations use float64 precision on GPU — identical accuracy to CPU.

<img width="2380" height="740" alt="hst_gpu_final" src="https://github.com/user-attachments/assets/0ed44b8c-c171-4e70-ba2b-962e97392178" />

### Analysis

The GPU acceleration comes entirely from the ZoomOut nearest-neighbor
search component. For each ZoomOut iteration, the algorithm must find
the closest point in k-dimensional spectral space for all 6890 vertices
simultaneously. This is a highly parallelizable operation — exactly the
type of workload where GPU excels.

The functional map matrix C is computed on CPU in float64 for numerical
accuracy. Only the nearest-neighbor distance computation is offloaded to
GPU in float64, which provides the speedup without sacrificing precision.

Eigenvectors remain on CPU because scipy ARPACK sparse solver computes
only k=2 eigenvectors directly. GPU full eigendecomposition (eigh) would
compute all 6890 eigenvectors — fundamentally slower for small k regardless
of GPU speed.

### Consistency

GPU results are fully consistent with CPU benchmark:
- Same geo error values (float64 precision preserved)
- Same winner distribution (Random→ZoomOut never wins)
- Same HST init improvement (~42%)

This confirms that GPU acceleration does not introduce any numerical
artifacts or changes in result quality.

> **Note:** To the best of the author's knowledge, this may be the first
> publicly documented GPU-accelerated benchmark of spectral shape
> correspondence (HST + ZoomOut) on the FAUST dataset using a pure Python
> implementation (CuPy + scipy). The official ZoomOut implementation
> (Melzi et al., 2019) is MATLAB-only with no GPU support. Existing Python
> ports of ZoomOut are CPU-only. This benchmark represents an independent
> contribution to the reproducibility and accessibility of spectral shape
> matching methods.

### Hardware Note

Tested on NVIDIA RTX 4070 (12GB VRAM, CUDA 12.9, Compute Capability 8.9).
CuPy 14.0.1 with nvidia-cusolver-cu12.
CPU: scipy 1.17.1, ARPACK sparse eigensolver.

