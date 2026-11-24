const search = document.querySelector('#team-search');
const buttons = [...document.querySelectorAll('[data-filter]')];
const links = [...document.querySelectorAll('[data-team]')];
const panels = new Map(links.map(link => [
  link.dataset.team, document.querySelector(link.getAttribute('href')),
]));
const empty = document.querySelector('.no-result');
let group = 'all';

function requestedTeam() {
  return location.hash.match(/^#team-(\d{2})$/)?.[1];
}

function update(keepSelected = false) {
  const query = search.value.trim().toLowerCase();
  const number = /^\d{1,2}$/.test(query) ? query.padStart(2, '0') : null;
  const matches = links.filter(link =>
    (group === 'all' || group === link.dataset.group) &&
    (number ? link.dataset.team === number : link.dataset.search.toLowerCase().includes(query))
  );
  const active = keepSelected && matches.some(link => link.dataset.team === requestedTeam())
    ? requestedTeam() : matches[0]?.dataset.team;
  for (const link of links) {
    const selected = link.dataset.team === active;
    link.hidden = !matches.includes(link);
    if (selected) link.setAttribute('aria-current', 'true');
    else link.removeAttribute('aria-current');
    panels.get(link.dataset.team).hidden = !selected;
  }
  empty.hidden = matches.length > 0;
}

function setGroup(next) {
  group = next;
  for (const button of buttons) {
    button.setAttribute('aria-pressed', String(button.dataset.filter === group));
  }
}

function followTeam() {
  const target = requestedTeam();
  if (!panels.has(target)) return;
  const link = links.find(candidate => candidate.dataset.team === target);
  if (link.hidden) {
    setGroup('all');
    search.value = '';
  }
  update(true);
  panels.get(target).scrollIntoView({block: 'start'});
}

document.querySelector('.filters').hidden = false;
search.addEventListener('input', () => update(true));
for (const button of buttons) {
  button.addEventListener('click', () => {
    setGroup(button.dataset.filter);
    update(true);
  });
}
window.addEventListener('hashchange', followTeam);
update(true);
followTeam();
