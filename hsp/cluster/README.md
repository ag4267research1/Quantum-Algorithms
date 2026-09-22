# hsp/cluster

Runs a Deutsch-Jozsa parameter sweep (over `n` and `shots`) on a Slurm
cluster, one job per combination, each with its own folder, config and
results.

```bash
./generate_jobs.sh    # creates runs/n<N>_shots<S>/{config.yaml,job.slurm}
./submit_all.sh        # sbatch's every job.slurm it finds under runs/
```

## What `generate_jobs.sh` does

For every combination of `N_VALUES` x `SHOTS_VALUES`, it creates
`runs/n<N>_shots<S>/` holding:

* `config.yaml` -- the same schema as [`hsp/dj_hsp/config.yaml`](../dj_hsp/config.yaml),
  with `n` and `shots` set from the sweep and `results_dir: .` (this same
  folder), so a job's results never land anywhere but next to its own config.
* `job.slurm` -- activates the `qalgos` environment and runs
  `hsp/dj_hsp/run.py config.yaml`; its Slurm `--output`/`--error` logs are
  also written into this folder.

Override the sweep grid and the oracle/algorithm settings with environment
variables:

```bash
N_VALUES="2 4 6 8 10" SHOTS_VALUES="256 1024 4096 16384" ./generate_jobs.sh
KIND=constant SEED=42 ./generate_jobs.sh
```

See the top of `generate_jobs.sh` for every variable (`KIND`, `SECRET`,
`CONSTANT_VALUE`, `SEED`, `BACKEND`, `MEMORY`).

## Slurm settings

These are cluster-specific, so set them for yours via environment variables
(defaults shown):

| Variable        | Default    | Meaning                                          |
|-----------------|------------|---------------------------------------------------|
| `ACCOUNT`       | *(empty)*  | allocation/project id; omitted if empty            |
| `PARTITION`     | `compute`  | Slurm partition                                    |
| `QOS`           | *(empty)*  | QOS; omitted if empty                              |
| `NTASKS`        | `1`        | `--ntasks`                                         |
| `CPUS_PER_TASK` | `1`        | `--cpus-per-task`                                  |
| `TIME`          | `00:10:00` | wall time limit                                    |
| `CONDA_MODULE`  | *(empty)*  | `module load` target, e.g. `anaconda3/2024.10-1`; skipped if empty |
| `CONDA_ENV`     | `qalgos`   | environment name, or an absolute env path          |

Example for a cluster that needs an account, a QOS and a module:

```bash
ACCOUNT=my_alloc PARTITION=RM-shared QOS=low CONDA_MODULE=anaconda3/2024.10-1 \
  N_VALUES="2 4 6" SHOTS_VALUES="1024 4096" ./generate_jobs.sh
```

## Submitting and tracking

```bash
./submit_all.sh
```

This runs `sbatch --parsable` on every `runs/*/job.slurm`, prints each job
ID next to its folder, and writes `runs/submitted_jobs.tsv` (job ID, folder)
so you can match a finished job back to its results later. Track them with:

```bash
squeue -u $USER
```

## Results

Each folder ends up with everything for that one (n, shots) run: its
`config.yaml`, its `job.slurm`, the Slurm `slurm_<jobid>.out`/`.err` logs,
and `run.py`'s own JSON output (or `.xlsx`, if a job's `config.yaml` is
edited to set `shots_sweep`). Nothing is shared between folders, so results
never get mixed up across the sweep.

`runs/` is created locally by `generate_jobs.sh` and is not committed (see
`.gitignore`).
