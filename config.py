#---------------TRANSCODING_PARAMETERS-------------------------------------------#
CONSTANT_RATE_FACTOR = 28
PRESET = "medium"
SEGMENT_DURATION = 7500 # 7.5 sec
HDR2SDR_filter = f"zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p[scaled];"
