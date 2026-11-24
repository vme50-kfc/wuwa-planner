"""Build the GitHub Pages index from the planner's Markdown."""
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
REPO = 'https://github.com/vme50-kfc/wuwa-planner'
LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
BOLD = re.compile(r'\*\*(.+?)\*\*')

ELEMENTS = {
    'glacio': {'label': '冷凝', 'en': 'Glacio'},
    'aero': {'label': '气动', 'en': 'Aero'},
    'havoc': {'label': '湮灭', 'en': 'Havoc'},
    'spectro': {'label': '衍射', 'en': 'Spectro'},
    'electro': {'label': '导电', 'en': 'Electro'},
    'fusion': {'label': '热熔', 'en': 'Fusion'},
}

CHAR_ELEMENT = {
    '绯雪': 'glacio',
    '珂莱塔': 'glacio',
    '折枝': 'glacio',
    '散华': 'glacio',
    '卡提希娅': 'aero',
    '夏空': 'aero',
    '忌炎': 'aero',
    '仇远': 'aero',
    '漂泊者·气动': 'aero',
    '弗洛洛': 'havoc',
    '坎特蕾拉': 'havoc',
    '千咲': 'havoc',
    '椿': 'havoc',
    '守岸人': 'spectro',
    '维里奈': 'spectro',
    '赞妮': 'spectro',
    '菲比': 'spectro',
    '今汐': 'spectro',
    '琳奈': 'spectro',
    '相里要': 'electro',
    '吟霖': 'electro',
    '心': 'electro',
    '锁暝': 'electro',
    '长离': 'fusion',
    '安可': 'fusion',
    '莫特斐': 'fusion',
    '爱弥斯': 'fusion',
}

GROUP_META = {
    'main': {'label': '主力队', 'short': '主力'},
    'swap': {'label': '常用替换', 'short': '常用'},
    'reserve': {'label': '备用队', 'short': '备用'},
    'planned': {'label': '规划中', 'short': '规划'},
}

HIGHLIGHT_RULES = [
    (re.compile(r'(强化变奏|同奏延奏|变奏|延奏|同奏)'), 'swap'),
    (re.compile(r'(第一段解放|第二段解放|末段解放|转相解放|终结解放|长按解放|解放|开大)'), 'ult'),
    (re.compile(r'(强化重击|强化技能|强化普攻|强化下落|主动声骸|声骸|回路|协奏)'), 'forte'),
    (re.compile(r'(风蚀|光噪|焰光|离火|韶光|剑意|赫卡忒|星域|居合|乘岁|终夜|赦罪|告解|链锯|震谐)'), 'status'),
]

SVG_SPRITE = """<svg class="svg-defs" aria-hidden="true" focusable="false" hidden>
  <defs>
    <symbol id="icon-glacio" viewBox="0 0 24 24">
      <path fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" d="M12 2v20M4.2 6.5l15.6 11M19.8 6.5L4.2 17.5M9.5 4.2L12 6.8l2.5-2.6M9.5 19.8L12 17.2l2.5 2.6M5.2 10.6l2.6.8-.9 2.6M18.8 10.6l-2.6.8.9 2.6"/>
      <polygon fill="currentColor" points="12,8.4 15.1,10.2 15.1,13.8 12,15.6 8.9,13.8 8.9,10.2"/>
    </symbol>
    <symbol id="icon-aero" viewBox="0 0 24 24">
      <path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M3.5 11.5C6.5 6.8 12.8 5.2 17.4 8c2.6 1.6 3.5 4.9 1.6 7.1-1.7 2-5 2-6.5.2-1.1-1.3-.8-3.4.7-4.3 1.2-.7 2.8-.2 3.2 1"/>
      <path fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" d="M4.5 16.5c2.4 2.4 6.4 3.4 10.3 2.5"/>
    </symbol>
    <symbol id="icon-havoc" viewBox="0 0 24 24">
      <path fill="currentColor" d="M12 2.4l2.4 6.2 6.6.8-5 4.4 1.5 6.5L12 16.8l-5.5 3.5 1.5-6.5-5-4.4 6.6-.8z" opacity=".24"/>
      <path fill="none" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round" d="M12 3l2.1 5.9 6.2 1-4.6 4.1 1.3 6.2L12 16.9l-5 3.3 1.3-6.2-4.6-4.1 6.2-1z"/>
      <circle cx="12" cy="12" r="2.2" fill="currentColor"/>
    </symbol>
    <symbol id="icon-spectro" viewBox="0 0 24 24">
      <path fill="currentColor" d="M12 2l2.3 7.7L22 12l-7.7 2.3L12 22l-2.3-7.7L2 12l7.7-2.3z"/>
      <circle cx="12" cy="12" r="2.1" fill="#091018"/>
    </symbol>
    <symbol id="icon-electro" viewBox="0 0 24 24">
      <path fill="currentColor" d="M13.6 2.2L5.8 13h5.1l-1.5 8.8 8.8-11.2h-5.2z"/>
    </symbol>
    <symbol id="icon-fusion" viewBox="0 0 24 24">
      <path fill="currentColor" d="M12.7 2.4c.5 3.4-2.1 5.1-2.1 7.6 0 1.4 1 2.4 2.3 2.4 1.6 0 2.7-1.4 2.6-3.4 2.4 1.8 4 4.5 4 7.4 0 3.7-3 6.2-7.5 6.2S4.5 20.1 4.5 16c0-4.6 3.5-8.9 8.2-13.6z"/>
      <path fill="#091018" d="M12.2 14.3c1.4 1.1 2.2 2.4 2.2 3.7a2.4 2.4 0 1 1-4.8 0c0-1.4 1-2.6 2.6-3.7z" opacity=".55"/>
    </symbol>
    <symbol id="icon-astrite" viewBox="0 0 24 24">
      <path fill="currentColor" d="M12 1.8l2.7 7.5 7.5 2.7-7.5 2.7-2.7 7.5-2.7-7.5L1.8 12l7.5-2.7z"/>
      <path fill="currentColor" d="M12 5.4l1.3 5.3 5.3 1.3-5.3 1.3-1.3 5.3-1.3-5.3-5.3-1.3 5.3-1.3z" opacity=".38"/>
    </symbol>
    <symbol id="icon-tacet" viewBox="0 0 64 16">
      <line x1="0" y1="8" x2="17" y2="8" stroke="currentColor" stroke-width="1" opacity=".55"/>
      <polygon fill="currentColor" points="22,8 25,4.2 28,8 25,11.8" opacity=".65"/>
      <polygon fill="currentColor" points="32,1.6 35.6,8 32,14.4 28.4,8"/>
      <polygon fill="currentColor" points="42,8 39,4.2 36,8 39,11.8" opacity=".65"/>
      <line x1="47" y1="8" x2="64" y2="8" stroke="currentColor" stroke-width="1" opacity=".55"/>
    </symbol>
    <symbol id="icon-moon" viewBox="0 0 24 24">
      <path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M20.2 14.8A8.5 8.5 0 1 1 9.2 3.8a6.8 6.8 0 0 0 11 11z"/>
    </symbol>
    <symbol id="icon-sun" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/>
      <path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M12 2.5v2.3M12 19.2v2.3M4.9 4.9l1.6 1.6M17.5 17.5l1.6 1.6M2.5 12h2.3M19.2 12h2.3M4.9 19.1l1.6-1.6M17.5 6.5l1.6-1.6"/>
    </symbol>
    <symbol id="icon-system" viewBox="0 0 24 24">
      <rect x="3" y="4.5" width="18" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/>
      <path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M8.5 20h7M12 16.5V20"/>
    </symbol>
    <symbol id="icon-search" viewBox="0 0 24 24">
      <circle cx="10.8" cy="10.8" r="6.6" fill="none" stroke="currentColor" stroke-width="1.9"/>
      <path fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" d="M15.8 15.8L20.6 20.6"/>
    </symbol>
    <symbol id="icon-video" viewBox="0 0 24 24">
      <polygon fill="currentColor" points="8.2,6.2 18.8,12 8.2,17.8"/>
    </symbol>
    <symbol id="icon-book" viewBox="0 0 24 24">
      <path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" d="M4.5 5.5A2.5 2.5 0 0 1 7 3h12.5v16.5H7a2.5 2.5 0 0 0-2.5 2.5zM4.5 19.5A2.5 2.5 0 0 1 7 17h12.5"/>
    </symbol>
    <symbol id="icon-check" viewBox="0 0 24 24">
      <path fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" d="M5 12.5l4.4 4.4L19 7.3"/>
    </symbol>
    <symbol id="icon-reset" viewBox="0 0 24 24">
      <path fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" d="M4 12a8 8 0 1 0 2.3-5.6L4 8.7M4 4.5v4.2h4.2"/>
    </symbol>
  </defs>
</svg>"""


def asset(name):
    path = f'assets/{name}'
    digest = sha256((ROOT / 'docs' / path).read_bytes()).hexdigest()[:12]
    return f'{path}?v={digest}'


def icon(name, cls='icon'):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#icon-{name}"/></svg>'


def element_of(character):
    return CHAR_ELEMENT.get(character.strip(), 'spectro')


def element_badge(el, show_label=True):
    info = ELEMENTS[el]
    label_html = f'<span>{info["label"]}</span>' if show_label else ''
    return (
        f'<span class="el-badge" data-el="{el}" title="{info["label"]} · {info["en"]}">'
        f'{icon(el, "el-icon")}{label_html}</span>'
    )


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
        cls = ' class="inline-team-ref"' if team else ''
        parts.append(f'<a{cls} href="{escape(url, quote=True)}"{attrs}>{bold(label)}</a>')
        cursor = match.end()
    parts.append(bold(text[cursor:]))
    return ''.join(parts)


def highlight_terms(html_text):
    """Apply subtle semantic tags to WuWa combat keywords outside HTML tags."""
    tokens = re.split(r'(<[^>]+>)', html_text)
    in_link = 0
    out = []
    for token in tokens:
        if token.startswith('<'):
            low = token.lower()
            if low.startswith('<a ') or low == '<a>':
                in_link += 1
            elif low.startswith('</a'):
                in_link = max(0, in_link - 1)
            out.append(token)
            continue
        if in_link:
            out.append(token)
            continue
        segment = token
        # Single-pass replacement to avoid nested <mark> tags
        combined = re.compile(
            '|'.join(f'(?P<t{idx}>{rx.pattern})' for idx, (rx, _) in enumerate(HIGHLIGHT_RULES))
        )

        def repl(m):
            for idx, (_, kind) in enumerate(HIGHLIGHT_RULES):
                val = m.group(f't{idx}')
                if val is not None:
                    return f'<mark class="term term-{kind}">{val}</mark>'
            return m.group(0)

        out.append(combined.sub(repl, segment))
    return ''.join(out)


def classify_reference(label, url):
    if 'bilibili.com' in url:
        return ('B站视频', 'video', 'ref-video')
    if 'prydwen.gg' in url or 'gamearchive' in url or 'wuthering.gg' in url:
        return ('机制攻略', 'book', 'ref-guide')
    if 'gamer.com.tw' in url:
        return ('巴哈资料', 'book', 'ref-forum')
    return ('外部参考', 'book', 'ref-guide')


def tables(text):
    return [
        [[v.strip() for v in line.strip().strip('|').split('|')] for line in block.splitlines()]
        for block in re.findall(r'(?m)(?:^\|.*\|\n)+', text)
    ]


def parse_int(text):
    digits = re.sub(r'[^\d]', '', text)
    return int(digits) if digits else 0


def parse_snapshot():
    snap_files = sorted((ROOT / 'snapshots').glob('20*.md'))
    snap_path = snap_files[-1]
    snap_text = snap_path.read_text()
    snap_date = snap_path.stem.replace('-', '.')
    ver_match = re.search(r'游戏版本\s*([0-9.]+)', snap_text)
    version = ver_match.group(1) if ver_match else '3.8'
    snap_tables = tables(snap_text)

    res_map = {row[0]: row[1] for row in snap_tables[0][2:]}
    astrite, lunite = [parse_int(x) for x in res_map.get('星声 / 月相', '0 / 0').split('/')]
    radiant, forging = [parse_int(x) for x in res_map.get('浮金波纹 / 铸潮波纹', '0 / 0').split('/')]
    afterglow, oscillated = [parse_int(x) for x in res_map.get('余波珊瑚 / 残振珊瑚', '0 / 0').split('/')]
    shell_credits = res_map.get('贝币', '')

    char_pity_raw = res_map.get('角色活动池', '')
    weap_pity_raw = res_map.get('武器活动池', '')
    char_pity_m = re.search(r'垫\s*(\d+)\s*抽', char_pity_raw)
    weap_pity_m = re.search(r'垫\s*(\d+)\s*抽', weap_pity_raw)
    char_pity = int(char_pity_m.group(1)) if char_pity_m else 0
    weap_pity = int(weap_pity_m.group(1)) if weap_pity_m else 0
    guaranteed = '大保底' in char_pity_raw

    char_states = {row[0]: row[1] for row in snap_tables[1][2:]}

    return {
        'date': snap_date,
        'version': version,
        'astrite': astrite,
        'lunite': lunite,
        'radiant': radiant,
        'forging': forging,
        'charPity': char_pity,
        'weapPity': weap_pity,
        'guaranteed': guaranteed,
        'afterglow': afterglow,
        'oscillated': oscillated,
        'shellCredits': shell_credits,
        'charPityText': char_pity_raw,
        'weapPityText': weap_pity_raw,
        'charStates': char_states,
    }


def render_team_body(lines):
    steps = []
    notes = []
    references = []
    for raw in lines:
        if not raw.strip():
            continue
        step = re.match(r'^(\d+)\. (.+)$', raw)
        if step:
            idx = step[1].zfill(2)
            content = highlight_terms(inline(step[2]))
            steps.append(
                f'<li class="step-item">'
                f'<span class="step-index" aria-hidden="true">{idx}</span>'
                f'<div class="step-content">{content}</div>'
                f'</li>'
            )
            continue
        links = list(LINK.finditer(raw))
        if links and all(link[2].startswith('https://') for link in links):
            plain = LINK.sub('', raw).strip(' ·')
            if plain:
                notes.append(f'<p>{highlight_terms(inline(plain))}</p>')
            for link in links:
                label, url = link.groups()
                tag, ic, cls = classify_reference(label, url)
                references.append(
                    f'<li><a class="ref-card {cls}" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">'
                    f'<span class="ref-badge">{icon(ic, "ref-icon")}{tag}</span>'
                    f'<span class="ref-title">{escape(label)}</span>'
                    f'<span class="ref-arrow" aria-hidden="true">↗</span>'
                    f'</a></li>'
                )
        else:
            notes.append(f'<p>{highlight_terms(inline(raw))}</p>')

    result = [f'<ol class="steps">{"".join(steps)}</ol>']
    if notes:
        result.append(
            f'<div class="team-notes">'
            f'<span class="notes-tag">实战要点</span>'
            f'<div class="notes-body">{"".join(notes)}</div>'
            f'</div>'
        )
    if references:
        result.append(
            '<footer class="team-references">'
            '<div class="ref-header"><h4>视频与资料</h4><span>点击跳转实机演示与机制拆解</span></div>'
            f'<ul role="list">{"".join(references)}</ul></footer>'
        )
    return ''.join(result)


def render_roster_chips(members):
    chips = []
    for idx, name in enumerate(members):
        el = element_of(name)
        role = '主C' if idx == 0 else ('副C / 协奏' if idx == 1 else '辅助 / 生存')
        chips.append(
            f'<span class="member-chip" data-el="{el}">'
            f'{icon(el, "el-icon")}'
            f'<span class="member-name">{escape(name)}</span>'
            f'<span class="member-role">{role}</span>'
            f'</span>'
        )
    return ''.join(chips)


def render_support_cards(support_md):
    cards = []
    for line in support_md.splitlines():
        if not line.startswith('- '):
            continue
        raw = line[2:].strip()
        m = re.match(r'^\*\*(.+?)\*\*。(.+)$', raw)
        if not m:
            cards.append(f'<article class="support-card">{inline(raw)}</article>')
            continue
        name, rest = m.groups()
        el = element_of(name)
        links = list(LINK.finditer(rest))
        text_only = LINK.sub('', rest).strip(' ·')
        link_html = ''
        if links:
            lbl, url = links[0].groups()
            link_html = (
                f'<a class="support-link" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">'
                f'{icon("video", "ref-icon")}{escape(lbl)} <span aria-hidden="true">↗</span></a>'
            )
        cards.append(
            f'<article class="support-card spotlight-card" data-el="{el}">'
            f'<div class="support-head">'
            f'<span class="support-name">{icon(el, "el-icon")}<strong>{escape(name)}</strong></span>'
            f'{element_badge(el)}'
            f'</div>'
            f'<p>{highlight_terms(inline(text_only))}</p>'
            f'{link_html}'
            f'</article>'
        )
    return ''.join(cards)


def parse_build_team_chips(team_spec):
    """Turn '仇远 · 3' or '守岸人 · 6–8、10 等' into character name + clickable team links."""
    parts = [p.strip() for p in team_spec.split('·', 1)]
    char_name = parts[0]
    raw_teams = parts[1] if len(parts) > 1 else ''
    team_nums = []
    for token in re.split(r'[、,，\s]+', raw_teams):
        token = token.replace('等', '').strip()
        if not token:
            continue
        rng = re.match(r'^(\d+)[–\-~](\d+)$', token)
        if rng:
            start, stop = int(rng.group(1)), int(rng.group(2))
            team_nums.extend(f'{n:02}' for n in range(start, stop + 1))
        elif token.isdigit():
            team_nums.append(token.zfill(2))
    has_more = '等' in raw_teams
    chips = [
        f'<a class="mini-team-chip" href="#team-{num}">#{num}</a>'
        for num in team_nums
    ]
    if has_more:
        chips.append('<span class="mini-team-more">等</span>')
    return char_name, ''.join(chips)


def render_weekly_checklist(builds_md):
    if '## 分周执行' not in builds_md:
        return ''
    weekly_raw = builds_md.split('## 分周执行', 1)[1]
    week_matches = list(re.finditer(r'^### (.+)$', weekly_raw, re.M))
    cards = []
    task_idx = 0
    for i, wm in enumerate(week_matches):
        title = wm.group(1).strip()
        end = week_matches[i + 1].start() if i + 1 < len(week_matches) else len(weekly_raw)
        block = weekly_raw[wm.end():end]
        items = []
        for line in block.splitlines():
            m = re.match(r'^- \[([ xX])\] (.+)$', line.strip())
            if not m:
                continue
            task_idx += 1
            tid = f'w{i + 1}-t{task_idx}'
            items.append(
                f'<label class="check-item" for="chk-{tid}">'
                f'<input type="checkbox" id="chk-{tid}" data-check-id="{tid}">'
                f'<span class="check-box" aria-hidden="true">{icon("check", "check-svg")}</span>'
                f'<span class="check-text">{highlight_terms(inline(m.group(2)))}</span>'
                f'</label>'
            )
        phase_code = f'PHASE 0{i + 1}'
        cards.append(
            f'<article class="week-card spotlight-card">'
            f'<div class="week-head">'
            f'<span class="week-code">{phase_code}</span>'
            f'<h3>{escape(title)}</h3>'
            f'</div>'
            f'<div class="check-list">{"".join(items)}</div>'
            f'</article>'
        )
    return (
        '<div class="weekly-board">'
        '<div class="weekly-header">'
        '<div>'
        '<p class="eyebrow-sm">EXECUTION ROADMAP</p>'
        '<h3>分周养成执行清单</h3>'
        '<p class="weekly-sub">点击即可本地记录完成进度，刷新页面自动保留。</p>'
        '</div>'
        '<div class="weekly-progress-box">'
        '<div class="weekly-stat"><span class="weekly-count" id="checklist-count">0 / '
        f'{task_idx}</span><span class="weekly-pct" id="checklist-pct">0%</span></div>'
        '<div class="progress-track"><div class="progress-fill" id="checklist-bar" style="width:0%"></div></div>'
        f'<button type="button" class="ghost-btn" id="checklist-reset">{icon("reset", "btn-icon")}重置进度</button>'
        '</div>'
        '</div>'
        f'<div class="week-grid">{"".join(cards)}</div>'
        '</div>'
    )


def render_budget_table(rows, max_need=33760):
    head = ''.join(f'<th scope="col">{inline(col)}</th>' for col in rows[0]) + '<th scope="col">筹备缺口占比</th>'
    body_rows = []
    for idx, row in enumerate(rows[2:]):
        need_val = parse_int(row[2])
        ratio = min(100, round(need_val / max_need * 100))
        is_primary = idx == 1
        row_cls = ' class="is-recommended"' if is_primary else ''
        cells = ''.join(f'<td>{inline(col)}</td>' for col in row)
        bar = (
            f'<td class="bar-cell">'
            f'<div class="mini-bar"><span style="width:{ratio}%"></span></div>'
            f'<span class="bar-pulls">≈ {(need_val + 159) // 160} 抽</span>'
            f'</td>'
        )
        body_rows.append(f'<tr{row_cls}>{cells}{bar}</tr>')
    return (
        '<div class="table-wrap" tabindex="0" aria-label="锁暝最坏情况预算对照表">'
        f'<table><thead><tr>{head}</tr></thead><tbody>{"".join(body_rows)}</tbody></table>'
        '</div>'
    )


def render_forecast_list(rows, ranked=False):
    entries = []
    for row in rows[2:]:
        label, status, description = row[-3:]
        rank = f'<span class="forecast-rank">{inline(row[0])}</span>' if ranked else ''
        entries.append(
            f'<li>{rank}<div class="forecast-entry"><div class="forecast-entry-head">'
            f'<strong>{inline(label)}</strong><span class="forecast-status" data-status="{escape(status)}">'
            f'{escape(status)}</span></div><p>{inline(description)}</p></div></li>'
        )
    return f'<ul class="forecast-list">{"".join(entries)}</ul>'


# --- Load & parse all Markdown sources ---
snapshot = parse_snapshot()
rotation_md = (ROOT / 'plans/rotations.md').read_text()
teams_md = (ROOT / 'plans/teams.md').read_text()
builds_md = (ROOT / 'plans/builds.md').read_text()
pulls_md = (ROOT / 'plans/pulls.md').read_text()

roster_md, planned_md = rotation_md.split('\n## 规划中的队伍\n', 1)
team_matches = list(re.finditer(r'^### (\d{2}) 号队\n\n\*\*(.+)\*\*\n', roster_md, re.M))
presets = {row[0]: row[2] for row in tables(teams_md)[0][2:]}
assert [m[1] for m in team_matches] == [f'{i:02}' for i in range(1, 21)]

# Parse planned teams subtitles from plans/teams.md
planned_subtitles = {}
if '## 规划中的队伍' in teams_md:
    for line in teams_md.split('## 规划中的队伍', 1)[1].splitlines():
        pm = re.match(r'^- \*\*(.+?)\*\*，(.+?)(?:\s*\[|$)', line.strip())
        if pm:
            planned_subtitles[pm.group(1).strip()] = pm.group(2).strip('。 ')

all_teams = []
for i, match in enumerate(team_matches):
    num, names = match.groups()
    end = team_matches[i + 1].start() if i + 1 < len(team_matches) else len(roster_md)
    lines = [line for line in roster_md[match.end():end].splitlines() if not line.startswith('## ')]
    group = 'main' if i < 7 else 'swap' if i < 14 else 'reserve'
    members = [m.strip() for m in names.split('、')]
    all_teams.append({
        'id': num,
        'badge': num,
        'title': names,
        'subtitle': presets[num],
        'group': group,
        'members': members,
        'primary_el': element_of(members[0]),
        'lines': lines,
        'search': f'{num} {names} {presets[num]} {ELEMENTS[element_of(members[0])]["label"]}',
    })

planned_matches = list(re.finditer(r'^### (.+)\n\n\*\*(.+)\*\*\n', planned_md, re.M))
for j, match in enumerate(planned_matches):
    plan_title, names = match.groups()
    end = planned_matches[j + 1].start() if j + 1 < len(planned_matches) else len(planned_md)
    lines = [line for line in planned_md[match.end():end].splitlines() if not line.startswith('## ')]
    code = f'P{j + 1}'
    members = [m.strip() for m in names.split('、')]
    sub = planned_subtitles.get(names, plan_title)
    all_teams.append({
        'id': code,
        'badge': code,
        'title': f'{names}',
        'subtitle': f'{plan_title} · {sub}',
        'group': 'planned',
        'members': members,
        'primary_el': element_of(members[0]),
        'lines': lines,
        'search': f'{code} {plan_title} {names} {sub} {ELEMENTS[element_of(members[0])]["label"]}',
    })

# Count shared support occurrences across preset 20 teams
support_freq = {}
for t in all_teams[:20]:
    for m in t['members']:
        support_freq[m] = support_freq.get(m, 0) + 1

HIGH_CONTESTED = ('千咲', '守岸人', '琳奈', '夏空', '坎特蕾拉', '折枝', '维里奈')

team_links = []
team_panels = []
for t in all_teams:
    tid = t['id']
    el = t['primary_el']
    grp = t['group']
    grp_label = GROUP_META[grp]['label']
    member_dots = ''.join(
        f'<span class="el-dot" data-el="{element_of(m)}" title="{escape(m)}（{ELEMENTS[element_of(m)]["label"]}）"></span>'
        for m in t['members']
    )
    team_links.append(
        f'<a class="team-link" data-team="{tid}" data-group="{grp}" data-element="{el}" '
        f'data-search="{escape(t["search"], quote=True)}" href="#team-{tid}">'
        f'<span class="team-number" data-el="{el}">{tid}</span>'
        f'<span class="team-link-body">'
        f'<span class="team-link-names">{escape(t["title"])}</span>'
        f'<span class="team-link-meta">{member_dots}<span class="team-link-tag">{GROUP_META[grp]["short"]}</span></span>'
        f'</span></a>'
    )

    shared_pills = []
    for m in t['members']:
        cnt = support_freq.get(m, 0)
        if m in HIGH_CONTESTED and cnt >= 2:
            shared_pills.append(
                f'<button type="button" class="shared-chip" data-quick-search="{escape(m, quote=True)}" '
                f'title="筛选包含 {escape(m)} 的全部队伍">'
                f'<span class="el-dot" data-el="{element_of(m)}"></span>{escape(m)} · 跨 {cnt} 队</button>'
            )
    shared_html = (
        f'<div class="shared-strip"><span class="shared-label">共享位提醒</span>{"".join(shared_pills)}</div>'
        if shared_pills else ''
    )

    team_panels.append(
        f'<article class="team-panel spotlight-card" id="team-{tid}" data-el="{el}" data-group="{grp}" aria-labelledby="title-{tid}">'
        f'<div class="team-panel-accent" aria-hidden="true"></div>'
        f'<header class="team-title">'
        f'<div class="team-title-top">'
        f'<span class="team-number team-number-lg" data-el="{el}">{tid}</span>'
        f'<div class="team-heading-main">'
        f'<div class="team-badges">'
        f'<span class="group-pill group-{grp}">{grp_label}</span>'
        f'{element_badge(el)}'
        f'</div>'
        f'<h3 id="title-{tid}">{escape(t["title"])}</h3>'
        f'<p class="team-purpose">{escape(t["subtitle"])}</p>'
        f'</div>'
        f'</div>'
        f'<div class="roster-bar">{render_roster_chips(t["members"])}</div>'
        f'{shared_html}'
        f'</header>'
        f'{render_team_body(t["lines"])}'
        f'</article>'
    )

# Quick-start support cards
support_md = roster_md.split('## 常用角色怎么起手', 1)[1].split('## 主力队', 1)[0]
support_cards_html = render_support_cards(support_md)

# Character builds
build_rows = tables(builds_md)[0][2:]
build_cards = []
for row in build_rows:
    rank = row[0].zfill(2)
    char_name, team_chips = parse_build_team_chips(row[1])
    el = element_of(char_name)
    snap_state = snapshot['charStates'].get(char_name, '')
    state_html = (
        f'<p class="build-snapshot"><span class="snap-label">当前快照</span>{escape(snap_state)}</p>'
        if snap_state else ''
    )
    build_cards.append(
        f'<li class="build-card spotlight-card" data-el="{el}">'
        f'<div class="build-head">'
        f'<div class="build-id">'
        f'<span class="build-rank">{rank}</span>'
        f'<div>'
        f'<div class="build-name-row"><h3>{escape(char_name)}</h3>{element_badge(el)}</div>'
        f'<div class="build-teams">关联配队：{team_chips}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'{state_html}'
        f'<div class="build-detail">'
        f'<div class="build-action"><span class="detail-tag">核心改造</span><p>{highlight_terms(inline(row[2]))}</p></div>'
        f'<div class="build-check"><span class="detail-tag detail-tag-ok">验收标准</span><p>{highlight_terms(inline(row[3]))}</p></div>'
        f'</div>'
        f'</li>'
    )

# Follow-up planned resonators card (心 & 爱弥斯)
followup_cards = []
for f_name, f_team, f_note in [
    ('心', 'P1', '收尾主队后优先拉至 Lv80→Lv90，搭配已有专武玉阙玄华与衔梦照世之心 5 件，备战锁暝导电同奏队。'),
    ('爱弥斯', 'P2', '按热熔深塔需求开启培养，配长路启航之星 5 件与辛吉勒姆，过渡借用 Lv90 千古洑流。'),
]:
    el = element_of(f_name)
    st = snapshot['charStates'].get(f_name, '')
    followup_cards.append(
        f'<div class="followup-card spotlight-card" data-el="{el}">'
        f'<div class="followup-head">'
        f'<span class="followup-title">{icon(el, "el-icon")}<strong>{f_name}</strong>{element_badge(el)}</span>'
        f'<a class="mini-team-chip" href="#team-{f_team}">查看 {f_team} 手法 ↗</a>'
        f'</div>'
        f'<p class="followup-snap">{escape(st)}</p>'
        f'<p class="followup-note">{f_note}</p>'
        f'</div>'
    )

weekly_html = render_weekly_checklist(builds_md)

# Pulls tables
budget_tables = tables(pulls_md)
budget_html = render_budget_table(budget_tables[1], max_need=33760)
base_deficit = parse_int(budget_tables[1][3][2])  # 18,912
base_target_total = 24800
base_ready_pct = max(0, min(100, round((base_target_total - base_deficit) / base_target_total * 100)))

forecast_md = pulls_md.split('\n## 4.0 到 4.3 抽卡优先级\n', 1)[1].split('\n## ', 1)[0]
forecast_timeline, forecast_ranking = tables(forecast_md)
forecast_blocks = forecast_md.strip().split('\n\n')

element_filter_buttons = ''.join(
    f'<button type="button" class="el-filter" data-el-filter="{code}" data-el="{code}" aria-pressed="false">'
    f'{icon(code, "el-icon")}<span>{info["label"]}</span></button>'
    for code, info in ELEMENTS.items()
)

snapshot_json = json.dumps(snapshot, ensure_ascii=False)

index = f"""<!doctype html>
<html lang="zh-CN" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark light">
  <meta name="description" content="鸣潮账号养成、锁暝抽卡预算试算与 20+2 队实战操作手法终端。">
  <title>鸣潮 · 共鸣账号规划终端</title>
  <link rel="icon" type="image/x-icon" sizes="36x36" href="{asset('favicon.ico')}">
  <script src="{asset('theme.js')}"></script>
  <link rel="stylesheet" href="{asset('styles.css')}">
  <script id="snapshot-data" type="application/json">{snapshot_json}</script>
  <script defer src="{asset('resonance-fx.js')}"></script>
  <script defer src="{asset('planner.js')}"></script>
</head>
<body>
  {SVG_SPRITE}
  <div class="ambient-backdrop" aria-hidden="true"></div>
  <div class="scroll-progress" aria-hidden="true"><span id="scroll-progress-bar"></span></div>
  <a class="skip" href="#main">跳到正文</a>

  <header class="site-header">
    <div class="wrap masthead">
      <a class="brand" href="#top">
        <span class="brand-mark" aria-hidden="true">{icon('astrite', 'brand-star')}</span>
        <span class="brand-text">鸣潮</span>
        <span class="brand-sub">共鸣规划终端</span>
      </a>
      <nav class="main-nav" aria-label="站点导航">
        <a href="#teams" data-nav="teams">22 队手法</a>
        <a href="#builds" data-nav="builds">角色养成</a>
        <a href="#pulls" data-nav="pulls">锁暝预算</a>
      </nav>
      <div class="header-actions">
        <div class="theme-segmented" role="group" aria-label="切换外观主题">
          <button type="button" data-theme-set="dark" aria-pressed="true" aria-label="深色" title="深色 · 黑海岸玄青">
            {icon('moon', 'theme-icon')}<span class="theme-label">深色</span>
          </button>
          <button type="button" data-theme-set="light" aria-pressed="false" aria-label="浅色" title="浅色 · 今州霜白">
            {icon('sun', 'theme-icon')}<span class="theme-label">浅色</span>
          </button>
          <button type="button" data-theme-set="system" aria-pressed="false" aria-label="跟随系统" title="跟随系统外观">
            {icon('system', 'theme-icon')}<span class="theme-label">自动</span>
          </button>
        </div>
        <a class="header-link header-download" href="guide.pdf">PDF <span aria-hidden="true">↗</span></a>
        <a class="header-link" href="{REPO}" target="_blank" rel="noopener noreferrer" aria-label="GitHub 仓库">GitHub <span aria-hidden="true">↗</span></a>
      </div>
    </div>
  </header>

  <main id="main">
    <section class="hero" id="top" aria-labelledby="hero-title">
      <div class="hero-media" aria-hidden="true">
        <img class="hero-art" src="{asset('resonance-coast.webp')}" width="1942" height="809" fetchpriority="high" alt="">
        <canvas class="hero-canvas" id="resonance-canvas"></canvas>
        <div class="hero-vignette"></div>
      </div>
      <div class="wrap hero-inner">
        <div class="hero-copy">
          <p class="game-title" lang="en">
            {icon('tacet', 'tacet-icon')}
            <span>WUTHERING WAVES // SOLARIS-III</span>
          </p>
          <h1 id="hero-title">鸣潮账号规划</h1>
          <div class="hero-telemetry">
            <span class="telemetry-pill"><span class="pulse-dot" aria-hidden="true"></span>版本 {escape(snapshot['version'])}</span>
            <span class="telemetry-pill">{escape(snapshot['date'])} 账号快照</span>
            <span class="telemetry-pill">20 预设 + 2 规划队</span>
          </div>
          <p class="hero-text">围绕角色养成缺口、锁暝唤取保底试算与全阵容轮切手法打造的共鸣战术终端。</p>
          <div class="hero-links">
            <a class="button primary" href="#teams">进入 22 队手法库 <span aria-hidden="true">↓</span></a>
            <a class="button secondary" href="#pulls">锁暝抽卡试算 <span aria-hidden="true">→</span></a>
            <a class="button tertiary" href="guide.pdf">完整版 PDF <span aria-hidden="true">↗</span></a>
          </div>
        </div>
      </div>
    </section>

    <aside class="overview" aria-label="当前规划重点">
      <div class="wrap overview-grid">
        <a class="overview-card spotlight-card" href="#builds">
          <span class="ov-label">养成优先顺位</span>
          <strong class="ov-value">仇远 → 弗洛洛 → 琳奈</strong>
          <span class="ov-sub">主队收尾后衔接 心 + 玉阙玄华</span>
        </a>
        <a class="overview-card spotlight-card" href="#team-P1">
          <span class="ov-label">唤取核心目标</span>
          <strong class="ov-value ov-electro">{icon('electro', 'ov-el-icon')}锁暝 0 链</strong>
          <span class="ov-sub">到手即组 心 · 锁暝 · 守岸人 同奏队</span>
        </a>
        <a class="overview-card spotlight-card overview-highlight" href="#pulls">
          <span class="ov-label">最坏情况剩余缺口 · 计入月相</span>
          <strong class="ov-amount">
            {icon('astrite', 'astrite-icon')}
            <span data-count-to="{base_deficit}">{base_deficit:,}</span>
            <small>星声</small>
          </strong>
          <div class="ov-meter">
            <div class="ov-meter-track"><span style="width:{base_ready_pct}%"></span></div>
            <span class="ov-sub">已备 {base_ready_pct}% · 约需 {(base_deficit + 159) // 160} 抽</span>
          </div>
        </a>
        <a class="overview-card spotlight-card" href="#pulls">
          <span class="ov-label">快照库存 · {escape(snapshot['date'])}</span>
          <strong class="ov-value ov-tabular">{snapshot['astrite']:,} 星声 / {snapshot['lunite']:,} 月相</strong>
          <span class="ov-sub">角色垫 {snapshot['charPity']} 抽（小保底） · 武器垫 {snapshot['weapPity']} 抽</span>
        </a>
      </div>
    </aside>

    <section class="wrap section reveal" id="teams" aria-labelledby="teams-title">
      <div class="section-heading">
        <div>
          <p class="eyebrow-sm">RESONANCE ROTATIONS // 20 PRESETS + 2 PLANNED</p>
          <h2 id="teams-title">实战阵容与轮切手法</h2>
          <p>支持按分组、主 C 属性、队号或角色名检索；按 <kbd>/</kbd> 快速搜索，<kbd>↑</kbd><kbd>↓</kbd> 切换队伍。</p>
        </div>
        <a class="text-link" href="guide.pdf#page=7">PDF 队号目录 <span aria-hidden="true">↗</span></a>
      </div>

      <div class="tower-preset-bar" aria-label="深塔三队无冲突推荐">
        <span class="tower-label">深塔无冲突推荐</span>
        <div class="tower-chips">
          <a class="tower-chip" href="#team-01" data-el="glacio"><span>01</span> 绯雪 · 琳奈 · 千咲</a>
          <span class="tower-plus" aria-hidden="true">+</span>
          <a class="tower-chip" href="#team-03" data-el="havoc"><span>03</span> 弗洛洛 · 坎特蕾拉 · 仇远</a>
          <span class="tower-plus" aria-hidden="true">+</span>
          <a class="tower-chip" href="#team-05" data-el="aero"><span>05</span> 卡提希娅 · 夏空 · 气动主</a>
          <span class="tower-sep" aria-hidden="true">/</span>
          <a class="tower-chip tower-chip-opt" href="#team-11" data-el="spectro"><span>11</span> 今汐 · 折枝 · 维里奈（衍射补位）</a>
        </div>
      </div>

      <details class="quick-start">
        <summary>
          <span class="summary-main">常用辅助起手速查</span>
          <span class="summary-meta">千咲 · 守岸人 · 维里奈 · 琳奈（展开查看基础协奏节奏）</span>
        </summary>
        <div class="support-grid">{support_cards_html}</div>
      </details>

      <div class="team-layout">
        <aside class="picker" aria-label="选择队伍">
          <div class="filters" hidden>
            <div class="search-field">
              <label class="sr-only" for="team-search">搜索队伍</label>
              {icon('search', 'search-icon')}
              <input id="team-search" type="search" placeholder="搜队号、角色名或属性…" autocomplete="off">
              <kbd class="search-kbd" aria-hidden="true">/</kbd>
            </div>
            <div class="filter-buttons" role="group" aria-label="队伍分组">
              <button type="button" data-filter="all" aria-pressed="true">全部 <span class="count-tag">22</span></button>
              <button type="button" data-filter="main" aria-pressed="false">主力</button>
              <button type="button" data-filter="swap" aria-pressed="false">常用</button>
              <button type="button" data-filter="reserve" aria-pressed="false">备用</button>
              <button type="button" data-filter="planned" aria-pressed="false">规划</button>
            </div>
            <div class="element-filters" role="group" aria-label="按主 C 属性筛选">
              <button type="button" class="el-filter" data-el-filter="all" aria-pressed="true">全属性</button>
              {element_filter_buttons}
            </div>
          </div>
          <div class="picker-status">
            <span id="team-match-count">共 22 支队伍</span>
            <button type="button" class="clear-filter-btn" id="clear-team-filters" hidden>重置筛选</button>
          </div>
          <nav aria-label="队号目录" class="team-list">{''.join(team_links)}</nav>
          <p class="no-result" role="status" hidden>没有匹配的队伍。换一个队号、角色名或清除属性筛选试试。</p>
        </aside>
        <div class="team-panels">{''.join(team_panels)}</div>
      </div>
    </section>

    <section class="wrap section reveal" id="builds" aria-labelledby="builds-title">
      <div class="section-heading">
        <div>
          <p class="eyebrow-sm">RESONATOR DEVELOPMENT // PRIORITY QUEUE</p>
          <h2 id="builds-title">角色养成与分周路线</h2>
          <p>按队伍强度、声骸缺口与补强性价比排序；点击队号标签可直达对应手法。</p>
        </div>
        <a class="text-link" href="{REPO}/blob/main/plans/builds.md" target="_blank" rel="noopener noreferrer">Markdown 计划原文 <span aria-hidden="true">↗</span></a>
      </div>

      <ol class="builds-grid">{''.join(build_cards)}</ol>

      <div class="followup-section">
        <p class="eyebrow-sm">NEXT STAGE // UPCOMING BUILD TARGETS</p>
        <div class="followup-grid">{''.join(followup_cards)}</div>
      </div>

      {weekly_html}
    </section>

    <section class="wrap section reveal" id="pulls" aria-labelledby="pulls-title">
      <div class="section-heading">
        <div>
          <p class="eyebrow-sm">CONVENE FORECAST // WORST-CASE SIMULATION</p>
          <h2 id="pulls-title">锁暝唤取预算与实时试算</h2>
          <p>默认载入 {escape(snapshot['date'])} 实测库存（角色池垫 {snapshot['charPity']} 抽小保底 · 武器池垫 {snapshot['weapPity']} 抽），可实时输入最新星声与波纹试算缺口。</p>
        </div>
        <div class="pulls-links">
          <a class="text-link" href="#pull-priority">4.0 到 4.3 抽卡优先级 <span aria-hidden="true">↓</span></a>
          <a class="text-link" href="{REPO}/blob/main/plans/pulls.md" target="_blank" rel="noopener noreferrer">完整预算与抽卡顺序 <span aria-hidden="true">↗</span></a>
        </div>
      </div>

      <div class="pulls-layout">
        <div class="calc-card spotlight-card" id="convene-calc">
          <div class="calc-top">
            <div>
              <span class="calc-eyebrow">INTERACTIVE SIMULATOR</span>
              <h3>锁暝保底缺口试算仪</h3>
            </div>
            <button type="button" class="ghost-btn" id="calc-reset">{icon('reset', 'btn-icon')}恢复快照</button>
          </div>

          <div class="calc-gauge-row">
            <div class="gauge-wrap" aria-hidden="true">
              <svg class="gauge-svg" viewBox="0 0 140 140">
                <circle class="gauge-bg" cx="70" cy="70" r="56"/>
                <circle class="gauge-arc" id="calc-ring" cx="70" cy="70" r="56" stroke-dasharray="351.86" stroke-dashoffset="351.86"/>
              </svg>
              <div class="gauge-center">
                <span class="gauge-pct" id="calc-pct">{base_ready_pct}%</span>
                <span class="gauge-cap">保底筹备度</span>
              </div>
            </div>
            <div class="calc-readout">
              <span class="readout-label" id="calc-target-label">锁暝 0 链 · 最坏情况还差</span>
              <div class="readout-num">
                {icon('astrite', 'astrite-icon-lg')}
                <strong id="calc-deficit">{base_deficit:,}</strong>
                <span>星声</span>
              </div>
              <div class="readout-meta">
                <span>折合还需 <strong id="calc-need-pulls">{(base_deficit + 159) // 160}</strong> 抽</span>
                <span class="meta-dot">·</span>
                <span>总计目标 <strong id="calc-total-pulls">155</strong> 抽</span>
              </div>
              <p class="calc-hint" id="calc-status-note">已计入当前星声与全部月相；出本体后再按剩余库存评估专武沉冥。</p>
            </div>
          </div>

          <div class="calc-targets" role="group" aria-label="选择唤取目标">
            <button type="button" data-calc-target="c0" aria-pressed="true">锁暝 0 链</button>
            <button type="button" data-calc-target="c0r1" aria-pressed="false">锁暝 0 链 + 沉冥</button>
            <button type="button" data-calc-target="next5" aria-pressed="false">角色下一金</button>
          </div>

          <div class="calc-inputs">
            <label class="field-box">
              <span>现有星声</span>
              <input type="number" id="in-astrite" min="0" step="10" value="{snapshot['astrite']}">
            </label>
            <label class="field-box">
              <span>现有月相</span>
              <input type="number" id="in-lunite" min="0" step="10" value="{snapshot['lunite']}">
            </label>
            <label class="field-box">
              <span>浮金波纹（角色）</span>
              <input type="number" id="in-radiant" min="0" step="1" value="{snapshot['radiant']}">
            </label>
            <label class="field-box">
              <span>铸潮波纹（武器）</span>
              <input type="number" id="in-forging" min="0" step="1" value="{snapshot['forging']}">
            </label>
            <label class="field-box">
              <span>角色池垫抽</span>
              <input type="number" id="in-char-pity" min="0" max="79" step="1" value="{snapshot['charPity']}">
            </label>
            <label class="field-box">
              <span>武器池垫抽</span>
              <input type="number" id="in-weap-pity" min="0" max="79" step="1" value="{snapshot['weapPity']}">
            </label>
            <label class="field-box">
              <span>余波珊瑚（8=1抽）</span>
              <input type="number" id="in-coral" min="0" step="1" value="{snapshot['afterglow']}">
            </label>
            <label class="field-box">
              <span>角色池保底状态</span>
              <select id="in-guarantee">
                <option value="5050" selected>小保底（最坏 160 抽）</option>
                <option value="guaranteed">大保底（最坏 80 抽）</option>
              </select>
            </label>
          </div>

          <div class="calc-toggles">
            <label class="toggle-pill">
              <input type="checkbox" id="opt-lunite" checked>
              <span>计入全部月相</span>
            </label>
            <label class="toggle-pill">
              <input type="checkbox" id="opt-coral">
              <span>计入余波珊瑚换抽（<span id="coral-pulls-preview">{snapshot['afterglow'] // 8}</span> 抽）</span>
            </label>
            <span class="saved-badge" id="calc-saved-state">基准快照</span>
          </div>
        </div>

        <div class="pulls-side">
          <div class="budget-table-card spotlight-card">
            <div class="card-subhead">
              <h3>{escape(snapshot['date'])} 基准预算对照表</h3>
              <span>最坏情况硬吃保底计算</span>
            </div>
            {budget_html}
          </div>

          <div class="prep-card spotlight-card" data-el="electro">
            <div class="prep-head">
              {element_badge('electro')}
              <h3>抽取策略与锁暝预留材料</h3>
            </div>
            <p>先保锁暝本体；拿到本体并实测「心 · 锁暝 · 守岸人」同奏循环后，再根据剩余星声与武器池垫抽决定是否抽专武<strong>沉冥</strong>。</p>
            <div class="prep-mats">
              <div class="mat-pill"><strong>46</strong><span>赝仙的嗟叹</span></div>
              <div class="mat-pill"><strong>60</strong><span>瘴痕残株</span></div>
              <div class="mat-pill"><strong>5 件套</strong><span>轻云出月 / 衔梦照世</span></div>
            </div>
          </div>
        </div>
      </div>

      <section class="pull-forecast" id="pull-priority" aria-labelledby="pull-priority-title">
        <div class="section-heading">
          <div>
            <h2 id="pull-priority-title">4.0 到 4.3 抽卡优先级</h2>
            <p>{inline(forecast_blocks[0])}</p>
          </div>
          <a class="text-link" href="guide.pdf#page=18">PDF 抽卡计划 <span aria-hidden="true">↗</span></a>
        </div>
        <div class="forecast-grid">
          <div class="forecast-card spotlight-card">
            <h3>版本动向</h3>
            {render_forecast_list(forecast_timeline)}
          </div>
          <div class="forecast-card spotlight-card">
            <h3>复刻抽取顺序</h3>
            {render_forecast_list(forecast_ranking, ranked=True)}
          </div>
        </div>
        <p class="forecast-note">{inline(forecast_blocks[-1])}</p>
      </section>
    </section>
  </main>

  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div class="footer-brand">
        {icon('tacet', 'tacet-icon')}
        <span>鸣潮 · 个人共鸣账号规划终端</span>
      </div>
      <div class="footer-links">
        <a href="guide.pdf">完整版 PDF ↗</a>
        <a href="{REPO}" target="_blank" rel="noopener noreferrer">GitHub 仓库 ↗</a>
        <a href="#top">回到顶部 ↑</a>
      </div>
    </div>
  </footer>
</body>
</html>
"""
(ROOT / 'docs/index.html').write_text(index)
print(f'Built docs/index.html ({len(index):,} chars, {len(all_teams)} teams)')
