# Tim Cornwell <realtimcornwell@gmail.com>
#
# Visibility data structure: a Table with columns ['uvw', 'time', 'antenna1', 'antenna2', 'vis', 'weight']
# and an attached attribute which is the frequency of each channel

from astropy import constants as const
from astropy.coordinates import SkyCoord, CartesianRepresentation
from astropy.table import Table, vstack

from crocodile.simulate import *
from arl.simulate_visibility import Configuration, create_named_configuration

"""
Functions that represent a visibility set.

The data structure:
- an AstroPy Table with columns ['uvw', 'time', 'antenna1', 'antenna2', 'vis', 'weight']
- An attached attribute which is the frequency of each channel as a numy array
- An attached attribute which is the phase centre as an AstroPy SkyCoord
"""


class GainTable:
    """
    Gain table with time, antenna, gain[:,chan,pol] columns
    """
    
    # TODO: Implement gaintables with Jones and Mueller matrices
    
    def __init__(self):
        self.data = None
        self.frequency = None


def filter_gaintable(fg: GainTable, **kwargs):
    """Filer a Gaintable

    :param fg:
    :type GainTable:
    :returns: GainTable
    """
    print("define_visibility.filter_gain: not yet implemented")
    return fg


def create_gaintable_from_array(gain: numpy.array, time: numpy.array, antenna: numpy.array, weight: numpy.array,
                                frequency: numpy.array, copy=False, meta=None, **kwargs):
    """ Create a gaintable from arrays

    :param gain:
    :type GainTable:
    :param time:
    :type numpy.array:
    :param antenna:
    :type numpy.array:
    :param weight:
    :type numpy.array:
    :param frequency:
    :type numpy.array:
    :param copy:
    :type bool:
    :param meta:
    :type dict:
    :param kwargs:
    :returns: Gaintable
    """
    if meta is None:
        meta = {}
    nrows = time.shape[0]
    assert len(frequency) == gain.shape[1], "Discrepancy in frequency channels"
    assert len(antenna) == nrows, "Discrepancy in number of antenna rows"
    assert gain.shape[0] == nrows, "Discrepancy in number of gain rows"
    assert weight.shape[0] == nrows, "Discrepancy in number of weight rows"
    fg = GainTable()
    
    fg.data = Table(data=[gain, time, antenna, weight], names=['gain', 'time', 'antenna', 'weight'], copy=copy,
                    meta=meta)
    fg.frequency = frequency
    return fg


def interpolate_gaintable(gt: GainTable, **kwargs):
    """ Interpolate a GainTable to new sampling

    :param gt:
    :type GainTable:
    :param kwargs:
    :returns: Gaintable
    """
    print('"define_visibility.interpolate_gaintable: not yet implemented')
    return GainTable()


class Visibility:
    """ Visibility table class
    
    Visibility with uvw, time, a1, a2, vis, weight Columns in
    an astropy Table along with an attribute to hold the frequencies
    and an attribute to hold the direction.

    Visibility is defined to hold an observation with one set of frequencies and one
    direction.

    The data column has vis:[row,nchan,npol], uvw:[row,3]
    """

    def __init__(self):
        self.data = None
        self.frequency = None
        self.phasecentre = None
        self.configuration = None


def combine_visibility(fvt1: Visibility, fvt2: Visibility, w1: float = 1.0, w2: float = 1.0, **kwargs) -> Visibility:
    """ Linear combination of two visibility sets
    
    :param fvt1: Visibility set 1
    :type Visibility:
    :param fvt2: Visibility set 2
    :type Visibility:
    :param w1: Weight of visibility set 1
    :type float:
    :param w2: Weight of visibility set 2
    :type float:
    :param kwargs:
    :returns: Visibility
    """
    assert len(fvt1.frequency) == len(fvt2.frequency), "Visibility: frequencies should be the same"
    assert numpy.max(numpy.abs(fvt1.frequency - fvt2.frequency)) < 1.0, "Visibility: frequencies should be the same"
    print("visibility.combine: combining tables with %d rows and %d rows" % (len(fvt1.data), len(fvt2.data)))
    print("visibility.combine: weights %f, %f" % (w1, w2))
    fvt = Visibility()
    fvt.data['vis'] = w1 * fvt1.data['weight'] * fvt1.data['vis'] + w2 * fvt1.data['weight'] * fvt2.data['vis']
    fvt.data['weight'] = w1 * fvt1.data['weight'] + w2 * fvt1.data['weight']
    fvt.data['vis'][fvt.data['weight'] > 0.0] = fvt.data['vis'][fvt.data['weight'] > 0.0] / \
                                                fvt.data['weight'][fvt.data['weight'] > 0.0]
    fvt.data['vis'][fvt.data['weight'] > 0.0] = 0.0
    fvt.phasecentre = fvt1.phasecentre
    fvt.frequency = fvt1.frequency
    print(u"visibility.filter: Created table with {0:d} rows".format(len(fvt.data)))
    assert (len(fvt.data) == (len(fvt1.data) + len(fvt2.data))), 'Length of output data table wrong'
    return fvt


def concatenate_visibility(fvt1: Visibility, fvt2: Visibility, **kwargs) -> \
        Visibility:
    """ Concatentate the data sets in time, optionally phase rotating the second to the phasecenter of the first
    
    :param fvt1:
    :type Visibility:
    :param fvt2:
    :type Visibility:
    :param kwargs:
    :returns: Visibility
    """
    assert len(fvt1.frequency) == len(fvt2.frequency), "Visibility: frequencies should be the same"
    assert numpy.max(numpy.abs(fvt1.frequency - fvt2.frequency)) < 1.0, "Visibility: frequencies should be the same"
    print("visibility.concatenate: combining two tables with %d rows and %d rows" % (len(fvt1.data), len(fvt2.data)))
    fvt2rot = phaserotate_visibility(fvt2, fvt1.phasecentre)
    fvt = Visibility()
    fvt.data = vstack([fvt1.data, fvt2rot.data], join_type='exact')
    fvt.phasecentre = fvt1.phasecentre
    fvt.frequency = fvt1.frequency
    print(u"visibility.concatenate: Created table with {0:d} rows".format(len(fvt.data)))
    assert (len(fvt.data) == (len(fvt1.data) + len(fvt2.data))), 'Length of output data table wrong'
    return fvt


def flag_visibility(fvis: Visibility, gt: GainTable = None, **kwargs) -> Visibility:
    """ Flags a visibility set, optionally using GainTable

    :param fvis:
    :type Visibility:
    :param gt:
    :type GainTable:
    :param kwargs:
    :returns: Visibility
    """
    print("define_visibility.flag_visibility: not yet implemented")
    return fvis


def filter_visibility(fvis: Visibility, **kwargs) -> Visibility:
    """ Filter a visibility set

    :param fvis:
    :type Visibility:
    :param kwargs:
    :returns: Visibility
    """
    print("define_visibility.filter_visibility: not yet implemented")
    return fvis


def create_gaintable_from_visibility(vt: Visibility, **kwargs):
    """Create an empty gaintable from a visibilty set

    :param vt: Visibility to be used as template
    :type Visibility:
    :returns: GainTable
    """
    print("define_visibility.create_gaintable_from_visibility: not yet implemented")
    return object()


def create_visibility_from_ms(msfile: str, **kwargs) -> Visibility:
    """ Create a visibility set from a measurement set

    :param msfile: Name of measurement set
    :type str:
    :returns: Visibility
    """
    print('define_visibility.visibilty_from_ms: not yet implemented')
    return Visibility()


def save_visibility_to_ms(vt: Visibility, msfile: str = None, **kwargs) -> Visibility:
    """ Write a visibility set to a measurement set

    :param vt: Name of visibility set
    :param Visibility:
    :param msfile: Name of output measurement set
    :type str:
    :returns: Visibility
    """
    print('define_visibility.visibilty_from_ms: not yet implemented')

def create_visibility(config: Configuration, times: numpy.array, freq: numpy.array, weight: float,
                      phasecentre: SkyCoord, meta: dict = None, **kwargs) -> Visibility:
    """ Create a vistable from Configuration, hour angles, and direction of source
    

    :param config: Configuration of antennas
    :type Configuration:
    :param times: hour angles in radians
    :type numpy.array:
    :param freq: frequencies (Hz] Shape [nchan, npol]
    :type numpy.array:
    :param weight: weight of a single sample
    :type float:
    :param phasecentre: phasecentre of observation
    :type SkyCoord:
    :param meta:
    :type dict:
    :returns: Visibility
    """
    assert phasecentre is not None, "Must specify phase centre"
    nch = len(freq)
    npol = kwargs.get("npol", 4)
    ants_xyz = config.data['xyz']
    nants = len(config.data['names'])
    nbaselines = int(nants * (nants - 1) / 2)
    ntimes = len(times)
    nrows = nbaselines * ntimes
    row = 0
    rvis = numpy.zeros([nrows, nch, npol], dtype='complex')
    rweight = weight * numpy.ones([nrows, nch, npol])
    rtimes = numpy.zeros([nrows])
    rantenna1 = numpy.zeros([nrows], dtype='int')
    rantenna2 = numpy.zeros([nrows], dtype='int')
    for ha in times:
        rtimes[row:row + nbaselines] = ha * 43200.0 / numpy.pi
        for a1 in range(nants):
            for a2 in range(a1 + 1, nants):
                rantenna1[row] = a1
                rantenna2[row] = a2
                row += 1
    ruvw = xyz_to_baselines(ants_xyz, times, phasecentre.dec)
    print(u"visibility.create_visibility: Created {0:d} rows".format(nrows))
    vt = Visibility()
    vt.data = Table(data=[ruvw, rtimes, rantenna1, rantenna2, rvis, rweight],
                    names=['uvw', 'time', 'antenna1', 'antenna2', 'vis', 'weight'], meta=meta)
    vt.frequency = freq
    vt.phasecentre = phasecentre
    vt.configuration = config
    return vt


def phaserotate_visibility(vt: Visibility, newphasecentre: SkyCoord, **kwargs) -> Visibility:
    """ Phase rotate from the current phase centre to a new phase centre: works in place
    
    :param vt: Visibility to be rotated
    :type Visibility:
    :returns: Visibility
    """
    pcof = newphasecentre.skyoffset_frame()
    todc = vt.phasecentre.transform_to(pcof)
    dc = todc.represent_as(CartesianRepresentation)
    print('visibility.sum_visibility: Relative cartesian representation of direction = (%f, %f, %f)' % (dc.x, dc.y,
                                                                                                       dc.z))

    if numpy.abs(dc.x) > 1e-15 or numpy.abs(dc.y) > 1e-15:
        print('visibility.phaserotate: Phase rotation from %s to %s' % (vt.phasecentre, newphasecentre))
        nchan = vt.data['vis'].shape[1]
        npol = vt.data['vis'].shape[2]
        for channel in range(nchan):
            uvw = vt.data['uvw'] * (vt.frequency[channel] / const.c).value
            uvw[:, 2] *= -1.0
            phasor = simulate_point(uvw, dc.y, dc.z)
            for pol in range(npol):
                print('visibility.phaserotate: Phaserotating visibility for channel %d, polarisation %d' %
                      (channel, pol))
                vt.data['vis'][:, channel, pol] = vt.data['vis'][:, channel, pol] * phasor
    # TODO: rotate uvw as well!!!

    vt.phasecentre = newphasecentre
    return vt


def sum_visibility(vt: Visibility, direction: SkyCoord, **kwargs) -> numpy.array:
    """ Direct Fourier summation in a given direction
    
    :param vt: Visibility to be summed
    :type Visibility:
    :param direction: Direction of summation
    :type SkyCoord:
    :returns: flux[nch,npol], weight[nch,pol]
    """
    dc = direction.represent_as(CartesianRepresentation)
    print('visibility.sum_visibility: Cartesian representation of direction = (%f, %f, %f)' % (dc.x, dc.y, dc.z))
    nchan = vt.data['vis'].shape[1]
    npol = vt.data['vis'].shape[2]
    flux = numpy.zeros([nchan, npol])
    weight = numpy.zeros([nchan, npol])
    for channel in range(nchan):
        uvw = vt.data['uvw'] * (vt.frequency[channel] / const.c).value
        uvw[:, 2] *= -1.0
        phasor = numpy.conj(simulate_point(uvw, dc.z, dc.y))
        for pol in range(npol):
            print('imaging.sum_visibility: Summing visibility for channel %d, polarisation %d' % (channel, pol))
            flux[channel, pol] = flux[channel, pol] + \
                                 numpy.sum(numpy.real(vt.data['vis'][:, channel, pol] *
                                                      vt.data['weight'][:, channel, pol] * phasor))
            weight[channel, pol] = weight[channel, pol] + numpy.sum(vt.data['weight'][:, channel, pol])
    flux[weight > 0.0] = flux[weight > 0.0] / weight[weight > 0.0]
    flux[weight <= 0.0] = 0.0
    return flux, weight

def average_visibility(vt: Visibility, **kwargs) -> Visibility:
    """ Average visibility in time and frequency
    
    Creates new Visibility by averaging in time and frequency
    
    :param vt: Visibility to be averaged
    :type Visibility:
    :returns: Visibility after averaging
    """
    print("define_visibility.average_visibility: not yet implemented")
    return vt

def de_average_visibility(vt: Visibility, vttemplate: Visibility, **kwargs) -> Visibility:
    """ De-average visibility in time and frequency i.e. replicate to template Visibility
    
    This is the opposite of averaging - the Visibility is expanded into the template format.
    
    :param vt: Visibility to be de-averaged
    :type Visibility:
    :param vttemplate: template Visibility
    :type Visibility:
    :returns: Visibility after de-averaging
    """
    print("define_visibility.de_average_visibility: not yet implemented")
    return vt


def weight_visibility(vt, im, **kwargs):
    """ Reweight the visibility data in place a selected algorithm

    :param vt:
    :type Visibility:
    :param im:
    :type Image:
    :param kwargs:
    :returns: Configuration
    """
    print("define_visibility.weight_visibility: not yet implemented")
    return vt


if __name__ == '__main__':
    config = create_named_configuration('VLAA')
    times1 = numpy.arange(-3.0, 0.0, 3.0 / 60.0) * numpy.pi / 12.0
    times2 = numpy.arange(0.0, +3.0, 3.0 / 60.0) * numpy.pi / 12.0
    freq1 = numpy.arange(5e6, 150.0e6, 1e7)
    freq2 = numpy.arange(6e6, 150.0e6, 1e7)
    phasecentre1 = SkyCoord(ra='00h42m30s', dec='+41d12m00s', frame='icrs', equinox=2000.0)
    phasecentre2 = SkyCoord(ra='04h56m10s', dec='+63d00m00s', frame='icrs', equinox=2000.0)
    vt1 = create_visibility(config, times1, freq1, weight=1.0, phasecentre=phasecentre1)
    vt2 = create_visibility(config, times2, freq1, weight=1.0, phasecentre=phasecentre2)
    vtsum = concatenate_visibility(vt1, vt2)
    print(vtsum.data)
    print(vtsum.frequency)
    print(numpy.unique(vtsum.data['time']))
    
    
