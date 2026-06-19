import os

base = 'skills/全域专家团'
platforms = [
    'dist-v2/claude-code/.claude/agents',
    'dist-v2/codex-cli/.codex/agents',
    'dist-v2/hermes/skills'
]

results = {}
for plat in platforms:
    pname = plat.split('/')[1]
    for (dirpath, dirnames, filenames) in os.walk(base):
        for fn in filenames:
            if fn != 'SKILL.md':
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), base)
            # For hermes, rel is like 'constraint-flexible-rules/SKILL.md'
            # dist path: dist-v2/hermes/skills/constraint-flexible-rules/SKILL.md
            dist_path = os.path.join(plat, rel)
            if not os.path.exists(dist_path):
                continue
            with open(os.path.join(dirpath, fn), encoding='utf-8') as f:
                a = f.read()
            with open(dist_path, encoding='utf-8') as f:
                b = f.read()
            if a == b:
                status = 'SAME'
            else:
                status = 'DIFF'
            key = rel
            if key not in results:
                results[key] = {}
            results[key][pname] = status

print('=== SKILL.md 文件差异汇总 ===')
all_same = []
any_diff = []
for k in sorted(results.keys()):
    vals = list(results[k].values())
    if all(v == 'SAME' for v in vals):
        all_same.append(k)
    else:
        any_diff.append(k + ' : ' + str(results[k]))

print(f'\n完全一致（所有平台）: {len(all_same)} 个')
for x in all_same:
    print(f'  ✓ {x}')
print(f'\n存在差异: {len(any_diff)} 个')
for x in any_diff:
    print(f'  ✗ {x}')
