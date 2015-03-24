"""
CLEAN application illustration, the source field example
V.Stolyarov, 23.03.2015
"""

import numpy
import scipy
import scipy.special
import scipy.ndimage

from clean import *
from synthesis import *
from simulate import *
from simplots import *


if 1:
    """
    Read antenna positions from ASCII file (XYZ, meters)
    """
    vlas=numpy.genfromtxt("test/VLA_A_hor_xyz_5ants.txt", delimiter=",")
    plot_scatter(vlas[:,0], vlas[:,1], 'Antenna positions on the (X,Y) plane', 'X, meters', 'Y, meters')


    """
    Set the parameters of the observations, e.g. wavelength, declination of the tracking center,
    the lenth of the observations and the interval between the snapshots
    """
    uvstep = 22.9  	# an interval between the snapshots (a step in time), minutes
    uvstep = uvstep/60./12.* numpy.pi
    
    wl = 3.0 		# wavelength, meters
    
    dec = numpy.pi/4.0 	# Declination, radians
    
    obsTime = 12. 	# The length of the observations, hours
    obsTime = obsTime/12.*numpy.pi 
    
    
    """
    Generate UV plane coverage for a batch of the snapshots taken every uvstep
    during obsTime at the declination dec, wavelength is wl.
    """  
    vobs=genuv(vlas, numpy.arange(0,obsTime,uvstep) ,  dec)
    plot_scatter(vobs[:,0]/wl, vobs[:,1]/wl,'UV plane coverage for 12h observation, wavelength = 3m', 
    	'U, number of wavelengths','V, number of wavelengths')

    
    """
    Read ASCII file with pixel intensities (3 columns - x, y, I(x,y) )
    """
    sfield = numpy.genfromtxt("test/GroupOfSources.txt")
    smat = sfield[:,2].reshape(int(max(sfield[:,0]))+1, int(max(sfield[:,1]))+1)
    deltaRad = 1e-4 # pixel size in radians
    sfield[:,0] =  sfield[:,0] - max(sfield[:,0])/2
    sfield[:,1] =  sfield[:,1] - max(sfield[:,1])/2
    sfield[:,0] =  sfield[:,0] * deltaRad # convert XY into radians w.r.t. the phase centre 
    sfield[:,1] =  sfield[:,1] * deltaRad # convert XY into radians w.r.t. the phase centre 
    
    
    """
    Generate contribution of each pixel into visibility
    """
    yy=sfield[0,2]*genvis(vobs/wl, sfield[0,0], sfield[0,1])
    for i in range(1,numpy.size(sfield[:,0])-1):
    	yy = yy + sfield[i,2]*genvis(vobs/wl, sfield[i,0], sfield[i,1])
    
    """
    Copy uv coverage and visibilities for later use in majorcycle
    """    
    yy1 = numpy.copy(yy)
    vobs1 = numpy.copy(vobs)

    """
    No UV plane rotation to get zero W component - done later in majorcycle_imshow()
    """
#    yy=rotw(vobs/wl, yy)

    """
    Fill the Hermitian conjugated part of the UV plane, V(-u,-v) = V*(u,v)
    """
    vobs_tmp = numpy.copy(vobs)
    vobs_tmp[:,0] *= -1.0
    vobs_tmp[:,1] *= -1.0
    vobs_new = numpy.concatenate((vobs, vobs_tmp))
    yy_tmp = numpy.conjugate(yy)
    yy_new = numpy.concatenate((yy, yy_tmp))


    plot_scatter(vobs_new[:,0]/wl, vobs_new[:,1]/wl,'UV plane coverage for 12h observation with Hermitian part',
    	'U, number of wavelengths','V, number of wavelengths' )

    """
    Plot the model of the sources    
    """
    plot_image(smat, 'A model of the source field, 44 x 44 arcmin',
    	'l, pixel number', 'm, pixel number', 'I(l,m)')

    """
    Transfer visibilities to the square matrix nmat x nmat using
    re-gridding routine (no visibility stacking in UV cells, correct for the 
    sparse UV plane coverage)

    """
    nmat = 512
    mat_a = numpy.zeros((nmat,nmat),'D')
    maxvobs = max(vobs_new[:,0:1])[0] + 1
    mat_a = grid1(mat_a,(vobs_new/maxvobs),yy_new)
    plot_contour(numpy.abs(mat_a), 'Module of visibility V(u,v) resampled to the matrix',
    	'V, number of pixel', 'U, number of pixel', 'abs(V(u,v)')


    """
    Apply FFTSHIFT to shift the phase center to the origin
    """
    mat_b = numpy.fft.ifftshift(mat_a)
    plot_contour(numpy.abs(mat_b), 'Module of V(u,v) resampled to the matrix after FFTSHIFT',
    	'V, number of pixel', 'U, number of pixel', 'abs(V(u,v)')
    

    """
    Make inverse Fourier-transform to get the dirty image and apply FFTSHIFT again
    to return the phase center to the middle of the matrix
    Since no UV plane rotation is done so far, the phase error is high and the image is noisy.	
    """
    c = numpy.fft.ifft2(mat_b)
    c1 = numpy.fft.fftshift(c)*numpy.size(vobs_new,0)
    
    plot_image(numpy.abs(c1), 'Dirty image of the test source field with phase errors',
    	'l, number of pixel', 'm, number of pixel', 'I(l,m)')
     



    """
    Smooth and decimate the dirty image for 3D surface plot	
    """
if(0):
    ncomp = 4
    c2 = scipy.ndimage.gaussian_filter(abs(c1), ncomp) 	# smooth with a Gaussian kernel
    c3 = c2[::ncomp,::ncomp]				# decimate
    plot_3Dsurface(c3, '3D surface of the dirty image recovered (smoothed)',
    	'l, number of pixel', 'm, number of pixel', 'I(l,m), amplitude')
	

"""
Application of CLEAN Cotton-Schwab algorithm, in
Synthesis Imaging in Radio Astronomy II, ed. by Taylor G.B., Carilli C.L. and Perley R.A,
ASP conf. series, vol 180, p.155 (1999)  
"""
if 1:
    """
    Call majorcycle function (Cotton-Schwab algorithm) and plot the image solution for
    every of nmajor iteration. Parameters returned are
    ps - points in UV plane
    vs - cleaned visibilities    
    """

    nmajor = 5 # number of iterations in the major cycle
    nminor = 100 # number of iterations in the minor cycle (Hogborn algorithm)
    gain = 0.1
    wstep = 250000
    T2 = 0.025 # Theta2, the half-width of the field of view to be synthetised  (radian)
    L2 = 15000 # Half-width of the uv-plane (unitless). Controls resultion of the images

    ps,vs = majorcycle_imshow(T2, L2, vobs/wl , yy, gain, nmajor, nminor, wstep)

    """
    Construct the image and the beam (PSF, point spread function) after CLEAN iterations
    and plot them.
    """
    dirty,psf = doimg(T2, L2, ps,vs, lambda *x: wslicimg(*x, wstep=wstep) )

    plot_image(numpy.abs(dirty), 'Dirty image after majorcycle',
    	'l, number of pixel', 'm, number of pixel', 'I(l,m)')

    plot_image(numpy.abs(psf), 'psf after majorcycle',
    	'l, number of pixel', 'm, number of pixel', 'I(l,m)')

     