# Helper file for plotting windbarbs. 
# Adapted from low-level-jet code. 
# Authors: Sara Vannah, Stephen Leroy (JANUS/AER).
# 7/29/26
#####################################################

import numpy as np
from pyllj.podutilities.isohypses import WindBarbs, compute_windbarbs, windbarbs_ax
import matplotlib.pyplot as plt

months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()

def plot_windbarbs_full( reanalysis:{"narr","merra2","era5"}="narr", region="southern-plains", 
        scale=12.0, scale_length=10.0, outputfile=None ): 

    #  Get data. 

    w = compute_windbarbs( reanalysis, region=region )
    windbarbs = WindBarbs( **w )

    #  Define output file. 

    if outputfile is None: 
        outfile = f'{reanalysis}_windbarbs.{region}.pdf'
    else: 
        outfile = outputfile

    #  Geometry of figure. 

    xmargin = 0.45
    ymargin = 0.40
    nx, ny = 4, 3

    figsize = ( xmargin + 1.5 * nx, ymargin + 1.2 * ny )
    offset = np.array( [ xmargin/figsize[0], ymargin/figsize[1], 0.0, 0.0 ] )
    window = np.array( [ 0.04, 0.04, 0.90, 0.80 ] )
    wscale = ( 1.0 - np.array( [ offset[0], offset[1], offset[0], offset[1] ] ) ) / np.array( [nx,ny,nx,ny] )

    fig = plt.figure( figsize=figsize )

    xmin, xmax = 0.5, 0.5
    ymin, ymax = 0.5, 0.5

    #  Loop over month. 

    for imonth in range(12): 

        ix, iy = imonth % nx, ny - int(imonth/nx) - 1
        pos = ( window + np.array( [ix,iy,0,0] ) ) * wscale + offset

        xmin, xmax = min( xmin, pos[0] ), max( xmax, pos[0]+pos[2] )
        ymin, ymax = min( ymin, pos[1] ), max( ymax, pos[1]+pos[3] )

        meta = { 'xticks': (iy==0), 'yticks': (ix==0), 'scale': scale, 'scale_length': None }
        if ix==nx-1 and iy==0: 
            meta['scale_length'] = scale_length

        ax = windbarbs_ax( fig, pos, windbarbs, imonths=imonth, **meta )
        ax.set_xlabel( "" )
        ax.set_ylabel( "" )

        label = '({:}) {:}'.format( chr(ord('a')+imonth), months[imonth] )
        ax.text( -2.0, 3.12, label, ha="left" )

    fig.supxlabel( "UTC hour", x=0.5*(xmin+xmax), y=0.01, ha="center", va="bottom" )
    fig.supylabel( "Height above surface [km]", x=0.01, y=0.5*(ymin+ymax), ha="left", va="center" )

    print( f'Saving to {outfile}' )
    fig.savefig( outfile )

    return


def plot_windbarbs_summer( reference=None, region="southern-plains", 
        outputfile="windbarbs_summer.pdf", scale=12.0, scale_length=10.0 ): 

    #  Get data. 

    windbarbs = []
    for reanalysis in [ "narr", "merra2", "era5" ]: 
        w = compute_windbarbs( reanalysis, region=region )
        windbarbs.append( WindBarbs( **w ) )

    #  Geometry of figure. 

    xmargin = 0.35
    ymargin = 0.35

    if reference is None: 
        nx, ny = len(windbarbs), 1
    else: 
        nx, ny = len(windbarbs)-1, 1

    figsize = ( xmargin + 1.9 * nx, ymargin + 1.5 * ny )
    offset = np.array( [ xmargin/figsize[0], ymargin/figsize[1], 0.0, 0.0 ] )
    window = np.array( [ 0.04, 0.04, 0.90, 0.80 ] )
    wscale = ( 1.0 - np.array( [ offset[0], offset[1], offset[0], offset[1] ] ) ) / np.array( [nx,ny,nx,ny] )

    fig = plt.figure( figsize=figsize )

    xmin, xmax = 0.5, 0.5
    ymin, ymax = 0.5, 0.5

    #  Loop over month. 

    isummer = np.arange(5,8)
    ix, iy = -1, 0

    if reference is not None: 
        wbref = [ wb for wb in windbarbs if wb.model==reference ]
        if len( wbref ) != 1: 
            print( f'Model {reference} does not exist and cannot be used as a reference. Exiting.' )
            return
        wbref = wbref[0]

    for wb in windbarbs: 

        if reference is None: 
            ix += 1
            wbp = wb
        else: 
            if wb.model == wbref.model: 
                continue
            else: 
                ix += 1
                wbp = wb - wbref
        pos = ( window + np.array( [ix,iy,0,0] ) ) * wscale + offset

        xmin, xmax = min( xmin, pos[0] ), max( xmax, pos[0]+pos[2] )
        ymin, ymax = min( ymin, pos[1] ), max( ymax, pos[1]+pos[3] )

        meta = { 'xticks': (iy==0), 'yticks': (ix==0), 'scale_length': None, 'scale': scale }
        if ix==nx-1 and iy==0: 
            meta['scale_length'] = scale_length

        ax = windbarbs_ax( fig, pos, wbp, imonths=isummer, **meta )
        ax.set_xlabel( "" )
        ax.set_ylabel( "" )

        label = '({:}) {:}'.format( chr(ord('a')+ix), wbp.modelname )
        ax.text( -2.0, 3.12, label, ha="left" )

    fig.supxlabel( "UTC hour", x=0.5*(xmin+xmax), y=0.01, ha="center", va="bottom" )
    fig.supylabel( "Height above surface [km]", x=0.01, y=0.5*(ymin+ymax), ha="left", va="center" )

    print( f'Saving to {outputfile}' )
    fig.savefig( outputfile )

    return


def plot_windbarbs_summer_sgp( outputfile="windbarbs_summer_sgp.pdf" ): 

    scale, scale_length = 2.5, 1.0

    #  Get data. 

    reanalyses_at_sgp = []
    reanalyses_at_southernplains = []

    for reanalysis in [ "narr", "merra2", "era5" ]: 
        analysisfile = os.path.join( default_dataroot, reanalysis.upper(), "isohypses", "isohypses.2007-2020.nc" )
        w = compute_windbarbs( analysisfile, sourcelabel=reanalysis.upper(), sonde="sgp" )
        reanalyses_at_sgp.append( WindBarbs( **w ) )
        w = compute_windbarbs( analysisfile, sourcelabel=reanalysis.upper(), region="southern-plains" )
        reanalyses_at_southernplains.append( WindBarbs( **w ) )

    #  Use SGP climatology as reference for all plots. 

    w = compute_windbarbs( "sgp" )
    sgp = WindBarbs( **w )

    #  Geometry of figure. 

    xmargin = 0.35
    ymargin = 0.35
    nx, ny = 3, 2

    figsize = ( xmargin + 1.9 * nx, ymargin + 1.5 * ny )
    offset = np.array( [ xmargin/figsize[0], ymargin/figsize[1], 0.0, 0.0 ] )
    window = np.array( [ 0.04, 0.04, 0.90, 0.80 ] )
    wscale = ( 1.0 - np.array( [ offset[0], offset[1], offset[0], offset[1] ] ) ) / np.array( [nx,ny,nx,ny] )

    fig = plt.figure( figsize=figsize )

    xmin, xmax = 0.5, 0.5
    ymin, ymax = 0.5, 0.5

    #  Loop over month. 

    isummer = np.arange(5,8)
    ix, iy = -1, 0
    iplot = 0

    for reanalyses, clabel in [ ( reanalyses_at_sgp, "SGP" ), ( reanalyses_at_southernplains, "Southern Plains" ) ]: 
        for wb in reanalyses: 
            wbp = wb - sgp
            ix, iy = iplot % nx, ny - int(iplot/nx) - 1
            pos = ( window + np.array( [ix,iy,0,0] ) ) * wscale + offset

            xmin, xmax = min( xmin, pos[0] ), max( xmax, pos[0]+pos[2] )
            ymin, ymax = min( ymin, pos[1] ), max( ymax, pos[1]+pos[3] )

            meta = { 'xticks': (iy==0), 'yticks': (ix==0), 'scale_length': None, 'scale': scale }
            if ix==nx-1 and iy==0: 
                meta['scale_length'] = scale_length

            ax = windbarbs_ax( fig, pos, wbp, imonths=isummer, **meta )
            ax.set_xlabel( "" )
            ax.set_ylabel( "" )

            label = '({:}) {:}({:})'.format( chr(ord('a')+iplot), wb.sourcename, clabel )
            ax.text( -2.0, 3.12, label, ha="left" )

            iplot += 1

    fig.supxlabel( "UTC hour", x=0.5*(xmin+xmax), y=0.01, ha="center", va="bottom" )
    fig.supylabel( "Height above surface [km]", x=0.01, y=0.5*(ymin+ymax), ha="left", va="center" )

    print( f'Saving to {outputfile}' )
    fig.savefig( outputfile )

    return
