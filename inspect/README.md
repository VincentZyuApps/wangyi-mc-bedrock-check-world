# 🔎 Inspect Toolkit

这里有 5 个主题脚本，加一个共享模块：

- `inspect_common.py`
- `01_world_overview.py`
- `02_leveldat_inspect.py`
- `03_player_inspect.py`
- `04_inventory_inspect.py`
- `05_db_patterns_inspect.py`

## 🎯 目标

- 🧩 每个脚本只负责一个主题
- 🎮 支持交互式选择存档
- ⌨️ 也支持命令行参数直接选中存档
- 🔁 参数解析失败时，会自动回退到交互式选择

## 🕹️ 交互方式

直接运行任意脚本，比如：

```powershell
python .\inspect\01_world_overview.py
```

会进入交互式选择：

- ⬆️ `↑ / ↓` 切换存档
- ✅ `Enter` 确认
- ❌ `Esc` 退出

## ⌨️ 直接传参

### ⭐ 最常用的 3 个参数

这 3 个参数是最值得记住的：

- 🔢 `--index`
  按顺序直接选择第几个存档，适合你已经知道大概排位的时候
- 📁 `--folder`
  按文件夹名直接选择存档，适合你已经知道具体目录名的时候
- 🧾 `--json`
  直接输出结构化 JSON，适合保存结果、喂给别的脚本、或者后续做 GUI / 自动化处理

### 🔢 按顺序选

> `python .\inspect\02_leveldat_inspect.py --index 1`

### 📁 按文件夹名选

> `python .\inspect\03_player_inspect.py --folder "+f5urF+txhQ="`

### 🧾 输出 JSON

> `python .\inspect\04_inventory_inspect.py --index 1 --json`

如果 `--index` 或 `--folder` 解析失败，脚本会回退到交互式选择，不会直接报错退出。

> 组合起来也很好用，比如：
> 
> ```bash
> python .\inspect\02_leveldat_inspect.py --index 1 --json
> python .\inspect\03_player_inspect.py --folder "+f5urF+txhQ="
> python .\inspect\04_inventory_inspect.py --folder "HZ7NPA0xCw8=" --json
> ```

## 🧰 每个脚本是干什么的

### 1️⃣ 01_world_overview.py

看世界整体概况。

输出内容：
- 世界名
- 文件夹名
- 路径
- 总大小
- `config` 里的网易关键信息
- 行为包 / 资源包数量

### 2️⃣ 02_leveldat_inspect.py

看 `level.dat` 的核心元数据。

输出内容：
- NBT 偏移
- `LevelName`
- `GameType`
- `Difficulty`
- `InventoryVersion`
- `NetworkVersion`
- `RandomSeed`
- 出生点
- 时间
- abilities / experiments

### 3️⃣ 03_player_inspect.py

看 `local_player` 的状态信息。

输出内容：
- 坐标
- 朝向
- 维度
- 游戏模式
- 当前选中槽位
- 死亡点
- 出生点
- 玩家属性

### 4️⃣ 04_inventory_inspect.py

看玩家物品容器。

输出内容：
- `Armor`
- `Inventory`
- `EnderChestInventory`
- `Mainhand`
- `Offhand`

重点展示非空物品。

### 5️⃣ 05_db_patterns_inspect.py

看 `db` 里大概都存了哪些类型的东西。

输出内容：
- `local_player`
- `playerish`
- `positionish`
- `attributeish`
- `inventoryish`
- `entityish`
- `recipeish`
- `block_item_names`
- 每个 `.log/.ldb` 文件的模式命中数量

## 🚀 推荐顺序

第一次看某个世界，建议这样跑：

```powershell
python .\inspect\01_world_overview.py
python .\inspect\02_leveldat_inspect.py
python .\inspect\03_player_inspect.py
python .\inspect\04_inventory_inspect.py
python .\inspect\05_db_patterns_inspect.py
```

## 📌 当前状态

这套脚本已经在真实网易基岩世界上跑通过。

目前已经确认：

- 🧱 `level.dat` 可按 Bedrock 小端 NBT 读取
- 🧍 `local_player` 可读出坐标、属性、物品栏
- 📦 网易版的 `config` 和 pack 清单是附加 sidecar 数据
