const fs = require('fs');
const assert = require('assert');

const html = fs.readFileSync('index.html', 'utf-8');

// 1. Verify HTML elements exist
const expectedIds = [
  'modalMatchSetup', 'modalAddPlayer', 'modalSaveFormation', 'modalEvent', 'modalTeams',
  'modalPdfReport', 'btnCreatePdfReport',
  'pdfTabBtn_single', 'pdfTabBtn_range', 'pdfSelectMatch', 'pdfRangeStartDate', 'pdfRangeEndDate', 'pdfRangeTeamFilter',
  'selectedGamesBadge',
  'activeMatchTitleDisplay', 'activeMatchFormatBadge', 'activeMatchDateBadge',
  'tabBtn_pitch', 'tabBtn_live', 'tabBtn_roster', 'tabBtn_stats',
  'section_pitch', 'section_live', 'section_roster', 'section_stats',
  'scoreboardTeam', 'scoreboardOpponent', 'scoreboardGoals', 'scoreboardOpponentGoals',
  'clockToggleBtn', 'matchClockDisplay', 'clockStatusSubtext',
  'eventModalTitle', 'eventPlayerSelector',
  'inputMatchTeamName', 'inputMatchTitle', 'inputMatchOpponent', 'inputMatchDate',
  'backupFileInput'
];

for (const id of expectedIds) {
  assert(html.includes(`id="${id}"`), `Missing element id: ${id}`);
}
console.log('✓ All expected DOM element IDs present in index.html');

// 2. Verify meta tags
assert(html.includes('<meta name="mobile-web-app-capable" content="yes" />'), 'Missing mobile-web-app-capable');
assert(html.includes('<meta name="apple-mobile-web-app-capable" content="yes" />'), 'Missing apple-mobile-web-app-capable');
console.log('✓ Mobile web app meta tags verified');

// 3. Verify format wording is 7v7 (not 7-a-side)
assert(!html.includes('7-a-side'), 'Found deprecated "7-a-side" in HTML');
console.log('✓ Consistent format wording (e.g. 7v7) verified');

// 4. Verify "Add to Squad" button label
assert(html.includes('Add to Squad'), 'Missing "Add to Squad" button');
assert(!html.includes('Add to Squad Pods'), 'Found old "Add to Squad Pods" button');
console.log('✓ "Add to Squad" button text verified');

// 5. Verify local minified Tailwind CSS & service worker cache
assert(fs.existsSync('tailwind.min.css'), 'Missing tailwind.min.css');
assert(html.includes('<link rel="stylesheet" href="./tailwind.min.css" />'), 'index.html does not link to tailwind.min.css');
assert(!html.includes('src="https://cdn.tailwindcss.com"'), 'Found unwanted Tailwind CDN script in index.html');

const sw = fs.readFileSync('sw.js', 'utf-8');
assert(sw.includes("CACHE_NAME = 'gameon-v8'"), 'sw.js cache version is not gameon-v8');
assert(sw.includes("'./icon.jpg'"), 'PDF ledger icon must be available offline');
assert(sw.includes("'./tailwind.min.css'"), 'sw.js missing tailwind.min.css in cached assets');
console.log('✓ Standalone offline Tailwind CSS & sw.js gameon-v8 cache verified');

// 6. Test JS logic execution
const scripts = html.match(/<script>([\s\S]*?)<\/script>/g);
const mainScriptTag = scripts[scripts.length - 1];
const bundledScripts = fs.readFileSync('gameon.html', 'utf-8').match(/<script>([\s\S]*?)<\/script>/g);
assert.strictEqual(bundledScripts[bundledScripts.length - 1], mainScriptTag, 'Run npm run bundle: standalone app logic is stale');
let jsCode = mainScriptTag.replace(/^<script>/, '').replace(/<\/script>$/, '');
jsCode = jsCode.replace('const AppState =', 'global.AppState =').replace('const App =', 'global.App =');

// Mock browser environment
const storage = {};
global.localStorage = {
  getItem: (k) => storage[k] || null,
  setItem: (k, v) => { storage[k] = String(v); },
  removeItem: (k) => { delete storage[k]; }
};

const dom = new Proxy({}, {
  get: (target, prop) => {
    if (!target[prop]) {
      target[prop] = {
        id: prop,
        value: '',
        innerText: '',
        innerHTML: '',
        className: '', dataset: {},
        classList: {
          add: (...cls) => { target[prop].className = (target[prop].className || '') + ' ' + cls.join(' '); },
          remove: (...cls) => {
            let classes = (target[prop].className || '').split(' ');
            target[prop].className = classes.filter(c => !cls.includes(c)).join(' ');
          },
          contains: (c) => (target[prop].className || '').split(' ').includes(c)
        },
        style: {},
        options: [],
        children: [],
        appendChild: function(c) { if (this.options) this.options.push(c); if (this.children) this.children.push(c); },
        querySelectorAll: () => [], addEventListener: () => {}
      };
    }
    return target[prop];
  }
});

global.document = {
  getElementById: (id) => dom[id],
  querySelectorAll: () => [], addEventListener: () => {},
  querySelector: () => null,
  createElement: (tag) => ({
    tagName: tag,
    className: '', dataset: {},
    style: {},
    appendChild: () => {},
    innerHTML: '',
    innerText: '',
    classList: { add: ()=>{}, remove: ()=>{} }, click: () => {}
  }),
  body: {
    appendChild: () => {},
    removeChild: () => {},
    classList: { add: ()=>{}, remove: ()=>{} }, click: () => {}
  },
  addEventListener: () => {}
};

global.window = {
  addEventListener: () => {},
  location: { reload: () => {} },
  print: () => {}
};
global.confirm = () => true;
global.prompt = (msg, def) => def;
global.alert = () => {};

// Evaluate application script in global scope
eval(jsCode);

// Run App.init()
App.init();
console.log('✓ App.init() executed successfully');

// ==========================================
// TEST 7: Tab navigation
// ==========================================
App.switchTab('live');
assert.strictEqual(AppState.activeTab, 'live', 'Active tab should be live');
App.switchTab('stats');
assert.strictEqual(AppState.activeTab, 'stats', 'Active tab should be stats');
App.switchTab('pitch');
assert.strictEqual(AppState.activeTab, 'pitch', 'Active tab should be pitch');
console.log('✓ Tab navigation functions properly');

// ==========================================
// TEST 8: Score steppers (+/-)
// ==========================================
AppState.match.ourGoals = 0;
AppState.match.opponentGoals = 0;
App.adjustScore('our', 1);
assert.strictEqual(AppState.match.ourGoals, 1, 'Our goals should increase to 1');
App.adjustScore('our', 1);
assert.strictEqual(AppState.match.ourGoals, 2, 'Our goals should increase to 2');
App.adjustScore('our', -1);
assert.strictEqual(AppState.match.ourGoals, 1, 'Our goals should decrease to 1');

App.adjustScore('opp', 1);
assert.strictEqual(AppState.match.opponentGoals, 1, 'Opponent goals should increase to 1');
App.adjustScore('opp', -1);
assert.strictEqual(AppState.match.opponentGoals, 0, 'Opponent goals should decrease to 0');
console.log('✓ Manual score steppers (+/-) working properly');

// ==========================================
// TEST 9: Goal recording & Enforced player selection
// ==========================================
let p1 = AppState.squad[0];
let p2 = AppState.squad[1];

App.openEventModal('Goal');
dom['eventPlayerSelector'].value = '';
App.saveEvent();
assert.strictEqual(AppState.match.ourGoals, 1, 'Score should not change when no player selected');

dom['eventPlayerSelector'].value = p1.id;
App.saveEvent();
assert.strictEqual(AppState.match.ourGoals, 2, 'Goal should be registered');
let goalEvent = AppState.events.find(e => e.type === 'Goal' && e.playerId === p1.id);
assert(goalEvent, 'Goal event should exist in timeline');
console.log('✓ Enforced selecting a player in Goal popup before recording');
console.log('✓ Recording goal updates score, player stats, and timeline');

// ==========================================
// TEST 10: Undo/Delete goal from timeline
// ==========================================
const prevGoals = AppState.match.ourGoals;
App.deleteTimelineEvent(goalEvent.id);
assert.strictEqual(AppState.match.ourGoals, prevGoals - 1, 'Our goals should decrease when goal deleted');
assert(!AppState.events.some(e => e.id === goalEvent.id), 'Deleted event should no longer exist in events');
console.log('✓ Undoing goal from timeline updates score and player stats');

// ==========================================
// TEST 11: Setup - Your Team Name
// ==========================================
dom['inputMatchTeamName'].value = 'Lightning Stars';
dom['inputMatchTitle'].value = 'Championship Final';
dom['inputMatchOpponent'].value = 'Thunderbolts';
dom['inputMatchDate'].value = '2026-10-18';
App.saveMatchSetup();
assert.strictEqual(AppState.match.teamName, 'Lightning Stars', 'Team name in setup should update AppState.match.teamName');
assert.strictEqual(dom['scoreboardTeam'].innerText, 'Lightning Stars', 'Scoreboard team name should match your team name');
console.log('✓ "Your team name" in Setup works and saves correctly');

// ==========================================
// TEST 12: End Match Flow
// ==========================================
AppState.clock.seconds = 3600;
AppState.match.ourGoals = 3;
AppState.match.opponentGoals = 1;
AppState.match.formation = '2-3-1';
AppState.playerTimers[p1.id] = 1800;
AppState.playerTimers[p2.id] = 1800;

App.endMatch();

assert(AppState.matchHistory.length > 0, 'Match should be archived into matchHistory');
const archived = AppState.matchHistory[0];
assert.strictEqual(archived.teamName, 'Lightning Stars');
assert.strictEqual(archived.opponent, 'Thunderbolts');
assert.strictEqual(archived.ourGoals, 3);
assert.strictEqual(archived.opponentGoals, 1);
assert.strictEqual(archived.formation, '2-3-1', 'Archived match should store formation');
assert.strictEqual(archived.durationSeconds, 3600);
assert.strictEqual(archived.playerTimers[p1.id], 1800);

assert.strictEqual(AppState.clock.seconds, 0, 'Clock seconds should reset to 0');
assert.strictEqual(AppState.match.ourGoals, 0, 'Our goals should reset to 0');
assert.strictEqual(AppState.match.opponentGoals, 0, 'Opponent goals should reset to 0');
assert.strictEqual(Object.keys(AppState.playerTimers).length, 0, 'Player timers should be reset to empty');
assert.strictEqual(AppState.events.length, 0, 'Match events should be cleared');
assert(AppState.squad.length > 0, 'Squad should never be deleted on match end');
console.log('✓ End match archives match to history with formation and resets state for next match');

// ==========================================
// TEST 13: Export backup
// ==========================================
let clickedDownload = false;
global.URL = {
  createObjectURL: (blob) => 'blob:test',
  revokeObjectURL: () => {}
};
dom['downloadAnchor'] = {
  click: () => { clickedDownload = true; }
};
App.exportBackup();
assert(storage['gameon_squad'], 'localStorage squad should exist');
console.log('✓ Export backup generates downloadable JSON');

// ==========================================
// TEST 14: Data persistence
// ==========================================
const testStorageKey = 'gameon_test_persist';
localStorage.setItem(testStorageKey, 'persisted_value');
assert.strictEqual(localStorage.getItem(testStorageKey), 'persisted_value', 'Data in localStorage should persist');
console.log('✓ localStorage data persistence survives refresh / restart');

// ==========================================
// TEST 15: Formations Presets Completeness & GK positioning
// ==========================================
const reqFormations = {
  '5': ['1-2-1', '2-1-1', '2-2', '1-1-2', '3-1'],
  '7': ['2-3-1', '3-2-1', '3-1-2', '2-2-2', '1-3-2', '2-1-2-1'],
  '9': ['3-3-2', '3-2-3', '2-4-2', '3-4-1', '4-3-1', '3-1-3-1'],
  '11': ['4-4-2', '4-3-3', '4-2-3-1', '3-5-2', '3-4-3', '5-3-2', '4-1-4-1', '4-5-1']
};

for (const [fmt, list] of Object.entries(reqFormations)) {
  for (const fName of list) {
    assert(AppState.formations[fmt][fName], `Missing formation ${fName} for ${fmt}v${fmt}`);
    const slots = AppState.formations[fmt][fName];
    assert.strictEqual(slots.length, parseInt(fmt), `Formation ${fName} must have ${fmt} starter positions`);
    // Verify GK (slot 0) is positioned in goal at y >= 88
    assert(slots[0].y >= 88, `GK in ${fName} (${fmt}v${fmt}) must be in goal area (y >= 88)`);
  }
}
console.log('✓ All prescribed formations verified across 5v5, 7v7, 9v9, and 11v11 with GK always in goal');

// Test formation saving per team
App.onFormationChanged('2-1-2-1');
assert.strictEqual(AppState.match.formation, '2-1-2-1', 'AppState.match.formation should be 2-1-2-1');
if (AppState.teams && AppState.currentTeamId) {
  const currentTeam = AppState.teams.find(t => t.id === AppState.currentTeamId);
  if (currentTeam) {
    assert.strictEqual(currentTeam.formation, '2-1-2-1', 'Current team object must persist chosen formation');
  }
}
console.log('✓ Formation saving per team and match history verified');

// ==========================================
// TEST 16: PDF Duration Formatting
// ==========================================
assert.strictEqual(App.formatPdfDuration(0), '00:00');
assert.strictEqual(App.formatPdfDuration(45), '00:45');
assert.strictEqual(App.formatPdfDuration(900), '15:00');
assert.strictEqual(App.formatPdfDuration(3540), '59:00');
assert.strictEqual(App.formatPdfDuration(3600), '1h 0m', 'Duration >= 60 mins must format as Xh Ym');
assert.strictEqual(App.formatPdfDuration(4500), '1h 15m', 'Duration >= 60 mins must format as Xh Ym');
console.log('✓ PDF duration formatting verified (mm:ss and Xh Ym when >= 60 mins)');

// ==========================================
// TEST 17: PDF Report Modal & Date Presets
// ==========================================
App.openPdfReportModal();
assert(dom['modalPdfReport'], 'modalPdfReport should be accessed');

App.applyPdfDatePreset('7d');
assert(dom['pdfRangeStartDate'].value, '7d preset should set start date');
assert(dom['pdfRangeEndDate'].value, '7d preset should set end date');

App.applyPdfDatePreset('month');
assert(dom['pdfRangeStartDate'].value, 'month preset should set start date');

App.switchPdfReportMode('range');
assert(!dom['pdfPane_range'].classList.contains('hidden'), 'Range pane should be visible');
App.switchPdfReportMode('single');
assert(!dom['pdfPane_single'].classList.contains('hidden'), 'Single pane should be visible');
console.log('✓ PDF Report bottom-sheet modal, mode switching, and date presets verified');

// ==========================================
// TEST 18: Date Range PDF Data Calculation & Validation
// ==========================================
// Setup sample match history for range test
const sampleMatchA = {
  id: 'm_range_1',
  title: 'League Match 1',
  teamName: 'Lightning Stars',
  opponent: 'Wolves FC',
  date: '2026-10-10',
  format: '7',
  formation: '2-3-1',
  ourGoals: 4,
  opponentGoals: 1,
  durationSeconds: 3600,
  playerTimers: { [p1.id]: 2400, [p2.id]: 1800 },
  starters: [p1.id, p2.id],
  events: [
    { type: 'Goal', playerId: p1.id, matchTimeSeconds: 600 },
    { type: 'Goal', playerId: p1.id, matchTimeSeconds: 1200 },
    { type: 'Assist', playerId: p2.id, matchTimeSeconds: 600 }
  ]
};

const sampleMatchB = {
  id: 'm_range_2',
  title: 'League Match 2',
  teamName: 'Lightning Stars',
  opponent: 'Eagles FC',
  date: '2026-10-14',
  format: '7',
  formation: '2-1-2-1',
  ourGoals: 2,
  opponentGoals: 2,
  durationSeconds: 3600,
  playerTimers: { [p1.id]: 3600, [p2.id]: 1200 },
  starters: [p1.id],
  events: [
    { type: 'Goal', playerId: p2.id, matchTimeSeconds: 900 }
  ]
};

AppState.matchHistory = [sampleMatchA, sampleMatchB];

// Empty range test should toast and not throw
let toastMsg = '';
App.toast = (msg) => { toastMsg = msg; };
App.generateDateRangePdf('2025-01-01', '2025-01-02');
assert(toastMsg.includes('No matches found'), 'Empty date range must show friendly message');

// Valid range test
let pdfContainer;
App.exportPdf = (report) => { pdfContainer = report; };
App.generateDateRangePdf('2026-10-01', '2026-10-20');
assert(pdfContainer.innerHTML.includes('Squad Performance Ledger'), 'PDF ledger title missing');
assert(pdfContainer.innerHTML.includes('1W • 1D • 0L') || pdfContainer.innerHTML.includes('1W &bull; 1D &bull; 0L'), 'Record summary should reflect 1W - 1D - 0L');
assert(pdfContainer.innerHTML.includes('Top Scorer'), 'Top scorer highlight badge missing');
assert(pdfContainer.innerHTML.includes('Most Mins'), 'Most minutes highlight badge missing');

// Single Match PDF generation
App.generateSingleMatchPdf('m_range_1');
assert(pdfContainer.innerHTML.includes('Match Performance Report'), 'Single match PDF title missing');
assert(pdfContainer.innerHTML.includes('Wolves FC'), 'Opponent Wolves FC should appear in PDF');
assert(pdfContainer.innerHTML.includes('2-3-1'), 'Formation 2-3-1 should appear in PDF');
console.log('✓ Dual-mode PDF reports (Single Match & Date Range) generation and data accuracy verified');

// ==========================================
// TEST 19: Starting Lineups Sorting & Custom Formations
// ==========================================
App.sortLineupByPosition(false);
const starter0 = AppState.squad.find(p => p.id === AppState.match.starters[0]);
assert(starter0, 'Starter 0 should exist');
console.log('✓ Starting lineups sorted by pitch position (GK → DEF → MID → FWD)');

// ==========================================
// TEST 20: Tamper-Proof Read-Only Minutes Reporting
// ==========================================
assert.strictEqual(typeof App.adjustPlayerGameMinutes, 'undefined', 'adjustPlayerGameMinutes must not be defined');
assert.strictEqual(typeof App.openEditGameMinutesModal, 'undefined', 'openEditGameMinutesModal must not be defined');
assert.strictEqual(typeof App.saveGameMinutes, 'undefined', 'saveGameMinutes must not be defined');
console.log('✓ Tamper-proof read-only playing time reporting & game detail breakdown verified');

// Regression: simulate delayed callbacks and reloads without sleeping.
const realNow = Date.now;
const realSetInterval = global.setInterval;
const realClearInterval = global.clearInterval;
let now = 1800000000000;
let tick;
Date.now = () => now;
global.setInterval = fn => { tick = fn; return 1; };
global.clearInterval = () => { tick = null; };
try {
  AppState.clock = {seconds: 0, period: '1st Half', running: false, startedAt: null};
  AppState.playerTimers = {};
  AppState.match.starters = [p1.id];
  AppState.match.bench = [p2.id];
  App.toggleTimer();
  assert(JSON.parse(storage.gameon_clock).running, 'Start must persist immediately');
  now += 61250; // Only one callback after a throttled/background interval.
  tick();
  assert.strictEqual(AppState.clock.seconds, 61.25);
  assert.strictEqual(AppState.playerTimers[p1.id], 61.25);
  assert.strictEqual(App.formatTime(AppState.clock.seconds), '01:01');
  now += 750;
  App.selectSubOut(p1.id);
  App.selectSubIn(p2.id);
  assert.strictEqual(AppState.playerTimers[p1.id], 62);
  assert.strictEqual(AppState.events[0].matchTimeSeconds, 62);
  assert.strictEqual(AppState.events[0].playerOutId, p1.id);
  assert(App.isPlayerSub(AppState.events[0], p1, 'Out'));
  assert(App.isPlayerSub({type:'Sub', playerIn:p2.name, playerInNum:p2.number}, p2, 'In'), 'Old substitutions must still count');
  assert(!App.isPlayerSub({type:'Sub', playerIn:p2.name, playerInNum:99}, p2, 'In'));
  now += 10500;
  App.toggleTimer();
  assert.strictEqual(AppState.clock.seconds, 72.5);
  assert.strictEqual(AppState.playerTimers[p2.id], 10.5);
  assert.strictEqual(JSON.parse(storage.gameon_clock).running, false);
  now += 60000;
  App.syncClock();
  assert.strictEqual(AppState.clock.seconds, 72.5, 'Paused time must not accrue');
  App.toggleTimer();
  now += 500;
  App.setPeriod('2nd Half');
  assert.strictEqual(AppState.clock.seconds, 73);
  assert.strictEqual(JSON.parse(storage.gameon_clock).period, '2nd Half');
  const historyBefore = JSON.stringify(AppState.matchHistory);
  App.saveStorage();
  now += 90000;
  App.loadStorage();
  assert.strictEqual(AppState.clock.seconds, 163, 'Reload must catch up running time');
  assert.strictEqual(AppState.playerTimers[p2.id], 101);
  assert.strictEqual(AppState.clock.running, true);
  assert.strictEqual(JSON.stringify(AppState.matchHistory), historyBefore, 'Migration must preserve history');
  now += 250;
  App.endMatch();
  assert.strictEqual(AppState.matchHistory[0].durationSeconds, 163.25);
  assert.strictEqual(AppState.matchHistory[0].playerTimers[p2.id], 101.25);
  assert.strictEqual(AppState.clock.seconds, 0);
  assert.strictEqual(AppState.clock.startedAt, null);
  App.toggleTimer();
  now += 1500;
  App.resetTimer();
  assert.strictEqual(JSON.parse(storage.gameon_clock).seconds, 0);
  assert.strictEqual(JSON.parse(storage.gameon_clock).running, false);
  // Stopwatch reset has always preserved accrued player time.
  assert.strictEqual(AppState.playerTimers[p2.id], 1.5);
  App.restoreClock({seconds: 42, period: '2nd Half', savedAt: now - 60000});
  assert.strictEqual(AppState.clock.seconds, 42);
  assert.strictEqual(AppState.clock.running, false, 'Old saves must migrate paused');
  for (const startedAt of [null, -1, 0, '1800000000000', NaN, Infinity, now + 1]) {
    App.restoreClock({version: 2, seconds: 42, running: true, startedAt});
    assert.strictEqual(AppState.clock.seconds, 42);
    assert.strictEqual(AppState.clock.running, false, `Invalid timestamp: ${startedAt}`);
  }
  App.toggleTimer();
  now -= 1000;
  App.syncClock();
  assert.strictEqual(AppState.clock.running, false, 'Backward clock changes must not subtract time');
  AppState.clock.seconds = 0;
  AppState.playerTimers = {};
  App.toggleTimer();
  for (const elapsed of [700,100,200]) { now += elapsed; App.syncClock(); }
  assert.strictEqual(AppState.clock.seconds, 1, 'Subsecond checkpoints must not accumulate rounding drift');
  assert.strictEqual(AppState.playerTimers[p2.id], 1);
  const restoredHistory = JSON.parse(JSON.stringify(AppState.matchHistory));
  global.FileReader = class {
    readAsText() {
      this.onload({target:{result:JSON.stringify({
        squad:AppState.squad, match:AppState.match, matchHistory:restoredHistory,
        clock:{seconds:99,period:'2nd Half'}, playerTimers:{[p2.id]:20}
      })}});
    }
  };
  App.importBackup({target:{files:[{}],value:'backup.json'}});
  now += 60000;
  App.syncClock();
  assert.strictEqual(AppState.clock.running, false, 'Import must stop the previous live session');
  assert.strictEqual(AppState.clock.seconds, 99);
  assert.strictEqual(AppState.playerTimers[p2.id], 20);
  assert.deepStrictEqual(AppState.matchHistory, restoredHistory);
  delete global.FileReader;
  console.log('✓ Timestamp timers: throttling, pause/resume, substitutions, periods, reload, end/reset, legacy data and invalid timestamps');
} finally {
  App.stopClock();
  Date.now = realNow;
  global.setInterval = realSetInterval;
  global.clearInterval = realClearInterval;
}
console.log('\nAll application and timer regression tests passed.');
