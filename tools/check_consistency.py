"""核对指标字典 CSV 与方案文档的一致性。

检查两处：
1. 第四部分"指标总表"：每个指标的 ★ 和依赖校验与 CSV 一致；
2. 第六部分"指标 × 校验对照"：● / ○ 与 CSV 的依赖校验 / 辅助校验一致。

用法（在仓库根目录）：python3 tools/check_consistency.py
"""
import csv
import re
import sys

DOC = 'docs/研发数据体系方案.md'
CSV = 'metrics/指标字典.csv'
COLS = ['1.1', '1.2', '1.3', '1.4', '2.1', '2.2', '2.3', '2.4',
        '3.1', '3.2', '3.3', '4.1', '4.2', '5.1', '5.2']

rows = list(csv.reader(open(CSV, encoding='utf-8-sig')))[1:]
md = open(DOC, encoding='utf-8').read()

table = {}
for m in re.finditer(r'^\| ([EPAQGF]0\d) \| ([^|]+?) \|\s*(★?)\s*\| ([^|]+?) \| ([^|]+?) \|$', md, re.M):
    table[m.group(1)] = (m.group(3) == '★', m.group(5).replace('、', '；'))

matrix = {}
for line in md.splitlines():
    if line.count('|') != len(COLS) + 2:
        continue
    m = re.match(r'^\| ([EPAGF]0\d)[^|]*\|(.*)\|$', line) or re.match(r'^\| (Q02) / Q03 \|(.*)\|$', line)
    if m:
        cells = [c.strip() for c in m.group(2).split('|')]
        matrix[m.group(1)] = (sorted(c for c, v in zip(COLS, cells) if v == '●'),
                              sorted(c for c, v in zip(COLS, cells) if v == '○'))

problems = []
for r in rows:
    code = r[0]
    if code not in table:
        problems.append(f'{code}: 指标总表中找不到')
        continue
    star, deps = table[code]
    if (r[3] == '是') != star:
        problems.append(f'{code}: ★ 不一致')
    if deps != r[11]:
        problems.append(f'{code}: 依赖校验不一致（文档 {deps} / CSV {r[11]}）')
    if code in matrix:
        dep = sorted(x for x in r[11].split('；') if x != '—')
        aux = sorted(x for x in r[12].split('；') if x != '—')
        if matrix[code] != (dep, aux):
            problems.append(f'{code}: 对照矩阵不一致（文档 {matrix[code]} / CSV {(dep, aux)}）')

print(f'CSV {len(rows)} 行；指标总表 {len(table)} 行；对照矩阵 {len(matrix)} 行')
if problems:
    print('\n'.join(problems))
    sys.exit(1)
print('一致')
