/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Website:  https://openfoam.org
    \\  /    A nd           | Version:  8
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "system";
    object      decomposeParDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

numberOfSubdomains  NUM;

//- Keep owner and neighbour on same processor for faces in zones:
// preserveFaceZones (heater solid1 solid3);

//- Keep owner and neighbour on same processor for faces in patches:
//  (makes sense only for cyclic patches)
//preservePatches (cyclic_left_right);

//- Use the volScalarField named here as a weight for each cell in the
//  decomposition.  For example, use a particle population field to decompose
//  for a balanced number of particles in a lagrangian simulation.
// weightField dsmcRhoNMean;

// method          metis;
// method          hierarchical;
// method          simple;
// method          metis;
method          scotch;
// method          manual;

simpleCoeffs
{
    n           (NUM 1 1);
    delta       0.001;
}

hierarchicalCoeffs
{
    n           (2 2 1);
    delta       0.001;
    order       xyz;
}

metisCoeffs
{
/*
    processorWeights
    (
        1
        1
        1
        1
    );
*/
}

scotchCoeffs
{
    //processorWeights
    //(
    //    1
    //    1
    //    1
    //    1
    //);
    //writeGraph  true;
    //strategy "b";
}

manualCoeffs
{
    dataFile    "cellDecomposition";
}


// Is the case distributed
// distributed     yes;
// Per slave (so nProcs-1 entries) the directory above the case.
// roots
// (
//     "/tmp"
//     "/tmp"
// );

// ************************************************************************* //
