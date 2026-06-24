import re
import math
import html
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime

BILITOOL_LINK_URL = "https://emr.bilitool.org/results.php"
BTC_TECNICO_SEM_BTC = 0.1
BILITOOL_MIN_GA_SEMANAS = 35
BILITOOL_MAX_GA_SEMANAS = 40


# ============================================================
# TABELAS INTERGROWTH-21st - Z-SCORES DE PESO AO NASCER
# Unidades: kg
# Colunas: IG  z-3 z-2 z-1 z0 z+1 z+2 z+3
# ============================================================

Z_BOYS_24_32 = """
24+0 0.36 0.43 0.53 0.64 0.77 0.94 1.14
24+1 0.36 0.44 0.54 0.65 0.79 0.96 1.16
24+2 0.37 0.45 0.55 0.66 0.80 0.98 1.18
24+3 0.38 0.46 0.56 0.68 0.82 0.99 1.21
24+4 0.39 0.47 0.57 0.69 0.84 1.01 1.23
24+5 0.39 0.48 0.58 0.70 0.85 1.03 1.25
24+6 0.40 0.49 0.59 0.72 0.87 1.05 1.28
25+0 0.41 0.50 0.60 0.73 0.88 1.07 1.30
25+1 0.42 0.50 0.61 0.74 0.90 1.09 1.33
25+2 0.42 0.51 0.62 0.76 0.92 1.11 1.35
25+3 0.43 0.52 0.64 0.77 0.94 1.14 1.38
25+4 0.44 0.53 0.65 0.79 0.95 1.16 1.40
25+5 0.45 0.54 0.66 0.80 0.97 1.18 1.43
25+6 0.46 0.55 0.67 0.82 0.99 1.20 1.46
26+0 0.47 0.56 0.69 0.83 1.01 1.22 1.48
26+1 0.47 0.58 0.70 0.85 1.03 1.25 1.51
26+2 0.48 0.59 0.71 0.86 1.05 1.27 1.54
26+3 0.49 0.60 0.72 0.88 1.07 1.29 1.57
26+4 0.50 0.61 0.74 0.89 1.09 1.32 1.60
26+5 0.51 0.62 0.75 0.91 1.11 1.34 1.63
26+6 0.52 0.63 0.77 0.93 1.13 1.37 1.66
27+0 0.53 0.64 0.78 0.95 1.15 1.39 1.69
27+1 0.54 0.65 0.79 0.96 1.17 1.42 1.72
27+2 0.55 0.67 0.81 0.98 1.19 1.44 1.75
27+3 0.56 0.68 0.82 1.00 1.21 1.47 1.78
27+4 0.57 0.69 0.84 1.02 1.23 1.50 1.81
27+5 0.58 0.70 0.85 1.03 1.26 1.52 1.85
27+6 0.59 0.72 0.87 1.05 1.28 1.55 1.88
28+0 0.60 0.73 0.88 1.07 1.30 1.58 1.92
28+1 0.61 0.74 0.90 1.09 1.32 1.61 1.95
28+2 0.62 0.76 0.92 1.11 1.35 1.64 1.98
28+3 0.63 0.77 0.93 1.13 1.37 1.67 2.02
28+4 0.65 0.78 0.95 1.15 1.40 1.70 2.06
28+5 0.66 0.80 0.97 1.17 1.42 1.73 2.09
28+6 0.67 0.81 0.98 1.19 1.45 1.76 2.13
29+0 0.68 0.83 1.00 1.21 1.47 1.79 2.17
29+1 0.69 0.84 1.02 1.24 1.50 1.82 2.21
29+2 0.70 0.85 1.04 1.26 1.53 1.85 2.25
29+3 0.72 0.87 1.06 1.28 1.55 1.88 2.29
29+4 0.73 0.89 1.07 1.30 1.58 1.92 2.33
29+5 0.74 0.90 1.09 1.33 1.61 1.95 2.37
29+6 0.76 0.92 1.11 1.35 1.64 1.98 2.41
30+0 0.77 0.93 1.13 1.37 1.66 2.02 2.45
30+1 0.78 0.95 1.15 1.40 1.69 2.05 2.49
30+2 0.80 0.97 1.17 1.42 1.72 2.09 2.54
30+3 0.81 0.98 1.19 1.45 1.75 2.13 2.58
30+4 0.82 1.00 1.21 1.47 1.78 2.16 2.62
30+5 0.84 1.02 1.23 1.50 1.81 2.20 2.67
30+6 0.85 1.03 1.25 1.52 1.85 2.24 2.72
31+0 0.87 1.05 1.28 1.55 1.88 2.28 2.76
31+1 0.88 1.07 1.30 1.57 1.91 2.32 2.81
31+2 0.90 1.09 1.32 1.60 1.94 2.36 2.86
31+3 0.91 1.11 1.34 1.63 1.97 2.40 2.91
31+4 0.93 1.13 1.36 1.66 2.01 2.44 2.96
31+5 0.94 1.14 1.39 1.68 2.04 2.48 3.01
31+6 0.96 1.16 1.41 1.71 2.08 2.52 3.06
32+0 0.98 1.18 1.44 1.74 2.11 2.56 3.11
32+1 0.99 1.20 1.46 1.77 2.15 2.61 3.16
32+2 1.01 1.22 1.48 1.80 2.18 2.65 3.21
32+3 1.03 1.24 1.51 1.83 2.22 2.69 3.27
32+4 1.04 1.26 1.53 1.86 2.26 2.74 3.32
32+5 1.06 1.29 1.56 1.89 2.30 2.79 3.38
32+6 1.08 1.31 1.59 1.92 2.33 2.83 3.43
"""

Z_GIRLS_24_32 = """
24+0 0.34 0.41 0.50 0.60 0.73 0.89 1.07
24+1 0.34 0.42 0.51 0.61 0.74 0.90 1.10
24+2 0.35 0.43 0.52 0.63 0.76 0.92 1.12
24+3 0.36 0.43 0.53 0.64 0.77 0.94 1.14
24+4 0.36 0.44 0.54 0.65 0.79 0.96 1.16
24+5 0.37 0.45 0.55 0.66 0.80 0.98 1.18
24+6 0.38 0.46 0.56 0.68 0.82 0.99 1.21
25+0 0.39 0.47 0.57 0.69 0.84 1.01 1.23
25+1 0.39 0.48 0.58 0.70 0.85 1.03 1.25
25+2 0.40 0.49 0.59 0.71 0.87 1.05 1.28
25+3 0.41 0.49 0.60 0.73 0.88 1.07 1.30
25+4 0.42 0.50 0.61 0.74 0.90 1.09 1.33
25+5 0.42 0.51 0.62 0.76 0.92 1.11 1.35
25+6 0.43 0.52 0.64 0.77 0.93 1.13 1.38
26+0 0.44 0.53 0.65 0.78 0.95 1.16 1.40
26+1 0.45 0.54 0.66 0.80 0.97 1.18 1.43
26+2 0.46 0.55 0.67 0.81 0.99 1.20 1.45
26+3 0.46 0.56 0.68 0.83 1.01 1.22 1.48
26+4 0.47 0.57 0.70 0.85 1.03 1.24 1.51
26+5 0.48 0.58 0.71 0.86 1.04 1.27 1.54
26+6 0.49 0.60 0.72 0.88 1.06 1.29 1.57
27+0 0.50 0.61 0.74 0.89 1.08 1.31 1.59
27+1 0.51 0.62 0.75 0.91 1.10 1.34 1.62
27+2 0.52 0.63 0.76 0.93 1.12 1.36 1.65
27+3 0.53 0.64 0.78 0.94 1.14 1.39 1.68
27+4 0.54 0.65 0.79 0.96 1.16 1.41 1.71
27+5 0.55 0.66 0.81 0.98 1.19 1.44 1.74
27+6 0.56 0.68 0.82 1.00 1.21 1.46 1.78
28+0 0.57 0.69 0.84 1.01 1.23 1.49 1.81
28+1 0.58 0.70 0.85 1.03 1.25 1.52 1.84
28+2 0.59 0.71 0.87 1.05 1.27 1.55 1.87
28+3 0.60 0.73 0.88 1.07 1.30 1.57 1.91
28+4 0.61 0.74 0.90 1.09 1.32 1.60 1.94
28+5 0.62 0.75 0.91 1.11 1.34 1.63 1.98
28+6 0.63 0.77 0.93 1.13 1.37 1.66 2.01
29+0 0.64 0.78 0.95 1.15 1.39 1.69 2.05
29+1 0.65 0.79 0.96 1.17 1.42 1.72 2.08
29+2 0.67 0.81 0.98 1.19 1.44 1.75 2.12
29+3 0.68 0.82 1.00 1.21 1.47 1.78 2.16
29+4 0.69 0.84 1.01 1.23 1.49 1.81 2.20
29+5 0.70 0.85 1.03 1.25 1.52 1.84 2.23
29+6 0.71 0.87 1.05 1.27 1.55 1.87 2.27
30+0 0.73 0.88 1.07 1.30 1.57 1.91 2.31
30+1 0.74 0.90 1.09 1.32 1.60 1.94 2.35
30+2 0.75 0.91 1.11 1.34 1.63 1.97 2.39
30+3 0.76 0.93 1.13 1.36 1.66 2.01 2.44
30+4 0.78 0.94 1.14 1.39 1.68 2.04 2.48
30+5 0.79 0.96 1.16 1.41 1.71 2.08 2.52
30+6 0.80 0.98 1.18 1.44 1.74 2.11 2.56
31+0 0.82 0.99 1.20 1.46 1.77 2.15 2.61
31+1 0.83 1.01 1.23 1.49 1.80 2.19 2.65
31+2 0.85 1.03 1.25 1.51 1.83 2.22 2.70
31+3 0.86 1.04 1.27 1.54 1.87 2.26 2.74
31+4 0.88 1.06 1.29 1.56 1.90 2.30 2.79
31+5 0.89 1.08 1.31 1.59 1.93 2.34 2.84
31+6 0.91 1.10 1.33 1.62 1.96 2.38 2.89
32+0 0.92 1.12 1.36 1.64 1.99 2.42 2.94
32+1 0.94 1.14 1.38 1.67 2.03 2.46 2.99
32+2 0.95 1.16 1.40 1.70 2.06 2.50 3.04
32+3 0.97 1.17 1.43 1.73 2.10 2.54 3.09
32+4 0.98 1.19 1.45 1.76 2.13 2.59 3.14
32+5 1.00 1.21 1.47 1.79 2.17 2.63 3.19
32+6 1.02 1.23 1.50 1.82 2.20 2.67 3.24
"""

Z_BOYS_33_42 = """
33+0 0.63 1.13 1.55 1.95 2.39 2.88 3.47
33+1 0.67 1.17 1.59 1.99 2.43 2.92 3.51
33+2 0.71 1.21 1.63 2.03 2.47 2.96 3.55
33+3 0.75 1.25 1.67 2.07 2.50 2.99 3.59
33+4 0.79 1.29 1.71 2.11 2.54 3.03 3.62
33+5 0.83 1.33 1.75 2.15 2.58 3.07 3.66
33+6 0.87 1.37 1.79 2.18 2.62 3.11 3.70
34+0 0.91 1.40 1.82 2.22 2.65 3.14 3.73
34+1 0.95 1.44 1.86 2.26 2.69 3.18 3.77
34+2 0.98 1.48 1.90 2.29 2.73 3.21 3.80
34+3 1.02 1.51 1.93 2.33 2.76 3.25 3.84
34+4 1.05 1.55 1.97 2.36 2.80 3.28 3.87
34+5 1.09 1.58 2.00 2.40 2.83 3.32 3.91
34+6 1.12 1.62 2.04 2.43 2.86 3.35 3.94
35+0 1.16 1.65 2.07 2.47 2.90 3.38 3.97
35+1 1.19 1.69 2.10 2.50 2.93 3.42 4.00
35+2 1.23 1.72 2.14 2.53 2.96 3.45 4.04
35+3 1.26 1.75 2.17 2.57 3.00 3.48 4.07
35+4 1.29 1.78 2.20 2.60 3.03 3.51 4.10
35+5 1.32 1.82 2.23 2.63 3.06 3.54 4.13
35+6 1.36 1.85 2.26 2.66 3.09 3.57 4.16
36+0 1.39 1.88 2.29 2.69 3.12 3.60 4.19
36+1 1.42 1.91 2.33 2.72 3.15 3.63 4.22
36+2 1.45 1.94 2.36 2.75 3.18 3.66 4.25
36+3 1.48 1.97 2.38 2.78 3.21 3.69 4.28
36+4 1.51 2.00 2.41 2.81 3.24 3.72 4.30
36+5 1.54 2.03 2.44 2.84 3.26 3.75 4.33
36+6 1.57 2.06 2.47 2.87 3.29 3.78 4.36
37+0 1.59 2.08 2.50 2.89 3.32 3.80 4.39
37+1 1.62 2.11 2.53 2.92 3.35 3.83 4.41
37+2 1.65 2.14 2.55 2.95 3.37 3.86 4.44
37+3 1.68 2.17 2.58 2.97 3.40 3.88 4.46
37+4 1.70 2.19 2.61 3.00 3.43 3.91 4.49
37+5 1.73 2.22 2.63 3.03 3.45 3.93 4.51
37+6 1.76 2.24 2.66 3.05 3.48 3.96 4.54
38+0 1.78 2.27 2.68 3.08 3.50 3.98 4.56
38+1 1.81 2.29 2.71 3.10 3.53 4.01 4.59
38+2 1.83 2.32 2.73 3.12 3.55 4.03 4.61
38+3 1.86 2.34 2.76 3.15 3.57 4.05 4.63
38+4 1.88 2.37 2.78 3.17 3.60 4.08 4.66
38+5 1.90 2.39 2.80 3.19 3.62 4.10 4.68
38+6 1.93 2.41 2.82 3.22 3.64 4.12 4.70
39+0 1.95 2.43 2.85 3.24 3.66 4.14 4.72
39+1 1.97 2.46 2.87 3.26 3.68 4.16 4.74
39+2 1.99 2.48 2.89 3.28 3.71 4.19 4.76
39+3 2.01 2.50 2.91 3.30 3.73 4.21 4.78
39+4 2.04 2.52 2.93 3.32 3.75 4.23 4.80
39+5 2.06 2.54 2.95 3.34 3.77 4.25 4.82
39+6 2.08 2.56 2.97 3.36 3.79 4.27 4.84
40+0 2.10 2.58 2.99 3.38 3.81 4.29 4.86
40+1 2.12 2.60 3.01 3.40 3.83 4.30 4.88
40+2 2.14 2.62 3.03 3.42 3.85 4.32 4.90
40+3 2.16 2.64 3.05 3.44 3.86 4.34 4.92
40+4 2.17 2.66 3.07 3.46 3.88 4.36 4.94
40+5 2.19 2.68 3.09 3.48 3.90 4.38 4.95
40+6 2.21 2.70 3.10 3.49 3.92 4.39 4.97
41+0 2.23 2.71 3.12 3.51 3.93 4.41 4.99
41+1 2.25 2.73 3.14 3.53 3.95 4.43 5.00
41+2 2.26 2.75 3.16 3.55 3.97 4.44 5.02
41+3 2.28 2.76 3.17 3.56 3.98 4.46 5.04
41+4 2.30 2.78 3.19 3.58 4.00 4.48 5.05
41+5 2.31 2.80 3.20 3.59 4.02 4.49 5.07
41+6 2.33 2.81 3.22 3.61 4.03 4.51 5.08
42+0 2.34 2.83 3.24 3.62 4.05 4.52 5.10
42+1 2.36 2.84 3.25 3.64 4.06 4.54 5.11
42+2 2.37 2.86 3.26 3.65 4.07 4.55 5.12
42+3 2.39 2.87 3.28 3.67 4.09 4.56 5.14
42+4 2.40 2.88 3.29 3.68 4.10 4.58 5.15
42+5 2.42 2.90 3.31 3.69 4.11 4.59 5.16
42+6 2.43 2.91 3.32 3.71 4.13 4.60 5.18
"""

Z_GIRLS_33_42 = """
33+0 0.75 1.15 1.50 1.85 2.23 2.66 3.16
33+1 0.79 1.19 1.55 1.89 2.27 2.70 3.21
33+2 0.83 1.23 1.59 1.93 2.31 2.74 3.25
33+3 0.86 1.27 1.62 1.97 2.35 2.78 3.29
33+4 0.90 1.31 1.66 2.01 2.39 2.83 3.34
33+5 0.94 1.35 1.70 2.05 2.43 2.87 3.38
33+6 0.97 1.38 1.74 2.09 2.47 2.91 3.42
34+0 1.01 1.42 1.78 2.13 2.51 2.95 3.46
34+1 1.04 1.46 1.81 2.16 2.55 2.99 3.50
34+2 1.08 1.49 1.85 2.20 2.59 3.03 3.54
34+3 1.11 1.53 1.89 2.24 2.63 3.06 3.58
34+4 1.15 1.56 1.92 2.27 2.66 3.10 3.62
34+5 1.18 1.59 1.95 2.31 2.70 3.14 3.66
34+6 1.21 1.63 1.99 2.34 2.73 3.17 3.70
35+0 1.24 1.66 2.02 2.38 2.77 3.21 3.73
35+1 1.27 1.69 2.05 2.41 2.80 3.24 3.77
35+2 1.31 1.72 2.09 2.44 2.84 3.28 3.80
35+3 1.34 1.75 2.12 2.48 2.87 3.31 3.84
35+4 1.37 1.78 2.15 2.51 2.90 3.35 3.87
35+5 1.39 1.81 2.18 2.54 2.93 3.38 3.91
35+6 1.42 1.84 2.21 2.57 2.97 3.41 3.94
36+0 1.45 1.87 2.24 2.60 3.00 3.45 3.97
36+1 1.48 1.90 2.27 2.63 3.03 3.48 4.01
36+2 1.51 1.93 2.30 2.66 3.06 3.51 4.04
36+3 1.53 1.96 2.33 2.69 3.09 3.54 4.07
36+4 1.56 1.99 2.36 2.72 3.12 3.57 4.10
36+5 1.59 2.01 2.38 2.74 3.15 3.60 4.13
36+6 1.61 2.04 2.41 2.77 3.17 3.63 4.16
37+0 1.64 2.06 2.44 2.80 3.20 3.65 4.19
37+1 1.66 2.09 2.46 2.83 3.23 3.68 4.22
37+2 1.68 2.11 2.49 2.85 3.26 3.71 4.25
37+3 1.71 2.14 2.51 2.88 3.28 3.74 4.28
37+4 1.73 2.16 2.54 2.90 3.31 3.76 4.30
37+5 1.75 2.19 2.56 2.93 3.33 3.79 4.33
37+6 1.78 2.21 2.58 2.95 3.36 3.82 4.36
38+0 1.80 2.23 2.61 2.97 3.38 3.84 4.38
38+1 1.82 2.25 2.63 3.00 3.41 3.86 4.41
38+2 1.84 2.27 2.65 3.02 3.43 3.89 4.43
38+3 1.86 2.30 2.67 3.04 3.45 3.91 4.46
38+4 1.88 2.32 2.69 3.06 3.47 3.94 4.48
38+5 1.90 2.34 2.72 3.09 3.50 3.96 4.51
38+6 1.92 2.36 2.74 3.11 3.52 3.98 4.53
39+0 1.94 2.38 2.76 3.13 3.54 4.00 4.55
39+1 1.96 2.40 2.78 3.15 3.56 4.02 4.57
39+2 1.98 2.41 2.80 3.17 3.58 4.05 4.59
39+3 1.99 2.43 2.81 3.19 3.60 4.07 4.62
39+4 2.01 2.45 2.83 3.21 3.62 4.09 4.64
39+5 2.03 2.47 2.85 3.22 3.64 4.11 4.66
39+6 2.04 2.48 2.87 3.24 3.66 4.12 4.68
40+0 2.06 2.50 2.88 3.26 3.68 4.14 4.70
40+1 2.08 2.52 2.90 3.28 3.69 4.16 4.72
40+2 2.09 2.53 2.92 3.29 3.71 4.18 4.73
40+3 2.11 2.55 2.93 3.31 3.73 4.20 4.75
40+4 2.12 2.56 2.95 3.33 3.74 4.21 4.77
40+5 2.13 2.58 2.96 3.34 3.76 4.23 4.79
40+6 2.15 2.59 2.98 3.36 3.78 4.25 4.81
41+0 2.16 2.61 2.99 3.37 3.79 4.26 4.82
41+1 2.17 2.62 3.01 3.39 3.81 4.28 4.84
41+2 2.19 2.63 3.02 3.40 3.82 4.29 4.85
41+3 2.20 2.64 3.03 3.41 3.83 4.31 4.87
41+4 2.21 2.66 3.05 3.43 3.85 4.32 4.88
41+5 2.22 2.67 3.06 3.44 3.86 4.34 4.90
41+6 2.23 2.68 3.07 3.45 3.87 4.35 4.91
42+0 2.24 2.69 3.08 3.46 3.89 4.36 4.93
42+1 2.25 2.70 3.09 3.48 3.90 4.38 4.94
42+2 2.26 2.71 3.10 3.49 3.91 4.39 4.95
42+3 2.27 2.72 3.12 3.50 3.92 4.40 4.97
42+4 2.28 2.73 3.13 3.51 3.93 4.41 4.98
42+5 2.29 2.74 3.14 3.52 3.94 4.42 4.99
42+6 2.30 2.75 3.14 3.53 3.96 4.43 5.00
"""


def carregar_tabela_z(texto):
    tabela = {}
    for linha in texto.strip().splitlines():
        partes = linha.split()
        if len(partes) != 8:
            continue
        ig = partes[0]
        valores = [float(x) for x in partes[1:]]
        tabela[ig] = {
            -3: valores[0],
            -2: valores[1],
            -1: valores[2],
            0: valores[3],
            1: valores[4],
            2: valores[5],
            3: valores[6],
        }
    return tabela


def combinar_tabelas(*tabelas):
    final = {}
    for t in tabelas:
        final.update(t)
    return final


TABELA_Z = {
    "M": combinar_tabelas(carregar_tabela_z(Z_BOYS_24_32), carregar_tabela_z(Z_BOYS_33_42)),
    "F": combinar_tabelas(carregar_tabela_z(Z_GIRLS_24_32), carregar_tabela_z(Z_GIRLS_33_42)),
}

ZS = [-3, -2, -1, 0, 1, 2, 3]


# ============================================================
# FORMATAÇÃO
# ============================================================

def titulo_nome(nome):
    if not nome:
        return ""

    minusculas = {"de", "da", "do", "das", "dos", "e"}
    palavras = nome.strip().lower().split()
    final = []

    for p in palavras:
        if p in minusculas:
            final.append(p)
        else:
            final.append(p.capitalize())

    return " ".join(final)


def normalizar_rh(valor):
    if not valor:
        return None

    v = valor.strip().lower()

    if "positivo" in v or v == "+":
        return "+"

    if "negativo" in v or v == "-":
        return "-"

    return None


def formatar_tipo(abo, rh):
    if not abo:
        return "desconhecido"

    if not rh:
        return abo

    return f"{abo}{rh}"


def formatar_ig(semanas, dias):
    return f"{semanas}+{dias}"


def formatar_numero(valor):
    if valor is None:
        return ""

    try:
        return f"{float(valor):.1f}"
    except Exception:
        return str(valor)


def formatar_btc(valor):
    if valor is None:
        return "__"
    return f"{float(valor):.1f}"


# ============================================================
# EXTRAÇÃO DO PRONTUÁRIO E ENTRADA SIMPLIFICADA
# ============================================================

ROTULOS_ESTRUTURADOS = {
    "leito": {"leito", "quarto leito", "numero do leito", "n do leito"},
    "nome": {"nome", "nome rn", "rn", "paciente", "mae", "mãe"},
    "nascimento": {"nascimento", "data hora nascimento", "data e hora nascimento", "data-hora nascimento"},
    "data_nasc": {"data nascimento", "data de nascimento", "data nasc"},
    "hora_nasc": {"hora nascimento", "hora de nascimento", "hora nasc"},
    "sexo": {"sexo"},
    "ig": {"ig", "idade gestacional", "semanas gestacao", "semanas gestação"},
    "peso_nascimento": {"pn", "peso nascimento", "peso de nascimento", "peso ao nascer"},
    "peso_atual": {"pa", "peso atual", "ultimo peso", "último peso", "peso mais recente"},
    "data_peso_atual": {"data peso atual", "data do peso atual", "data ultima afericao", "data última aferição"},
    "hora_peso_atual": {"hora peso atual", "hora do peso atual", "hora ultima afericao", "hora última aferição"},
    "data_hora_peso_atual": {
        "data hora peso atual", "data e hora peso atual", "afericao peso atual", "aferição peso atual",
        "data hora ultima afericao", "data hora última aferição"
    },
    "tipo_parto": {"parto", "tipo parto", "tipo de parto", "tipo obstetricia", "tipo obstetrícia"},
    "apgar": {"apgar"},
    "apgar1": {"apgar 1", "apgar 1 min", "apgar 1o min", "apgar 1º min"},
    "apgar5": {"apgar 5", "apgar 5 min", "apgar 5o min", "apgar 5º min"},
    "tsm": {"tsm", "tipo sanguineo mae", "tipo sanguíneo mãe", "abo rh mae", "abo rh mãe"},
    "tsrn": {"tsrn", "tipo sanguineo rn", "tipo sanguíneo rn", "abo rh rn"},
    "abo_mae": {"abo mae", "abo mãe"},
    "rh_mae": {"rh mae", "rh mãe", "fator rh mae", "fator rh mãe"},
    "abo_rn": {"abo rn"},
    "rh_rn": {"rh rn", "fator rh rn"},
    "ci": {"ci", "coombs", "coombs direto", "coombs indireto"},
    "btc": {"btc", "bilirrubina total", "bilirrubina"},
    "observacao_manual": {"obs", "observacao", "observação"},
}


def _sem_acentos(texto):
    return "".join(
        ch for ch in unicodedata.normalize("NFD", str(texto or ""))
        if unicodedata.category(ch) != "Mn"
    )


def normalizar_rotulo(rotulo):
    r = _sem_acentos(rotulo).strip().lower()
    r = re.sub(r"[^a-z0-9]+", " ", r)
    return re.sub(r"\s+", " ", r).strip()


ROTULO_PARA_CAMPO = {}
for campo, aliases in ROTULOS_ESTRUTURADOS.items():
    for alias in aliases:
        ROTULO_PARA_CAMPO[normalizar_rotulo(alias)] = campo


def dividir_blocos(texto):
    texto = texto.strip()

    if re.search(r"Prontuário do RN", texto, flags=re.IGNORECASE):
        partes = re.split(r"(?=Prontuário do RN)", texto, flags=re.IGNORECASE)
        return [p.strip() for p in partes if p.strip().lower().startswith("prontuário do rn")]

    if re.search(r"\bMãe\s*:", texto, flags=re.IGNORECASE):
        partes = re.split(r"(?=\bMãe\s*:)", texto, flags=re.IGNORECASE)
        return [p.strip() for p in partes if p.strip().lower().startswith("mãe")]

    return []


def extrair_apos_rotulo(bloco, rotulo):
    linhas = bloco.splitlines()
    alvo = rotulo.lower().strip()

    for i, linha in enumerate(linhas):
        linha_limpa = linha.strip()
        linha_lower = linha_limpa.lower()

        if linha_lower.startswith(alvo + ":"):
            resto = linha_limpa.split(":", 1)[1].strip()

            if resto:
                return resto

            for j in range(i + 1, len(linhas)):
                prox = linhas[j].strip()
                if prox:
                    return prox

    return None


def extrair_campo_linha(bloco, rotulo):
    linhas = bloco.splitlines()
    alvo = rotulo.lower().strip()

    for linha in linhas:
        linha_limpa = linha.strip()
        linha_lower = linha_limpa.lower()

        if alvo in linha_lower:
            idx = linha_lower.find(alvo)
            resto = linha_limpa[idx + len(rotulo):].strip(" \t:-")
            if not resto:
                return None
            return resto.strip()

    return None


def extrair_nome_mae(bloco):
    nome_rn = extrair_apos_rotulo(bloco, "Nome RN")

    if nome_rn:
        nome = re.sub(r"^RN\s+de\s+", "", nome_rn, flags=re.IGNORECASE).strip()
        return titulo_nome(nome)

    m = re.search(r"\d+\s*-\s*RN DE\s+(.+?)\s+\(", bloco, flags=re.IGNORECASE)
    if m:
        return titulo_nome(m.group(1))

    mae = extrair_apos_rotulo(bloco, "Mãe")
    if mae:
        mae = re.sub(r"^\d+\s*-\s*", "", mae).strip()
        return titulo_nome(mae)

    return ""


def extrair_data_hora(bloco):
    data = extrair_apos_rotulo(bloco, "Data")
    hora = extrair_apos_rotulo(bloco, "Hora")

    if data and hora:
        return data, hora

    data_hora = extrair_apos_rotulo(bloco, "Data - Hora")
    if data_hora:
        m = re.search(r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})", data_hora)
        if m:
            return m.group(1), m.group(2)

    return data, hora


def parse_data_hora(valor):
    if not valor:
        return None, None
    m = re.search(r"(\d{1,2}/\d{1,2}/\d{2,4})\D+(\d{1,2}:\d{2})", str(valor))
    if not m:
        return None, None
    data = normalizar_data(m.group(1))
    hora = normalizar_hora(m.group(2))
    return data, hora


def normalizar_data(valor):
    if not valor:
        return None
    texto = str(valor).strip()
    for formato in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(texto, formato).strftime("%d/%m/%Y")
        except ValueError:
            pass
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", texto)
    if m:
        d, mes, ano = m.groups()
        if len(ano) == 2:
            ano = "20" + ano
        try:
            return datetime(int(ano), int(mes), int(d)).strftime("%d/%m/%Y")
        except ValueError:
            return texto
    return texto


def normalizar_hora(valor):
    if not valor:
        return None
    texto = str(valor).strip()
    m = re.search(r"(\d{1,2}):(\d{2})", texto)
    if not m:
        return texto
    h, minuto = int(m.group(1)), int(m.group(2))
    if 0 <= h <= 23 and 0 <= minuto <= 59:
        return f"{h:02d}:{minuto:02d}"
    return texto


def extrair_ig(bloco):
    valor = extrair_apos_rotulo(bloco, "Semanas gestacao")
    return parse_ig_valor(valor)


def parse_ig_valor(valor):
    if not valor:
        return None, None

    texto = _sem_acentos(str(valor)).lower().strip()
    padroes = [
        r"\b(\d{2})\s*[+]\s*([0-6])\b",
        r"\b(\d{2})\s*s(?:em(?:anas?)?)?\s*([0-6])\s*d(?:ias?)?\b",
        r"\b(\d{2})\s*(?:semanas?|sem)\s*(?:e|\+)?\s*([0-6])?\s*(?:dias?|d)?\b",
        r"\b(\d{2})\s*e\s*([0-6])\s*dia",
        r"\b(\d{2})\b",
    ]
    for padrao in padroes:
        m = re.search(padrao, texto, flags=re.IGNORECASE)
        if m:
            semanas = int(m.group(1))
            dias = int(m.group(2)) if m.lastindex and m.lastindex >= 2 and m.group(2) else 0
            return semanas, dias
    return None, None


def parse_peso_g(valor):
    if valor in (None, ""):
        return None
    texto = str(valor).strip().lower().replace(" ", "")
    m = re.search(r"-?[\d.,]+", texto)
    if not m:
        return None
    bruto = m.group(0)
    if "," in bruto and "." in bruto:
        if bruto.rfind(",") > bruto.rfind("."):
            bruto = bruto.replace(".", "").replace(",", ".")
        else:
            bruto = bruto.replace(",", "")
    else:
        bruto = bruto.replace(",", ".")
    try:
        numero = float(bruto)
    except ValueError:
        return None
    if "kg" in texto or abs(numero) < 20:
        numero *= 1000
    if numero <= 0:
        return None
    return int(round(numero))


def extrair_peso_g(bloco):
    return parse_peso_g(extrair_apos_rotulo(bloco, "Peso"))


def extrair_abo_mae(bloco):
    valor = extrair_campo_linha(bloco, "ABO RH - Mãe")
    return parse_tipo_sanguineo(valor)[0] if valor else None


def extrair_rh_mae(bloco):
    valor = extrair_campo_linha(bloco, "Fator RH - Mãe")
    return normalizar_rh(valor) if valor else None


def extrair_abo_rn(bloco):
    valor = extrair_campo_linha(bloco, "ABO RH - RN")
    return parse_tipo_sanguineo(valor)[0] if valor else None


def extrair_rh_rn(bloco):
    valor = extrair_campo_linha(bloco, "Fator RH - RN")
    return normalizar_rh(valor) if valor else None


def parse_tipo_sanguineo(valor):
    if not valor:
        return None, None
    texto = _sem_acentos(str(valor)).upper().strip()
    m_abo = re.search(r"\b(AB|A|B|O)\b", texto)
    abo = m_abo.group(1) if m_abo else None
    rh = None
    if re.search(r"POSITIV|\+", texto):
        rh = "+"
    elif re.search(r"NEGATIV|\-", texto):
        rh = "-"
    return abo, rh


def extrair_leito_bruto(bloco):
    for rotulo in ("Leito", "Quarto/Leito", "Nº Leito", "N° Leito"):
        valor = extrair_apos_rotulo(bloco, rotulo)
        if valor:
            return str(valor).strip()
    m = re.search(r"\bLEITO\s*[:#-]?\s*([A-Za-z0-9./_-]+)", bloco, flags=re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extrair_peso_atual_bruto(bloco):
    for rotulo in ("Peso atual", "Último peso", "Ultimo peso", "Peso mais recente"):
        valor = extrair_apos_rotulo(bloco, rotulo)
        if valor:
            return parse_peso_g(valor)
    return None


def parse_prontuarios(texto):
    blocos = dividir_blocos(texto)
    pacientes = []

    for bloco in blocos:
        data_nasc, hora_nasc = extrair_data_hora(bloco)
        semanas, dias = extrair_ig(bloco)
        paciente = {
            "leito": extrair_leito_bruto(bloco),
            "nome": extrair_nome_mae(bloco),
            "data_nasc": normalizar_data(data_nasc),
            "hora_nasc": normalizar_hora(hora_nasc),
            "tipo_parto": extrair_apos_rotulo(bloco, "Tipo obstetricia"),
            "sexo": extrair_apos_rotulo(bloco, "Sexo"),
            "ig_sem": semanas,
            "ig_dias": dias,
            "peso_g": extrair_peso_g(bloco),
            "peso_atual_g": extrair_peso_atual_bruto(bloco),
            "data_peso_atual": None,
            "hora_peso_atual": None,
            "apgar1": extrair_apos_rotulo(bloco, "Apgar 1º min"),
            "apgar5": extrair_apos_rotulo(bloco, "Apgar 5º min"),
            "abo_mae": extrair_abo_mae(bloco),
            "rh_mae": extrair_rh_mae(bloco),
            "abo_rn": extrair_abo_rn(bloco),
            "rh_rn": extrair_rh_rn(bloco),
            "ci": extrair_apos_rotulo(bloco, "Coombs") or "",
            "btc_entrada": None,
            "observacao_manual": "",
            "formato_origem": "prontuario_bruto",
            "bloco": bloco,
        }
        pacientes.append(paciente)

    return pacientes


def parece_entrada_simplificada(texto):
    normalizado = _sem_acentos(texto).lower()
    if "prontuario do rn" in normalizado:
        return False
    marcadores = 0
    for rotulo in ("leito:", "nome:", "nascimento:", "ig:", "pn:", "tsm:", "tsrn:"):
        if rotulo in normalizado:
            marcadores += 1
    return marcadores >= 3


def dividir_blocos_estruturados(texto):
    texto = texto.replace("\r\n", "\n").strip()
    if not texto:
        return []

    partes = re.split(r"(?m)^\s*(?:-{3,}|={3,}|\*{3,})\s*$", texto)
    partes = [p.strip() for p in partes if p.strip()]
    if len(partes) > 1:
        return partes

    inicios_leito = list(re.finditer(r"(?mi)^\s*LEITO\s*[:=]", texto))
    if len(inicios_leito) > 1:
        cortes = [m.start() for m in inicios_leito] + [len(texto)]
        return [texto[cortes[i]:cortes[i + 1]].strip() for i in range(len(cortes) - 1)]

    inicios_nome = list(re.finditer(r"(?mi)^\s*(?:NOME(?:\s+RN)?|PACIENTE)\s*[:=]", texto))
    if len(inicios_nome) > 1:
        cortes = [m.start() for m in inicios_nome] + [len(texto)]
        return [texto[cortes[i]:cortes[i + 1]].strip() for i in range(len(cortes) - 1)]

    return [texto]


def campos_estruturados(bloco):
    campos = {}
    for linha in bloco.splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        m = re.match(r"^\s*([^:=]+?)\s*[:=]\s*(.*?)\s*$", linha)
        if not m:
            continue
        rotulo, valor = m.group(1), m.group(2)
        campo = ROTULO_PARA_CAMPO.get(normalizar_rotulo(rotulo))
        if campo:
            campos[campo] = valor.strip()
    return campos


def parse_entrada_simplificada(texto):
    pacientes = []
    for bloco in dividir_blocos_estruturados(texto):
        c = campos_estruturados(bloco)
        if not c:
            continue

        data_nasc, hora_nasc = parse_data_hora(c.get("nascimento"))
        data_nasc = normalizar_data(c.get("data_nasc")) or data_nasc
        hora_nasc = normalizar_hora(c.get("hora_nasc")) or hora_nasc
        ig_sem, ig_dias = parse_ig_valor(c.get("ig"))

        apgar1, apgar5 = c.get("apgar1"), c.get("apgar5")
        if c.get("apgar"):
            m_apgar = re.search(r"(\d{1,2})\s*[/|-]\s*(\d{1,2})", c["apgar"])
            if m_apgar:
                apgar1 = apgar1 or m_apgar.group(1)
                apgar5 = apgar5 or m_apgar.group(2)

        abo_mae, rh_mae = parse_tipo_sanguineo(c.get("tsm"))
        abo_rn, rh_rn = parse_tipo_sanguineo(c.get("tsrn"))
        abo_mae = parse_tipo_sanguineo(c.get("abo_mae"))[0] or abo_mae
        rh_mae = normalizar_rh(c.get("rh_mae")) or parse_tipo_sanguineo(c.get("rh_mae"))[1] or rh_mae
        abo_rn = parse_tipo_sanguineo(c.get("abo_rn"))[0] or abo_rn
        rh_rn = normalizar_rh(c.get("rh_rn")) or parse_tipo_sanguineo(c.get("rh_rn"))[1] or rh_rn

        data_pa, hora_pa = parse_data_hora(c.get("data_hora_peso_atual"))
        data_pa = normalizar_data(c.get("data_peso_atual")) or data_pa
        hora_pa = normalizar_hora(c.get("hora_peso_atual")) or hora_pa

        nome = re.sub(r"^RN\s+de\s+", "", c.get("nome", ""), flags=re.IGNORECASE).strip()
        paciente = {
            "leito": c.get("leito", "").strip(),
            "nome": titulo_nome(nome),
            "data_nasc": data_nasc,
            "hora_nasc": hora_nasc,
            "tipo_parto": c.get("tipo_parto") or "",
            "sexo": c.get("sexo") or "",
            "ig_sem": ig_sem,
            "ig_dias": ig_dias,
            "peso_g": parse_peso_g(c.get("peso_nascimento")),
            "peso_atual_g": parse_peso_g(c.get("peso_atual")),
            "data_peso_atual": data_pa,
            "hora_peso_atual": hora_pa,
            "apgar1": apgar1,
            "apgar5": apgar5,
            "abo_mae": abo_mae,
            "rh_mae": rh_mae,
            "abo_rn": abo_rn,
            "rh_rn": rh_rn,
            "ci": c.get("ci") or "",
            "btc_entrada": parse_decimal(c.get("btc")),
            "observacao_manual": c.get("observacao_manual") or "",
            "formato_origem": "entrada_simplificada",
            "bloco": bloco,
        }
        pacientes.append(paciente)
    return pacientes


def parse_decimal(valor):
    if valor in (None, ""):
        return None
    m = re.search(r"-?[\d.,]+", str(valor))
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", "."))
    except ValueError:
        return None


def parse_entrada(texto, modo="automatico"):
    modo = (modo or "automatico").strip().lower()
    if modo == "simplificado":
        return parse_entrada_simplificada(texto)
    if modo == "bruto":
        return parse_prontuarios(texto)

    if parece_entrada_simplificada(texto):
        pacientes = parse_entrada_simplificada(texto)
        if pacientes:
            return pacientes
    return parse_prontuarios(texto)

# ============================================================
# REGRAS OPERACIONAIS
# ============================================================

def calcular_hv(data_nasc, hora_nasc, data_avaliacao, hora_avaliacao):
    nascimento = datetime.strptime(f"{data_nasc} {hora_nasc}", "%d/%m/%Y %H:%M")
    avaliacao = datetime.strptime(f"{data_avaliacao} {hora_avaliacao}", "%d/%m/%Y %H:%M")

    horas = (avaliacao - nascimento).total_seconds() / 3600

    return round(horas)


def definir_neuro(abo_mae, rh_mae, abo_rn, rh_rn):
    abo_mae = abo_mae.upper() if abo_mae else None
    abo_rn = abo_rn.upper() if abo_rn else None

    risco_abo = False
    risco_rh = False

    if abo_mae == "O":
        if not abo_rn:
            risco_abo = True
        elif abo_rn != "O":
            risco_abo = True

    if rh_mae == "-":
        if not rh_rn:
            risco_rh = True
        elif rh_rn == "+":
            risco_rh = True

    return risco_abo or risco_rh


def semanas_bilitool(ig_sem):
    """
    O BiliTool/AAP 2022 é aplicável para RN com IG >=35 semanas.
    Para IG >=40 semanas, o parâmetro aceito pelo BiliTool é 40.
    Retorna None quando não deve consultar o BiliTool.
    """
    if ig_sem is None:
        return None

    if ig_sem < BILITOOL_MIN_GA_SEMANAS:
        return None

    if ig_sem >= BILITOOL_MAX_GA_SEMANAS:
        return BILITOOL_MAX_GA_SEMANAS

    return ig_sem


def aplicar_arredondamento_ig_bilitool(ig_sem, ig_dias, modo_arredondamento):
    """
    Aplica arredondamento opcional apenas para o parâmetro gestationalWeeks
    enviado ao BiliTool. Não altera a IG original do prontuário, nem percentil,
    nem classificação gestacional.

    modo_arredondamento:
    - "nenhum" -> não arredonda
    - "6_dias" -> arredonda X+6 para X+1
    - "5_dias" -> arredonda X+5 e X+6 para X+1
    """
    if ig_sem is None:
        return None, False

    if ig_dias is None:
        ig_dias = 0

    semana_ajustada = ig_sem
    arredondou = False

    if modo_arredondamento == "6_dias" and ig_dias >= 6:
        semana_ajustada = ig_sem + 1
        arredondou = True
    elif modo_arredondamento == "5_dias" and ig_dias >= 5:
        semana_ajustada = ig_sem + 1
        arredondou = True

    return semana_ajustada, arredondou


def semanas_bilitool_ajustada(ig_sem, ig_dias, modo_arredondamento="nenhum"):
    semana_ajustada, arredondou = aplicar_arredondamento_ig_bilitool(
        ig_sem=ig_sem,
        ig_dias=ig_dias,
        modo_arredondamento=modo_arredondamento,
    )
    return semanas_bilitool(semana_ajustada), semana_ajustada, arredondou


def bilitool_aplicavel(ig_sem):
    return semanas_bilitool(ig_sem) is not None


def parse_btcs(texto):
    linhas = [x.strip().replace(",", ".") for x in texto.splitlines() if x.strip()]
    btcs = []

    for linha in linhas:
        try:
            btcs.append(float(linha))
        except ValueError:
            raise ValueError(f"BTC inválido: {linha}")

    return btcs


def sexo_abreviado(sexo):
    if not sexo:
        return ""

    s = sexo.strip().lower()

    if s.startswith("masc") or s == "m":
        return "M"

    if s.startswith("fem") or s == "f":
        return "F"

    return ""


def normal_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def percentil_txt_de_z(z):
    p = normal_cdf(z) * 100

    if p < 1:
        return "p<1", p

    if p > 99:
        return "p>99", p

    return f"p{int(round(p))}", p


def calcular_z_intergrowth(sexo, ig_sem, ig_dias, peso_g):
    sexo = sexo_abreviado(sexo)

    if not sexo or peso_g is None or ig_sem is None or ig_dias is None:
        return None, "", "", None

    chave = f"{ig_sem}+{ig_dias}"
    tabela = TABELA_Z.get(sexo, {})

    if chave not in tabela:
        return None, "", "", None

    peso_kg = peso_g / 1000
    linha = tabela[chave]

    if peso_kg <= linha[-3]:
        z = -3
    elif peso_kg >= linha[3]:
        z = 3
    else:
        z = None
        for z1, z2 in zip(ZS, ZS[1:]):
            p1 = linha[z1]
            p2 = linha[z2]

            if p1 <= peso_kg <= p2:
                if p2 == p1:
                    z = z1
                else:
                    frac = (peso_kg - p1) / (p2 - p1)
                    z = z1 + frac * (z2 - z1)
                break

    if z is None:
        return None, "", "", None

    percentil_txt, percentil_num = percentil_txt_de_z(z)

    if z < -1.2816:
        classificacao = "PIG"
    elif z > 1.2816:
        classificacao = "GIG"
    else:
        classificacao = "AIG"

    return z, percentil_txt, classificacao, percentil_num


def classificar_ig(ig_sem, ig_dias):
    if ig_sem is None or ig_dias is None:
        return ""

    dias_total = ig_sem * 7 + ig_dias

    if dias_total < 28 * 7:
        return "Pré-termo extremo"
    if dias_total <= 31 * 7 + 6:
        return "Muito pré-termo"
    if dias_total <= 33 * 7 + 6:
        return "Pré-termo moderado"
    if dias_total <= 36 * 7 + 6:
        return "Pré-termo tardio"
    if dias_total <= 38 * 7 + 6:
        return "Termo precoce"
    if dias_total <= 40 * 7 + 6:
        return "Termo pleno"
    if dias_total <= 41 * 7 + 6:
        return "Termo tardio"
    return "Pós-termo"


def resumo_rn(p, percentil_txt="", classificacao="", classe_ig=""):
    itens = []

    sexo = sexo_abreviado(p.get("sexo"))
    if sexo:
        itens.append(sexo)

    if p.get("peso_g"):
        peso = f"PN {p['peso_g']}g"
        if percentil_txt:
            peso += f" ({percentil_txt})"
        itens.append(peso)

    if classificacao:
        itens.append(classificacao)

    if classe_ig:
        itens.append(classe_ig)

    if p.get("tipo_parto"):
        itens.append(p["tipo_parto"])

    if p.get("apgar1") and p.get("apgar5"):
        itens.append(f"Apgar {p['apgar1']}/{p['apgar5']}")

    return " | ".join(itens)


# ============================================================
# LINKS E BILITOOL
# ============================================================

def gerar_link_bilitool(hv, btc, ig_sem_bilitool, neuro):
    if ig_sem_bilitool is None:
        return ""

    # Quando o usuário não informou BTC, enviamos 0.1 apenas para o BiliTool
    # devolver NC/NF. A saída do app continua exibindo BTC em branco.
    btc_para_link = btc if btc is not None else BTC_TECNICO_SEM_BTC

    params = {
        "ageHours": str(hv),
        "totalBilirubin": f"{btc_para_link:.1f}",
        "bilirubinUnits": "US",
        "gestationalWeeks": str(ig_sem_bilitool),
        "neuroRiskFactors": "Yes" if neuro else "No"
    }

    return BILITOOL_LINK_URL + "?" + urllib.parse.urlencode(params)


def extrair_threshold(texto, rotulo):
    padrao_com_decisao = rf"{rotulo}\?\s*(YES|NO)\s*\(([\d.]+)\s*mg/dL\)"
    m = re.search(padrao_com_decisao, texto, flags=re.IGNORECASE)

    if m:
        return m.group(1).upper(), float(m.group(2))

    padrao_sem_decisao = rf"{rotulo}\?.*?\(([\d.]+)\s*mg/dL\)"
    m = re.search(padrao_sem_decisao, texto, flags=re.IGNORECASE | re.S)

    if m:
        return None, float(m.group(1))

    return None, None


def consultar_bilitool_online(hv, btc, ig_sem_bilitool, neuro):
    if ig_sem_bilitool is None:
        raise ValueError("BiliTool não aplicável para IG <35 semanas.")

    url = gerar_link_bilitool(
        hv=hv,
        btc=btc,
        ig_sem_bilitool=ig_sem_bilitool,
        neuro=neuro
    )

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://emr.bilitool.org/",
            "Connection": "close"
        }
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        html_text = response.read().decode("utf-8", errors="ignore")

    m = re.search(
        r'<textarea[^>]*id="bar"[^>]*>(.*?)</textarea>',
        html_text,
        flags=re.S | re.I
    )

    if not m:
        raise ValueError("Não foi possível localizar o resumo do BiliTool no HTML.")

    resumo = m.group(1)

    decisao_nc, nc = extrair_threshold(resumo, r"Check serum bilirubin if using TcB")
    decisao_nf, nf = extrair_threshold(resumo, r"Phototherapy")
    decisao_ne, ne = extrair_threshold(resumo, r"Escalation of care")
    decisao_ext, ext = extrair_threshold(resumo, r"Exchange transfusion")

    return {
        "NC": nc,
        "NF": nf,
        "NE": ne,
        "EXT": ext,
        "coletar": decisao_nc == "YES" if decisao_nc is not None else None,
        "fototerapia": decisao_nf == "YES" if decisao_nf is not None else None,
        "escalonar": decisao_ne == "YES" if decisao_ne is not None else None,
        "exsanguineo": decisao_ext == "YES" if decisao_ext is not None else None,
        "resumo": resumo
    }

# ============================================================
# MODELO, CÁLCULOS DERIVADOS E SAÍDAS
# ============================================================

def calcular_perda_ponderal(peso_nascimento_g, peso_atual_g):
    if not peso_nascimento_g or not peso_atual_g or peso_nascimento_g <= 0:
        return None
    return ((peso_nascimento_g - peso_atual_g) / peso_nascimento_g) * 100


def formatar_percentual(valor):
    if valor is None:
        return ""
    return f"{abs(float(valor)):.2f}".replace(".", ",") + "%"


def montar_observacao_peso(p, percentil_txt="", classificacao=""):
    pn = p.get("peso_g")
    pa = p.get("peso_atual_g")
    partes = []

    if pn:
        trecho_pn = f"PN {int(pn)} g"
        complementos = [x for x in (percentil_txt, classificacao) if x]
        if complementos:
            trecho_pn += f" ({', '.join(complementos)})"
        partes.append(trecho_pn)
    else:
        partes.append("PN não informado")

    perda = calcular_perda_ponderal(pn, pa)
    if pa:
        momento = " ".join(x for x in (p.get("data_peso_atual"), p.get("hora_peso_atual")) if x)
        trecho_pa = f"PA {int(pa)} g"
        if momento:
            trecho_pa += f" ({momento})"
        partes.append(trecho_pa)
        if perda is not None:
            if perda >= 0:
                partes.append(f"perda {formatar_percentual(perda)}")
            else:
                partes.append(f"ganho {formatar_percentual(perda)}")

    if p.get("observacao_manual"):
        partes.append(str(p["observacao_manual"]).strip())

    return " | ".join(partes), perda


def validar_paciente_para_calculo(p, identificador=""):
    nomes = {
        "nome": "nome",
        "data_nasc": "data de nascimento",
        "hora_nasc": "hora de nascimento",
        "ig_sem": "idade gestacional",
        "ig_dias": "dias da idade gestacional",
        "abo_mae": "ABO materno",
        "rh_mae": "Rh materno",
    }
    faltantes = [rotulo for campo, rotulo in nomes.items() if p.get(campo) in (None, "")]
    if faltantes:
        prefixo = f"{identificador}: " if identificador else ""
        raise ValueError(prefixo + "campos faltantes: " + ", ".join(faltantes))


def montar_item(p, ordem, btc, data_avaliacao_str, hora_avaliacao, modo_arredondamento_bilitool="nenhum"):
    validar_paciente_para_calculo(p, p.get("nome") or f"Paciente {ordem}")

    hv = calcular_hv(p["data_nasc"], p["hora_nasc"], data_avaliacao_str, hora_avaliacao)
    if hv < 0:
        raise ValueError(f"{p.get('nome') or 'Paciente'}: nascimento posterior à avaliação.")

    neuro = definir_neuro(p.get("abo_mae"), p.get("rh_mae"), p.get("abo_rn"), p.get("rh_rn"))
    tsm = formatar_tipo(p.get("abo_mae"), p.get("rh_mae"))
    tsrn = formatar_tipo(p.get("abo_rn"), p.get("rh_rn"))
    ig = formatar_ig(p.get("ig_sem"), p.get("ig_dias"))

    z_score, percentil_txt, classificacao, percentil_num = calcular_z_intergrowth(
        sexo=p.get("sexo"),
        ig_sem=p.get("ig_sem"),
        ig_dias=p.get("ig_dias"),
        peso_g=p.get("peso_g"),
    )
    class_ig = classificar_ig(p.get("ig_sem"), p.get("ig_dias"))
    resumo = resumo_rn(p, percentil_txt=percentil_txt, classificacao=classificacao, classe_ig=class_ig)

    ig_sem_bilitool, ig_sem_ajustada_bilitool, ig_arredondada_bilitool = semanas_bilitool_ajustada(
        ig_sem=p.get("ig_sem"),
        ig_dias=p.get("ig_dias"),
        modo_arredondamento=modo_arredondamento_bilitool,
    )
    link = gerar_link_bilitool(
        hv=hv,
        btc=btc,
        ig_sem_bilitool=ig_sem_bilitool,
        neuro=neuro,
    )

    if ig_sem_bilitool is None:
        observacao_bilitool = "BiliTool não aplicável para IG <35s"
        ig_bilitool_txt = ""
    elif ig_arredondada_bilitool:
        observacao_bilitool = f"BiliTool: IG {ig_sem_bilitool}s por arredondamento de {ig}"
        ig_bilitool_txt = str(ig_sem_bilitool)
    else:
        observacao_bilitool = ""
        ig_bilitool_txt = str(ig_sem_bilitool)

    observacao_peso, perda_ponderal = montar_observacao_peso(
        p, percentil_txt=percentil_txt, classificacao=classificacao
    )
    observacao = " | ".join(x for x in (observacao_peso, observacao_bilitool) if x)

    return {
        "ordem": ordem,
        "leito": str(p.get("leito") or "").strip(),
        "paciente": p.get("nome") or "",
        "data_nasc": p.get("data_nasc"),
        "hora_nasc": p.get("hora_nasc"),
        "sexo": p.get("sexo") or "",
        "tipo_parto": p.get("tipo_parto") or "",
        "apgar1": p.get("apgar1"),
        "apgar5": p.get("apgar5"),
        "ci": p.get("ci") or "",
        "tsm": tsm,
        "tsrn": tsrn,
        "abo_mae": p.get("abo_mae"),
        "rh_mae": p.get("rh_mae"),
        "abo_rn": p.get("abo_rn"),
        "rh_rn": p.get("rh_rn"),
        "ig": ig,
        "ig_sem": p.get("ig_sem"),
        "ig_dias": p.get("ig_dias"),
        "peso_g": p.get("peso_g"),
        "peso_atual_g": p.get("peso_atual_g"),
        "data_peso_atual": p.get("data_peso_atual"),
        "hora_peso_atual": p.get("hora_peso_atual"),
        "perda_ponderal": perda_ponderal,
        "hv": hv,
        "neuro": neuro,
        "btc": btc,
        "z": z_score,
        "percentil": percentil_num,
        "percentil_txt": percentil_txt,
        "classificacao": classificacao,
        "classe_ig": class_ig,
        "ig_sem_bilitool": ig_sem_bilitool,
        "ig_sem_ajustada_bilitool": ig_sem_ajustada_bilitool,
        "ig_arredondada_bilitool": ig_arredondada_bilitool,
        "modo_arredondamento_bilitool": modo_arredondamento_bilitool,
        "ig_bilitool_txt": ig_bilitool_txt,
        "resumo": resumo,
        "link": link,
        "observacao_peso": observacao_peso,
        "observacao_bilitool": observacao_bilitool,
        "observacao": observacao,
        "paciente_obj": dict(p),
        "NC": None,
        "NF": None,
        "NE": None,
        "EXT": None,
        "coletar": None,
        "fototerapia": None,
        "escalonar": None,
        "exsanguineo": None,
    }


def resolver_btc_paciente(p, btc_externo=None):
    return btc_externo if btc_externo is not None else p.get("btc_entrada")


def identificador_item(item, para_impressao=False):
    leito = str(item.get("leito") or "").strip()
    if leito:
        return leito
    return "________" if para_impressao else ""


def item_para_linha_final(item):
    prefixo = f"Leito {item.get('leito')} | " if item.get("leito") else "Leito __ | "
    return (
        prefixo
        + f"{item['paciente']} | "
        + f"TSM {item['tsm']} | "
        + f"TSRN {item['tsrn']} | "
        + f"IG {item['ig']} | "
        + f"{item['hv']}hv | "
        + f"BTC {formatar_btc(item.get('btc'))} | "
        + f"NC {formatar_numero(item.get('NC')) or '__'} | "
        + f"NF {formatar_numero(item.get('NF')) or '__'}"
    )



def montar_observacao_complementar(item):
    p = item.get("paciente_obj") or {}
    partes = []

    pa = p.get("peso_atual_g")
    if pa:
        momento = " ".join(x for x in (p.get("data_peso_atual"), p.get("hora_peso_atual")) if x)
        trecho_pa = f"PA {int(pa)} g"
        if momento:
            trecho_pa += f" ({momento})"
        partes.append(trecho_pa)

        perda = item.get("perda_ponderal")
        if perda is not None:
            if perda >= 0:
                partes.append(f"perda {formatar_percentual(perda)}")
            else:
                partes.append(f"ganho {formatar_percentual(perda)}")

    observacao_manual = str(p.get("observacao_manual") or "").strip()
    if observacao_manual:
        partes.append(observacao_manual)

    observacao_bilitool = str(item.get("observacao_bilitool") or "").strip()
    if observacao_bilitool:
        partes.append(observacao_bilitool)

    return " | ".join(partes)


def montar_resumo_observacoes(item):
    partes = []
    resumo = str(item.get("resumo") or "").strip()
    if resumo:
        partes.append(resumo)

    complemento = montar_observacao_complementar(item)
    if complemento:
        partes.append(complemento)

    return " | ".join(partes)

def montar_saida_texto(dados):
    blocos = []
    for item in dados:
        bloco = item_para_linha_final(item)
        resumo_obs = montar_resumo_observacoes(item)
        if resumo_obs:
            bloco += f"\nResumo/observações: {resumo_obs}"
        blocos.append(bloco)
    return "\n\n".join(blocos)


def montar_linhas_tabela(dados):
    linhas = []
    for item in dados:
        linhas.append({
            "Leito": item.get("leito", ""),
            "Paciente": item.get("paciente"),
            "TSM": item.get("tsm"),
            "TSRN": item.get("tsrn"),
            "IG": item.get("ig"),
            "HV": item.get("hv"),
            "Neuro": "Sim" if item.get("neuro") else "Não",
            "BTC": formatar_btc(item.get("btc")),
            "NC": formatar_numero(item.get("NC")),
            "NF": formatar_numero(item.get("NF")),
            "Coletar?": "Sim" if item.get("coletar") else "Não" if item.get("coletar") is not None else "",
            "Foto?": "Sim" if item.get("fototerapia") else "Não" if item.get("fototerapia") is not None else "",
            "Cresc.": item.get("classificacao"),
            "Percentil": item.get("percentil_txt"),
            "Class. IG": item.get("classe_ig"),
            "Resumo/Observações RN": montar_resumo_observacoes(item),
            "Link": item.get("link"),
        })
    return linhas


def montar_html_impressao(dados, data_avaliacao, hora_avaliacao):
    linhas_html = ""
    for item in dados:
        resumo_obs = html.escape(montar_resumo_observacoes(item))
        linhas_html += f"""
        <tr>
            <td class="manual">{html.escape(identificador_item(item, para_impressao=True))}</td>
            <td>{html.escape(str(item.get('paciente', '')))}</td>
            <td>{html.escape(str(item.get('tsm', '')))}</td>
            <td>{html.escape(str(item.get('tsrn', '')))}</td>
            <td>{html.escape(str(item.get('ig', '')))}</td>
            <td>{html.escape(str(item.get('hv', '')))}hv</td>
            <td>{html.escape(str(item.get('classificacao', '')))}</td>
            <td>{html.escape(str(item.get('percentil_txt', '')))}</td>
            <td>{html.escape(str(item.get('classe_ig', '')))}</td>
            <td class="manual">________</td>
            <td>{html.escape(formatar_numero(item.get('NC')) or '__')}</td>
            <td>{html.escape(formatar_numero(item.get('NF')) or '__')}</td>
            <td class="resumo">{resumo_obs}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>BiliTool Rotina Neonatal</title>
        <style>
            @page {{ size: landscape; margin: 10mm; }}
            body {{ font-family: Arial, sans-serif; margin: 18px; font-size: 10px; }}
            h1 {{ font-size: 17px; margin-bottom: 4px; }}
            .sub {{ margin-bottom: 12px; color: #333; }}
            table {{ width: 100%; border-collapse: collapse; table-layout: auto; }}
            th, td {{ border: 1px solid #333; padding: 4px; text-align: center; vertical-align: middle; }}
            th {{ background: #eee; }}
            td:nth-child(2), td.resumo {{ text-align: left; }}
            td.resumo {{ min-width: 230px; }}
            .manual {{ font-size: 12px; font-weight: bold; white-space: nowrap; }}
            @media print {{ button {{ display: none; }} body {{ margin: 0; }} }}
        </style>
    </head>
    <body>
        <button onclick="window.print()">Imprimir</button>
        <h1>BiliTool - Rotina Neonatal</h1>
        <div class="sub">Avaliação: {html.escape(str(data_avaliacao))} às {html.escape(str(hora_avaliacao))}</div>
        <table>
            <thead>
                <tr>
                    <th>Leito</th><th>Paciente</th><th>TSM</th><th>TSRN</th><th>IG</th><th>HV</th>
                    <th>Cresc.</th><th>Percentil</th><th>Class. IG</th><th>BTC</th><th>NC</th><th>NF</th><th>Resumo / Observações</th>
                </tr>
            </thead>
            <tbody>{linhas_html}</tbody>
        </table>
    </body>
    </html>
    """

