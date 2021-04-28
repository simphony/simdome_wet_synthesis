import os
import math
import numpy as np
import matplotlib.pyplot as plt

from osp.core.namespaces import wet_synthesis
import osp.core.utils.simple_search as search


def reconstruct_log_norm_dist(moments):

    maxSize = 5000
    minSize = maxSize/1e8
    divisions = int(1e7)

    normalizedMoments = [moment / moments[0] for moment in moments]

    moments_Micron = [
        moment*((1e6)**k) for k, moment in enumerate(normalizedMoments)]

    # print(moments_Micron)

    # meanOfNormDist = (4.0/3.0)*math.log(moments_Micron[3]) \
    #     - (3.0/4.0)*math.log(moments_Micron[4])

    # sigmaOfNormDist = math.sqrt(math.log(moments_Micron[4]) / 2.0
    #                             - (2.0/3.0)*math.log(moments_Micron[3]))

    meanOfNormDist = (3.0/2.0)*math.log(moments_Micron[2]) \
        - (2.0/3.0)*math.log(moments_Micron[3])

    sigmaOfNormDist = math.sqrt((2.0/3.0)*math.log(moments_Micron[3])
                                - math.log(moments_Micron[2]))

    # x = np.linspace(minSize, maxSize, divisions)
    x = np.power(
        10, np.linspace(math.log10(minSize), math.log10(maxSize), divisions))

    logNormalDist = np.exp(
        -np.square(np.log(x) - meanOfNormDist) / (2*(sigmaOfNormDist**2))) \
        / x / sigmaOfNormDist / math.sqrt(2*math.pi)

    # print(np.trapz(logNormalDist, x))
    # print(np.trapz(logNormalDist*(x), x))
    # print(np.trapz(logNormalDist*(x**2), x))
    # print(np.trapz(logNormalDist*(x**3), x))
    # print(np.trapz(logNormalDist*(x**4), x))
    # print(np.trapz(logNormalDist*(x**5), x))

    file_dir = os.path.dirname(__file__)

    binMinSize = np.load(os.path.join(file_dir, 'bin_min_size.npy'))
    binMaxSize = np.load(os.path.join(file_dir, 'bin_max_size.npy'))
    # binAveSize = np.sqrt(binMinSize * binMaxSize)

    bins = np.insert(
        np.append(binMinSize, binMaxSize[-1]), 0,
        np.linspace(minSize, binMinSize[0], 10, endpoint=False))

    log10BinSize = np.diff(np.log10(bins[-2:]))[0]

    nRightPoints = int(
        round((math.log10(maxSize) - math.log10(bins[-1])) / log10BinSize))

    log10NewMaxSize = math.log10(bins[-1]) + nRightPoints*log10BinSize

    rightBins = np.linspace(
        math.log10(bins[-1]), log10NewMaxSize, num=nRightPoints + 1)[1:]

    bins = np.append(bins, np.power(10, rightBins))

    distByVol = logNormalDist*(x**3)
    volPercent = 100*(distByVol[:-1] + np.diff(distByVol) / 2)*np.diff(x) \
        / np.trapz(distByVol, x)
    # print(np.sum(volPercent))

    # print(bins)
    hist, _ = np.histogram(x[:-1], bins=bins, weights=volPercent)
    # print(np.sum(hist))

    negligible_threshold = 1e-3
    negligible_indices = (hist < negligible_threshold)
    hist[negligible_indices] = 0.0

    non_zero_indices = np.nonzero(hist)

    binAveSize = np.sqrt(bins[:-1] * bins[1:])
    trimmedBinAveSize = binAveSize[
        np.amin(non_zero_indices):np.amax(non_zero_indices) + 1]

    return np.trim_zeros(hist, trim='fb'), trimmedBinAveSize


def plot_size_dist(size_dist_cud):

    plt.rc('text', usetex=False)
    plt.rc('font',
           **{'family': 'serif', 'sans-serif': ['Arial'], 'style': 'normal'})
    plt.rc('axes.formatter', useoffset=False)
    plt.rcParams['ps.usedistiller'] = 'xpdf'
    plt.rcParams['xtick.labelsize'] = 11
    plt.rcParams['ytick.labelsize'] = 11
    plt.rcParams['axes.linewidth'] = 1
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    lineWidth = 2.0

    number = list()
    size = list()
    volume_percent = list()

    for bin_i in size_dist_cud.get(oclass=wet_synthesis.Bin):
        number.append(bin_i.number)
        size.append(bin_i.get(oclass=wet_synthesis.ParticleDiameter)[0].value)
        volume_percent.append(
            bin_i.get(oclass=wet_synthesis.ParticleVolumePercentage)[0].value)

    ordered_indices = np.argsort(np.array(number))

    fig1 = plt.figure(figsize=(6, 4))

    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.plot(
        np.array(size)[ordered_indices],
        np.array(volume_percent)[ordered_indices],
        linewidth=lineWidth, label='0D-Model', zorder=2)

    ax1.set_ylabel(r'volume %', fontsize=13)
    ax1.set_xlabel(r"Particle size ($\mu$m)", fontsize=13)

    ax1.yaxis.labelpad = 5

    fig1.tight_layout()

    plt.xlim(left=0.0)
    plt.ylim(bottom=0.0)

    plt.savefig(
        'volPercentDist.png', bbox_inches='tight', pad_inches=0.1, dpi=220)
    plt.close(fig1)


def read_compartment_data(case_dir):

    zone_ave_filePath = os.path.join(
        case_dir, 'react_zone_ave.txt')

    zone_flux_filePath = os.path.join(
        case_dir, 'react_zone_flux.txt')

    zone_fromBoundary_filePath = os.path.join(
        case_dir, 'react_zone_fromBoundary.txt')

    zone_id, zone_ave, zone_volume = np.loadtxt(
        zone_ave_filePath, dtype={'names': ('id', 'dissipation', 'volume'),
                                  'formats': (np.int, np.float, np.float)},
        skiprows=2, usecols=(0, 1, 4), unpack=True)

    origin_id, destination_id, flowrate = np.loadtxt(
        zone_flux_filePath, dtype={'names': ('origin', 'dest', 'flowrate'),
                                   'formats': (np.int, np.int, np.float)},
        skiprows=2, usecols=(1, 3, 5), unpack=True)

    boundary_name = \
        np.loadtxt(
            zone_fromBoundary_filePath, dtype=np.str,
            skiprows=2, usecols=(1, ))

    boundary_destination, boundary_flowrate = \
        np.loadtxt(
            zone_fromBoundary_filePath,
            dtype={'names': ('dest', 'flowrate'),
                   'formats': (np.int, np.float)},
            skiprows=2, usecols=(3, 5), unpack=True)

    return zone_id, zone_ave, zone_volume, \
        origin_id, destination_id, flowrate, \
        boundary_name, boundary_destination, boundary_flowrate


def find_compartment_by_id(compartment_id, compartmentNetwork):

    compartment = search.find_cuds_object(
        criterion=lambda x:
        compartment_id == x.ID if hasattr(x, 'ID') else False,
        root=compartmentNetwork, rel=wet_synthesis.hasPart,
        find_all=False, max_depth=1, current_depth=0)

    if not compartment:
        print('\nError:\nNo CUD found for compartment id: {}'.format(
            compartment_id))
        raise Exception()

    return compartment
