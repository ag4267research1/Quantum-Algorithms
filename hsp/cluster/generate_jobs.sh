#!/usr/bin/env bash
# Generate one job folder per (n, shots) combination for a Deutsch-Jozsa
# parameter sweep on a Slurm cluster.
#
# Each combination gets its own folder under runs/, named n<N>_shots<S>,
# holding a config.yaml and a job.slurm that runs hsp/dj_hsp/run.py against
# it. Every job's results_dir is set to "." (its own folder), so results
# from different (n, shots) combinations are never mixed together.
#
# Usage:
#   ./generate_jobs.sh
#   N_VALUES="2 4 6" SHOTS_VALUES="256 1024" ./generate_jobs.sh
#   PARTITION=gpu ACCOUNT=my_alloc TIME=00:30:00 ./generate_jobs.sh
#
# Then submit everything with:
#   ./submit_all.sh
set -euo pipefail

# --- sweep grid: every (n, shots) pair is one job -----------------------
N_VALUES="${N_VALUES:-2 4 6 8}"
SHOTS_VALUES="${SHOTS_VALUES:-256 1024 4096}"

# --- oracle / algorithm settings, the same for every job ----------------
KIND="${KIND:-balanced}"                  # constant | balanced
SECRET="${SECRET:-null}"                  # YAML null, or a fixed n-bit string
CONSTANT_VALUE="${CONSTANT_VALUE:-0}"
SEED="${SEED:-7}"
BACKEND="${BACKEND:-aer_simulator}"
MEMORY="${MEMORY:-false}"

# --- Slurm settings: edit these for your cluster, or override via env ---
ACCOUNT="${ACCOUNT:-}"            # your allocation/project id; leave empty if none
PARTITION="${PARTITION:-compute}"
QOS="${QOS:-}"                    # leave empty if your cluster has no QOS
NTASKS="${NTASKS:-1}"
CPUS_PER_TASK="${CPUS_PER_TASK:-1}"
TIME="${TIME:-00:10:00}"
CONDA_MODULE="${CONDA_MODULE:-}"  # e.g. anaconda3/2024.10-1; leave empty if
                                   # conda is already on PATH without a module
CONDA_ENV="${CONDA_ENV:-qalgos}"  # env name, or an absolute env path

CLUSTER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$CLUSTER_DIR/../.." && pwd)"
RUNS_DIR="$CLUSTER_DIR/runs"
RUN_PY="$REPO_DIR/hsp/dj_hsp/run.py"

log() { printf '\n==> %s\n' "$*"; }

mkdir -p "$RUNS_DIR"

count=0
for n in $N_VALUES; do
  for shots in $SHOTS_VALUES; do
    job_dir="$RUNS_DIR/n${n}_shots${shots}"
    mkdir -p "$job_dir"

    cat > "$job_dir/config.yaml" <<YAML
n: $n
kind: $KIND
constant_value: $CONSTANT_VALUE
secret: $SECRET
seed: $SEED
shots: $shots
backend: $BACKEND
memory: $MEMORY
results_dir: .              # this folder: keeps each job's results with its own config
shots_sweep: null
YAML

    account_directive=""
    [ -n "$ACCOUNT" ] && account_directive=$'#SBATCH --account='"$ACCOUNT"$'\n'
    qos_directive=""
    [ -n "$QOS" ] && qos_directive=$'#SBATCH --qos='"$QOS"$'\n'
    module_load=""
    [ -n "$CONDA_MODULE" ] && module_load=$'module load '"$CONDA_MODULE"$'\n'

    cat > "$job_dir/job.slurm" <<SLURM
#!/usr/bin/env bash
#SBATCH --job-name=dj_n${n}_s${shots}
${account_directive}#SBATCH --partition=$PARTITION
${qos_directive}#SBATCH --ntasks=$NTASKS
#SBATCH --cpus-per-task=$CPUS_PER_TASK
#SBATCH --time=$TIME
#SBATCH --output=$job_dir/slurm_%j.out
#SBATCH --error=$job_dir/slurm_%j.err

set -euo pipefail

${module_load}source "\$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV"

cd "$job_dir"
python "$RUN_PY" config.yaml
SLURM

    chmod +x "$job_dir/job.slurm"
    count=$((count + 1))
    log "wrote $job_dir/{config.yaml,job.slurm}"
  done
done

log "Generated $count job folder(s) under $RUNS_DIR"
echo "Submit them all with: ./submit_all.sh"
