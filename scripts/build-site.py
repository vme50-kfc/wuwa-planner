"""Build the GitHub Pages index from the planner's Markdown."""
from html import escape
from hashlib import sha256
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
REPO = 'https://github.com/vme50-kfc/wuwa-planner'
LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
BOLD = re.compile(r'\*\*(.+?)\*\*')


def asset(name):
    path = f'assets/{name}'
    digest = sha256((ROOT / 'docs' / path).read_bytes()).hexdigest()[:12]
    return f'{path}?v={digest}'


def inline(text):
    def bold(chunk):
        return BOLD.sub(r'<strong>\1</strong>', escape(chunk))
    cursor = 0
    parts = []
    for match in LINK.finditer(text):
        parts.append(bold(text[cursor:match.start()]))
        label, url = match.groups()
        team = re.fullmatch(r'#(\d{2})-号队', url)
        if team:
            url = '#team-' + team[1]
        attrs = ' target="_blank" rel="noopener noreferrer"' if url.startswith('https://') else ''
        parts.append(f'<a href="{escape(url, quote=True)}"{attrs}>{bold(label)}</a>')
        cursor = match.end()
    parts.append(bold(text[cursor:]))
    return ''.join(parts)


def tables(text):
    return [
        [[v.strip() for v in line.strip().strip('|').split('|')] for line in block.splitlines()]
        for block in re.findall(r'(?m)(?:^\|.*\|\n)+', text)
    ]


def render_table(rows):
    head = ''.join(f'<th scope="col">{inline(col)}</th>' for col in rows[0])
    body = ''.join(
        '<tr>' + ''.join(f'<td>{inline(col)}</td>' for col in row) + '</tr>'
        for row in rows[2:]
    )
    return f'<div class="table-wrap" tabindex="0" aria-label="可横向滚动的表格"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def body(lines):
    steps = []
    notes = []
    references = []
    for raw in lines:
        if not raw.strip():
            continue
        step = re.match(r'^\d\. (.+)$', raw)
        if step:
            steps.append(f'<li>{inline(step[1])}</li>')
            continue
        links = list(LINK.finditer(raw))
        if links and all(link[2].startswith('https://') for link in links):
            plain = LINK.sub('', raw).strip(' ·')
            if plain:
                notes.append(f'<p>{inline(plain)}</p>')
            references.extend(f'<li>{inline(link[0])}</li>' for link in links)
        else:
            notes.append(f'<p>{inline(raw)}</p>')
    result = [f'<ol class="steps">{"".join(steps)}</ol>']
    if notes:
        result.append(f'<div class="team-notes">{"".join(notes)}</div>')
    if references:
        result.append(
            '<footer class="team-references"><h4>视频与资料</h4>'
            f'<ul role="list">{"".join(references)}</ul></footer>'
        )
    return ''.join(result)


rotation = (ROOT/'plans/rotations.md').read_text()
roster, _ = rotation.split('\n## 规划中的队伍\n', 1)
team_matches = list(re.finditer(r'^### (\d{2}) 号队\n\n\*\*(.+)\*\*\n', roster, re.M))
presets = {row[0]: row[2] for row in tables((ROOT/'plans/teams.md').read_text())[0][2:]}
assert [m[1] for m in team_matches] == [f'{i:02}' for i in range(1, 21)]
team_links = []
team_panels = []
for i, match in enumerate(team_matches):
    num, names = match.groups()
    end = team_matches[i+1].start() if i+1 < len(team_matches) else len(roster)
    lines = [line for line in roster[match.end():end].splitlines() if not line.startswith('## ')]
    group = 'main' if i < 7 else 'swap' if i < 14 else 'reserve'
    search = names
    team_links.append(
        f'<a class="team-link" data-team="{num}" data-group="{group}" data-search="{escape(search, quote=True)}" href="#team-{num}">'
        f'<span class="team-number">{num}</span><span>{escape(names)}</span></a>'
    )
    team_panels.append(
        f'<article class="team-panel" id="team-{num}" aria-labelledby="title-{num}">'
        f'<div class="team-title"><span class="team-number">{num}</span><div><h3 id="title-{num}">{escape(names)}</h3>'
        f'<p>{escape(presets[num])}</p></div></div>{body(lines)}</article>'
    )
support = roster.split('## 常用角色怎么起手', 1)[1].split('## 主力队', 1)[0]
support_html = ''.join(f'<li>{inline(line[2:])}</li>' for line in support.splitlines() if line.startswith('- '))
build_rows = tables((ROOT/'plans/builds.md').read_text())[0][2:]
build_html = ''.join(
    f'<li class="build-row"><span class="team-number">{row[0].zfill(2)}</span>'
    f'<div><h3>{inline(row[1])}</h3><p>{inline(row[2])}</p><p class="check">{inline(row[3])}</p></div></li>'
    for row in build_rows
)
budget = tables((ROOT/'plans/pulls.md').read_text())
budget_html = render_table(budget[1])
index = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <meta name="description" content="鸣潮账号养成、锁暝抽卡预算和20队操作手法。">
  <title>鸣潮 · 账号规划</title>
  <script src="{asset('theme.js')}"></script>
  <link rel="stylesheet" href="{asset('styles.css')}">
  <script defer src="{asset('planner.js')}"></script>
</head>
<body>
  <a class="skip" href="#main">跳到正文</a>
  <header class="site-header">
    <div class="wrap masthead">
      <a class="brand" href="#top">鸣潮 <span>账号规划</span></a>
      <nav aria-label="站点导航">
        <a href="#teams">20 队手法</a>
        <a href="#builds">角色养成</a>
        <a href="#pulls">抽卡预算</a>
      </nav>
      <div class="header-actions">
        <label class="theme-control" hidden>
          <select id="theme" aria-label="网站外观">
            <option value="system">跟随系统</option>
            <option value="light">浅色</option>
            <option value="dark">深色</option>
          </select>
        </label>
        <a class="header-link header-download" href="guide.pdf">PDF <span aria-hidden="true">↗</span></a>
        <a class="header-link" href="{REPO}" aria-label="GitHub 仓库">GitHub <span aria-hidden="true">↗</span></a>
      </div>
    </div>
  </header>
  <main id="main">
    <section class="hero" id="top" aria-labelledby="hero-title">
      <img class="hero-art" src="assets/resonance-coast.webp" width="1942" height="809" fetchpriority="high" alt="">
      <div class="wrap hero-inner">
        <div class="hero-copy">
          <p class="game-title" lang="en">Wuthering Waves</p>
          <h1 id="hero-title">鸣潮账号规划</h1>
          <p class="version">3.8 版本 · 2026.11.24 账号快照</p>
          <p class="hero-text">角色养成、锁暝抽卡预算与 20 队实战手法。</p>
          <div class="hero-links">
            <a class="button primary" href="#teams">查看 20 队手法 <span aria-hidden="true">↓</span></a>
            <a class="button secondary" href="guide.pdf">打开完整版 PDF <span aria-hidden="true">↗</span></a>
          </div>
        </div>
      </div>
    </section>
    <aside class="overview" aria-label="当前规划重点">
      <div class="wrap overview-inner">
        <div><span>养成优先</span><strong>仇远 → 弗洛洛 → 琳奈</strong></div>
        <div><span>抽卡目标</span><strong>锁暝 0 链</strong></div>
        <div><span>最坏情况剩余缺口 · 计入现有月相</span><strong class="amount">18,912 <small>星声</small></strong></div>
      </div>
    </aside>
    <section class="wrap section" id="teams" aria-labelledby="teams-title">
      <div class="section-heading">
        <div><h2 id="teams-title">20 队操作与视频</h2><p>选一队，查看进场顺序、输出步骤和对应视频。</p></div>
        <a class="text-link" href="guide.pdf#page=7">PDF 队号目录 ↗</a>
      </div>
      <details class="quick-start">
        <summary>千咲、守岸人、维里奈、琳奈的起手</summary>
        <ul>{support_html}</ul>
      </details>
      <div class="team-layout">
        <aside class="picker" aria-label="选择队伍">
          <div class="filters" hidden>
            <label for="team-search">搜索队伍</label>
            <input id="team-search" type="search" placeholder="队号或角色名">
            <div class="filter-buttons" role="group" aria-label="队伍分组">
              <button type="button" data-filter="all" aria-pressed="true">全部</button>
              <button type="button" data-filter="main" aria-pressed="false">主力</button>
              <button type="button" data-filter="swap" aria-pressed="false">常用</button>
              <button type="button" data-filter="reserve" aria-pressed="false">备用</button>
            </div>
          </div>
          <nav aria-label="队号目录" class="team-list">{''.join(team_links)}</nav>
          <p class="no-result" role="status" hidden>没有匹配的队伍。换一个队号或角色名试试。</p>
        </aside>
        <div class="team-panels">{''.join(team_panels)}</div>
      </div>
    </section>
    <section class="wrap section" id="builds" aria-labelledby="builds-title">
      <div class="section-heading">
        <div><h2 id="builds-title">角色养成</h2><p>按队伍强度、现有缺口和补强成本排序。</p></div>
        <a class="text-link" href="{REPO}/blob/main/plans/builds.md">分周计划 ↗</a>
      </div>
      <ol class="builds">{build_html}</ol>
      <p class="after-build">收尾主队后练心和已有专武玉阙玄华，再按热熔需求开练爱弥斯。</p>
    </section>
    <section class="wrap section" id="pulls" aria-labelledby="pulls-title">
      <div class="section-heading">
        <div><h2 id="pulls-title">锁暝抽卡预算</h2><p>角色池垫 5 抽、小保底。武器池垫 19 抽。按最坏情况计算。</p></div>
        <a class="text-link" href="{REPO}/blob/main/plans/pulls.md">完整预算与抽卡顺序 ↗</a>
      </div>
      {budget_html}
      <p class="after-build">先保锁暝本体。拿到本体后，再用剩余星声和武器池垫抽决定要不要抽沉冥。</p>
    </section>
  </main>
  <footer class="site-footer">
    <div class="wrap"><span>鸣潮 · 个人账号规划</span><a href="{REPO}">GitHub 仓库 ↗</a><a href="#top">回到顶部 ↑</a></div>
  </footer>
</body>
</html>
"""
(ROOT/'docs/index.html').write_text(index)
