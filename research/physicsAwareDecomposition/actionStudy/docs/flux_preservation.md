# Repeated cyclic face-flux loss and bounded correctness controls

The original heldoutMoving mesh trial, repeat 0, fails the predefined full-field endpoint gate: T differs by 0.338292 K. Its timing remains in the dataset and its policy aggregate remains numerically ineligible. Reducing the global timestep or tightening ODE tolerances does not remove the failure.

At the third migration checkpoint (200 μs), cell T, p, U, species, h and rho agree with A0. Cell centres agree to roundoff. The stored face-flux divergence differs by 89437.7 kg m⁻³ s⁻¹, while reconstructed divergence from rho/U agrees within 2.6e-9. The face audit finds eight exactly zero copies on `procBoundary2to1throughleft`, type `processorCyclic`. Their periodic partners retain approximately 5.58986e-5 kg/s. These are missing values, not sign reversals. Repeats 1 and 2 have no such mismatch.

`padFluxState` is an optional correctness reference. Before native migration it writes each physical face centre, dominant axis and globally oriented flux to rank-local snapshots. After migration it matches physical faces and restores their new local orientation. Each rank reads the global face table, so memory and reads scale with global face count. Axis-aligned stationary geometry, x-origin zero and translational x-periodicity are its explicit scope; the default period is 0.02 m. Rotated cyclic faces, moving geometry and production-scale distributed matching are not supported. Inputs must be consistent across duplicate faces; conflicting nonzero values cause an error.

```bash
bash actionStudy/scripts/buildFluxState.sh
mpirun --bind-to core --map-by core --nooversubscribe -np 4 padFluxState -parallel -time 0.0002
mpirun --bind-to core --map-by core --nooversubscribe -np 4 redistributeParPAD -parallel -overwrite -time 0.0002
mpirun --bind-to core --map-by core --nooversubscribe -np 4 padFluxState -restore -parallel -time 0.0002
```

The separate `-repairZeroCoupled` diagnostic permits a missing exact-zero duplicate to be filled by its existing nonzero partner. It is used on copies of the original failed state and does not use A0 fields for restoration. All three corrected original-state controls pass the original endpoint gate; maximum T difference is below 1e-10 K. This specialized repair is not an arbitrary corruption recovery rule.

Six separate manual-decomposition controls replay the exact three observed ownership maps, with and without the snapshot utility. All pass. Manual mapping itself does not reproduce the original cyclic patch loss, so the evidence does not identify ownership alone as its cause or isolate the exact native source instruction responsible. The first attempt to redistribute an unoriented scalar flux field fails and remains in `data/raw/fluxRepairRejected`; the delivered utility bypasses that native field mapper.

Preparation, migration, restoration and continuation process costs are individually recorded in `flux_repair.json`. The original live study is not rerun or relabelled with this repair. The utility does not support a new controller speedup claim. `fluxRepair.py` regenerates the separate controls, retaining incomplete attempts and preserving all original trials and gate thresholds.
