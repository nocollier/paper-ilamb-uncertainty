# ILAMB Uncertainty Paper

## Introduction

This is a paper about including reference data uncertainty when synthesizing model performance.

Modelers use benchmarking tools to evaulate model predictions with respect to reference data.

To evaluate we calculate bias and RMSE (and other quantities) between models and reference data.

More philosophy about the importance or usefulness of synthesis.

While we frequently attribute the cause of a high bias or RMSE to a departure of the model data from the reference, it can also be because of reference data uncertainty.

This is important because errors can lead model developers to focus on parameterization improvements. If we report large errors in areas where the reference data is uncertain, then we mislead this develpoment.

To address this problem we propose a change to the ILAMB methodology that accounts for reference uncertainty when given.

While there are not a lot of global scale reference datasets that include uncertainty, there are some. However, what they mean by providing uncertainty varies.

The meaning of uncertainty varies in the reference data.

While more reference data products provide uncertainty estimates, there is not uniformity in what that uncertainty represents. In CLASS its blah while in CARDAMOM its blah. We shy away from uncertainty from method, such as in FLUXNET-MTE.

Due to this ambiguity, we do not want to make methodological assumptions about (e.g. normally distributed) what the uncertainty constitutes. For this reason our methodology will adopt a simple "perfect in the envelope" paradigm.

It is not that we declare models perfect if in the envlope of uncertainty, it is rather that we are not comfortable reporting such areas as bad when our notion is so uncertain. These changes prevent modeler from assuming an error is their model and chasing down a bad lead.

Goal: Incoporate uncertainty into the ILAMB scoring methods.

## Methods

Generalization of the Collier2018 in the Hoffman nbp dataset.

...

Cartoons illustrating how big the changes may be and motivting why it is important to consider.

Blunts the sharpness of our measuring tool--creates a feedback mechanism for when constraints are not tight enough.

## Datasets

A subsection for each broad class of datasets

- LORA/DOLCE/CLASS, make a comparison of source spread/std and CLASS uncertainty
- CARDAMOM
- Fluxnet
- ...

We will want to talk about what uncertainty represents in each dataset.

Summarizing table of the reference data used with explanations of what uncertainty means for each.

## Experimental Setup

Describe the numerical experiment we designed to highlight and explain the consequences. Table of the model data? Pointers to the ilamb assets.

## Results

Scores only increase. Literally "number go up". This is by construction, because we are discounting errors by the uncertainty. As the uncertainty tends to 0, the new method reduces to the old method.

For the reference and model data selected, there is no large change in model rankings. Pairwise plots of new vs old. This implies that we have not committed a large sin in ignoring uncertainty. It is rather that score maps stand to communicate more information about where models are truly deficient.

Specific cases

- Small changes: call them out but then show a few maps of what that looks like?
- Larger changes: call them out but then show a few maps of what that looks like?
- Anomalies:
  - soil carbon, especially Soil Grids 2, product is not useful for constraining models, feedback loop to data providers for tighter constraints
  - constrast to Wang where data is USA and therefore certainties are tighter
  - look at the 2 different uncertainty representations in WangMao

Select and show maps with clear interpretability improvements.

## Conclusion

Provides a feedback mechanism to reference data producers and providers of when we need better data.
