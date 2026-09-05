# 自动化求职工具（JobHunter）

面向学生求职者的自动化求职工具：采集招聘网站职位信息 → 清洗入库 → 分析薪资 / 技能 / 企业画像 → 基于简历画像做个性化推荐，并用 Streamlit 呈现全流程可视化。

本仓库是短学期《Python 数据分析与可视化》课程项目（往届题目 3「招聘网站职位信息可视化分析与个性化推荐」的自动化升级版）的核心原型。

## 功能

- **市场总览**：岗位数、平均薪资、城市 / 学历 / 岗位分布、薪资分布
- **薪资分析**：分城市 / 学历 / 经验的箱线图；随机森林薪资预测器（MAE、R²、特征重要性）
- **技能图谱**：热门技能 Top 20、词云、技能共现网络
- **我的匹配**：输入技能 / 城市 / 学历 / 期望薪资，输出 Top-N 岗位推荐（TF-IDF 余弦相似度 + 硬过滤）
- **数据链路**：样例数据生成 → 清洗（薪资解析 / 去重 / 标准化）→ SQLite 存储 → 分析（推荐 / 预测 / 聚类）

## 快速开始

### 1. 安装依赖

需要 Python 3.11+。推荐用 venv：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

> 当前开发环境使用系统自带 Python 3.12 + `--system-site-packages` 创建的虚拟环境，依赖已装好；`requirements.txt` 用于其他机器复现。

### 2. 生成样例数据并跑通全流程

```powershell
.\.venv\Scripts\python.exe scripts\run_pipeline.py
```

输出：

- `data/sample/sample_jobs.csv`（320 条确定性样例数据）
- `data/cleaned/cleaned_jobs.csv`（清洗后）
- `data/cleaned/quality_report.json`（数据质量报告）
- `data/jobs.db`（SQLite 数据库）

单独生成样例数据：

```powershell
.\.venv\Scripts\python.exe scripts\generate_sample_data.py --count 320 --seed 42
```

### 3. 启动 Web 应用

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

浏览器访问 `http://localhost:8501`。

## 运行测试

```powershell
.\.venv\Scripts\python.exe -m pytest
```

测试覆盖：薪资解析、去重与标准化、样例数据生成、推荐排序、薪资预测、聚类、SQLite 往返、Streamlit 页面冒烟。

## 目录结构

```text
jobhunter/
├── streamlit_app.py        # Streamlit 入口
├── app_pages/              # 多页面（总览 / 薪资 / 技能 / 匹配）
├── ui/                     # 数据加载与图表辅助
├── analysis/               # 推荐、薪资预测、聚类、技能图谱
├── cleaner/                # 薪资解析、技能提取、清洗流水线
├── storage/                # SQLite / CSV 存取
├── datagen/                # 确定性样例数据生成
├── config/                 # 路径与常量
├── scripts/                # 命令行入口
├── tests/                  # pytest 测试
└── docs/                   # 数据字典等文档
```

## 配置说明

- 数据路径与常量：`config/settings.py`
- Streamlit 主题与服务器：`.streamlit/config.toml`
- 真实招聘网站爬虫计划：`spider/` 模块（本里程碑用样例数据兜底，后续接入智联 / BOSS 直聘等站点）

## 已知说明

- 薪资单位统一为 K/月；`面议` 的岗位薪资列为空，不参与预测训练。
- 样例数据由固定随机种子生成，薪资与城市 / 学历 / 经验挂钩，用于演示算法链路。
- 测试中 `LOKY_MAX_CPU_COUNT` 环境变量用于抑制沙箱环境的 CPU 探测告警。
