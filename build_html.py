import os

# Historical scaffold only. It predates the maintained app and would overwrite fixes.
raise SystemExit('index.html is the maintained source. Use python bundle_offline.py to build gameon.html; do not regenerate index.html from this legacy scaffold.')

with open('icon_b64.txt', 'r', encoding='utf-8') as f:
    icon_b64 = f.read().strip()

with open('icon_b64_png.txt', 'r', encoding='utf-8') as f:
    icon_b64_png = f.read().strip()

html_template = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <title>GameOn — Tactical Pitch & Live Rotations</title>
  <link rel="manifest" href="./manifest.json" />
  <meta name="theme-color" content="#0a1222" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <meta name="apple-mobile-web-app-title" content="GameOn" />
  
  <!-- Apple Home Screen Icons -->
  <link rel="apple-touch-icon" href="./icon-180.png" />
  <link rel="apple-touch-icon" sizes="180x180" href="./icon-180.png" />
  <link rel="apple-touch-icon" sizes="192x192" href="./icon-192.png" />
  <link rel="apple-touch-icon" sizes="512x512" href="./icon-512.png" />

  <!-- Standard & Android Favicons -->
  <link rel="icon" type="image/png" sizes="192x192" href="./icon-192.png" />
  <link rel="icon" type="image/png" sizes="512x512" href="./icon-512.png" />
  <link rel="shortcut icon" href="./icon-192.png" />

  <!-- Tailwind CSS (Offline local with CDN fallback) -->
  <script src="./tailwind.js"></script>
  <script>
    if (typeof tailwind === 'undefined') {
      document.write('<script src="https://cdn.tailwindcss.com"><\\/script>');
    }
  </script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            obsidian: { 950: '#070d18', 900: '#0a1222', 800: '#111b2f', 700: '#1b2a47' },
            cyber: { cyan: '#00f2fe', mint: '#10b981', emerald: '#059669', darkgreen: '#064e3b' }
          },
          fontFamily: {
            sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', 'sans-serif']
          }
        }
      }
    };
  </script>

  <!-- html2pdf (Offline local with CDN fallback) -->
  <script src="./html2pdf.bundle.min.js"></script>
  <script>
    if (typeof html2pdf === 'undefined') {
      document.write('<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"><\\/script>');
    }
  </script>

  <style>
    /* Safe Area & Mobile Optimization */
    body {
      -webkit-tap-highlight-color: transparent;
      overscroll-behavior-y: none;
      user-select: none;
      -webkit-user-select: none;
    }
    .pb-safe { padding-bottom: env(safe-area-inset-bottom, 16px); }

    .glass-card {
      background: rgba(17, 27, 47, 0.75);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .glow-cyan {
      box-shadow: 0 0 20px -2px rgba(0, 242, 254, 0.35);
    }
    .glow-pulse {
      animation: pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    @keyframes pulse-ring {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: .75; transform: scale(1.05); }
    }
    
    .pitch-night {
      background: radial-gradient(circle at 50% 50%, #064e3b 0%, #043629 60%, #022018 100%);
      box-shadow: inset 0 0 35px rgba(0, 0, 0, 0.8), 0 10px 30px -10px rgba(0, 242, 254, 0.2);
    }
    .pitch-day {
      background: radial-gradient(circle at 50% 50%, #16a34a 0%, #15803d 60%, #166534 100%);
      box-shadow: inset 0 0 25px rgba(0, 0, 0, 0.4), 0 10px 25px -10px rgba(22, 163, 74, 0.3);
    }

    .player-token {
      transition: transform 0.12s ease-out, box-shadow 0.15s ease-out;
      touch-action: none;
    }
    .player-token:active {
      transform: scale(1.12);
    }
  </style>
</head>
<body class="bg-obsidian-950 text-slate-100 min-h-screen font-sans flex flex-col transition-colors duration-300 select-none pb-24">

  <!-- HEADER -->
  <header class="sticky top-0 z-40 bg-obsidian-950/85 backdrop-blur-md border-b border-white/10 px-4 py-3 flex items-center justify-between">
    <div class="flex items-center space-x-3">
      <img id="appHeaderIcon" src="./icon.jpg" alt="GameOn" class="w-9 h-9 rounded-xl shadow-lg ring-1 ring-cyber-cyan/40 object-cover" />
      <div>
        <div class="flex items-center">
          <span class="text-xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-400">Game</span>
          <span class="text-xl font-black tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-cyber-cyan to-cyber-mint ml-0.5">On</span>
        </div>
      </div>
    </div>

    <!-- Header Actions (Day/Night, PDF) -->
    <div class="flex items-center space-x-2">
      <button id="themeToggleBtn" onclick="App.toggleDayNight()" class="w-9 h-9 rounded-2xl bg-obsidian-800 border border-white/10 flex items-center justify-center text-slate-300 hover:text-white transition active:scale-95" title="Toggle Day/Night Turf Mode">
        <span id="themeIcon">🌙</span>
      </button>
      <button onclick="App.openExportModal()" class="px-2.5 py-1.5 rounded-2xl bg-cyber-cyan/10 hover:bg-cyber-cyan/20 border border-cyber-cyan/30 text-cyber-cyan text-xs font-semibold flex items-center space-x-1 transition active:scale-95">
        <span>📄</span>
        <span>PDF</span>
      </button>
    </div>
  </header>

  <!-- MAIN VIEWPORT -->
  <main class="flex-1 max-w-lg w-full mx-auto p-3.5 space-y-4">
    
    <!-- MATCH METADATA STATUS POD -->
    <div class="glass-card rounded-[24px] p-3.5 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-cyber-cyan/20 to-cyber-mint/20 border border-cyber-cyan/40 flex items-center justify-center text-lg">
          ⚽
        </div>
        <div>
          <h2 id="activeMatchTitleDisplay" class="font-bold text-sm tracking-wide text-white">Match 1 vs Echo Strikers</h2>
          <div class="flex items-center space-x-2 text-[11px] text-slate-400 mt-0.5">
            <span id="activeMatchFormatBadge" class="px-1.5 py-0.2 rounded bg-white/10 text-white font-medium">7-a-side</span>
            <span id="activeMatchDateBadge">2026-10-15</span>
          </div>
        </div>
      </div>
      <button onclick="App.openMatchSetupModal()" class="px-3 py-1.5 rounded-xl bg-obsidian-800 hover:bg-obsidian-700 border border-white/10 text-xs font-semibold text-cyber-cyan transition active:scale-95">
        Setup ⚙️
      </button>
    </div>

    <!-- PRIMARY SEGMENT TABS -->
    <div class="grid grid-cols-4 gap-1.5 p-1 rounded-2xl bg-obsidian-900 border border-white/10 text-xs font-semibold">
      <button id="tabBtn_pitch" onclick="App.switchTab('pitch')" class="py-2 rounded-xl text-center transition flex flex-col items-center justify-center bg-gradient-to-r from-cyber-cyan to-cyber-mint text-obsidian-950 font-bold shadow-md">
        <span>Tactics</span>
      </button>
      <button id="tabBtn_live" onclick="App.switchTab('live')" class="py-2 rounded-xl text-center transition flex flex-col items-center justify-center text-slate-400 hover:text-white">
        <span>Live ⏱️</span>
      </button>
      <button id="tabBtn_roster" onclick="App.switchTab('roster')" class="py-2 rounded-xl text-center transition flex flex-col items-center justify-center text-slate-400 hover:text-white">
        <span>Squad</span>
      </button>
      <button id="tabBtn_stats" onclick="App.switchTab('stats')" class="py-2 rounded-xl text-center transition flex flex-col items-center justify-center text-slate-400 hover:text-white">
        <span>Stats</span>
      </button>
    </div>

    <!-- TAB 1: TACTICS & PITCH VIEW -->
    <section id="section_pitch" class="space-y-4">
      
      <!-- Formation & Kit Controls Bar -->
      <div class="glass-card rounded-[24px] p-3 flex flex-wrap items-center justify-between gap-2">
        <div class="flex items-center space-x-1.5">
          <span class="text-[11px] text-slate-400 uppercase font-bold">Preset:</span>
          <select id="formationSelect" onchange="App.onFormationChanged(this.value)" class="bg-obsidian-950 border border-white/15 text-white text-xs rounded-xl px-2.5 py-1.5 focus:outline-none focus:border-cyber-cyan">
          </select>
        </div>

        <div class="flex items-center space-x-1.5">
          <span class="text-[11px] text-slate-400 uppercase font-bold">Kit:</span>
          <div id="kitColorSwatches" class="flex items-center space-x-1"></div>
          <input type="color" id="customKitPicker" onchange="App.setKitColor(this.value)" class="w-6 h-6 rounded-lg cursor-pointer border border-white/20 bg-transparent p-0" title="Custom Spectrum Kit" />
        </div>
      </div>

      <!-- INTERACTIVE SOCCER PITCH -->
      <div class="relative w-full rounded-[28px] overflow-hidden p-2.5 transition-all duration-300 pitch-night" id="pitchCanvasContainer">
        <!-- SVG SOCCER PITCH MARKINGS -->
        <div class="relative w-full aspect-[3/4.2] rounded-[22px] border-2 border-white/60 overflow-hidden" id="pitchField">
          <!-- Grass Stripes Texture -->
          <div class="absolute inset-0 flex flex-col pointer-events-none opacity-15">
            <div class="flex-1 bg-white"></div><div class="flex-1"></div>
            <div class="flex-1 bg-white"></div><div class="flex-1"></div>
            <div class="flex-1 bg-white"></div><div class="flex-1"></div>
            <div class="flex-1 bg-white"></div><div class="flex-1"></div>
          </div>

          <!-- Pitch Vector Geometry -->
          <svg class="absolute inset-0 w-full h-full pointer-events-none stroke-white/80 fill-none stroke-[1.8]" viewBox="0 0 300 420">
            <rect x="2" y="2" width="296" height="416" rx="6" />
            <line x1="2" y1="210" x2="298" y2="210" />
            <circle cx="150" cy="210" r="42" />
            <circle cx="150" cy="210" r="3" class="fill-white" />

            <!-- Penalty Boxes -->
            <rect x="65" y="2" width="170" height="65" />
            <rect x="100" y="2" width="100" height="24" />
            <path d="M 115 67 A 38 38 0 0 0 185 67" />
            <circle cx="150" cy="48" r="2.5" class="fill-white" />

            <rect x="65" y="353" width="170" height="65" />
            <rect x="100" y="394" width="100" height="24" />
            <path d="M 115 353 A 38 38 0 0 1 185 353" />
            <circle cx="150" cy="372" r="2.5" class="fill-white" />

            <rect x="115" y="-3" width="70" height="5" class="stroke-white/90" />
            <rect x="115" y="418" width="70" height="5" class="stroke-white/90" />
          </svg>

          <!-- FIELD TOKENS LAYER (Drag & Drop) -->
          <div id="pitchTokensLayer" class="absolute inset-0 select-none"></div>
        </div>

        <div class="mt-2 px-1 flex items-center justify-between text-[11px] text-white/70">
          <span>Drag tokens to adjust tactical roles</span>
          <button onclick="App.saveCurrentFormation()" class="px-2 py-0.5 rounded-lg bg-black/40 hover:bg-black/60 border border-white/20 text-cyber-mint text-[10px] font-semibold flex items-center space-x-1">
            <span>💾 Save Positions</span>
          </button>
        </div>
      </div>

      <!-- LINEUP SELECTION & STARTER VALIDATOR -->
      <div class="glass-card rounded-[24px] p-4 space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-sm font-bold text-white">Starting Lineup vs Reserves</h3>
            <p class="text-xs text-slate-400" id="starterQuotaText">Required starters: 7</p>
          </div>
          <span id="starterStatusBadge" class="px-2.5 py-1 rounded-xl text-xs font-bold bg-cyber-mint/20 text-cyber-mint border border-cyber-mint/30">
            ✓ 7/7 Starters Ready
          </span>
        </div>

        <!-- BENCH RESERVES CAROUSEL -->
        <div class="border-t border-white/10 pt-3">
          <div class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2 flex items-center justify-between">
            <span>Bench Reserves (<span id="benchCountBadge">0</span>)</span>
            <span class="text-[10px] text-slate-500 font-normal">Tap player to swap into starters</span>
          </div>
          <div id="benchReservesList" class="flex space-x-2 overflow-x-auto py-1"></div>
        </div>
      </div>
    </section>

    <!-- TAB 2: LIVE MATCH CONSOLE & ROTATION ENGINE -->
    <section id="section_live" class="space-y-4 hidden">
      
      <!-- STOPWATCH & ROTATION CLOCK HERO POD -->
      <div class="glass-card rounded-[24px] p-4 text-center relative overflow-hidden">
        <div class="absolute -top-12 -left-12 w-32 h-32 bg-cyber-cyan/15 rounded-full blur-2xl pointer-events-none"></div>
        <div class="absolute -bottom-12 -right-12 w-32 h-32 bg-cyber-mint/15 rounded-full blur-2xl pointer-events-none"></div>

        <div class="flex items-center justify-between mb-2">
          <!-- Period Selector -->
          <div class="flex rounded-xl bg-obsidian-950 p-0.5 border border-white/10 text-xs">
            <button id="periodBtn_1" onclick="App.setPeriod('1st Half')" class="px-2.5 py-1 rounded-lg font-bold bg-cyber-cyan text-obsidian-950">1st Half</button>
            <button id="periodBtn_2" onclick="App.setPeriod('2nd Half')" class="px-2.5 py-1 rounded-lg text-slate-400 font-semibold hover:text-white">2nd Half</button>
          </div>

          <!-- Scoreboard Summary -->
          <div class="flex items-center space-x-2 text-sm font-black">
            <span class="text-white" id="scoreboardTeam">GameOn</span>
            <span id="scoreboardGoals" class="px-2 py-0.5 rounded-lg bg-cyber-mint/20 text-cyber-mint border border-cyber-mint/40 font-mono text-base">0</span>
            <span class="text-slate-500">:</span>
            <span id="scoreboardOpponentGoals" class="px-2 py-0.5 rounded-lg bg-white/10 text-slate-300 font-mono text-base">0</span>
            <span class="text-slate-400 font-semibold text-xs" id="scoreboardOpponent">Echo</span>
          </div>
        </div>

        <!-- Master Digital Stopwatch -->
        <div class="my-2">
          <div id="matchClockDisplay" class="font-mono text-5xl font-black tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-100 to-slate-300">
            00:00
          </div>
          <p id="clockStatusSubtext" class="text-xs text-cyber-cyan font-medium mt-1">Clock Paused — Ready to Kickoff</p>
        </div>

        <!-- Clock Action Controls -->
        <div class="flex items-center justify-center space-x-2 mt-4">
          <button id="clockToggleBtn" onclick="App.toggleTimer()" class="flex-1 max-w-[140px] py-2.5 rounded-2xl bg-gradient-to-r from-cyber-cyan to-cyber-mint text-obsidian-950 font-black text-sm tracking-wide shadow-lg active:scale-95 transition">
            START ▶
          </button>
          <button onclick="App.resetTimer()" class="px-4 py-2.5 rounded-2xl bg-obsidian-950 hover:bg-obsidian-900 border border-white/10 text-slate-300 font-bold text-xs active:scale-95 transition">
            Reset ↺
          </button>
        </div>

        <!-- DEDICATED GOAL & ASSIST ACTION BUTTONS -->
        <div class="grid grid-cols-2 gap-2.5 mt-4 pt-3 border-t border-white/10">
          <button onclick="App.openEventModal('Goal')" class="py-2.5 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-extrabold text-xs uppercase tracking-wider shadow-md hover:brightness-110 active:scale-95 transition flex items-center justify-center space-x-1.5">
            <span class="text-base">⚽</span>
            <span>+ Goal</span>
          </button>
          <button onclick="App.openEventModal('Assist')" class="py-2.5 rounded-2xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-extrabold text-xs uppercase tracking-wider shadow-md hover:brightness-110 active:scale-95 transition flex items-center justify-center space-x-1.5">
            <span class="text-base">👟</span>
            <span>+ Assist</span>
          </button>
        </div>
      </div>

      <!-- ONE-TAP LIVE SUB ROTATION BOARD -->
      <div class="glass-card rounded-[24px] p-4 space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-sm font-bold text-white flex items-center space-x-2">
              <span>Tactical Sub Board</span>
              <span class="text-[10px] px-2 py-0.5 rounded-full bg-cyber-cyan/15 text-cyber-cyan border border-cyber-cyan/30">One-Tap Swap</span>
            </h3>
            <p class="text-xs text-slate-400 mt-0.5" id="subInstructionText">Step 1: Tap a player on field to sub OUT</p>
          </div>
          <button id="cancelSubBtn" onclick="App.cancelSubSelection()" class="hidden px-2.5 py-1 rounded-xl bg-red-500/20 text-red-400 text-xs font-semibold border border-red-500/30">
            Cancel
          </button>
        </div>

        <!-- Active Field Players Sub Grid -->
        <div>
          <div class="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">Active On Pitch (Timer Counting)</div>
          <div id="liveOnPitchGrid" class="grid grid-cols-2 gap-2"></div>
        </div>

        <!-- Bench Reserves Ready to Enter -->
        <div class="pt-2 border-t border-white/10">
          <div class="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2">Available On Bench (Timer Paused)</div>
          <div id="liveBenchGrid" class="grid grid-cols-2 gap-2"></div>
        </div>
      </div>

      <!-- LIVE MATCH TIMELINE FEED -->
      <div class="glass-card rounded-[24px] p-4 space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-bold text-white">Match Event Timeline</h3>
          <span id="timelineEventCount" class="text-xs text-slate-400">0 events</span>
        </div>
        <div id="matchTimelineList" class="space-y-2 max-h-48 overflow-y-auto pr-1 text-xs">
          <div class="text-slate-500 text-center py-4 italic">No match events logged yet</div>
        </div>
      </div>
    </section>

    <!-- TAB 3: SQUAD REGISTRY & EDITABLE POSITIONS -->
    <section id="section_roster" class="space-y-4 hidden">
      <div class="glass-card rounded-[24px] p-4 space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-sm font-bold text-white">Squad Registry</h3>
            <p class="text-xs text-slate-400">Manage roster and pre-game availability</p>
          </div>
          <button onclick="App.openAddPlayerModal()" class="px-3 py-1.5 rounded-xl bg-gradient-to-r from-cyber-cyan to-cyber-mint text-obsidian-950 text-xs font-bold active:scale-95 transition shadow-sm">
            + Add Player
          </button>
        </div>

        <div class="flex items-center space-x-2 text-xs pt-1">
          <button onclick="App.setAllAvailability(true)" class="px-2 py-1 rounded-lg bg-cyber-mint/15 text-cyber-mint border border-cyber-mint/30 font-medium">Mark All Available</button>
          <button onclick="App.setAllAvailability(false)" class="px-2 py-1 rounded-lg bg-white/5 text-slate-400 border border-white/10 font-medium">Reset</button>
        </div>
      </div>

      <!-- Squad Cards Pod Container -->
      <div id="squadPodsList" class="space-y-2.5"></div>
    </section>

    <!-- TAB 4: STATS SUBTOTALS & AGGREGATIONS -->
    <section id="section_stats" class="space-y-4 hidden">
      <div class="glass-card rounded-[24px] p-4 space-y-3">
        <h3 class="text-sm font-bold text-white">Performance Analytics & Subtotals</h3>
        <div class="grid grid-cols-2 gap-2 text-xs">
          <div>
            <label class="text-slate-400 block mb-1 font-medium">From Date</label>
            <input type="date" id="statsStartDate" onchange="App.renderStats()" class="w-full bg-obsidian-950 border border-white/10 rounded-xl p-2 text-white focus:outline-none focus:border-cyber-cyan" />
          </div>
          <div>
            <label class="text-slate-400 block mb-1 font-medium">To Date</label>
            <input type="date" id="statsEndDate" onchange="App.renderStats()" class="w-full bg-obsidian-950 border border-white/10 rounded-xl p-2 text-white focus:outline-none focus:border-cyber-cyan" />
          </div>
        </div>
        <div class="flex justify-end">
          <button onclick="App.openExportModal()" class="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-cyber-cyan to-cyber-mint text-obsidian-950 font-bold text-xs flex items-center space-x-1.5 shadow-md active:scale-95">
            <span>📥 Export Match Summary PDF</span>
          </button>
        </div>
      </div>

      <div id="statsCardsContainer" class="space-y-2.5"></div>
    </section>

  </main>

  <!-- BOTTOM FLOATING PWA NAVIGATION DOCK -->
  <nav class="fixed bottom-0 left-0 right-0 z-40 bg-obsidian-950/90 backdrop-blur-lg border-t border-white/10 px-6 py-2 flex items-center justify-around pb-safe">
    <button onclick="App.switchTab('pitch')" class="dock-btn flex flex-col items-center text-cyber-cyan" data-dock="pitch">
      <span class="text-xl">📋</span>
      <span class="text-[10px] font-bold mt-0.5">Tactics</span>
    </button>
    <button onclick="App.switchTab('live')" class="dock-btn flex flex-col items-center text-slate-400 hover:text-white" data-dock="live">
      <span class="text-xl">⏱️</span>
      <span class="text-[10px] font-bold mt-0.5">Live Match</span>
    </button>
    <button onclick="App.switchTab('roster')" class="dock-btn flex flex-col items-center text-slate-400 hover:text-white" data-dock="roster">
      <span class="text-xl">👥</span>
      <span class="text-[10px] font-bold mt-0.5">Squad</span>
    </button>
    <button onclick="App.switchTab('stats')" class="dock-btn flex flex-col items-center text-slate-400 hover:text-white" data-dock="stats">
      <span class="text-xl">📊</span>
      <span class="text-[10px] font-bold mt-0.5">Analytics</span>
    </button>
  </nav>

  <!-- MODALS -->

  <!-- 1. MATCH SETUP MODAL -->
  <div id="modalMatchSetup" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="glass-card max-w-sm w-full rounded-[28px] p-5 space-y-4 border border-white/15 bg-obsidian-900">
      <div class="flex items-center justify-between">
        <h3 class="text-base font-bold text-white">Match Configuration</h3>
        <button onclick="App.closeModals()" class="w-7 h-7 rounded-full bg-white/10 text-slate-300 flex items-center justify-center text-sm">✕</button>
      </div>

      <div class="space-y-3 text-xs">
        <div>
          <label class="text-slate-400 font-medium block mb-1">Match Title / Label</label>
          <input type="text" id="inputMatchTitle" class="w-full bg-obsidian-950 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-cyber-cyan" placeholder="e.g. Quarter-Final" />
        </div>
        <div>
          <label class="text-slate-400 font-medium block mb-1">Opponent Club Name</label>
          <input type="text" id="inputMatchOpponent" class="w-full bg-obsidian-950 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-cyber-cyan" placeholder="e.g. Echo Strikers" />
        </div>
        <div>
          <label class="text-slate-400 font-medium block mb-1">Match Date</label>
          <input type="date" id="inputMatchDate" class="w-full bg-obsidian-950 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-cyber-cyan" />
        </div>
        <div>
          <label class="text-slate-400 font-medium block mb-1">Playing Format</label>
          <div class="grid grid-cols-4 gap-1.5">
            <button type="button" onclick="App.selectFormat('5')" class="format-btn py-2 rounded-xl bg-obsidian-950 border border-white/10 text-center font-bold text-slate-300" data-fmt="5">5v5</button>
            <button type="button" onclick="App.selectFormat('7')" class="format-btn py-2 rounded-xl bg-obsidian-950 border border-white/10 text-center font-bold text-slate-300" data-fmt="7">7v7</button>
            <button type="button" onclick="App.selectFormat('9')" class="format-btn py-2 rounded-xl bg-obsidian-950 border border-white/10 text-center font-bold text-slate-300" data-fmt="9">9v9</button>
            <button type="button" onclick="App.selectFormat('11')" class="format-btn py-2 rounded-xl bg-obsidian-950 border border-white/10 text-center font-bold text-slate-300" data-fmt="11">11v11</button>
          </div>
        </div>
      </div>

      <div class="flex space-x-2 pt-2">
        <button onclick="App.saveMatchSetup()" class="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-cyber-cyan to-cyber-mint text-obsidian-950 font-bold text-xs tracking-wide shadow-md active:scale-95">
          Save & Apply
        </button>
      </div>
    </div>
  </div>

  <!-- 2. ADD / EDIT PLAYER MODAL -->
  <div id="modalAddPlayer" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="glass-card max-w-sm w-full rounded-[28px] p-5 space-y-4 border border-white/15 bg-obsidian-900">
      <div class="flex items-center justify-between">
        <h3 class="text-base font-bold text-white">Add Squad Player</h3>
        <button onclick="App.closeModals()" class="w-7 h-7 rounded-full bg-white/10 text-slate-300 flex items-center justify-center text-sm">✕</button>
      </div>

      <div class="space-y-3 text-xs">
        <div>
          <label class="text-slate-400 font-medium block mb-1">Full Name</label>
          <input type="text" id="inputPlayerName" class="w-full bg-obsidian-950 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-cyber-cyan" placeholder="e.g. Liam Vance" />
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="text-slate-400 font-medium block mb-1">Shirt Number (1-99)</label>
            <input type="number" id="inputPlayerNumber" min="1" max="99" class="w-full bg-obsidian-950 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-cyber-cyan" placeholder="10" />
          </div>
          <div>
            <label class="text-slate-400 font-medium block mb-1">Position</label>
            <select id="inputPlayerPosition" class="w-full bg-obsidian-950 border border-white/10 rounded-xl px-3 py-2 text-white text-sm focus:outline-none focus:border-cyber-cyan">
              <option value="GK">GK (Goalkeeper)</option>
              <option value="DEF">DEF (Defender)</option>
              <option value="MID" selected>MID (Midfielder)</option>
              <option value="FWD">FWD (Forward)</option>
            </select>
          </div>
        </div>
      </div>

      <div class="pt-2">
        <button onclick="App.saveNewPlayer()" class="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyber-cyan to-cyber-mint text-obsidian-950 font-bold text-xs tracking-wide shadow-md active:scale-95">
          Add to Squad Pods
        </button>
      </div>
    </div>
  </div>

  <!-- 3. DEDICATED GOAL / ASSIST MODAL -->
  <div id="modalEvent" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="glass-card max-w-sm w-full rounded-[28px] p-5 space-y-4 border border-white/15 bg-obsidian-900">
      <div class="flex items-center justify-between">
        <h3 id="eventModalTitle" class="text-base font-bold text-white flex items-center space-x-2">
          <span>⚽ Register Goal</span>
        </h3>
        <button onclick="App.closeModals()" class="w-7 h-7 rounded-full bg-white/10 text-slate-300 flex items-center justify-center text-sm">✕</button>
      </div>

      <p class="text-xs text-slate-300">Select the squad member who achieved this:</p>

      <div>
        <select id="eventPlayerSelector" class="w-full bg-obsidian-950 border border-white/15 rounded-xl p-3 text-white text-sm font-semibold focus:outline-none focus:border-cyber-cyan">
        </select>
      </div>

      <div class="flex space-x-2 pt-2">
        <button onclick="App.confirmEvent()" class="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-cyber-cyan to-cyber-mint text-obsidian-950 font-bold text-xs tracking-wide shadow-md active:scale-95">
          Record Event
        </button>
      </div>
    </div>
  </div>

  <!-- 4. PDF EXPORT LEDGER TEMPLATE -->
  <div id="pdfExportContainer" class="hidden p-8 bg-white text-slate-900 font-sans space-y-6">
    <div class="flex items-center justify-between border-b-2 border-slate-900 pb-4">
      <div class="flex items-center space-x-3">
        <img id="pdfIcon" src="./icon.jpg" class="w-14 h-14 rounded-2xl object-cover" />
        <div>
          <h1 class="text-2xl font-black text-slate-900">GameOn <span class="text-emerald-600 font-bold">Tactical Ledger</span></h1>
          <p class="text-xs text-slate-500 font-medium uppercase tracking-wider">Official Match Intelligence & Performance Report</p>
        </div>
      </div>
      <div class="text-right text-xs">
        <div class="font-bold text-sm text-slate-800" id="pdfMatchDate">2026-10-15</div>
        <div class="text-slate-500 font-mono" id="pdfGeneratedTime">Generated: Oct 15, 2026</div>
      </div>
    </div>

    <div class="bg-slate-100 rounded-2xl p-4 flex justify-between items-center">
      <div>
        <div class="text-xs uppercase font-bold text-slate-500">Match Fixture</div>
        <div class="text-lg font-black text-slate-800" id="pdfFixtureTitle">GameOn vs Echo Strikers</div>
      </div>
      <div class="text-right">
        <div class="text-xs uppercase font-bold text-slate-500">Result & Duration</div>
        <div class="text-lg font-black text-emerald-700" id="pdfMatchResult">Score: 0 - 0 (Played: 00:00)</div>
      </div>
    </div>

    <div>
      <h3 class="text-sm font-bold uppercase text-slate-700 tracking-wider mb-2">Player Playing Time & Statistics</h3>
      <table class="w-full text-left text-xs border-collapse border border-slate-200 rounded-xl overflow-hidden">
        <thead class="bg-slate-800 text-white uppercase text-[10px]">
          <tr>
            <th class="p-2.5">#</th>
            <th class="p-2.5">Player Name</th>
            <th class="p-2.5">Pos</th>
            <th class="p-2.5">Status</th>
            <th class="p-2.5 text-center">Minutes</th>
            <th class="p-2.5 text-center">Goals</th>
            <th class="p-2.5 text-center">Assists</th>
          </tr>
        </thead>
        <tbody id="pdfPlayerTableBody" class="divide-y divide-slate-200"></tbody>
      </table>
    </div>

    <div>
      <h3 class="text-sm font-bold uppercase text-slate-700 tracking-wider mb-2">Tactical Substitutions & Key Moments</h3>
      <div id="pdfTimelineLog" class="space-y-1.5 text-xs text-slate-700 border-l-2 border-emerald-500 pl-3"></div>
    </div>

    <div class="text-[10px] text-center text-slate-400 pt-6 border-t border-slate-200">
      Generated locally on device via GameOn PWA — Tactical Pitch, Live Rotations & Match Intelligence.
    </div>
  </div>

  <!-- FLOATING TOAST -->
  <div id="toastPod" class="fixed top-16 left-1/2 transform -translate-x-1/2 z-50 transition-all duration-300 opacity-0 pointer-events-none max-w-xs w-full px-4">
    <div id="toastInner" class="bg-obsidian-900/95 backdrop-blur-md border border-cyber-cyan/50 text-white rounded-2xl p-3 shadow-2xl flex items-center space-x-2 text-xs font-semibold">
      <span id="toastIcon">✨</span>
      <span id="toastMessage">Notification</span>
    </div>
  </div>

  <!-- APPLICATION JAVASCRIPT LOGIC -->
  <script>
    const EMBEDDED_ICON_B64 = "data:image/png;base64," + """ + repr(icon_b64_png) + """;
    let deferredInstallPrompt = null;

    const AppState = {
      theme: 'night',
      activeTab: 'pitch',
      kitColor: '#00f2fe',
      isCustomKit: false,
      
      match: {
        id: 'm_' + Date.now(),
        title: 'Match 1',
        opponent: 'Echo Strikers',
        date: new Date().toISOString().split('T')[0],
        format: '7',
        availability: {},
        starters: [],
        bench: [],
        fieldPositions: {},
        ourGoals: 0,
        opponentGoals: 0
      },

      clock: {
        period: '1st Half',
        seconds: 0,
        running: false,
        intervalId: null
      },

      playerTimers: {},
      subOutPlayerId: null,
      events: [],

      squad: [
        { id: 'p_101', number: 1, name: 'Mateo Rossi', position: 'GK' },
        { id: 'p_102', number: 4, name: 'Julian Vance', position: 'DEF' },
        { id: 'p_103', number: 5, name: 'Tariq Sterling', position: 'DEF' },
        { id: 'p_104', number: 8, name: 'Leo De Jong', position: 'MID' },
        { id: 'p_105', number: 10, name: 'Liam Vance', position: 'MID' },
        { id: 'p_106', number: 7, name: 'Kaelan Diaz', position: 'FWD' },
        { id: 'p_107', number: 9, name: 'Noah Sinclair', position: 'FWD' },
        { id: 'p_108', number: 11, name: 'Sami Morales', position: 'MID' },
        { id: 'p_109', number: 2, name: 'Axel Lindqvist', position: 'DEF' },
        { id: 'p_110', number: 14, name: 'Lucas Chen', position: 'FWD' }
      ],

      formations: {
        '5': {
          '1-2-1': [
            { x: 50, y: 88 },
            { x: 50, y: 64 },
            { x: 26, y: 44 },
            { x: 74, y: 44 },
            { x: 50, y: 20 }
          ],
          '2-1-1': [
            { x: 50, y: 88 },
            { x: 30, y: 65 },
            { x: 70, y: 65 },
            { x: 50, y: 42 },
            { x: 50, y: 20 }
          ]
        },
        '7': {
          '2-3-1': [
            { x: 50, y: 88 },
            { x: 28, y: 68 },
            { x: 72, y: 68 },
            { x: 20, y: 45 },
            { x: 50, y: 48 },
            { x: 80, y: 45 },
            { x: 50, y: 22 }
          ],
          '3-2-1': [
            { x: 50, y: 88 },
            { x: 22, y: 70 },
            { x: 50, y: 68 },
            { x: 78, y: 70 },
            { x: 34, y: 44 },
            { x: 66, y: 44 },
            { x: 50, y: 22 }
          ]
        },
        '9': {
          '3-3-2': [
            { x: 50, y: 90 },
            { x: 22, y: 72 },
            { x: 50, y: 70 },
            { x: 78, y: 72 },
            { x: 22, y: 48 },
            { x: 50, y: 48 },
            { x: 78, y: 48 },
            { x: 36, y: 24 },
            { x: 64, y: 24 }
          ],
          '3-4-1': [
            { x: 50, y: 90 },
            { x: 22, y: 72 },
            { x: 50, y: 70 },
            { x: 78, y: 72 },
            { x: 18, y: 48 },
            { x: 40, y: 48 },
            { x: 60, y: 48 },
            { x: 82, y: 48 },
            { x: 50, y: 22 }
          ]
        },
        '11': {
          '4-3-3': [
            { x: 50, y: 90 },
            { x: 16, y: 75 },
            { x: 38, y: 75 },
            { x: 62, y: 75 },
            { x: 84, y: 75 },
            { x: 28, y: 52 },
            { x: 50, y: 55 },
            { x: 72, y: 52 },
            { x: 20, y: 26 },
            { x: 50, y: 20 },
            { x: 80, y: 26 }
          ],
          '3-5-2': [
            { x: 50, y: 90 },
            { x: 24, y: 76 },
            { x: 50, y: 74 },
            { x: 76, y: 76 },
            { x: 14, y: 50 },
            { x: 34, y: 52 },
            { x: 50, y: 48 },
            { x: 66, y: 52 },
            { x: 86, y: 50 },
            { x: 38, y: 24 },
            { x: 62, y: 24 }
          ]
        }
      }
    };

    const App = {
      init() {
        this.loadStorage();
        this.setupIcons();
        this.initKitColors();
        this.applyFormatDefaults();
        this.renderAll();
        this.setupDragging();
        this.registerServiceWorker();
        this.setupInstallPrompt();

        const today = new Date().toISOString().split('T')[0];
        document.getElementById('statsStartDate').value = today;
        document.getElementById('statsEndDate').value = today;
      },

      registerServiceWorker() {
        if ('serviceWorker' in navigator) {
          navigator.serviceWorker.register('./sw.js').catch(() => {});
        }
      },

      setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
          e.preventDefault();
          deferredInstallPrompt = e;
          const btn = document.getElementById('installPwaBtn');
          if (btn) btn.classList.remove('hidden');
        });

        window.addEventListener('appinstalled', () => {
          deferredInstallPrompt = null;
          App.toast('GameOn installed to home screen! 🚀');
        });
      },

      triggerInstallPrompt() {
        if (deferredInstallPrompt) {
          deferredInstallPrompt.prompt();
          deferredInstallPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
              App.toast('Installing GameOn icon...');
            }
            deferredInstallPrompt = null;
          });
        } else {
          // If iOS or already installed, show clear guide modal
          const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
          if (isIOS) {
            this.toast('Tap Share [↑] then "Add to Home Screen" 📲', '💡');
          } else {
            this.toast('Tap Chrome Menu (⋮) then "Add to Home screen" 📲', '💡');
          }
        }
      },

      setupIcons() {
        const headerIcon = document.getElementById('appHeaderIcon');
        const pdfIcon = document.getElementById('pdfIcon');
        if (headerIcon) {
          headerIcon.src = './icon-192.png';
          headerIcon.onerror = () => { headerIcon.src = EMBEDDED_ICON_B64; };
        }
        if (pdfIcon) {
          pdfIcon.src = './icon-192.png';
          pdfIcon.onerror = () => { pdfIcon.src = EMBEDDED_ICON_B64; };
        }
      },

      loadStorage() {
        try {
          const sQ = localStorage.getItem('gameon_squad');
          if (sQ) AppState.squad = JSON.parse(sQ);

          const sM = localStorage.getItem('gameon_match');
          if (sM) AppState.match = JSON.parse(sM);

          const sE = localStorage.getItem('gameon_events');
          if (sE) AppState.events = JSON.parse(sE);

          const sT = localStorage.getItem('gameon_timers');
          if (sT) AppState.playerTimers = JSON.parse(sT);

          const sK = localStorage.getItem('gameon_kit');
          if (sK) AppState.kitColor = sK;

          const sTh = localStorage.getItem('gameon_theme');
          if (sTh) AppState.theme = sTh;
          this.applyTheme();
        } catch (e) {}
      },

      saveStorage() {
        try {
          localStorage.setItem('gameon_squad', JSON.stringify(AppState.squad));
          localStorage.setItem('gameon_match', JSON.stringify(AppState.match));
          localStorage.setItem('gameon_events', JSON.stringify(AppState.events));
          localStorage.setItem('gameon_timers', JSON.stringify(AppState.playerTimers));
          localStorage.setItem('gameon_kit', AppState.kitColor);
          localStorage.setItem('gameon_theme', AppState.theme);
        } catch (e) {}
      },

      toggleDayNight() {
        AppState.theme = AppState.theme === 'night' ? 'day' : 'night';
        this.applyTheme();
        this.saveStorage();
        this.toast(AppState.theme === 'day' ? '☀️ Day Mode (High Turf Contrast)' : '🌙 Night Mode (Cyber Glow)');
      },

      applyTheme() {
        const isDay = AppState.theme === 'day';
        const body = document.body;
        const pitchCont = document.getElementById('pitchCanvasContainer');
        const themeIcon = document.getElementById('themeIcon');

        if (isDay) {
          body.classList.remove('bg-obsidian-950', 'text-slate-100');
          body.classList.add('bg-slate-100', 'text-slate-900');
          pitchCont.classList.remove('pitch-night');
          pitchCont.classList.add('pitch-day');
          themeIcon.innerText = '☀️';
        } else {
          body.classList.add('bg-obsidian-950', 'text-slate-100');
          body.classList.remove('bg-slate-100', 'text-slate-900');
          pitchCont.classList.remove('pitch-day');
          pitchCont.classList.add('pitch-night');
          themeIcon.innerText = '🌙';
        }
      },

      switchTab(tab) {
        AppState.activeTab = tab;
        ['pitch', 'live', 'roster', 'stats'].forEach(t => {
          const sec = document.getElementById('section_' + t);
          const btn = document.getElementById('tabBtn_' + t);
          const dock = document.querySelector(`.dock-btn[data-dock="${t}"]`);

          if (t === tab) {
            sec.classList.remove('hidden');
            btn.className = 'py-2 rounded-xl text-center transition flex flex-col items-center justify-center bg-gradient-to-r from-cyber-cyan to-cyber-mint text-obsidian-950 font-bold shadow-md';
            if (dock) {
              dock.className = 'dock-btn flex flex-col items-center text-cyber-cyan';
            }
          } else {
            sec.classList.add('hidden');
            btn.className = 'py-2 rounded-xl text-center transition flex flex-col items-center justify-center text-slate-400 hover:text-white';
            if (dock) {
              dock.className = 'dock-btn flex flex-col items-center text-slate-400 hover:text-white';
            }
          }
        });

        if (tab === 'live') this.renderLiveBoard();
        if (tab === 'roster') this.renderRoster();
        if (tab === 'stats') this.renderStats();
        if (tab === 'pitch') this.renderPitchTokens();
      },

      initKitColors() {
        const presets = ['#00f2fe', '#10b981', '#3b82f6', '#ef4444', '#f59e0b', '#ec4899', '#8b5cf6', '#ffffff', '#1e293b'];
        const container = document.getElementById('kitColorSwatches');
        container.innerHTML = '';
        presets.forEach(c => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'w-5 h-5 rounded-full border border-white/30 transition hover:scale-110';
          btn.style.backgroundColor = c;
          btn.onclick = () => App.setKitColor(c);
          container.appendChild(btn);
        });
        document.getElementById('customKitPicker').value = AppState.kitColor;
      },

      setKitColor(color) {
        AppState.kitColor = color;
        document.getElementById('customKitPicker').value = color;
        this.saveStorage();
        this.renderPitchTokens();
        this.toast('Kit color updated: ' + color);
      },

      getContrastTextColor(hex) {
        if (!hex || !hex.startsWith('#')) return '#ffffff';
        const r = parseInt(hex.substr(1, 2), 16) || 0;
        const g = parseInt(hex.substr(3, 2), 16) || 0;
        const b = parseInt(hex.substr(5, 2), 16) || 0;
        const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
        return (yiq >= 140) ? '#070d18' : '#ffffff';
      },

      getShirtSvg(number, kitColor, size = 48, strokeColor = 'rgba(255,255,255,0.35)') {
        const textColor = this.getContrastTextColor(kitColor);
        const collarColor = textColor === '#ffffff' ? 'rgba(255,255,255,0.45)' : 'rgba(0,0,0,0.35)';
        return `
          <svg width="${size}" height="${size}" viewBox="0 0 100 100" class="filter drop-shadow-md transition-transform" style="overflow: visible;">
            <!-- Jersey Body & Sleeves -->
            <path d="M 33 16 
                     C 37 23, 63 23, 67 16 
                     L 88 27 
                     L 78 47 
                     L 71 42 
                     L 71 85 
                     C 71 87, 69 88, 66 88 
                     L 34 88 
                     C 31 88, 29 87, 29 85 
                     L 29 42 
                     L 22 47 
                     L 12 27 
                     Z" 
                  fill="${kitColor}" 
                  stroke="${strokeColor}" 
                  stroke-width="2.5" 
                  stroke-linejoin="round" />
            <!-- V-Neck Collar detail -->
            <path d="M 34 17 C 40 25, 60 25, 66 17" fill="none" stroke="${collarColor}" stroke-width="3" stroke-linecap="round" />
            <!-- Sleeve Trim Left & Right -->
            <line x1="13" y1="28" x2="22" y2="46" stroke="${collarColor}" stroke-width="2" />
            <line x1="87" y1="28" x2="78" y2="46" stroke="${collarColor}" stroke-width="2" />
            <!-- Jersey Shirt Number -->
            <text x="50" y="66" 
                  text-anchor="middle" 
                  dominant-baseline="central" 
                  fill="${textColor}" 
                  font-size="28" 
                  font-weight="900" 
                  font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" 
                  letter-spacing="-1">
              ${number}
            </text>
          </svg>
        `;
      },

      applyFormatDefaults() {
        const fmt = AppState.match.format;
        const quota = parseInt(fmt);
        document.getElementById('activeMatchFormatBadge').innerText = fmt + '-a-side';
        document.getElementById('starterQuotaText').innerText = `Required starters: ${quota}`;

        const select = document.getElementById('formationSelect');
        select.innerHTML = '';
        const presets = AppState.formations[fmt] || {};
        Object.keys(presets).forEach(name => {
          const opt = document.createElement('option');
          opt.value = name;
          opt.innerText = name;
          select.appendChild(opt);
        });

        AppState.squad.forEach(p => {
          if (AppState.match.availability[p.id] === undefined) {
            AppState.match.availability[p.id] = true;
          }
        });

        if (AppState.match.starters.length === 0) {
          const avail = AppState.squad.filter(p => AppState.match.availability[p.id]);
          AppState.match.starters = avail.slice(0, quota).map(p => p.id);
          AppState.match.bench = avail.slice(quota).map(p => p.id);
        }

        this.applyFormationPositions(select.value || Object.keys(presets)[0]);
      },

      onFormationChanged(name) {
        this.applyFormationPositions(name);
        this.renderPitchTokens();
        this.toast('Formation preset loaded: ' + name);
      },

      applyFormationPositions(name) {
        const fmt = AppState.match.format;
        const formationSlots = (AppState.formations[fmt] && AppState.formations[fmt][name]) || [];
        
        AppState.match.starters.forEach((pid, idx) => {
          if (formationSlots[idx]) {
            AppState.match.fieldPositions[pid] = {
              x: formationSlots[idx].x,
              y: formationSlots[idx].y
            };
          } else {
            AppState.match.fieldPositions[pid] = { x: 50, y: 50 };
          }
        });
        this.saveStorage();
      },

      saveCurrentFormation() {
        this.saveStorage();
        this.toast('Custom pitch layout saved!');
      },

      renderPitchTokens() {
        const container = document.getElementById('pitchTokensLayer');
        container.innerHTML = '';

        const quota = parseInt(AppState.match.format);
        const starters = AppState.match.starters;

        starters.forEach(pid => {
          const p = AppState.squad.find(item => item.id === pid);
          if (!p) return;

          const pos = AppState.match.fieldPositions[pid] || { x: 50, y: 50 };

          const token = document.createElement('div');
          token.className = 'player-token absolute flex flex-col items-center justify-center cursor-grab active:cursor-grabbing';
          token.id = 'token_' + pid;
          token.dataset.playerId = pid;
          token.style.left = `${pos.x}%`;
          token.style.top = `${pos.y}%`;
          token.style.transform = 'translate(-50%, -50%)';

          token.innerHTML = `
            <div class="relative flex items-center justify-center transition-transform hover:scale-105 active:scale-110">
              ${this.getShirtSvg(p.number, AppState.kitColor, 46)}
            </div>
            <div class="mt-0.5 px-2 py-0.5 rounded-full bg-obsidian-950/90 border border-white/20 text-[10px] font-bold text-white tracking-wide shadow-md whitespace-nowrap">
              ${p.name.split(' ')[0]} <span class="text-cyber-cyan text-[8px]">${p.position}</span>
            </div>
          `;

          container.appendChild(token);
        });

        const badge = document.getElementById('starterStatusBadge');
        const count = starters.length;
        if (count === quota) {
          badge.className = 'px-2.5 py-1 rounded-xl text-xs font-bold bg-cyber-mint/20 text-cyber-mint border border-cyber-mint/30';
          badge.innerText = `✓ ${count}/${quota} Starters Ready`;
        } else {
          badge.className = 'px-2.5 py-1 rounded-xl text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30';
          badge.innerText = `⚠ ${count}/${quota} Starters (Need ${quota})`;
        }

        this.renderBenchReserves();
      },

      renderBenchReserves() {
        const container = document.getElementById('benchReservesList');
        container.innerHTML = '';
        const bench = AppState.match.bench || [];
        document.getElementById('benchCountBadge').innerText = bench.length;

        if (bench.length === 0) {
          container.innerHTML = `<span class="text-xs text-slate-500 italic py-1">No reserves on bench</span>`;
          return;
        }

        bench.forEach(pid => {
          const p = AppState.squad.find(item => item.id === pid);
          if (!p) return;

          const chip = document.createElement('button');
          chip.type = 'button';
          chip.onclick = () => App.promoteBenchToStarter(pid);
          chip.className = 'flex items-center space-x-2.5 px-3 py-1.5 rounded-2xl bg-obsidian-950 border border-white/10 hover:border-cyber-cyan/40 text-xs text-left transition active:scale-95 flex-shrink-0';
          chip.innerHTML = `
            <div class="flex-shrink-0">
              ${this.getShirtSvg(p.number, '#334155', 28, 'rgba(255,255,255,0.2)')}
            </div>
            <div>
              <div class="text-white font-semibold text-xs leading-none">${p.name}</div>
              <div class="text-[10px] text-slate-400 mt-0.5">${p.position} • Tap to Start</div>
            </div>
          `;
          container.appendChild(chip);
        });
      },

      promoteBenchToStarter(benchPid) {
        const quota = parseInt(AppState.match.format);
        if (AppState.match.starters.length < quota) {
          AppState.match.starters.push(benchPid);
          AppState.match.bench = AppState.match.bench.filter(id => id !== benchPid);
          AppState.match.fieldPositions[benchPid] = { x: 50, y: 50 };
        } else {
          const demoted = AppState.match.starters.pop();
          AppState.match.bench = AppState.match.bench.filter(id => id !== benchPid);
          AppState.match.bench.push(demoted);
          AppState.match.starters.push(benchPid);
          AppState.match.fieldPositions[benchPid] = AppState.match.fieldPositions[demoted] || { x: 50, y: 50 };
        }
        this.saveStorage();
        this.renderPitchTokens();
        this.toast('Lineup updated');
      },

      setupDragging() {
        const field = document.getElementById('pitchTokensLayer');
        let activeEl = null;

        const onPointerDown = (e) => {
          const token = e.target.closest('.player-token');
          if (!token) return;
          activeEl = token;
          activeEl.setPointerCapture(e.pointerId);
          activeEl.style.zIndex = 100;
        };

        const onPointerMove = (e) => {
          if (!activeEl) return;
          const rect = field.getBoundingClientRect();
          let x = ((e.clientX - rect.left) / rect.width) * 100;
          let y = ((e.clientY - rect.top) / rect.height) * 100;

          x = Math.max(8, Math.min(92, x));
          y = Math.max(8, Math.min(92, y));

          activeEl.style.left = `${x}%`;
          activeEl.style.top = `${y}%`;

          const pid = activeEl.dataset.playerId;
          if (pid) {
            AppState.match.fieldPositions[pid] = { x: Math.round(x), y: Math.round(y) };
          }
        };

        const onPointerUp = (e) => {
          if (!activeEl) return;
          try { activeEl.releasePointerCapture(e.pointerId); } catch (_) {}
          activeEl.style.zIndex = 10;
          activeEl = null;
          App.saveStorage();
        };

        field.addEventListener('pointerdown', onPointerDown);
        field.addEventListener('pointermove', onPointerMove);
        field.addEventListener('pointerup', onPointerUp);
        field.addEventListener('pointercancel', onPointerUp);
      },

      renderRoster() {
        const container = document.getElementById('squadPodsList');
        container.innerHTML = '';

        AppState.squad.forEach(p => {
          const isAvail = AppState.match.availability[p.id] !== false;
          const isStarter = AppState.match.starters.includes(p.id);
          const shirtColor = isStarter ? AppState.kitColor : '#334155';

          const card = document.createElement('div');
          card.className = 'glass-card rounded-[22px] p-3 flex items-center justify-between transition hover:border-white/20';
          card.innerHTML = `
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0 flex items-center justify-center">
                ${this.getShirtSvg(p.number, shirtColor, 40, isStarter ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.15)')}
              </div>
              <div>
                <div class="font-bold text-sm text-white flex items-center space-x-2">
                  <span>${p.name}</span>
                  ${isStarter ? '<span class="px-1.5 py-0.2 rounded bg-cyber-cyan/20 text-cyber-cyan text-[10px] font-bold">Starter</span>' : ''}
                </div>
                <div class="flex items-center space-x-2 mt-1">
                  <select onchange="App.updatePlayerPosition('${p.id}', this.value)" class="bg-obsidian-950/80 border border-white/15 text-[10px] font-bold text-cyber-cyan rounded-lg px-2 py-0.5 focus:outline-none">
                    <option value="GK" ${p.position === 'GK' ? 'selected' : ''}>GK</option>
                    <option value="DEF" ${p.position === 'DEF' ? 'selected' : ''}>DEF</option>
                    <option value="MID" ${p.position === 'MID' ? 'selected' : ''}>MID</option>
                    <option value="FWD" ${p.position === 'FWD' ? 'selected' : ''}>FWD</option>
                  </select>
                  <span class="text-[11px] text-slate-400 font-mono">${this.formatTime(AppState.playerTimers[p.id] || 0)}</span>
                </div>
              </div>
            </div>

            <div class="flex items-center space-x-2">
              <button onclick="App.toggleAvailability('${p.id}')" class="px-3 py-1.5 rounded-xl font-bold text-xs transition active:scale-95 ${
                isAvail ? 'bg-cyber-mint/20 text-cyber-mint border border-cyber-mint/40' : 'bg-red-500/20 text-red-400 border border-red-500/40'
              }">
                ${isAvail ? '✓ Available' : '✗ Out'}
              </button>

              <button onclick="App.deletePlayer('${p.id}')" class="w-8 h-8 rounded-xl bg-white/5 hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition flex items-center justify-center text-xs">
                🗑️
              </button>
            </div>
          `;
          container.appendChild(card);
        });
      },

      updatePlayerPosition(pid, pos) {
        const p = AppState.squad.find(i => i.id === pid);
        if (p) {
          p.position = pos;
          this.saveStorage();
          this.toast(`${p.name} reassigned to ${pos}`);
        }
      },

      toggleAvailability(pid) {
        AppState.match.availability[pid] = !AppState.match.availability[pid];
        if (!AppState.match.availability[pid]) {
          AppState.match.starters = AppState.match.starters.filter(id => id !== pid);
          AppState.match.bench = AppState.match.bench.filter(id => id !== pid);
        } else {
          if (!AppState.match.starters.includes(pid) && !AppState.match.bench.includes(pid)) {
            AppState.match.bench.push(pid);
          }
        }
        this.saveStorage();
        this.renderRoster();
        this.renderPitchTokens();
      },

      setAllAvailability(status) {
        AppState.squad.forEach(p => {
          AppState.match.availability[p.id] = status;
        });
        const quota = parseInt(AppState.match.format);
        if (status) {
          AppState.match.starters = AppState.squad.slice(0, quota).map(p => p.id);
          AppState.match.bench = AppState.squad.slice(quota).map(p => p.id);
        } else {
          AppState.match.starters = [];
          AppState.match.bench = [];
        }
        this.saveStorage();
        this.renderRoster();
        this.renderPitchTokens();
        this.toast(status ? 'All squad members marked Available' : 'Availability reset');
      },

      deletePlayer(pid) {
        AppState.squad = AppState.squad.filter(p => p.id !== pid);
        AppState.match.starters = AppState.match.starters.filter(id => id !== pid);
        AppState.match.bench = AppState.match.bench.filter(id => id !== pid);
        this.saveStorage();
        this.renderRoster();
        this.renderPitchTokens();
        this.toast('Player removed from registry');
      },

      toggleTimer() {
        if (AppState.clock.running) {
          clearInterval(AppState.clock.intervalId);
          AppState.clock.running = false;
          document.getElementById('clockToggleBtn').innerText = 'RESUME ▶';
          document.getElementById('clockToggleBtn').className = 'flex-1 max-w-[140px] py-2.5 rounded-2xl bg-gradient-to-r from-cyber-cyan to-cyber-mint text-obsidian-950 font-black text-sm tracking-wide shadow-lg active:scale-95 transition';
          document.getElementById('clockStatusSubtext').innerText = 'Clock Paused';
          document.getElementById('clockStatusSubtext').className = 'text-xs text-amber-400 font-medium mt-1';
        } else {
          AppState.clock.running = true;
          AppState.clock.intervalId = setInterval(() => {
            AppState.clock.seconds++;
            
            AppState.match.starters.forEach(pid => {
              AppState.playerTimers[pid] = (AppState.playerTimers[pid] || 0) + 1;
            });

            App.updateClockDisplay();
            if (AppState.clock.seconds % 5 === 0) App.saveStorage();
          }, 1000);

          document.getElementById('clockToggleBtn').innerText = 'PAUSE ⏸';
          document.getElementById('clockToggleBtn').className = 'flex-1 max-w-[140px] py-2.5 rounded-2xl bg-amber-500 text-obsidian-950 font-black text-sm tracking-wide shadow-lg active:scale-95 transition';
          document.getElementById('clockStatusSubtext').innerText = '● Live Match In Progress — Accumulating Playing Seconds';
          document.getElementById('clockStatusSubtext').className = 'text-xs text-cyber-mint font-medium mt-1 glow-pulse';
        }
      },

      resetTimer() {
        clearInterval(AppState.clock.intervalId);
        AppState.clock.running = false;
        AppState.clock.seconds = 0;
        this.updateClockDisplay();
        document.getElementById('clockToggleBtn').innerText = 'START ▶';
        document.getElementById('clockStatusSubtext').innerText = 'Clock Reset — Ready to Kickoff';
        document.getElementById('clockStatusSubtext').className = 'text-xs text-cyber-cyan font-medium mt-1';
        this.toast('Stopwatch reset to 00:00');
      },

      setPeriod(period) {
        AppState.clock.period = period;
        const b1 = document.getElementById('periodBtn_1');
        const b2 = document.getElementById('periodBtn_2');
        if (period === '1st Half') {
          b1.className = 'px-2.5 py-1 rounded-lg font-bold bg-cyber-cyan text-obsidian-950';
          b2.className = 'px-2.5 py-1 rounded-lg text-slate-400 font-semibold hover:text-white';
        } else {
          b2.className = 'px-2.5 py-1 rounded-lg font-bold bg-cyber-cyan text-obsidian-950';
          b1.className = 'px-2.5 py-1 rounded-lg text-slate-400 font-semibold hover:text-white';
        }
        this.toast('Period set to ' + period);
      },

      updateClockDisplay() {
        document.getElementById('matchClockDisplay').innerText = this.formatTime(AppState.clock.seconds);
        AppState.match.starters.forEach(pid => {
          const el = document.getElementById('liveTimer_' + pid);
          if (el) el.innerText = this.formatTime(AppState.playerTimers[pid] || 0);
        });
      },

      formatTime(sec) {
        const m = Math.floor(sec / 60);
        const s = sec % 60;
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
      },

      renderLiveBoard() {
        const pitchGrid = document.getElementById('liveOnPitchGrid');
        const benchGrid = document.getElementById('liveBenchGrid');
        pitchGrid.innerHTML = '';
        benchGrid.innerHTML = '';

        AppState.match.starters.forEach(pid => {
          const p = AppState.squad.find(i => i.id === pid);
          if (!p) return;

          const isSelected = AppState.subOutPlayerId === pid;
          const card = document.createElement('button');
          card.type = 'button';
          card.onclick = () => App.selectSubOut(pid);
          card.className = `p-3 rounded-2xl text-left transition flex items-center justify-between border ${
            isSelected
              ? 'bg-cyber-cyan/25 border-cyber-cyan ring-2 ring-cyber-cyan glow-cyan'
              : 'bg-obsidian-950/80 border-white/10 hover:border-cyber-cyan/40'
          }`;

          card.innerHTML = `
            <div class="flex items-center space-x-2.5">
              <div class="flex-shrink-0">
                ${this.getShirtSvg(p.number, AppState.kitColor, 34)}
              </div>
              <div>
                <div class="text-xs font-bold text-white truncate max-w-[85px]">${p.name}</div>
                <div class="text-[10px] text-cyber-cyan">${p.position}</div>
              </div>
            </div>
            <div class="text-right">
              <div id="liveTimer_${pid}" class="font-mono font-bold text-xs text-cyber-mint">
                ${this.formatTime(AppState.playerTimers[pid] || 0)}
              </div>
              <div class="text-[9px] text-slate-400">Pitch</div>
            </div>
          `;
          pitchGrid.appendChild(card);
        });

        if (AppState.match.bench.length === 0) {
          benchGrid.innerHTML = `<div class="col-span-2 text-slate-500 italic text-xs py-2 text-center">No reserve players on bench</div>`;
        } else {
          AppState.match.bench.forEach(pid => {
            const p = AppState.squad.find(i => i.id === pid);
            if (!p) return;

            const isSubReady = AppState.subOutPlayerId !== null;
            const card = document.createElement('button');
            card.type = 'button';
            card.onclick = () => App.selectSubIn(pid);
            card.className = `p-3 rounded-2xl text-left transition flex items-center justify-between border ${
              isSubReady
                ? 'bg-cyber-mint/20 border-cyber-mint ring-1 ring-cyber-mint hover:scale-[1.02]'
                : 'bg-obsidian-950/60 border-white/5 opacity-80'
            }`;

            card.innerHTML = `
              <div class="flex items-center space-x-2.5">
                <div class="flex-shrink-0">
                  ${this.getShirtSvg(p.number, '#334155', 34, 'rgba(255,255,255,0.2)')}
                </div>
                <div>
                  <div class="text-xs font-bold text-white truncate max-w-[85px]">${p.name}</div>
                  <div class="text-[10px] text-slate-400">${p.position}</div>
                </div>
              </div>
              <div class="text-right">
                <div class="font-mono font-bold text-xs text-slate-300">
                  ${this.formatTime(AppState.playerTimers[pid] || 0)}
                </div>
                <div class="text-[9px] text-cyber-mint font-semibold">${isSubReady ? 'TAP TO SUB' : 'Bench'}</div>
              </div>
            `;
            benchGrid.appendChild(card);
          });
        }

        this.renderTimeline();
      },

      selectSubOut(pid) {
        AppState.subOutPlayerId = pid;
        const p = AppState.squad.find(i => i.id === pid);
        document.getElementById('subInstructionText').innerText = `Step 2: Subbing OUT #${p.number} ${p.name}. Tap bench reserve!`;
        document.getElementById('cancelSubBtn').classList.remove('hidden');
        this.renderLiveBoard();
      },

      selectSubIn(benchPid) {
        if (!AppState.subOutPlayerId) {
          this.toast('Tap a field player first to substitute out');
          return;
        }

        const outPid = AppState.subOutPlayerId;
        const outPlayer = AppState.squad.find(i => i.id === outPid);
        const inPlayer = AppState.squad.find(i => i.id === benchPid);

        const savedPos = AppState.match.fieldPositions[outPid] || { x: 50, y: 50 };
        AppState.match.fieldPositions[benchPid] = savedPos;

        AppState.match.starters = AppState.match.starters.map(id => id === outPid ? benchPid : id);
        AppState.match.bench = AppState.match.bench.map(id => id === benchPid ? outPid : id);

        const eventRecord = {
          id: 'ev_' + Date.now(),
          matchId: AppState.match.id,
          type: 'Sub',
          playerOut: outPlayer.name,
          playerOutNum: outPlayer.number,
          playerIn: inPlayer.name,
          playerInNum: inPlayer.number,
          matchTimeSeconds: AppState.clock.seconds,
          period: AppState.clock.period,
          timestamp: Date.now()
        };
        AppState.events.unshift(eventRecord);

        AppState.subOutPlayerId = null;
        document.getElementById('cancelSubBtn').classList.add('hidden');
        document.getElementById('subInstructionText').innerText = 'Step 1: Tap a player on field to sub OUT';

        this.saveStorage();
        this.renderLiveBoard();
        this.renderPitchTokens();
        this.toast(`Sub: #${inPlayer.number} ${inPlayer.name} IN ⇄ #${outPlayer.number} ${outPlayer.name} OUT`);
      },

      cancelSubSelection() {
        AppState.subOutPlayerId = null;
        document.getElementById('cancelSubBtn').classList.add('hidden');
        document.getElementById('subInstructionText').innerText = 'Step 1: Tap a player on field to sub OUT';
        this.renderLiveBoard();
      },

      openEventModal(type) {
        AppState.currentEventType = type;
        const modal = document.getElementById('modalEvent');
        const title = document.getElementById('eventModalTitle');
        const selector = document.getElementById('eventPlayerSelector');

        title.innerHTML = type === 'Goal' ? '<span>⚽ Register Goal</span>' : '<span>👟 Register Assist</span>';
        selector.innerHTML = '';

        const activeIds = [...AppState.match.starters, ...AppState.match.bench];
        activeIds.forEach(pid => {
          const p = AppState.squad.find(i => i.id === pid);
          if (p) {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.innerText = `#${p.number} — ${p.name} (${p.position})`;
            selector.appendChild(opt);
          }
        });

        modal.classList.remove('hidden');
      },

      confirmEvent() {
        const type = AppState.currentEventType;
        const selector = document.getElementById('eventPlayerSelector');
        const pid = selector.value;
        const player = AppState.squad.find(i => i.id === pid);

        if (!player) return;

        if (type === 'Goal') {
          AppState.match.ourGoals = (AppState.match.ourGoals || 0) + 1;
          document.getElementById('scoreboardGoals').innerText = AppState.match.ourGoals;
        }

        const ev = {
          id: 'ev_' + Date.now(),
          matchId: AppState.match.id,
          type: type,
          playerId: pid,
          playerName: player.name,
          playerNumber: player.number,
          matchTimeSeconds: AppState.clock.seconds,
          period: AppState.clock.period,
          timestamp: Date.now()
        };

        AppState.events.unshift(ev);
        this.saveStorage();
        this.closeModals();
        this.renderTimeline();
        this.toast(`${type} logged for #${player.number} ${player.name}! 🎉`);
      },

      renderTimeline() {
        const list = document.getElementById('matchTimelineList');
        const countBadge = document.getElementById('timelineEventCount');
        countBadge.innerText = `${AppState.events.length} events`;

        if (AppState.events.length === 0) {
          list.innerHTML = `<div class="text-slate-500 text-center py-4 italic">No match events logged yet</div>`;
          return;
        }

        list.innerHTML = '';
        AppState.events.forEach(ev => {
          const item = document.createElement('div');
          item.className = 'p-2.5 rounded-xl bg-obsidian-950 border border-white/5 flex items-center justify-between';

          let icon = '⚽';
          let text = '';
          if (ev.type === 'Goal') {
            icon = '⚽';
            text = `<span class="font-bold text-cyber-mint">GOAL</span> by #${ev.playerNumber} ${ev.playerName}`;
          } else if (ev.type === 'Assist') {
            icon = '👟';
            text = `<span class="font-bold text-sky-400">ASSIST</span> by #${ev.playerNumber} ${ev.playerName}`;
          } else if (ev.type === 'Sub') {
            icon = '⇄';
            text = `<span class="font-bold text-amber-300">SUB</span> #${ev.playerInNum} ${ev.playerIn} ⇄ #${ev.playerOutNum} ${ev.playerOut}`;
          }

          item.innerHTML = `
            <div class="flex items-center space-x-2">
              <span class="text-base">${icon}</span>
              <div class="text-xs text-white">${text}</div>
            </div>
            <div class="text-right">
              <div class="font-mono font-bold text-xs text-cyber-cyan">${this.formatTime(ev.matchTimeSeconds)}</div>
              <div class="text-[9px] text-slate-400">${ev.period}</div>
            </div>
          `;
          list.appendChild(item);
        });
      },

      renderStats() {
        const container = document.getElementById('statsCardsContainer');
        container.innerHTML = '';

        AppState.squad.forEach(p => {
          const secPlayed = AppState.playerTimers[p.id] || 0;
          const goals = AppState.events.filter(e => e.type === 'Goal' && e.playerId === p.id).length;
          const assists = AppState.events.filter(e => e.type === 'Assist' && e.playerId === p.id).length;
          const wasStarter = AppState.match.starters.includes(p.id);
          const shirtColor = wasStarter ? AppState.kitColor : '#334155';

          const card = document.createElement('div');
          card.className = 'glass-card rounded-[22px] p-3 flex items-center justify-between';
          card.innerHTML = `
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0 flex items-center justify-center">
                ${this.getShirtSvg(p.number, shirtColor, 40, wasStarter ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.15)')}
              </div>
              <div>
                <div class="font-bold text-sm text-white">${p.name}</div>
                <div class="text-[11px] text-slate-400 mt-0.5">${p.position} • ${wasStarter ? 'Starter' : 'Bench'}</div>
              </div>
            </div>

            <div class="flex items-center space-x-4 text-right">
              <div>
                <div class="font-mono font-bold text-sm text-cyber-mint">${this.formatTime(secPlayed)}</div>
                <div class="text-[9px] uppercase tracking-wider text-slate-400">Game Time</div>
              </div>
              <div class="flex items-center space-x-1.5 text-xs font-bold">
                <span class="px-2 py-0.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">⚽ ${goals}</span>
                <span class="px-2 py-0.5 rounded-lg bg-sky-500/20 text-sky-400 border border-sky-500/30">👟 ${assists}</span>
              </div>
            </div>
          `;
          container.appendChild(card);
        });
      },

      openExportModal() {
        document.getElementById('pdfMatchDate').innerText = AppState.match.date;
        document.getElementById('pdfGeneratedTime').innerText = 'Generated: ' + new Date().toLocaleString();
        document.getElementById('pdfFixtureTitle').innerText = `${AppState.match.title} vs ${AppState.match.opponent} (${AppState.match.format}-a-side)`;
        document.getElementById('pdfMatchResult').innerText = `Score: ${AppState.match.ourGoals || 0} - ${AppState.match.opponentGoals || 0} (Played: ${this.formatTime(AppState.clock.seconds)})`;

        const tbody = document.getElementById('pdfPlayerTableBody');
        tbody.innerHTML = '';
        AppState.squad.forEach(p => {
          const sec = AppState.playerTimers[p.id] || 0;
          const goals = AppState.events.filter(e => e.type === 'Goal' && e.playerId === p.id).length;
          const assists = AppState.events.filter(e => e.type === 'Assist' && e.playerId === p.id).length;
          const isStarter = AppState.match.starters.includes(p.id);

          const row = document.createElement('tr');
          row.className = 'hover:bg-slate-50';
          row.innerHTML = `
            <td class="p-2 font-bold">${p.number}</td>
            <td class="p-2 font-semibold text-slate-800">${p.name}</td>
            <td class="p-2 text-slate-500 font-mono">${p.position}</td>
            <td class="p-2 text-slate-600">${isStarter ? 'Starter' : 'Bench'}</td>
            <td class="p-2 text-center font-mono font-bold text-emerald-700">${this.formatTime(sec)}</td>
            <td class="p-2 text-center font-bold">${goals}</td>
            <td class="p-2 text-center font-bold">${assists}</td>
          `;
          tbody.appendChild(row);
        });

        const log = document.getElementById('pdfTimelineLog');
        log.innerHTML = '';
        if (AppState.events.length === 0) {
          log.innerHTML = `<div class="text-slate-400 italic">No match events recorded during this session.</div>`;
        } else {
          AppState.events.forEach(ev => {
            const item = document.createElement('div');
            let txt = '';
            if (ev.type === 'Goal') txt = `[${this.formatTime(ev.matchTimeSeconds)}] ⚽ GOAL by #${ev.playerNumber} ${ev.playerName} (${ev.period})`;
            else if (ev.type === 'Assist') txt = `[${this.formatTime(ev.matchTimeSeconds)}] 👟 ASSIST by #${ev.playerNumber} ${ev.playerName} (${ev.period})`;
            else if (ev.type === 'Sub') txt = `[${this.formatTime(ev.matchTimeSeconds)}] ⇄ SUB: #${ev.playerInNum} ${ev.playerIn} IN for #${ev.playerOutNum} ${ev.playerOut}`;
            item.innerText = txt;
            log.appendChild(item);
          });
        }

        const el = document.getElementById('pdfExportContainer');
        el.classList.remove('hidden');

        if (typeof html2pdf !== 'undefined') {
          this.toast('Generating PDF document...');
          const opt = {
            margin: 10,
            filename: `GameOn_Match_${AppState.match.title.replace(/\\s+/g, '_')}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
          };
          html2pdf().set(opt).from(el).save().then(() => {
            el.classList.add('hidden');
            App.toast('PDF Exported successfully! 📄');
          }).catch(err => {
            console.error('PDF error:', err);
            el.classList.add('hidden');
            window.print();
          });
        } else {
          window.print();
          el.classList.add('hidden');
        }
      },

      openMatchSetupModal() {
        document.getElementById('inputMatchTitle').value = AppState.match.title;
        document.getElementById('inputMatchOpponent').value = AppState.match.opponent;
        document.getElementById('inputMatchDate').value = AppState.match.date;
        this.selectFormat(AppState.match.format);
        document.getElementById('modalMatchSetup').classList.remove('hidden');
      },

      selectFormat(fmt) {
        AppState.pendingFormat = fmt;
        document.querySelectorAll('.format-btn').forEach(btn => {
          if (btn.dataset.fmt === fmt) {
            btn.className = 'format-btn py-2 rounded-xl bg-gradient-to-r from-cyber-cyan to-cyber-mint text-obsidian-950 font-black';
          } else {
            btn.className = 'format-btn py-2 rounded-xl bg-obsidian-950 border border-white/10 text-slate-300 font-bold';
          }
        });
      },

      saveMatchSetup() {
        const title = document.getElementById('inputMatchTitle').value.trim() || 'Match 1';
        const opp = document.getElementById('inputMatchOpponent').value.trim() || 'Echo Strikers';
        const date = document.getElementById('inputMatchDate').value || new Date().toISOString().split('T')[0];
        const fmt = AppState.pendingFormat || AppState.match.format;

        AppState.match.title = title;
        AppState.match.opponent = opp;
        AppState.match.date = date;
        AppState.match.format = fmt;

        document.getElementById('activeMatchTitleDisplay').innerText = `${title} vs ${opp}`;
        document.getElementById('activeMatchDateBadge').innerText = date;
        document.getElementById('scoreboardOpponent').innerText = opp.split(' ')[0];

        this.applyFormatDefaults();
        this.saveStorage();
        this.closeModals();
        this.renderPitchTokens();
        this.toast('Match configuration saved!');
      },

      openAddPlayerModal() {
        document.getElementById('inputPlayerName').value = '';
        document.getElementById('inputPlayerNumber').value = '';
        document.getElementById('modalAddPlayer').classList.remove('hidden');
      },

      saveNewPlayer() {
        const name = document.getElementById('inputPlayerName').value.trim();
        const num = parseInt(document.getElementById('inputPlayerNumber').value);
        const pos = document.getElementById('inputPlayerPosition').value;

        if (!name || isNaN(num)) {
          this.toast('Please provide a valid name and shirt number (1-99)');
          return;
        }

        const newPlayer = {
          id: 'p_' + Date.now(),
          number: num,
          name: name,
          position: pos
        };

        AppState.squad.push(newPlayer);
        AppState.match.availability[newPlayer.id] = true;
        AppState.match.bench.push(newPlayer.id);

        this.saveStorage();
        this.closeModals();
        this.renderRoster();
        this.renderPitchTokens();
        this.toast(`Player #${num} ${name} added to squad!`);
      },

      closeModals() {
        document.querySelectorAll('#modalMatchSetup, #modalAddPlayer, #modalEvent').forEach(m => {
          m.classList.add('hidden');
        });
      },

      toast(msg, icon = '✨') {
        const pod = document.getElementById('toastPod');
        const msgEl = document.getElementById('toastMessage');
        const iconEl = document.getElementById('toastIcon');

        msgEl.innerText = msg;
        iconEl.innerText = icon;

        pod.classList.remove('opacity-0', 'pointer-events-none');
        pod.classList.add('opacity-100');

        if (this._toastTimer) clearTimeout(this._toastTimer);
        this._toastTimer = setTimeout(() => {
          pod.classList.add('opacity-0', 'pointer-events-none');
          pod.classList.remove('opacity-100');
        }, 2600);
      },

      renderAll() {
        document.getElementById('activeMatchTitleDisplay').innerText = `${AppState.match.title} vs ${AppState.match.opponent}`;
        document.getElementById('activeMatchDateBadge').innerText = AppState.match.date;
        document.getElementById('scoreboardOpponent').innerText = AppState.match.opponent.split(' ')[0];
        document.getElementById('scoreboardGoals').innerText = AppState.match.ourGoals || 0;
        document.getElementById('scoreboardOpponentGoals').innerText = AppState.match.opponentGoals || 0;

        this.renderPitchTokens();
        this.renderRoster();
        this.renderLiveBoard();
        this.renderStats();
      }
    };

    window.addEventListener('DOMContentLoaded', () => App.init());
  </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as out:
    out.write(html_template)
print("Successfully generated index.html")
