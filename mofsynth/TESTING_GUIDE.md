# Model Prediction Guide | 模型预测指南

## Overview | 概述

After training your PU-Learning models, use `test_model.sh` to predict CLscores for new crystal structures.

训练完 PU-Learning 模型后，使用 `test_model.sh` 为新晶体结构预测 CLscore。

---

## Quick Start | 快速开始

### Step 1: Prepare Your Data | 准备数据

Place your CIF files in the prediction directory:

将 CIF 文件放在预测目录中：

```bash
cd /opt/data/private/moffusion/mofsynth/prediction

# Create cif_files directory if it doesn't exist
mkdir -p cif_files

# Copy your CIF files here
cp /path/to/your/*.cif cif_files/

# Create id_prop.csv file
# Format: crystal_id,synthesizable
# Example:
cat > cif_files/id_prop.csv << EOF
your_structure_1,0
your_structure_2,0
your_structure_3,0
EOF
```

**Important Notes | 重要说明:**
- Use `synthesizable=0` for all structures you want to predict
- The `crystal_id` must match the CIF filename (without `.cif` extension)
- Example: For `mof_123.cif`, use `mof_123,0` in the CSV

**重要说明:**
- 对所有要预测的结构使用 `synthesizable=0`
- `crystal_id` 必须与 CIF 文件名匹配（不含 `.cif` 扩展名）
- 示例：对于 `mof_123.cif`，在 CSV 中使用 `mof_123,0`

### Step 2: Generate Crystal Graphs | 生成晶体图

If you haven't already generated crystal graphs for your CIF files:

如果还没有为 CIF 文件生成晶体图：

```bash
python generate_crystal_graph.py \
    --cifs ./cif_files \
    --n 12 \
    --r 8 \
    --f ./saved_crystal_graph
```

This step creates pickle files for faster loading during prediction.

这一步创建 pickle 文件以加速预测时的加载。

### Step 3: Run Prediction | 运行预测

```bash
./test_model.sh
```

Or with custom parameters:

或使用自定义参数：

```bash
python ./prediction/predict_PU_learning.py \
    --cifs ./cif_files \
    --graph ./saved_crystal_graph \
    --modeldir ./trained_models \
    --bag 50 \
    --batch-size 64 \
    --workers 0
```

---

## Understanding the Results | 理解结果

### Output File | 输出文件

Results are saved in: `./prediction/test_results_ensemble_50models.csv`

结果保存在：`./prediction/test_results_ensemble_50models.csv`

### CSV Format | CSV 格式

```csv
id,CLscore,bagging
your_structure_1,0.7543,50
your_structure_2,0.3212,50
your_structure_3,0.8901,50
```

### Interpreting CLscore | 解释 CLscore

- **CLscore Range**: 0.0 to 1.0
- **Higher CLscore** (closer to 1.0) = **More synthesizable**
- **Lower CLscore** (closer to 0.0) = **Less synthesizable**

**CLscore 范围**：0.0 到 1.0
- **更高的 CLscore**（接近 1.0）= **更易合成**
- **更低的 CLscore**（接近 0.0）= **更难合成**

**Typical Thresholds | 典型阈值:**
- **CLscore > 0.7**: High synthesizability (similar to ICSD structures)
- **0.5 < CLscore < 0.7**: Moderate synthesizability
- **CLscore < 0.5**: Low synthesizability (unusual or unstable structures)

**典型阈值:**
- **CLscore > 0.7**：高可合成性（类似于 ICSD 结构）
- **0.5 < CLscore < 0.7**：中等可合成性
- **CLscore < 0.5**：低可合成性（不寻常或不稳定的结构）

---

## Parameters | 参数说明

### test_model.sh Parameters

| Parameter | Default | Description | 描述 |
|-----------|---------|-------------|------|
| `NUM_MODELS` | `50` | Number of ensemble models to use | 使用的集成模型数量 |
| `BATCH_SIZE` | `64` | Batch size for prediction | 预测批次大小 |
| `CIF_FILES_DIR` | `./prediction/cif_files` | Directory with CIF files | CIF 文件目录 |
| `GRAPH_DIR` | `./prediction/saved_crystal_graph` | Directory with crystal graphs | 晶体图目录 |
| `MODEL_DIR` | `./prediction/trained_models` | Directory with trained models | 训练模型目录 |

### Command-Line Arguments | 命令行参数

```
--cifs DIR           Directory containing CIF files and id_prop.csv
--graph DIR          Directory containing pre-generated crystal graphs
--modeldir DIR       Directory containing trained model checkpoints
--bag N              Number of ensemble models (1-50 or 100)
--batch-size N       Mini-batch size for prediction (default: 64)
--workers N          Number of data loading workers (default: 0)
```

---

## Performance Tips | 性能建议

### Speed vs Accuracy | 速度与准确性

**More Models** (Higher NUM_MODELS):
- ✅ Better prediction stability
- ✅ Lower variance
- ❌ Slower prediction

**Fewer Models** (Lower NUM_MODELS):
- ✅ Faster prediction
- ❌ Higher variance
- ❌ Less robust

### Batch Size | 批次大小

- **Small batch** (32): Less memory, slower
- **Large batch** (128, 256): Faster, more memory

**Recommended | 推荐:** `batch-size=64` (default)

---

## Troubleshooting | 故障排除

### Issue: "atom_init.json does not exist!"

**Solution | 解决方案:**
```bash
cp atom_init.json ./cif_files/
```

### Issue: "id_prop.csv does not exist!"

**Solution | 解决方案:**
```bash
# Create id_prop.csv with your CIF IDs
cat > ./cif_files/id_prop.csv << EOF
structure1,0
structure2,0
structure3,0
EOF
```

### Issue: "No trained models found"

**Solution | 解决方案:**
```bash
# Check if models exist
ls -lh ./prediction/trained_models/*.pth.tar

# If not found, train models first
./train_model.sh
```

### Issue: Prediction is very slow

**Possible causes | 可能原因:**
1. Generating crystal graphs on-the-fly
   - **Fix | 修复:** Run `generate_crystal_graph.py` first

2. Too many models
   - **Fix | 修复:** Reduce `--bag` parameter

3. Small batch size
   - **Fix | 修复:** Increase `--batch-size` to 128 or 256

---

## Example Workflow | 完整工作流程示例

```bash
# 1. Prepare CIF files
cd /opt/data/private/moffusion/mofsynth/prediction
mkdir -p cif_files
cp /path/to/new_structures/*.cif cif_files/

# 2. Create id_prop.csv
ls cif_files/*.cif | sed 's/cif_files\///;s/\.cif$/,0/' > cif_files/id_prop.csv

# 3. Generate crystal graphs (one-time)
python generate_crystal_graph.py \
    --cifs ./cif_files \
    --n 12 \
    --r 8 \
    --f ./saved_crystal_graph

# 4. Run prediction
./test_model.sh

# 5. Check results
head -20 test_results_ensemble_50models.csv
```

---

## Advanced Usage | 高级用法

### Predicting with Specific Models

Use only the first 10 models:

仅使用前 10 个模型：

```bash
python ./prediction/predict_PU_learning.py \
    --cifs ./cif_files \
    --graph ./saved_crystal_graph \
    --modeldir ./trained_models \
    --bag 10 \
    --batch-size 64
```

### Batch Processing Large Datasets

For large datasets (>10k structures), split into multiple CSV files:

对于大型数据集（>10k 结构），分割成多个 CSV 文件：

```bash
# Split id_prop.csv into chunks of 1000
split -l 1000 cif_files/id_prop.csv cif_files/batch_

# Process each batch
for batch in cif_files/batch_*; do
    mv $batch cif_files/id_prop.csv
    ./test_model.sh
    mv test_results_ensemble_50models.csv results_${batch}.csv
done
```

---

## Related Scripts | 相关脚本

- `train_model.sh` - Train ensemble models
- `predict_PU_learning.py` - Prediction script (called by test_model.sh)
- `generate_crystal_graph.py` - Generate crystal graphs from CIFs
- `main_PU_learning.py` - Training script (called by train_model.sh)

---

**Last Updated | 最后更新:** 2026-01-04
**Training Status | 训练状态:** ✅ 50 models trained successfully
**Models Location | 模型位置:** `./prediction/trained_models/`
