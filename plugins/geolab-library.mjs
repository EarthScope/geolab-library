/**
 * GeoLab Library gallery.
 *
 * Provides a {geolab-library} directive that places an anywidget on the page.
 * library_listing.py (a document-stage transform) fills the widget's
 * `model.items` from projects/*.yml; this file's `render` then draws the
 * gallery in the browser: text search, tag/author filters, "show more"
 * paging, lazy thumbnails, and filter state kept in the URL.
 *
 * Only the current page of cards is ever in the DOM, so the page stays
 * light however many projects the library holds.
 */

const PLUGIN_PATH = decodeURIComponent(new URL(import.meta.url).pathname);
const PAGE_SIZE = 24;
const TOP_TAGS = 12;
// Project types appear in this order; any others follow, most common first.
const TYPE_ORDER = ['notebook', 'image'];
// Difficulty levels appear in this order; any others follow, most common first.
const DIFFICULTY_ORDER = ['beginner', 'intermediate', 'advanced', 'expert'];
// URL query parameters that hold the filter state.
const PARAMS = { q: 'q', type: 'type', tag: 'tag', author: 'author', difficulty: 'difficulty' };

// Relative POSIX path from directory `fromDir` to file `toFile`. MyST resolves
// a widget's `esm` against the page's folder, so the directive needs this.
function relativePath(fromDir, toFile) {
  const from = fromDir.split('/').filter(Boolean);
  const to = toFile.split('/').filter(Boolean);
  let i = 0;
  while (i < from.length && i < to.length && from[i] === to[i]) i++;
  return [...Array(from.length - i).fill('..'), ...to.slice(i)].join('/');
}

// --- Browser ---

const STYLE = `
.gl { --gl-border:#d0d7de; --gl-muted:#57606a; --gl-card:#fff; --gl-chip:#eef2f6;
      --gl-chip-on:#0969da; --gl-chip-on-fg:#fff; --gl-link:#0969da; --gl-thumb:#f0f3f6;
      font-size:0.95rem; margin:1rem 0; }
.gl.gl-dark { --gl-border:#3d444d; --gl-muted:#9198a1; --gl-card:#151b23; --gl-chip:#262c36;
      --gl-chip-on:#4493f8; --gl-chip-on-fg:#0d1117; --gl-link:#4493f8; --gl-thumb:#212830; }
.gl-search { width:100%; max-width:32rem; box-sizing:border-box; padding:0.55rem 0.75rem;
      font:inherit; color:inherit; background:transparent; border:1px solid var(--gl-border);
      border-radius:6px; }
.gl-facets { margin:0.75rem 0; display:grid; gap:0.4rem; }
.gl-facet-row { display:flex; flex-wrap:wrap; gap:0.35rem; align-items:center; }
.gl-facet-label { font-size:0.8rem; font-weight:600; color:var(--gl-muted); min-width:4rem; }
.gl-chip { font:inherit; font-size:0.78rem; line-height:1.4; padding:0.1rem 0.55rem;
      border:1px solid transparent; border-radius:999px; background:var(--gl-chip);
      color:inherit; cursor:pointer; }
.gl-chip[aria-pressed="true"] { background:var(--gl-chip-on); color:var(--gl-chip-on-fg); }
.gl-chip:focus-visible, .gl-more:focus-visible, .gl-search:focus-visible,
.gl-title button:focus-visible { outline:2px solid var(--gl-chip-on); outline-offset:2px; }
.gl-count { font-size:0.8rem; color:var(--gl-muted); background:none; }
.gl-link { font:inherit; font-size:0.8rem; background:none; border:none; padding:0;
      color:var(--gl-link); cursor:pointer; }
.gl-status { font-size:0.85rem; color:var(--gl-muted); margin:0.5rem 0; }
.gl-grid { display:grid; gap:1rem; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); }
.gl-card { display:flex; flex-direction:column; border:1px solid var(--gl-border);
      border-radius:8px; background:var(--gl-card); overflow:hidden; }
.gl-thumb { aspect-ratio:16/9; background:var(--gl-thumb); display:flex; align-items:center;
      justify-content:center; color:var(--gl-muted); font-size:1.6rem; font-weight:600; }
.gl-thumb img { width:100%; height:100%; object-fit:cover; display:block; }
.gl-body { padding:0.75rem; display:flex; flex-direction:column; gap:0.4rem; flex:1; }
.gl-title { margin:0; font-size:1rem; font-weight:600; line-height:1.3; }
.gl-title button { font:inherit; color:inherit; text-align:left; background:none; border:none;
      padding:0; cursor:pointer; }
.gl-title button:hover { text-decoration:underline; }
.gl-desc { margin:0; font-size:0.85rem; display:-webkit-box; -webkit-line-clamp:3;
      -webkit-box-orient:vertical; overflow:hidden; }
.gl-authors { font-size:0.8rem; color:var(--gl-muted); }
.gl-authors .gl-link { font-size:inherit; }
.gl-badges { display:flex; flex-wrap:wrap; gap:0.35rem; }
.gl-badge { font-size:0.75rem; line-height:1.4; padding:0.1rem 0.55rem; border-radius:999px;
      background:var(--gl-chip); color:var(--gl-muted); }
.gl-tags { display:flex; flex-wrap:wrap; gap:0.25rem; margin-top:auto; padding-top:0.25rem; }
.gl-actions { display:flex; gap:0.75rem; font-size:0.8rem; padding-top:0.25rem; }
.gl-actions a { color:var(--gl-link); }
.gl-more { display:block; margin:1.25rem auto 0; font:inherit; padding:0.45rem 1.1rem;
      border:1px solid var(--gl-border); border-radius:6px; background:transparent;
      color:inherit; cursor:pointer; }
.gl-more[hidden] { display:none; }
.gl-card { cursor:pointer; }
.gl-card:hover { border-color:var(--gl-muted); }
.gl-dialog { width:min(40rem, calc(100vw - 2rem)); max-height:min(85vh, 50rem); padding:0;
      border:1px solid var(--gl-border); border-radius:10px; background:var(--gl-card);
      color:inherit; overflow:auto; }
.gl-dialog::backdrop { background:rgb(0 0 0 / 0.45); }
.gl-dialog .gl-thumb { aspect-ratio:21/9; }
.gl-dialog-body { padding:1rem 1.25rem 1.25rem; display:flex; flex-direction:column; gap:0.6rem; }
.gl-dialog-title { margin:0; padding-right:2rem; font-size:1.3rem; line-height:1.3; }
.gl-dialog-summary { margin:0; white-space:pre-line; line-height:1.5; }
.gl-close { position:absolute; top:0.5rem; right:0.5rem; z-index:1;
      width:2rem; height:2rem; font:inherit; font-size:1.2rem; line-height:1; border-radius:999px;
      border:1px solid var(--gl-border); background:var(--gl-card); color:inherit; cursor:pointer; }
.gl-close:focus-visible, .gl-actions a:focus-visible, .gl-link:focus-visible { outline:2px solid var(--gl-chip-on); outline-offset:2px; }
.gl-meta { margin:0.25rem 0 0; display:grid; grid-template-columns:max-content 1fr; gap:0.35rem 1rem;
      font-size:0.85rem; }
.gl-meta dt { font-weight:600; color:var(--gl-muted); }
.gl-meta dd { margin:0; overflow-wrap:anywhere; }
.gl-meta a { color:var(--gl-link); }
@media (max-width:30rem) { .gl-meta { grid-template-columns:1fr; } .gl-meta dd { margin-bottom:0.35rem; } }
`;

function h(tag, props = {}, ...children) {
  const el = document.createElement(tag);
  for (const [key, value] of Object.entries(props)) {
    if (value === undefined || value === null || value === false) continue;
    if (key === 'class') el.className = value;
    else if (key.startsWith('on')) el.addEventListener(key.slice(2), value);
    else el.setAttribute(key, value === true ? '' : value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

const norm = (s) => String(s ?? '').toLowerCase();

/** Precompute lowercase search fields once per item. */
function indexItems(items) {
  return items.map((item) => ({
    item,
    title: norm(item.title),
    tags: (item.tags ?? []).map(norm),
    authors: (item.authors ?? []).map(norm),
    desc: norm(item.description),
  }));
}

/** Score an item against query terms: every term must match somewhere. */
function score(entry, terms) {
  let total = 0;
  for (const term of terms) {
    let best = 0;
    if (entry.title.includes(term)) best = entry.title.startsWith(term) ? 6 : 4;
    if (best < 3 && entry.tags.some((t) => t.includes(term))) best = 3;
    if (best < 3 && entry.authors.some((a) => a.includes(term))) best = 3;
    if (best < 1 && entry.desc.includes(term)) best = 1;
    if (!best) return 0;
    total += best;
  }
  return total;
}

/** Count how often each value of `field` occurs, most frequent first. Handles both array and scalar fields. */
function countValues(items, field) {
  const counts = new Map();
  for (const item of items) {
    const v = item[field];
    const values = Array.isArray(v) ? v : v ? [v] : [];
    for (const value of values) counts.set(value, (counts.get(value) ?? 0) + 1);
  }
  return [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

/** Rank of a project type in TYPE_ORDER; unlisted types sort after. */
const typeRank = (t) => {
  const i = TYPE_ORDER.indexOf(t);
  return i === -1 ? TYPE_ORDER.length : i;
};

/** Rank of a difficulty in DIFFICULTY_ORDER; unlisted values sort after. */
const difficultyRank = (d) => {
  const i = DIFFICULTY_ORDER.indexOf(d);
  return i === -1 ? DIFFICULTY_ORDER.length : i;
};

function readState() {
  const params = new URL(window.location).searchParams;
  return {
    q: params.get(PARAMS.q) ?? '',
    types: new Set(params.getAll(PARAMS.type)),
    tags: new Set(params.getAll(PARAMS.tag)),
    authors: new Set(params.getAll(PARAMS.author)),
    difficulties: new Set(params.getAll(PARAMS.difficulty)),
  };
}

function writeState(state) {
  const url = new URL(window.location);
  for (const key of Object.values(PARAMS)) url.searchParams.delete(key);
  if (state.q) url.searchParams.set(PARAMS.q, state.q);
  for (const t of state.types) url.searchParams.append(PARAMS.type, t);
  for (const t of state.tags) url.searchParams.append(PARAMS.tag, t);
  for (const a of state.authors) url.searchParams.append(PARAMS.author, a);
  for (const d of state.difficulties) url.searchParams.append(PARAMS.difficulty, d);
  history.replaceState(history.state, '', url);
}

function render({ model, el }) {
  const items = model.get('items') ?? [];
  const entries = indexItems(items);
  // Stable sort keeps unlisted types/difficulties in most-common-first order.
  const typeCounts = countValues(items, 'types').sort((a, b) => typeRank(a[0]) - typeRank(b[0]));
  const tagCounts = countValues(items, 'tags');
  const difficultyCounts = countValues(items, 'difficulty').sort((a, b) => difficultyRank(a[0]) - difficultyRank(b[0]));
  const state = readState();
  let shown = PAGE_SIZE;
  let showAllTypes = false;
  let showAllDifficulties = false;
  let showAllTags = false;

  const root = h('div', { class: 'gl' });
  const search = h('input', {
    class: 'gl-search',
    type: 'search',
    placeholder: `Search ${items.length} projects by title, summary, author, or tag`,
    'aria-label': 'Search projects',
    value: state.q,
  });
  const facets = h('div', { class: 'gl-facets' });
  const status = h('div', { class: 'gl-status', role: 'status', 'aria-live': 'polite' });
  const grid = h('div', { class: 'gl-grid' });
  const more = h('button', { class: 'gl-more', type: 'button' });
  const dialog = h('dialog', { class: 'gl-dialog', 'aria-labelledby': 'gl-dialog-title' });
  // A click on the backdrop lands on the <dialog> itself; close on it.
  dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); });
  root.append(h('style', {}, STYLE), search, facets, status, grid, more, dialog);
  el.append(root);

  // Follow the site's light/dark theme (the theme toggles `dark` on <html>).
  const syncTheme = () => root.classList.toggle('gl-dark', document.documentElement.classList.contains('dark'));
  const themeWatcher = new MutationObserver(syncTheme);
  themeWatcher.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
  syncTheme();

  function toggle(set, value) {
    set.has(value) ? set.delete(value) : set.add(value);
    shown = PAGE_SIZE;
    update();
  }

  function chip(label, pressed, onclick, count) {
    return h(
      'button',
      { class: 'gl-chip', type: 'button', 'aria-pressed': String(pressed), onclick },
      label,
      count !== undefined ? h('span', { class: 'gl-count' }, ` ${count}`) : null,
    );
  }

  function results() {
    const terms = norm(state.q).split(/\s+/).filter(Boolean);
    const matches = [];
    for (const entry of entries) {
      const { item } = entry;
      if (state.types.size && ![...state.types].every((t) => item.types?.includes(t))) continue;
      if (state.tags.size && ![...state.tags].every((t) => item.tags?.includes(t))) continue;
      if (state.authors.size && ![...state.authors].every((a) => item.authors?.includes(a))) continue;
      // Difficulty is a single value per project, so selecting several is an "either" match, not "all".
      if (state.difficulties.size && !state.difficulties.has(item.difficulty)) continue;
      const s = terms.length ? score(entry, terms) : 1;
      if (s) matches.push({ item, s });
    }
    matches.sort((a, b) => b.s - a.s || String(a.item.title).localeCompare(String(b.item.title)));
    return matches.map((m) => m.item);
  }

  /** A row of chips for one field, most common values first, collapsed to TOP_TAGS. */
  function facetRow(label, counts, selected, showAll, onShowAll) {
    const row = h('div', { class: 'gl-facet-row' }, h('span', { class: 'gl-facet-label' }, label));
    const visible = showAll ? counts : counts.slice(0, TOP_TAGS);
    // Always show selected values, even when they're not among the most common.
    const visibleNames = new Set(visible.map(([v]) => v));
    const extra = [...selected].filter((v) => !visibleNames.has(v)).map((v) => [v, undefined]);
    for (const [value, count] of [...extra, ...visible]) {
      row.append(chip(value, selected.has(value), () => toggle(selected, value), count));
    }
    if (counts.length > TOP_TAGS) {
      const noun = label.toLowerCase();
      row.append(
        h('button', {
          class: 'gl-link',
          type: 'button',
          onclick: () => { onShowAll(!showAll); renderFacets(); },
        }, showAll ? `Fewer ${noun}` : `All ${counts.length} ${noun}`),
      );
    }
    return row;
  }

  function renderFacets() {
    facets.replaceChildren(
      ...(difficultyCounts.length
        ? [facetRow('Difficulty', difficultyCounts, state.difficulties, showAllDifficulties, (v) => { showAllDifficulties = v; })]
        : []),
      ...(typeCounts.length
        ? [facetRow('Project Type', typeCounts, state.types, showAllTypes, (v) => { showAllTypes = v; })]
        : []),
      facetRow('Tags', tagCounts, state.tags, showAllTags, (v) => { showAllTags = v; }),
    );
    if (state.authors.size) {
      const authorRow = h('div', { class: 'gl-facet-row' }, h('span', { class: 'gl-facet-label' }, 'Authors'));
      for (const a of state.authors) authorRow.append(chip(a, true, () => toggle(state.authors, a)));
      facets.append(authorRow);
    }
  }

  function thumbnail(item, loading = 'lazy') {
    const fallback = () => h('div', { class: 'gl-thumb', 'aria-hidden': 'true' }, String(item.title ?? '?').trim().charAt(0).toUpperCase());
    if (!item.thumbnail) return fallback();
    const img = h('img', { src: item.thumbnail, alt: '', loading, decoding: 'async' });
    const box = h('div', { class: 'gl-thumb' }, img);
    img.addEventListener('error', () => box.replaceWith(fallback()), { once: true });
    return box;
  }

  // Card and pop-out pieces. `then` runs before a filter toggles (the pop-out closes itself).
  const external = (href) => ({ href, target: '_blank', rel: 'noopener' });

  function authorLinks(item, then = () => {}) {
    return (item.authors ?? []).flatMap((a, i) => [
      i ? ', ' : null,
      h('button', { class: 'gl-link', type: 'button', title: `Show projects by ${a}`, onclick: () => { then(); toggle(state.authors, a); } }, a),
    ]);
  }

  /** Clickable type chips (notebook, image, …), sorted like the type facet. */
  function typeChips(item, then = () => {}) {
    const types = [...(item.types ?? [])].sort((a, b) => typeRank(a) - typeRank(b));
    return types.length ? types.map((t) => chip(t, state.types.has(t), () => { then(); toggle(state.types, t); })) : null;
  }

  /** Top-of-card row: project type chips alongside difficulty/time-commitment pills. */
  function badges(item, then = () => {}) {
    const types = typeChips(item, then);
    const parts = [item.difficulty, item.time_commitment].filter(Boolean);
    if (!types && !parts.length) return null;
    return h('div', { class: 'gl-badges' }, types, parts.map((p) => h('span', { class: 'gl-badge' }, p)));
  }

  function tagChips(item, then = () => {}) {
    if (!(item.tags ?? []).length) return null;
    return h('div', { class: 'gl-tags' }, item.tags.map((t) => chip(t, state.tags.has(t), () => { then(); toggle(state.tags, t); })));
  }

  function actions(item, ...extra) {
    return h(
      'div',
      { class: 'gl-actions' },
      item.url ? h('a', external(item.url), 'Open in GeoLab') : null,
      item.github ? h('a', external(item.github), 'Source') : null,
      ...extra,
    );
  }

  /** An email address or URL as a link; anything else as plain text. */
  function contactLink(value) {
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return h('a', { href: `mailto:${value}` }, value);
    if (/^https?:\/\//.test(value)) return h('a', external(value), value);
    return value;
  }

  function showDetails(item) {
    const close = () => dialog.close();
    const meta = [
      ['Institution', item.institution],
      ['Maintainer contact', item.contact && contactLink(item.contact)],
      ['Recommended image', item.image],
      ['Recommended resources', item.resources],
      ['Citation', item.citation],
      ['Last updated', item.last_updated],
    ].filter(([, value]) => value);
    dialog.replaceChildren(
      h('button', { class: 'gl-close', type: 'button', 'aria-label': 'Close', onclick: close }, '×'),
      thumbnail(item, 'eager'),
      h(
        'div',
        { class: 'gl-dialog-body' },
        h('h2', { class: 'gl-dialog-title', id: 'gl-dialog-title' }, item.title),
        (item.authors ?? []).length ? h('div', { class: 'gl-authors' }, authorLinks(item, close)) : null,
        badges(item, close),
        tagChips(item, close),
        item.description ? h('p', { class: 'gl-dialog-summary' }, item.description) : null,
        item.long_description ? h('p', { class: 'gl-dialog-summary' }, item.long_description) : null,
        meta.length ? h('dl', { class: 'gl-meta' }, meta.flatMap(([label, value]) => [h('dt', {}, label), h('dd', {}, value)])) : null,
        actions(item),
      ),
    );
    dialog.showModal();
    dialog.scrollTop = 0;
  }

  function card(item) {
    const authors = item.authors ?? [];
    return h(
      'article',
      {
        class: 'gl-card',
        // Clicks on the card's own links and buttons do their own thing.
        onclick: (e) => { if (!e.target.closest('a, button')) showDetails(item); },
      },
      thumbnail(item),
      h(
        'div',
        { class: 'gl-body' },
        // A button, so the pop-out is also reachable by keyboard.
        h('h3', { class: 'gl-title' }, h('button', { type: 'button', onclick: () => showDetails(item) }, item.title)),
        authors.length ? h('div', { class: 'gl-authors' }, authorLinks(item)) : null,
        badges(item),
        item.description ? h('p', { class: 'gl-desc' }, item.description) : null,
        tagChips(item),
        actions(item),
      ),
    );
  }

  function update() {
    const matches = results();
    renderFacets();
    grid.replaceChildren(...matches.slice(0, shown).map(card));
    const filtered = state.q || state.types.size || state.tags.size || state.authors.size || state.difficulties.size;
    const count = filtered ? `${matches.length} of ${items.length} projects match` : `${items.length} projects`;
    status.textContent = matches.length
      ? (shown < matches.length ? `${count} · showing ${shown}` : count)
      : 'No projects match these filters.';
    more.hidden = shown >= matches.length;
    more.textContent = `Show ${Math.min(PAGE_SIZE, matches.length - shown)} more`;
    writeState(state);
  }

  let timer;
  search.addEventListener('input', () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      state.q = search.value.trim();
      shown = PAGE_SIZE;
      update();
    }, 120);
  });
  more.addEventListener('click', () => {
    shown += PAGE_SIZE;
    update();
  });

  update();

  // Clean up when the widget leaves the page (client-side navigation), so
  // our query parameters don't follow the reader to other pages.
  let cleaned = false;
  function cleanup() {
    if (cleaned) return;
    cleaned = true;
    clearTimeout(timer);
    themeWatcher.disconnect();
    removalWatcher.disconnect();
    const url = new URL(window.location);
    if (Object.values(PARAMS).some((k) => url.searchParams.has(k))) {
      for (const key of Object.values(PARAMS)) url.searchParams.delete(key);
      history.replaceState(history.state, '', url);
    }
  }
  const removalWatcher = new MutationObserver(() => {
    if (!root.isConnected) cleanup();
  });
  removalWatcher.observe(document.body, { childList: true, subtree: true });
  return cleanup;
}

// --- Build (runs in MyST, not the browser) ---

const geolabLibraryDirective = {
  name: 'geolab-library',
  doc: 'Searchable gallery of GeoLab Library projects (items filled by library_listing.py).',
  run(_data, vfile) {
    const fromDir = vfile.path.replace(/\/[^/]*$/, '');
    return [
      {
        type: 'anywidget',
        esm: relativePath(fromDir, PLUGIN_PATH),
        // `source` marks this widget for library_listing.py, which adds `items`.
        model: { source: 'geolab', items: [] },
        id: Math.random().toString(36).slice(2),
      },
    ];
  },
};

export default {
  name: 'GeoLab Library gallery',
  directives: [geolabLibraryDirective],
  render,
};
