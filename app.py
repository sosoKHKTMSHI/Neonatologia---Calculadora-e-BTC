import re
import csv
import time
import math
import html
import urllib.parse
import urllib.request
from datetime import datetime, date
from io import StringIO, BytesIO

import pandas as pd
import streamlit as st

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
# EXTRAÇÃO DO PRONTUÁRIO
# ============================================================

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


def extrair_ig(bloco):
    valor = extrair_apos_rotulo(bloco, "Semanas gestacao")

    if not valor:
        return None, None

    m = re.search(r"(\d{2})(?:\s*e\s*(\d+)\s*dia)?", valor, flags=re.IGNORECASE)

    if not m:
        return None, None

    semanas = int(m.group(1))
    dias = int(m.group(2)) if m.group(2) else 0

    return semanas, dias


def extrair_peso_g(bloco):
    peso = extrair_apos_rotulo(bloco, "Peso")

    if not peso:
        return None

    m = re.search(r"([\d.,]+)", peso)

    if not m:
        return None

    valor = m.group(1).replace(",", ".")

    try:
        numero = float(valor)

        if numero < 20:
            return int(round(numero * 1000))

        return int(round(numero))
    except ValueError:
        return None


def extrair_abo_mae(bloco):
    valor = extrair_campo_linha(bloco, "ABO RH - Mãe")

    if not valor:
        return None

    m = re.search(r"\b(AB|A|B|O)\b", valor, flags=re.IGNORECASE)

    return m.group(1).upper() if m else None


def extrair_rh_mae(bloco):
    valor = extrair_campo_linha(bloco, "Fator RH - Mãe")

    if not valor:
        return None

    return normalizar_rh(valor)


def extrair_abo_rn(bloco):
    valor = extrair_campo_linha(bloco, "ABO RH - RN")

    if not valor:
        return None

    m = re.search(r"\b(AB|A|B|O)\b", valor, flags=re.IGNORECASE)

    return m.group(1).upper() if m else None


def extrair_rh_rn(bloco):
    valor = extrair_campo_linha(bloco, "Fator RH - RN")

    if not valor:
        return None

    return normalizar_rh(valor)


def parse_prontuarios(texto):
    blocos = dividir_blocos(texto)
    pacientes = []

    for bloco in blocos:
        data_nasc, hora_nasc = extrair_data_hora(bloco)
        semanas, dias = extrair_ig(bloco)

        paciente = {
            "nome": extrair_nome_mae(bloco),
            "data_nasc": data_nasc,
            "hora_nasc": hora_nasc,
            "tipo_parto": extrair_apos_rotulo(bloco, "Tipo obstetricia"),
            "sexo": extrair_apos_rotulo(bloco, "Sexo"),
            "ig_sem": semanas,
            "ig_dias": dias,
            "peso_g": extrair_peso_g(bloco),
            "apgar1": extrair_apos_rotulo(bloco, "Apgar 1º min"),
            "apgar5": extrair_apos_rotulo(bloco, "Apgar 5º min"),
            "abo_mae": extrair_abo_mae(bloco),
            "rh_mae": extrair_rh_mae(bloco),
            "abo_rn": extrair_abo_rn(bloco),
            "rh_rn": extrair_rh_rn(bloco),
            "bloco": bloco
        }

        pacientes.append(paciente)

    return pacientes


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
# STREAMLIT UI
# ============================================================

st.set_page_config(
    page_title="BiliTool Rotina Neonatal",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("BiliTool - Rotina Neonatal")
st.caption("Extração de dados do prontuário, HV, percentil INTERGROWTH-21st, classificação gestacional e consulta ao BiliTool.")
st.info("BTC é opcional. Sem BTC, o app ainda calcula NC/NF; a decisão 'Coletar?/Foto?' fica em branco porque depende do BTC real.")


def montar_item(p, i, btc, data_avaliacao_str, hora_avaliacao, modo_arredondamento_bilitool="nenhum"):
    faltantes = []
    for campo in ["nome", "data_nasc", "hora_nasc", "ig_sem", "abo_mae", "rh_mae"]:
        if p.get(campo) in [None, ""]:
            faltantes.append(campo)

    if faltantes:
        raise ValueError(f"Paciente {i} com campos faltantes: {', '.join(faltantes)}")

    hv = calcular_hv(p["data_nasc"], p["hora_nasc"], data_avaliacao_str, hora_avaliacao)
    if hv < 0:
        raise ValueError(f"{p['nome']}: nascimento posterior à avaliação.")

    neuro = definir_neuro(p["abo_mae"], p["rh_mae"], p["abo_rn"], p["rh_rn"])
    tsm = formatar_tipo(p["abo_mae"], p["rh_mae"])
    tsrn = formatar_tipo(p["abo_rn"], p["rh_rn"])
    ig = formatar_ig(p["ig_sem"], p["ig_dias"])

    z_score, percentil_txt, classificacao, percentil_num = calcular_z_intergrowth(
        sexo=p.get("sexo"),
        ig_sem=p.get("ig_sem"),
        ig_dias=p.get("ig_dias"),
        peso_g=p.get("peso_g"),
    )
    class_ig = classificar_ig(p.get("ig_sem"), p.get("ig_dias"))
    resumo = resumo_rn(p, percentil_txt=percentil_txt, classificacao=classificacao, classe_ig=class_ig)

    ig_sem_bilitool, ig_sem_ajustada_bilitool, ig_arredondada_bilitool = semanas_bilitool_ajustada(
        ig_sem=p["ig_sem"],
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
        observacao = "BiliTool não aplicável para IG <35s"
    elif ig_arredondada_bilitool:
        observacao = f"BiliTool: IG {ig_sem_bilitool}s por arredondamento de {ig}"
    else:
        observacao = ""

    return {
        "ordem": i,
        "paciente": p["nome"],
        "tsm": tsm,
        "tsrn": tsrn,
        "ig": ig,
        "ig_sem": p["ig_sem"],
        "ig_dias": p["ig_dias"],
        "hv": hv,
        "neuro": neuro,
        "btc": btc,
        "percentil": percentil_num,
        "percentil_txt": percentil_txt,
        "classificacao": classificacao,
        "class_ig": class_ig,
        "ig_sem_bilitool": ig_sem_bilitool,
        "ig_sem_ajustada_bilitool": ig_sem_ajustada_bilitool,
        "ig_arredondada_bilitool": ig_arredondada_bilitool,
        "modo_arredondamento_bilitool": modo_arredondamento_bilitool,
        "resumo": resumo,
        "link": link,
        "observacao": observacao,
        "paciente_obj": p,
        "NC": None,
        "NF": None,
        "NE": None,
        "EXT": None,
        "coletar": None,
        "fototerapia": None,
        "escalonar": None,
        "exsanguineo": None,
    }


def item_para_linha_final(item):
    return (
        f"{item['paciente']} | "
        f"TSM {item['tsm']} | "
        f"TSRN {item['tsrn']} | "
        f"IG {item['ig']} | "
        f"{item['hv']}hv | "
        f"BTC {formatar_btc(item.get('btc'))} | "
        f"NC {formatar_numero(item.get('NC')) or '__'} | "
        f"NF {formatar_numero(item.get('NF')) or '__'}"
    )


def montar_saida_texto(dados):
    blocos = []
    for item in dados:
        bloco = item_para_linha_final(item)
        if item.get("resumo"):
            bloco += f"\nResumo: {item['resumo']}"
        blocos.append(bloco)
    return "\n\n".join(blocos)


def montar_dataframe(dados):
    linhas = []
    for item in dados:
        linhas.append({
            "#": item.get("ordem"),
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
            "Class. IG": item.get("class_ig"),
            "Resumo RN": item.get("resumo"),
            "Observação": item.get("observacao", ""),
            "Link": item.get("link"),
        })
    return pd.DataFrame(linhas)


def montar_csv(dados):
    df = montar_dataframe(dados)
    return df.to_csv(index=False, sep=";", encoding="utf-8-sig")


def montar_html_impressao(dados, data_avaliacao, hora_avaliacao):
    linhas_html = ""
    for item in dados:
        linhas_html += f"""
        <tr>
            <td>{html.escape(str(item.get('ordem', '')))}</td>
            <td>{html.escape(item.get('paciente', ''))}</td>
            <td>{html.escape(item.get('tsm', ''))}</td>
            <td>{html.escape(item.get('tsrn', ''))}</td>
            <td>{html.escape(item.get('ig', ''))}</td>
            <td>{html.escape(str(item.get('hv', '')))}hv</td>
            <td>{html.escape(item.get('classificacao', ''))}</td>
            <td>{html.escape(item.get('percentil_txt', ''))}</td>
            <td>{html.escape(item.get('class_ig', ''))}</td>
            <td class="btc">________</td>
            <td>{html.escape(formatar_numero(item.get('NC')) or '__')}</td>
            <td>{html.escape(formatar_numero(item.get('NF')) or '__')}</td>
            <td>{html.escape(item.get('resumo', ''))}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>BiliTool Rotina Neonatal</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 24px; font-size: 12px; }}
            h1 {{ font-size: 18px; margin-bottom: 4px; }}
            .sub {{ margin-bottom: 16px; color: #333; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #333; padding: 5px; text-align: center; vertical-align: middle; }}
            th {{ background: #eee; }}
            td:nth-child(2), td:nth-child(13) {{ text-align: left; }}
            .btc {{ font-size: 14px; font-weight: bold; }}
            @media print {{ button {{ display: none; }} }}
        </style>
    </head>
    <body>
        <button onclick="window.print()">Imprimir</button>
        <h1>BiliTool - Rotina Neonatal</h1>
        <div class="sub">Avaliação: {html.escape(data_avaliacao)} às {html.escape(hora_avaliacao)}</div>
        <table>
            <thead>
                <tr>
                    <th>#</th><th>Paciente</th><th>TSM</th><th>TSRN</th><th>IG</th><th>HV</th>
                    <th>Cresc.</th><th>Percentil</th><th>Class. IG</th><th>BTC</th><th>NC</th><th>NF</th><th>Resumo RN</th>
                </tr>
            </thead>
            <tbody>{linhas_html}</tbody>
        </table>
    </body>
    </html>
    """


if "dados_conferencia" not in st.session_state:
    st.session_state.dados_conferencia = []
if "dados_resultado" not in st.session_state:
    st.session_state.dados_resultado = []
if "links_gerados" not in st.session_state:
    st.session_state.links_gerados = ""

col_data, col_hora = st.columns([1, 1])
with col_data:
    data_avaliacao = st.date_input("Data avaliação", value=date.today(), format="DD/MM/YYYY")
with col_hora:
    hora_avaliacao = st.text_input("Hora", value="08:00")

data_avaliacao_str = data_avaliacao.strftime("%d/%m/%Y")

st.markdown("### Ajuste opcional para consulta ao BiliTool")
modo_arredondamento_label = st.radio(
    "Arredondar idade gestacional apenas para o BiliTool",
    options=[
        "Não arredondar",
        "Arredondar apenas 6 dias para a semana seguinte (ex.: 37+6 → 38)",
        "Arredondar 5 ou 6 dias para a semana seguinte (ex.: 37+5/37+6 → 38)",
    ],
    index=0,
    horizontal=False,
    help=(
        "Esse ajuste altera somente o parâmetro gestationalWeeks enviado ao BiliTool. "
        "A IG original do prontuário, o percentil INTERGROWTH e a classificação gestacional permanecem inalterados."
    ),
)

MAPA_MODO_ARREDONDAMENTO = {
    "Não arredondar": "nenhum",
    "Arredondar apenas 6 dias para a semana seguinte (ex.: 37+6 → 38)": "6_dias",
    "Arredondar 5 ou 6 dias para a semana seguinte (ex.: 37+5/37+6 → 38)": "5_dias",
}
modo_arredondamento_bilitool = MAPA_MODO_ARREDONDAMENTO[modo_arredondamento_label]

col1, col2 = st.columns([3, 1])
with col1:
    texto_prontuario = st.text_area("Cole aqui os prontuários", height=260)
with col2:
    texto_btcs = st.text_area("Cole aqui os BTCs, um por linha, na mesma ordem. Opcional.", height=260)

b1, b2, b3, b4 = st.columns([1, 1, 1, 1])

with b1:
    extrair = st.button("1) Extrair e conferir", type="primary")
with b2:
    gerar_links = st.button("2) Gerar links")
with b3:
    consultar = st.button("Consultar BiliTool online")
with b4:
    limpar = st.button("Limpar")

if limpar:
    st.session_state.dados_conferencia = []
    st.session_state.dados_resultado = []
    st.session_state.links_gerados = ""
    st.rerun()

if extrair:
    try:
        pacientes = parse_prontuarios(texto_prontuario)
        btcs = parse_btcs(texto_btcs)

        if not pacientes:
            st.error("Nenhum paciente identificado.")
        elif btcs and len(pacientes) != len(btcs):
            st.error(
                f"Foram identificados {len(pacientes)} pacientes, mas há {len(btcs)} BTCs. "
                "Se não quiser inserir BTC agora, deixe o campo de BTC vazio."
            )
        else:
            dados = []
            for i, p in enumerate(pacientes, start=1):
                btc = btcs[i - 1] if btcs else None
                dados.append(montar_item(
                    p,
                    i,
                    btc,
                    data_avaliacao_str,
                    hora_avaliacao,
                    modo_arredondamento_bilitool=modo_arredondamento_bilitool,
                ))

            st.session_state.dados_conferencia = dados
            st.session_state.dados_resultado = []
            st.session_state.links_gerados = ""
            st.success("Dados extraídos com sucesso.")
    except Exception as e:
        st.error(f"Erro: {e}")

if gerar_links:
    dados = st.session_state.dados_conferencia
    if not dados:
        st.warning("Primeiro clique em 'Extrair e conferir'.")
    else:
        st.session_state.links_gerados = "\n".join(
            f"{item['ordem']} | {item['paciente']} | {item['link'] or item.get('observacao', 'sem link')}"
            for item in dados
        )
        st.success("Links gerados.")

if consultar:
    dados = st.session_state.dados_conferencia
    if not dados:
        st.warning("Primeiro clique em 'Extrair e conferir'.")
    else:
        resultados = []
        barra = st.progress(0)
        try:
            for idx, item in enumerate(dados, start=1):
                ig_bt = item.get("ig_sem_bilitool")

                if ig_bt is None:
                    resultados.append({
                        **item,
                        "NC": None,
                        "NF": None,
                        "NE": None,
                        "EXT": None,
                        "coletar": None,
                        "fototerapia": None,
                        "escalonar": None,
                        "exsanguineo": None,
                        "observacao": item.get("observacao") or "BiliTool não aplicável para IG <35s",
                    })
                    barra.progress(idx / len(dados))
                    continue

                r = consultar_bilitool_online(
                    hv=item["hv"],
                    btc=item["btc"],
                    ig_sem_bilitool=ig_bt,
                    neuro=item["neuro"],
                )

                # Se não há BTC real, NC/NF são válidos, mas a decisão clínica
                # de coletar/fototerapia deve permanecer em branco.
                tem_btc_real = item.get("btc") is not None

                resultados.append({
                    **item,
                    "NC": r["NC"],
                    "NF": r["NF"],
                    "NE": r["NE"],
                    "EXT": r["EXT"],
                    "coletar": r["coletar"] if tem_btc_real else None,
                    "fototerapia": r["fototerapia"] if tem_btc_real else None,
                    "escalonar": r["escalonar"] if tem_btc_real else None,
                    "exsanguineo": r["exsanguineo"] if tem_btc_real else None,
                })
                barra.progress(idx / len(dados))
            st.session_state.dados_resultado = resultados
            st.success("Consulta ao BiliTool concluída.")
        except Exception as e:
            st.error(f"Não foi possível consultar o BiliTool automaticamente. Detalhe técnico: {e}")

dados_atuais = st.session_state.dados_resultado or st.session_state.dados_conferencia

st.subheader("Conferência / Resultado")
if dados_atuais:
    df = montar_dataframe(dados_atuais)
    st.dataframe(df.drop(columns=["Link"], errors="ignore"), use_container_width=True, hide_index=True)

    saida = montar_saida_texto(dados_atuais)
    st.subheader("Saída final")
    st.code(saida, language="text")
    st.text_area("Saída final para copiar", value=saida, height=180)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.download_button(
            "Baixar TXT",
            data=saida.encode("utf-8"),
            file_name="bilitool_saida.txt",
            mime="text/plain",
        )
    with c2:
        csv_data = montar_csv(dados_atuais)
        st.download_button(
            "Baixar CSV",
            data=csv_data.encode("utf-8-sig"),
            file_name="bilitool_saida.csv",
            mime="text/csv",
        )
    with c3:
        html_doc = montar_html_impressao(dados_atuais, data_avaliacao_str, hora_avaliacao)
        st.download_button(
            "Baixar HTML para imprimir",
            data=html_doc.encode("utf-8"),
            file_name="bilitool_impressao.html",
            mime="text/html",
        )
else:
    st.info("Cole os prontuários e clique em 'Extrair e conferir'.")

st.subheader("Links")
if st.session_state.links_gerados:
    st.text_area("Links gerados", value=st.session_state.links_gerados, height=160)
    st.download_button(
        "Baixar links TXT",
        data=st.session_state.links_gerados.encode("utf-8"),
        file_name="bilitool_links.txt",
        mime="text/plain",
    )
elif dados_atuais:
    st.caption("Clique em 'Gerar links' para exibir os links do BiliTool.")
