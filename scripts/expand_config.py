import copy
import sys

import yaml

with open(sys.argv[1]) as fin:
    cfg = yaml.safe_load(fin)

cfg["No Uncertainty"] = copy.deepcopy(cfg["Uncertainty"])


def _negate_uncertainty(data):
    out = {}
    for key, val in data.items():
        if isinstance(val, dict):
            out[key] = _negate_uncertainty(val)
        elif key == "use_uncertainty":
            out[key] = False
        else:
            out[key] = val
    return out


cfg["No Uncertainty"] = _negate_uncertainty(cfg["No Uncertainty"])

print(yaml.dump(cfg))
