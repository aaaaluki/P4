#! /usr/bin/python3 -u

import struct

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from docopt import docopt
import numpy as np
from scipy.stats import multivariate_normal as gauss

def read_gmm(fileGMM):
    '''
       Reads the weights, means and convariances from a GMM
       stored using format "UPC: GMM V 2.0"
    '''

    header = b'UPC: GMM V 2.0\x00'

    try:
        with open(fileGMM, 'rb') as fpGmm:
            headIn = fpGmm.read(15)
    
            if headIn != header:
                print(f'ERROR: {fileGMM} is not a valid GMM file')
                exit(-1)

            numMix = struct.unpack('@I', fpGmm.read(4))[0]
            weights = np.array(struct.unpack(f'@{numMix}f', fpGmm.read(numMix * 4)))

            (numMix, numCof) = struct.unpack('@II', fpGmm.read(2 * 4))
            means = struct.unpack(f'@{numMix * numCof}f', fpGmm.read(numMix * numCof * 4))
            means = np.array(means).reshape(numMix, numCof)

            (numMix, numCof) = struct.unpack('@II', fpGmm.read(2 * 4))
            invStd = struct.unpack(f'@{numMix * numCof}f', fpGmm.read(numMix * numCof * 4))
            covs = np.array(invStd).reshape(numMix, numCof) ** -2

            return weights, means, covs
    except:
        raise Exception(f'Error al leer el fichero {fileGMM}')


def read_fmatrix(fileFM):
    '''
       Reads an fmatrix from a file
    '''
    try:
        with open(fileFM, 'rb') as fpFM:
            (numFrm, numCof) = struct.unpack('@II', fpFM.read(2 * 4))
            data = struct.unpack(f'@{numFrm * numCof}f', fpFM.read(numFrm * numCof * 4))
            data = np.array(data).reshape(numFrm, numCof)

            return data
    except:
        raise Exception(f'Error al leer el fichero {fileFM}')


def pdfGMM(X, weights, means, covs):
    '''
       Returns the probability density function (PDF) of a population X
       given a Gaussian Mixture Model (GMM) defined by its weights,
       means and covariances.
    '''

    pdf = np.zeros(len(X))
    for mix, weight in enumerate(weights):
        try:
            pdf += weight * gauss.pdf(X, mean=means[mix], cov=covs[mix])
        except:
            raise Exception(f'Error al calcular la mezcla {mix} del GMM')

    return pdf

def limsGMM(means, covs, fStd=3):
    '''
       Returns the maximum and minimum values of the mean plus/minus fStd
       times the standard deviation for a set of Gaussians defined by their
       means and convariances.
    '''

    numMix = len(means)

    min_ = means[0][:]
    max_ = means[0][:]

    for mix in range(numMix):
        min_ = np.min((min_, means[mix] - fStd * covs[mix] ** 0.5), axis=0)
        max_ = np.max((max_, means[mix] + fStd * covs[mix] ** 0.5), axis=0)

    margin = max(max_ - min_)

    return min_, max_

def plotGMM(fileGMM, xDim, yDim, percents, colorGmm, filesFeat=None, colorFeat=None, limits=None, subplot=111):
    weights, means, covs = read_gmm(fileGMM)

    ax = plt.subplot(subplot)
    if filesFeat:
        feats = np.ndarray((0, 2))
        for fileFeat in filesFeat:
            feat = read_fmatrix(fileFeat)
            feat = np.stack((feat[..., xDim], feat[..., yDim]), axis=-1)
            feats = np.concatenate((feats, feat))

        ax.scatter(feats[:, 0], feats[:, 1], .05, color=colorFeat)

    means = np.stack((means[..., xDim], means[..., yDim]), axis=-1)
    covs = np.stack((covs[..., xDim], covs[..., yDim]), axis=-1)

    if not limits:
        min_, max_ = limsGMM(means, covs)
        limits = (min_[0], max_[0], min_[1], max_[1])
    else:
        min_, max_ = (limits[0], limits[2]), (limits[1], limits[3])

    plt.title(f'{fileGMM.split("/")[2].upper()}: Coefs {xDim} and {yDim} dependance')
    plt.axis('tight')
    plt.axis(limits)
    plt.show()


########################################################################################################
# Main Program
########################################################################################################

USAGE='''
Draws the regions in space covered with a certain probability by a GMM.

Usage:
    plotGMM [--help|-h] [options] <file-gmm> [<file-feat>...]

Options:
    --xDim INT, -x INT               'x' dimension to use from GMM and feature vectors [default: 0]
    --yDim INT, -y INT               'y' dimension to use from GMM and feature vectors [default: 1]
    --percents FLOAT..., -p FLOAT...  Percentages covered by the regions [default: 90,50]
    --colorGMM STR, -g STR            Color of the GMM regions boundaries [default: red]
    --colorFEAT STR, -f STR           Color of the feature population [default: red]
    --limits xyLimits -l xyLimits     xyLimits are the four values xMin,xMax,yMin,yMax [default: auto]

    --help, -h                        Shows this message

Arguments:
    <file-gmm>    File with the Gaussian mixture model to be plotted
    <file-fear>   Feature files to be plotted along the GMM
'''

if __name__ == '__main__':
    args = docopt(USAGE)

    fileGMM = args['<file-gmm>']
    filesFeat = args['<file-feat>']
    xDim = int(args['--xDim'])
    yDim = int(args['--yDim'])
    percents = args['--percents']
    if percents:
        percents = percents.split(',')
        percents = np.array([float(percent) / 100 for percent in percents])
    colorGmm = args['--colorGMM']
    colorFeat = args['--colorFEAT']
    limits = args['--limits']
    if limits != 'auto':
        limits = [float(limit) for limit in limits.split(',')]
        if len(limits) != 4:
            print('ERROR: xyLimits must be four comma-separated values')
            exit(1)
    else:
        limits = None

    plotGMM(fileGMM, xDim, yDim, percents, colorGmm, filesFeat, colorFeat, limits, 111)

