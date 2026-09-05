# 数据字典

## 原始字段（样例数据 / 爬虫目标字段）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| title | str | 职位名称 |
| city | str | 工作城市 |
| education | str | 学历要求（本科 / 硕士 / 大专 / 学历不限） |
| experience | str | 经验要求（经验不限 / 在校/应届 / 1-3年 / 3-5年 / 5-10年） |
| company | str | 公司名称 |
| company_size | str | 公司规模（少于50人 / 50-150人 / 150-500人 / 500-2000人 / 2000人以上） |
| company_type | str | 公司性质（民营 / 国企 / 外资 / 合资 / 上市公司） |
| salary_text | str | 原始薪资文本，如 `15-25K·14薪`、`1-2万/月`、`面议` |
| skills | str | 逗号分隔的技能标签 |
| description | str | 职位描述 |
| publish_date | str | 发布日期（YYYY-MM-DD） |
| link | str | 职位链接 |

## 清洗后新增字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| salary_min | float | 月薪下限（K/月），`面议` 为空 |
| salary_max | float | 月薪上限（K/月），`面议` 为空 |
| salary_avg | float | 平均月薪（K/月），`(min+max)/2` |
| skill_list | list[str] | 技能标签列表 |
| skill_count | int | 技能数量 |

## 薪资解析规则

| 输入示例 | salary_min | salary_max | salary_avg |
| --- | --- | --- | --- |
| `15-25K` | 15.0 | 25.0 | 20.0 |
| `15-25K·14薪` | 15.0 | 25.0 | 20.0 |
| `8千-1.2万/月` | 8.0 | 12.0 | 10.0 |
| `1-2万/月` | 10.0 | 20.0 | 15.0 |
| `面议` / `薪资面议` | 空 | 空 | 空 |

## 质量报告（data/cleaned/quality_report.json）

- `rows_before` / `rows_after`：清洗前后行数
- `duplicates_removed`：按（职位 + 公司 + 城市 + 薪资文本）去重删除的行数
- `missing_rate`：各关键字段缺失率
- `education_distribution`：学历类别分布
