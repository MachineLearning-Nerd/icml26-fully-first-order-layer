# Claim 5 — VERIFIED

**Contract.** The released PyTorch layer is objective-agnostic through the
detached coefficient `c := detach(dF/dy*)`, and can replace CvxpyLayer with
minimal call-site change.

The actual released PyTorch layer and actual CvxpyLayer were compared in 27
checks spanning QPs and LPs, three seeds, and three upper objectives. The call
shape was unchanged, only constructor/tolerances changed. Maximum output error
was `3.804e-9`, maximum gradient relative error `9.820e-5`, and minimum
gradient cosine `0.9999999952`. Reusing one lower solution across objectives
also passed.

- Raw: [claim 5 JSON](../../../evidence/current/claim_5.json)
- Contract: [claim contract](../../../evidence/current/contracts/claim_5/claim_contract.json), [source audit](../../../evidence/current/contracts/claim_5/source_audit.md)
- Code: [native comparison](../../../evidence/current/code/native_layer.py), [checker](../../../evidence/current/code/native_check.py)
- Control: wrong detached coefficient exits 2 in [control output](../../../evidence/current/negative_control_output.txt)

Limit: “minimal” is operationalized as the released constructor substitution
with the same forward call shape, not a claim about every downstream codebase.
