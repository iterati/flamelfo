from collections import defaultdict

flam3_nvariations = 99

VAR_LINEAR = 0
VAR_SINUSOIDAL =   1
VAR_SPHERICAL = 2
VAR_SWIRL =3
VAR_HORSESHOE  =4
VAR_POLAR =5
VAR_HANDKERCHIEF =6
VAR_HEART = 7
VAR_DISC = 8
VAR_SPIRAL = 9
VAR_HYPERBOLIC = 10
VAR_DIAMOND = 11
VAR_EX = 12
VAR_JULIA = 13
VAR_BENT = 14
VAR_WAVES = 15
VAR_FISHEYE = 16
VAR_POPCORN = 17
VAR_EXPONENTIAL = 18
VAR_POWER = 19
VAR_COSINE = 20
VAR_RINGS = 21
VAR_FAN = 22
VAR_BLOB = 23
VAR_PDJ = 24
VAR_FAN2 = 25
VAR_RINGS2 = 26
VAR_EYEFISH = 27
VAR_BUBBLE = 28
VAR_CYLINDER = 29
VAR_PERSPECTIVE = 30
VAR_NOISE = 31
VAR_JULIAN = 32
VAR_JULIASCOPE = 33
VAR_BLUR = 34
VAR_GAUSSIAN_BLUR = 35
VAR_RADIAL_BLUR = 36
VAR_PIE = 37
VAR_NGON = 38
VAR_CURL = 39
VAR_RECTANGLES = 40
VAR_ARCH = 41
VAR_TANGENT = 42
VAR_SQUARE = 43
VAR_RAYS = 44
VAR_BLADE = 45
VAR_SECANT2 = 46
VAR_TWINTRIAN = 47
VAR_CROSS = 48
VAR_DISC2 = 49
VAR_SUPER_SHAPE = 50
VAR_FLOWER = 51
VAR_CONIC = 52
VAR_PARABOLA = 53
VAR_BENT2 = 54
VAR_BIPOLAR = 55
VAR_BOARDERS = 56
VAR_BUTTERFLY = 57
VAR_CELL = 58
VAR_CPOW = 59
VAR_CURVE = 60
VAR_EDISC = 61
VAR_ELLIPTIC = 62
VAR_ESCHER = 63
VAR_FOCI = 64
VAR_LAZYSUSAN = 65
VAR_LOONIE = 66
VAR_PRE_BLUR = 67
VAR_MODULUS = 68
VAR_OSCILLOSCOPE = 69
VAR_POLAR2 = 70
VAR_POPCORN2 = 71
VAR_SCRY = 72
VAR_SEPARATION = 73
VAR_SPLIT = 74
VAR_SPLITS = 75
VAR_STRIPES = 76
VAR_WEDGE = 77
VAR_WEDGE_JULIA = 78
VAR_WEDGE_SPH = 79
VAR_WHORL = 80
VAR_WAVES2 = 81
VAR_EXP = 82
VAR_LOG = 83
VAR_SIN = 84
VAR_COS = 85
VAR_TAN = 86
VAR_SEC = 87
VAR_CSC = 88
VAR_COT = 89
VAR_SINH = 90
VAR_COSH = 91
VAR_TANH = 92
VAR_SECH = 93
VAR_CSCH = 94
VAR_COTH = 95
VAR_AUGER = 96
VAR_FLUX = 97
VAR_MOBIUS = 98


variations = {}
variation_list = [None] * 99 #flam3_nvariations
for k,v in locals().items():
    if k.startswith("VAR_"):
        name = k[4:].lower()
        variations[name] = v
        variation_list[v] = name


variable_list = ['blob_low',
                 'blob_high',
                 'blob_waves',
                 'pdj_a',
                 'pdj_b',
                 'pdj_c',
                 'pdj_d',
                 'fan2_x',
                 'fan2_y',
                 'rings2_val',
                 'perspective_angle',
                 'perspective_dist',
                 'julian_power',
                 'julian_dist',
                 'juliascope_power',
                 'juliascope_dist',
                 'radial_blur_angle',
                 'pie_slices',
                 'pie_rotation',
                 'pie_thickness',
                 'ngon_sides',
                 'ngon_power',
                 'ngon_circle',
                 'ngon_corners',
                 'curl_c1',
                 'curl_c2',
                 'rectangles_x',
                 'rectangles_y',
                 'disc2_rot',
                 'disc2_twist',
                 'super_shape_rnd',
                 'super_shape_m',
                 'super_shape_n1',
                 'super_shape_n2',
                 'super_shape_n3',
                 'super_shape_holes',
                 'flower_petals',
                 'flower_holes',
                 'conic_eccentricity',
                 'conic_holes',
                 'parabola_height',
                 'parabola_width',
                 'bent2_x',
                 'bent2_y',
                 'bipolar_shift',
                 'cell_size',
                 'cpow_r',
                 'cpow_i',
                 'cpow_power',
                 'curve_xamp',
                 'curve_yamp',
                 'curve_xlength',
                 'curve_ylength',
                 'escher_beta',
                 'lazysusan_spin',
                 'lazysusan_space',
                 'lazysusan_twist',
                 'lazysusan_x',
                 'lazysusan_y',
                 'modulus_x',
                 'modulus_y',
                 'oscilloscope_separation',
                 'oscilloscope_frequency',
                 'oscilloscope_amplitude',
                 'oscilloscope_damping',
                 'popcorn2_x',
                 'popcorn2_y',
                 'popcorn2_c',
                 'separation_x',
                 'separation_xinside',
                 'separation_y',
                 'separation_yinside',
                 'split_xsize',
                 'split_ysize',
                 'splits_x',
                 'splits_y',
                 'stripes_space',
                 'stripes_warp',
                 'wedge_angle',
                 'wedge_hole',                   
                 'wedge_count',
                 'wedge_swirl',                   
                 'wedge_julia_angle',
                 'wedge_julia_count',
                 'wedge_julia_power',
                 'wedge_julia_dist',
                 'wedge_sph_angle',
                 'wedge_sph_count',
                 'wedge_sph_hole',                   
                 'wedge_sph_swirl',                   
                 'whorl_inside',                   
                 'whorl_outside',                   
                 'waves2_freqx',
                 'waves2_scalex',
                 'waves2_freqy',
                 'waves2_scaley',
                 'auger_freq',
                 'auger_scale',
                 'auger_sym',
                 'auger_weight',
                 'flux_spread',
                 'mobius_re_a',
                 'mobius_im_a',
                 'mobius_re_b',
                 'mobius_im_b',
                 'mobius_re_c',
                 'mobius_im_c',
                 'mobius_re_d',
                 'mobius_im_d']


variables = defaultdict(list)
for k in variable_list:
    variation, variable = k.rsplit("_", 1)
    variables[variation].append(variable)
