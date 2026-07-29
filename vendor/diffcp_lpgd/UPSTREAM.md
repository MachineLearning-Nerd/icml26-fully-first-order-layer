# Vendored LPGD diffcp fork

Source: `https://github.com/martius-lab/diffcp-lpgd`, branch `LPGD`.

Pinned commit: `3e7243a808ce983279e31c24932188ee905c58d0`.

The four Python source files are copied from that commit. Imports are renamed
from `diffcp` to `diffcp_lpgd` so the fork can coexist with the locked upstream
`diffcp` package. The compiled `_diffcp` extension continues to come from the
locked package. The LPGD algorithm, `tau=1e-4`, and `rho=0.1` are unchanged.
