#!/bin/bash

for i in {0..5};
do
    Examples/Scripts/Python/full_chain_itk.py --doSingleMu --mu 0 --rnd ${i} --nEvents 5000
    Examples/Scripts/Python/full_chain_itk.py --doSingleMu --mu 40 --rnd ${i} --nEvents 20
    Examples/Scripts/Python/full_chain_itk.py --doSingleMu --mu 200 --rnd ${i} --nEvents 10

    Examples/Scripts/Python/full_chain_itk.py --dottbar --mu 40 --rnd ${i} --nEvents 20
    Examples/Scripts/Python/full_chain_itk.py --dottbar --mu 200 --rnd ${i} --nEvents 10
done
