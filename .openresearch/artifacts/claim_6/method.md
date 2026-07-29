# Claim 6 method

First run one actual optimizer step per method at the smallest reported
dimension (`y_dim=200`) with the released data generator, predictor, objective,
Adam learning rate, and batch size 8. Use identical data and predictor
initialization, eight CPU cores, and LPGD's paper-required `1e-12` solver
tolerance. This is a resource calibration only and cannot issue a claim
verdict.

The next child will use the observed step and construction costs to
independently fix the largest defensible full training horizon and seed count.
It must compare complete loss curves and runtime for actual LPGD and FFOLayer,
not a missing-import control or a nearby unrolling algorithm.
