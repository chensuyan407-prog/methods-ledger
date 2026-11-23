# Author question checklist (methods-ledger)

Ask only what the materials cannot answer; quote the conflicting sources.

| group | question | typical evidence that answers it |
|---|---|---|
| steps | order of stages; output and decision rule of each stage | run logs with timestamps, pipeline scripts |
| setup | hardware model and count of the reported run; software versions actually installed | log header, `pip freeze`, `nvidia-smi` |
| parameters | which value the reported run used when config, CLI and notes differ | run log (`Namespace(...)`, hparams dump) |
| data | dataset version / snapshot date; split sizes, method (random/stratified/official) and seed; filters with counts | data card, preprocessing log |
| controls | baselines: implementation + version, same data, same tuning budget?; checkpoint selection; metric definition and split | baseline configs/logs |
| repetitions | number of independent runs/replicates, seeds, mean ± SD or single run | per-seed logs, results table |
| statistics | test, alpha, correction; or uncertainty estimate | analysis script |
| reproducibility | commit/tag, exact commands, environment file, data access (URL/DOI, licence) | git log, launch script |
| limitations | untested conditions where the method may fail (data, scale, hardware, settings) | facts: single seed, one version, truncation, untuned baseline |
