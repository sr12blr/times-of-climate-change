// Torchlight — always-on DAILY leaderboard.
// Injected on demand into the live puzzle page (docs/torchlight/index.html) by the
// template's lazy loader. Depends on: window.LB_CONFIG (config.js) for Firebase creds,
// and the firebase compat SDK (loaded just before this file).
//
// Reuses the same Firestore schema as the QR event flow —
//   events/{eventId}/puzzles/{date}/results/{nameSlug}
// but under a dedicated, stable eventId ("daily") that is independent of the per-event
// LB_CONFIG.eventId, so running an event never touches the daily board and vice-versa.
//
// Scoring: adjusted = raw solve time + 30s per hint. Winners ranked by adjusted time.

(function () {
  var DAILY_EVENT_ID = 'daily';
  var HINT_PENALTY_MS = 30000;

  var _dbReady = false;
  // Remember the current player's result across mountInline() / openModal() calls,
  // and which container currently owns a live snapshot listener (so we can detach it).
  var _lastResult = null;
  var _listeners = []; // { el, unsub }

  function cfg() { return window.LB_CONFIG; }

  function haveFirebase() {
    return !!(window.firebase && cfg() && cfg().firebase);
  }

  function getDb() {
    if (!haveFirebase()) return null;
    if (!_dbReady) {
      if (!window.firebase.apps.length) window.firebase.initializeApp(cfg().firebase);
      _dbReady = true;
    }
    return window.firebase.firestore();
  }

  function resultsCollection(db, date) {
    return db.collection('events').doc(DAILY_EVENT_ID)
      .collection('puzzles').doc(date)
      .collection('results');
  }

  function nameSlug(s) {
    return String(s).toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 40);
  }

  function fmt(ms) {
    var s = Math.floor((ms || 0) / 1000);
    var m = Math.floor(s / 60);
    var rs = s % 60;
    return m + ':' + (rs < 10 ? '0' : '') + rs;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function adjustedOf(data) {
    if (typeof data.adjustedMs === 'number') return data.adjustedMs;
    return (data.ms || 0) + (data.hints || 0) * HINT_PENALTY_MS;
  }

  // ---- one-time scoped styles ----
  function injectStyles() {
    if (document.getElementById('tl-lb-styles')) return;
    var css = ''
      + '.tl-lb{font-family:"Nunito Sans",system-ui,sans-serif;color:#1a1a1a;text-align:left}'
      + '.tl-lb-yours{background:#eef7f4;border:1px solid #cbe6dd;border-radius:10px;padding:12px 14px;margin-bottom:14px;font-size:15px;text-align:center}'
      + '.tl-lb-yours b{color:#2C5F4A}'
      + '.tl-lb-form{background:#fff;border:1px solid #d8d2c4;border-radius:10px;padding:14px;margin-bottom:14px}'
      + '.tl-lb-form label{display:block;font-weight:700;margin-bottom:8px;font-size:14px}'
      + '.tl-lb-input{width:100%;font-size:17px;padding:11px 12px;border:1px solid #d8d2c4;border-radius:8px;font-family:inherit;box-sizing:border-box}'
      + '.tl-lb-btn{margin-top:12px;width:100%;background:#2C5F4A;color:#fff;border:0;padding:13px 20px;font-size:16px;font-weight:700;border-radius:8px;cursor:pointer;font-family:inherit}'
      + '.tl-lb-btn[disabled]{opacity:.5;cursor:not-allowed}'
      + '.tl-lb-err{background:#fbe9e7;color:#8b0000;padding:9px 11px;border-radius:6px;font-size:13px;margin-top:10px}'
      + '.tl-lb-note{color:#6b6b6b;font-size:14px;text-align:center;margin:0 0 12px}'
      + '.tl-lb-empty{text-align:center;color:#6b6b6b;padding:24px}'
      + '.tl-lb-table{width:100%;border-collapse:collapse;font-size:15px}'
      + '.tl-lb-table th,.tl-lb-table td{padding:9px 6px;text-align:left;border-bottom:1px solid #ece7db}'
      + '.tl-lb-table th{font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#6b6b6b;font-weight:700}'
      + '.tl-lb-table td.r{font-weight:800;color:#2C5F4A;width:34px}'
      + '.tl-lb-table td.sc,.tl-lb-table td.tm{font-variant-numeric:tabular-nums;font-family:ui-monospace,Menlo,monospace}'
      + '.tl-lb-table td.sc{font-weight:700}'
      + '.tl-lb-table td.num{text-align:center;color:#6b6b6b;width:34px}'
      + '.tl-lb-table tr.me{background:#fff7e6}'
      + '.tl-lb-table tr.me td.r{color:#C8602A}'
      + '.tl-lb-dnf{color:#9a9a9a}';
    var st = document.createElement('style');
    st.id = 'tl-lb-styles';
    st.textContent = css;
    document.head.appendChild(st);
  }

  // ---- submit ----
  function submitScore(date, name, result) {
    var db = getDb();
    if (!db) return Promise.reject(new Error('no db'));
    var slug = nameSlug(name);
    var ref = resultsCollection(db, date).doc(slug);
    return ref.get().then(function (snap) {
      if (snap.exists) return { slug: slug, already: true };
      return ref.set({
        name: name,
        ms: result.ms || 0,
        mistakes: result.mistakes || 0,
        hints: result.hints || 0,
        adjustedMs: (result.ms || 0) + (result.hints || 0) * HINT_PENALTY_MS,
        won: !!result.won,
        submittedAt: window.firebase.firestore.FieldValue.serverTimestamp()
      }).then(function () { return { slug: slug, already: false }; });
    });
  }

  // ---- board rendering ----
  function detachListener(el) {
    for (var i = _listeners.length - 1; i >= 0; i--) {
      if (_listeners[i].el === el) {
        try { _listeners[i].unsub(); } catch (e) {}
        _listeners.splice(i, 1);
      }
    }
  }

  function renderRows(tbody, empty, docs, mySlug) {
    var winners = [];
    var dnf = [];
    docs.forEach(function (d) {
      var data = d.data();
      data._id = d.id;
      (data.won ? winners : dnf).push(data);
    });
    winners.sort(function (a, b) { return adjustedOf(a) - adjustedOf(b); });
    dnf.sort(function (a, b) { return (a.name || '').localeCompare(b.name || ''); });

    tbody.innerHTML = '';
    if (!winners.length && !dnf.length) {
      empty.style.display = '';
      return;
    }
    empty.style.display = 'none';

    winners.forEach(function (r, i) {
      var mine = mySlug && r._id === mySlug;
      var hints = r.hints || 0;
      var tr = document.createElement('tr');
      if (mine) tr.className = 'me';
      tr.innerHTML =
        '<td class="r">' + (i + 1) + '</td>'
        + '<td>' + escapeHtml(r.name || '') + (mine ? ' <span style="font-size:12px;color:#C8602A">(you)</span>' : '') + '</td>'
        + '<td class="sc">' + fmt(adjustedOf(r)) + '</td>'
        + '<td class="tm">' + fmt(r.ms || 0) + '</td>'
        + '<td class="num">' + (hints ? hints : '—') + '</td>'
        + '<td class="num">' + (r.mistakes || 0) + '</td>';
      tbody.appendChild(tr);
    });
    dnf.forEach(function (r) {
      var mine = mySlug && r._id === mySlug;
      var tr = document.createElement('tr');
      tr.className = 'dnf' + (mine ? ' me' : '');
      tr.innerHTML =
        '<td class="r">—</td>'
        + '<td>' + escapeHtml(r.name || '') + (mine ? ' <span style="font-size:12px;color:#C8602A">(you)</span>' : '') + '</td>'
        + '<td class="sc">DNF</td>'
        + '<td class="tm">—</td>'
        + '<td class="num">' + (r.hints || 0 || '—') + '</td>'
        + '<td class="num">' + (r.mistakes || 0) + '</td>';
      tbody.appendChild(tr);
    });
  }

  // Build the board UI inside `el`. `result` may be null (player hasn't solved yet).
  function renderInto(el, date, result) {
    injectStyles();
    detachListener(el);

    var db = getDb();
    if (!db) {
      el.innerHTML = '<p class="tl-lb-note">Leaderboard unavailable right now.</p>';
      return;
    }

    var submittedKey = 'lb_submitted_' + date;
    var alreadySubmitted = false;
    try { alreadySubmitted = !!localStorage.getItem(submittedKey); } catch (e) {}
    var mySlug = '';
    try { mySlug = localStorage.getItem('lb_slug_' + date) || ''; } catch (e) {}

    var solvedWon = !!(result && result.won);
    var canSubmit = solvedWon && !alreadySubmitted;

    var wrap = document.createElement('div');
    wrap.className = 'tl-lb';

    // Your-score breakdown (when solved & won)
    if (solvedWon) {
      var hints = result.hints || 0;
      var adj = (result.ms || 0) + hints * HINT_PENALTY_MS;
      var breakdown = hints > 0
        ? (fmt(result.ms || 0) + ' + ' + fmt(hints * HINT_PENALTY_MS) + ' (' + hints + ' hint' + (hints !== 1 ? 's' : '') + ') = <b>' + fmt(adj) + '</b>')
        : ('<b>' + fmt(adj) + '</b> (no hints)');
      var yours = document.createElement('div');
      yours.className = 'tl-lb-yours';
      yours.innerHTML = 'Your score: ' + breakdown;
      wrap.appendChild(yours);
    } else if (!result) {
      var note = document.createElement('p');
      note.className = 'tl-lb-note';
      note.textContent = 'Solve today’s puzzle to add your time.';
      wrap.appendChild(note);
    }

    // Name form
    if (canSubmit) {
      var savedName = '';
      try { savedName = (localStorage.getItem('lb_name') || '').trim(); } catch (e) {}
      var form = document.createElement('div');
      form.className = 'tl-lb-form';
      form.innerHTML =
        '<label for="tlLbName">Add your name to today’s leaderboard</label>'
        + '<input id="tlLbName" class="tl-lb-input" autocomplete="off" maxlength="40" placeholder="e.g. Sailee" value="' + escapeHtml(savedName) + '">'
        + '<div class="tl-lb-err" id="tlLbErr" style="display:none"></div>'
        + '<button class="tl-lb-btn" id="tlLbSubmit">Add me →</button>';
      wrap.appendChild(form);
    }

    // Board table
    var card = document.createElement('div');
    card.innerHTML =
      '<table class="tl-lb-table"><thead><tr>'
      + '<th>#</th><th>Name</th><th>Score</th><th>Time</th><th>💡</th><th>✗</th>'
      + '</tr></thead><tbody></tbody></table>'
      + '<div class="tl-lb-empty" style="display:none">Be the first to finish today!</div>';
    wrap.appendChild(card);

    el.innerHTML = '';
    el.appendChild(wrap);

    var tbody = card.querySelector('tbody');
    var empty = card.querySelector('.tl-lb-empty');

    // Wire the form
    if (canSubmit) {
      var input = wrap.querySelector('#tlLbName');
      var err = wrap.querySelector('#tlLbErr');
      var btn = wrap.querySelector('#tlLbSubmit');
      var doSubmit = function () {
        var name = (input.value || '').trim();
        err.style.display = 'none';
        if (name.length < 1) { err.textContent = 'Please enter a name.'; err.style.display = ''; return; }
        var slug = nameSlug(name);
        if (!slug) { err.textContent = 'Name must contain letters or numbers.'; err.style.display = ''; return; }
        btn.disabled = true;
        btn.textContent = 'Adding…';
        submitScore(date, name, result).then(function (res) {
          try {
            localStorage.setItem('lb_name', name);
            localStorage.setItem(submittedKey, '1');
            localStorage.setItem('lb_slug_' + date, res.slug);
          } catch (e) {}
          // Re-render without the form; the snapshot listener will show the new row.
          renderInto(el, date, result);
        }).catch(function (e) {
          console.error('[lb] submit failed', e);
          btn.disabled = false;
          btn.textContent = 'Add me →';
          err.textContent = 'Could not submit right now. Try again.';
          err.style.display = '';
        });
      };
      btn.addEventListener('click', doSubmit);
      input.addEventListener('keydown', function (e) { if (e.key === 'Enter') doSubmit(); });
    }

    // Live results
    var unsub = resultsCollection(db, date).onSnapshot(function (snap) {
      var docs = [];
      snap.forEach(function (d) { docs.push(d); });
      var slugNow = mySlug;
      try { slugNow = localStorage.getItem('lb_slug_' + date) || mySlug; } catch (e) {}
      renderRows(tbody, empty, docs, slugNow);
    }, function (e) {
      console.error('[lb] listen error', e);
      empty.style.display = '';
      empty.textContent = 'Could not load the leaderboard.';
    });
    _listeners.push({ el: el, unsub: unsub });
  }

  window.TL_DAILY_LB = {
    // Called from the puzzle end screen once the player has finished.
    mountInline: function (result) {
      _lastResult = result || _lastResult;
      var el = document.getElementById('dailyLeaderboard');
      if (el) renderInto(el, (result && result.date) || (_lastResult && _lastResult.date), _lastResult);
    },
    // Called from the header "🏆 Leaderboard" button (may be before solving).
    // `date` is passed from the page (the player may not have solved yet, so there is
    // no _lastResult to read it from).
    openModal: function (date) {
      var el = document.getElementById('leaderboardModalBody');
      if (!el) return;
      var d = date || (_lastResult && _lastResult.date);
      renderInto(el, d, _lastResult);
    }
  };
})();
