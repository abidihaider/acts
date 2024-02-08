#!/usr/bin/env python3
import pathlib, acts, acts.examples, acts.examples.itk
from acts.examples.simulation import (
    addParticleGun,
    MomentumConfig,
    EtaConfig,
    ParticleConfig,
    addPythia8,
    addFatras,
    ParticleSelectorConfig,
    addDigitization,
)
from acts.examples.reconstruction import (
    addSeeding,
    TruthSeedRanges,
    addCKFTracks,
    CKFPerformanceConfig,
    TrackSelectorRanges,
    addAmbiguityResolution,
    AmbiguityResolutionConfig,
    addVertexFitting,
    VertexFinder,
)
from acts.examples import (
    CsvTrackingGeometryWriter,
)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--rnd",         type=int, required=True, help="random seed")
parser.add_argument("--mu",         type=int, required=True, help="pileup")
parser.add_argument("--nEvents",         type=int, required=True, help="nEvents")
parser.add_argument("--doSingleMu",  action='store_true', help="single muon as main process")
parser.add_argument("--dottbar",    action='store_true', help="ttbar as main process")
args = parser.parse_args()


u = acts.UnitConstants
geo_dir = pathlib.Path("acts-itk")
outFolder = ""
if args.doSingleMu: 
    outFolder = "singlemu"
elif args.dottbar:
    outFolder = "ttbar"
else:
    print("Process not specified")
    exit(1)

outFolder += "_mu" + str(args.mu) + "_s" + str(args.rnd)

outputDir = pathlib.Path.cwd() / outFolder


# acts.examples.dump_args_calls(locals())  # show acts.examples python binding calls

detector, trackingGeometry, decorators = acts.examples.itk.buildITkGeometry(geo_dir)
field = acts.examples.MagneticFieldMapXyz(str(geo_dir / "bfield/ATLAS-BField-xyz.root"))
rnd = acts.examples.RandomNumbers(seed=args.rnd)

s = acts.examples.Sequencer(events=args.nEvents, numThreads=-1, outputDir=str(outputDir))


# s.addWriter(CsvTrackingGeometryWriter(
#     level=acts.logging.INFO,
#     trackingGeometry=trackingGeometry,
#     outputDir=str(outputDir),
#     writePerEvent=True,
# ))
  


if args.doSingleMu:
    if(args.mu > 0):
        addParticleGun(
            s,
            MomentumConfig(1.0 * u.GeV, 10.0 * u.GeV, transverse=True),
            EtaConfig(-4.0, 4.0, uniform=True),
            ParticleConfig(30, acts.PdgParticle.eMuon, randomizeCharge=True),
            rnd=rnd,
            npileup=args.mu,
            vtxGen=acts.examples.GaussianVertexGenerator(
                stddev=acts.Vector4(0.0125 * u.mm, 0.0125 * u.mm, 55.5 * u.mm, 5.0 * u.ns),
                mean=acts.Vector4(0, 0, 0, 0),
            ),
        )
    else:
        addParticleGun(
            s,
            MomentumConfig(1.0 * u.GeV, 10.0 * u.GeV, transverse=True),
            EtaConfig(-4.0, 4.0, uniform=True),
            ParticleConfig(1, acts.PdgParticle.eMuon, randomizeCharge=True),
            # ParticleConfig(30, acts.PdgParticle.eMuon, randomizeCharge=True),
            vtxGen=acts.examples.GaussianVertexGenerator(
                stddev=acts.Vector4(0.0125 * u.mm, 0.0125 * u.mm, 55.5 * u.mm, 5.0 * u.ns),
                mean=acts.Vector4(0, 0, 0, 0),
            ),
            rnd=rnd,
        )
elif args.dottbar:
    addPythia8(
        s,
        hardProcess=["Top:qqbar2ttbar=on"],
        npileup=args.mu,
        vtxGen=acts.examples.GaussianVertexGenerator(
            stddev=acts.Vector4(0.0125 * u.mm, 0.0125 * u.mm, 55.5 * u.mm, 5.0 * u.ns),
            mean=acts.Vector4(0, 0, 0, 0),
        ),
        rnd=rnd,
        outputDirRoot=outputDir,
    )

addFatras(
    s,
    trackingGeometry,
    field,
    ParticleSelectorConfig(eta=(-4.0, 4.0), pt=(150 * u.MeV, None), removeNeutral=True)
    if args.dottbar or args.mu > 0
    else ParticleSelectorConfig(),
    outputDirRoot=outputDir,
    rnd=rnd,
)

addDigitization(
    s,
    trackingGeometry,
    field,
    digiConfigFile=geo_dir / "itk-hgtd/itk-smearing-config.json",
    outputDirRoot=outputDir,
    rnd=rnd,
)

#addSeeding(
#    s,
#    trackingGeometry,
#    field,
#    TruthSeedRanges(pt=(1.0 * u.GeV, None), eta=(-4.0, 4.0), nHits=(9, None))
#    if args.dottbar or args.mu > 0
#    else TruthSeedRanges(),
#    *acts.examples.itk.itkSeedingAlgConfig("PixelSpacePoints"),
#    geoSelectionConfigFile=geo_dir / "itk-hgtd/geoSelection-ITk.json",
#    outputDirRoot=outputDir,
#)

# addSeeding(
#     s,
#     trackingGeometry,
#     field,
#     *acts.examples.itk.itkSeedingAlgConfig("PixelSpacePoints"),
#     geoSelectionConfigFile=geo_dir / "itk-hgtd/geoSelection-ITk.json",
#     outputDirRoot=outputDir,
# )

# addCKFTracks(
#     s,
#     trackingGeometry,
#     field,
#     CKFPerformanceConfig(ptMin=1.0 * u.GeV if (args.dottbar or args.mu > 0) else 0.0, nMeasurementsMin=6),
#     TrackSelectorRanges(pt=(1.0 * u.GeV, None), absEta=(None, 4.0), removeNeutral=True),
#     outputDirRoot=outputDir,
#     writeTrajectories=True,
# )

# addAmbiguityResolution(
#     s,
#     AmbiguityResolutionConfig(maximumSharedHits=3),
#     CKFPerformanceConfig(ptMin=1.0 * u.GeV if (args.dottbar or args.mu > 0) else 0.0, nMeasurementsMin=6),
#     outputDirRoot=outputDir,
# )

# addVertexFitting(
#     s,
#     field,
#     vertexFinder=VertexFinder.Iterative,
#     outputDirRoot=outputDir,
# )

s.run()
