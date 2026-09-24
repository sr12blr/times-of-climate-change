// Torchlight — always-on DAILY leaderboard.
// Injected on demand into the live puzzle page (docs/torchlight/index.html) by the
// template's lazy loader. Depends on: window.LB_CONFIG (config.js) for Firebase creds,
// and the firebase compat SDK (loaded just before this file).
//
// Same Firestore path shape as the QR event flow, under a dedicated eventId ("daily"):
//   events/daily/puzzles/{date}/results/{uid}
// Unlike the QR events, posting here requires a Firebase Auth account (email + password).
// Each account picks a permanent display name once:
//   users/{uid}             { displayName, nameKey, createdAt }   (private to the owner)
//   displayNames/{nameKey}  { uid }                                (public; enforces uniqueness)
// Firestore rules (see SETUP.md) check that a result is posted by its owner under their
// own display name, once per puzzle. Older results keyed by name slug still render.
//
// Scoring: adjusted = raw solve time + 30s per hint. Winners ranked by adjusted time.

(function () {
  var DAILY_EVENT_ID = 'daily';
  var HINT_PENALTY_MS = 30000;
  var NAME_MIN = 2;
  var NAME_MAX = 24;
  var PASSWORD_MIN = 8;

  var _dbReady = false;
  var _authReady = null;   // Promise resolved after Firebase reports the initial sign-in state
  var _profile = null;     // { displayName } for the signed-in user, or null
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

  // Must match the nameKey check in the Firestore rules.
  function nameKey(s) {
    return String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
  }

  function auth() {
    getDb();
    return window.firebase.auth();
  }

  // Resolves once Firebase has restored any saved session (it keeps players signed in
  // on this browser by default), and loads their profile.
  function whenAuthReady() {
    if (_authReady) return _authReady;
    _authReady = new Promise(function (resolve) {
      var first = true;
      auth().onAuthStateChanged(function (user) {
        loadProfile(user).then(function () {
          if (first) { first = false; resolve(); }
        });
      });
    });
    return _authReady;
  }

  function loadProfile(user) {
    if (!user) { _profile = null; return Promise.resolve(); }
    if (_profile && _profile.uid === user.uid) return Promise.resolve();
    _profile = null;
    return getDb().collection('users').doc(user.uid).get().then(function (snap) {
      if (snap.exists) _profile = { uid: user.uid, displayName: snap.data().displayName };
    }).catch(function (e) {
      console.error('[lb] profile load failed', e);
    });
  }

  function validateName(name) {
    if (name.length < NAME_MIN || name.length > NAME_MAX) {
      return 'Display name must be ' + NAME_MIN + '–' + NAME_MAX + ' characters.';
    }
    if (nameKey(name).length < NAME_MIN) return 'Display name needs at least 2 letters or numbers.';
    return '';
  }

  function nameTaken(name) {
    return getDb().collection('displayNames').doc(nameKey(name)).get()
      .then(function (snap) { return snap.exists; });
  }

  // Claims the display name and creates the profile in one atomic write. The rules
  // reject it if another account already holds the name.
  function createProfile(user, name) {
    var db = getDb();
    var key = nameKey(name);
    var batch = db.batch();
    batch.set(db.collection('displayNames').doc(key), { uid: user.uid });
    batch.set(db.collection('users').doc(user.uid), {
      displayName: name,
      nameKey: key,
      createdAt: window.firebase.firestore.FieldValue.serverTimestamp()
    });
    return batch.commit().then(function () {
      _profile = { uid: user.uid, displayName: name };
    });
  }

  function authErrorMessage(e) {
    var code = (e && e.code) || '';
    switch (code) {
      case 'auth/email-already-in-use': return 'An account with this email already exists. Sign in instead.';
      case 'auth/invalid-email': return 'That email address doesn’t look right.';
      case 'auth/weak-password': return 'Password must be at least ' + PASSWORD_MIN + ' characters.';
      case 'auth/invalid-credential':
      case 'auth/invalid-login-credentials':
      case 'auth/wrong-password':
      case 'auth/user-not-found': return 'Email or password is incorrect.';
      case 'auth/too-many-requests': return 'Too many attempts. Wait a few minutes and try again.';
      case 'auth/network-request-failed': return 'No connection. Check your internet and try again.';
      case 'auth/operation-not-allowed': return 'Accounts aren’t switched on yet. Try again later.';
      case 'permission-denied': return 'That display name was just taken. Try another.';
    }
    console.error('[lb] auth error', e);
    return 'Something went wrong. Try again.';
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
      + '.tl-lb-dnf{color:#9a9a9a}'
      + '.tl-lb-form .tl-lb-input+.tl-lb-input{margin-top:8px}'
      + '.tl-lb-form p{font-size:13px;color:#6b6b6b;margin:0 0 10px}'
      + '.tl-lb-link{background:none;border:0;padding:0;color:#0E7C7B;font-weight:700;font-size:13px;text-decoration:underline;cursor:pointer;font-family:inherit}'
      + '.tl-lb-alt{margin-top:12px;font-size:13px;color:#6b6b6b;text-align:center}'
      + '.tl-lb-ok{background:#eef7f4;color:#2C5F4A;padding:9px 11px;border-radius:6px;font-size:13px;margin-top:10px}'
      + '.tl-lb-acct{font-size:12px;color:#6b6b6b;text-align:center;margin-top:12px}';
    var st = document.createElement('style');
    st.id = 'tl-lb-styles';
    st.textContent = css;
    document.head.appendChild(st);
  }

  // ---- submit ----
  // Posts the signed-in player's result under their uid. Resolves either way if they
  // already posted for this puzzle (e.g. from another device).
  function submitScore(date, result) {
    var db = getDb();
    var user = auth().currentUser;
    if (!db || !user || !_profile) return Promise.reject(new Error('not signed in'));
    var ref = resultsCollection(db, date).doc(user.uid);
    return ref.get().then(function (snap) {
      if (snap.exists) return;
      var ms = Math.round(result.ms || 0);
      var hints = result.hints || 0;
      return ref.set({
        name: _profile.displayName,
        ms: ms,
        mistakes: result.mistakes || 0,
        hints: hints,
        adjustedMs: ms + hints * HINT_PENALTY_MS,
        won: !!result.won,
        submittedAt: window.firebase.firestore.FieldValue.serverTimestamp()
      });
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

  function renderRows(tbody, empty, docs, myId) {
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
      var mine = myId && r._id === myId;
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
      var mine = myId && r._id === myId;
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

    el.innerHTML = '<p class="tl-lb-note">Loading…</p>';
    whenAuthReady().then(function () { buildBoard(el, date, result); });
  }

  function buildBoard(el, date, result) {
    var db = getDb();
    var user = auth().currentUser;
    var myId = user ? user.uid : '';
    var solvedWon = !!(result && result.won);
    var ctx = { el: el, date: date, result: result };

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

    // Account / post-your-time panel. Hidden again below once this account's row exists.
    var panel = document.createElement('div');
    if (solvedWon) {
      wrap.appendChild(panel);
      renderPanel(panel, ctx, defaultMode(user));
    }

    // Board table
    var card = document.createElement('div');
    card.innerHTML =
      '<table class="tl-lb-table"><thead><tr>'
      + '<th>#</th><th>Name</th><th>Score</th><th>Time</th><th>💡</th><th>✗</th>'
      + '</tr></thead><tbody></tbody></table>'
      + '<div class="tl-lb-empty" style="display:none">Be the first to finish today!</div>';
    wrap.appendChild(card);

    if (user) {
      var acct = document.createElement('div');
      acct.className = 'tl-lb-acct';
      acct.innerHTML = 'Signed in as ' + escapeHtml(_profile ? _profile.displayName : (user.email || ''))
        + ' · <button type="button" class="tl-lb-link">Sign out</button>';
      acct.querySelector('button').addEventListener('click', function () {
        auth().signOut().then(function () {
          _profile = null;
          renderInto(el, date, result);
        });
      });
      wrap.appendChild(acct);
    }

    el.innerHTML = '';
    el.appendChild(wrap);

    var tbody = card.querySelector('tbody');
    var empty = card.querySelector('.tl-lb-empty');

    // Live results
    var unsub = resultsCollection(db, date).onSnapshot(function (snap) {
      var docs = [];
      var posted = false;
      snap.forEach(function (d) {
        docs.push(d);
        if (myId && d.id === myId) posted = true;
      });
      if (posted) panel.style.display = 'none';
      renderRows(tbody, empty, docs, myId);
    }, function (e) {
      console.error('[lb] listen error', e);
      empty.style.display = '';
      empty.textContent = 'Could not load the leaderboard.';
    });
    _listeners.push({ el: el, unsub: unsub });
  }

  function defaultMode(user) {
    if (user) return _profile ? 'post' : 'name';
    var hasAccount = false;
    try { hasAccount = !!localStorage.getItem('lb_has_account'); } catch (e) {}
    return hasAccount ? 'signin' : 'signup';
  }

  // Real <form>s with autocomplete hints so phone password managers offer to save and
  // fill the email + password.
  var PANELS = {
    post: function () {
      return '<form class="tl-lb-form" action="#" method="post">'
        + '<label>Add your time to today’s leaderboard</label>'
        + '<p>Posting as <b>' + escapeHtml(_profile.displayName) + '</b></p>'
        + '<div class="tl-lb-err" style="display:none"></div>'
        + '<button type="submit" class="tl-lb-btn">Add my time →</button>'
        + '</form>';
    },
    name: function () {
      return '<form class="tl-lb-form" action="#" method="post">'
        + '<label for="tlLbDisplayName">Pick a display name</label>'
        + '<p>It’s shown on the leaderboard and can’t be changed later.</p>'
        + '<input id="tlLbDisplayName" name="displayName" class="tl-lb-input" autocomplete="nickname" maxlength="' + NAME_MAX + '" placeholder="Display name">'
        + '<div class="tl-lb-err" style="display:none"></div>'
        + '<button type="submit" class="tl-lb-btn">Save and add my time</button>'
        + '</form>';
    },
    signup: function () {
      return '<form class="tl-lb-form" action="#" method="post">'
        + '<label>Create an account to add your time</label>'
        + '<p>You’ll stay signed in on this browser. Your display name is shown on the leaderboard and can’t be changed later.</p>'
        + '<input name="displayName" class="tl-lb-input" autocomplete="nickname" maxlength="' + NAME_MAX + '" placeholder="Display name" aria-label="Display name">'
        + '<input name="email" type="email" class="tl-lb-input" autocomplete="username" inputmode="email" autocapitalize="none" placeholder="Email" aria-label="Email">'
        + '<input name="password" type="password" class="tl-lb-input" autocomplete="new-password" placeholder="Password (' + PASSWORD_MIN + '+ characters)" aria-label="Password">'
        + '<div class="tl-lb-err" style="display:none"></div>'
        + '<button type="submit" class="tl-lb-btn">Create account and add my time</button>'
        + '<div class="tl-lb-alt">Have an account? <button type="button" class="tl-lb-link" data-mode="signin">Sign in</button></div>'
        + '</form>';
    },
    signin: function () {
      return '<form class="tl-lb-form" action="#" method="post">'
        + '<label>Sign in to add your time</label>'
        + '<input name="email" type="email" class="tl-lb-input" autocomplete="username" inputmode="email" autocapitalize="none" placeholder="Email" aria-label="Email">'
        + '<input name="password" type="password" class="tl-lb-input" autocomplete="current-password" placeholder="Password" aria-label="Password">'
        + '<div class="tl-lb-err" style="display:none"></div>'
        + '<button type="submit" class="tl-lb-btn">Sign in and add my time</button>'
        + '<div class="tl-lb-alt"><button type="button" class="tl-lb-link" data-mode="reset">Forgot password?</button></div>'
        + '<div class="tl-lb-alt">New here? <button type="button" class="tl-lb-link" data-mode="signup">Create an account</button></div>'
        + '</form>';
    },
    reset: function () {
      return '<form class="tl-lb-form" action="#" method="post">'
        + '<label>Reset your password</label>'
        + '<p>We’ll email you a link to set a new password.</p>'
        + '<input name="email" type="email" class="tl-lb-input" autocomplete="username" inputmode="email" autocapitalize="none" placeholder="Email" aria-label="Email">'
        + '<div class="tl-lb-err" style="display:none"></div>'
        + '<div class="tl-lb-ok" style="display:none"></div>'
        + '<button type="submit" class="tl-lb-btn">Send reset link</button>'
        + '<div class="tl-lb-alt"><button type="button" class="tl-lb-link" data-mode="signin">Back to sign in</button></div>'
        + '</form>';
    }
  };

  var BUSY_LABEL = {
    post: 'Adding…', name: 'Saving…', signup: 'Creating account…',
    signin: 'Signing in…', reset: 'Sending…'
  };

  function renderPanel(panel, ctx, mode, errorMsg) {
    panel.innerHTML = PANELS[mode]();
    var form = panel.querySelector('form');
    var err = form.querySelector('.tl-lb-err');
    var btn = form.querySelector('button[type="submit"]');
    var idleLabel = btn.textContent;

    function fail(msg) {
      btn.disabled = false;
      btn.textContent = idleLabel;
      err.textContent = msg;
      err.style.display = '';
    }
    if (errorMsg) fail(errorMsg);

    form.querySelectorAll('[data-mode]').forEach(function (b) {
      b.addEventListener('click', function () { renderPanel(panel, ctx, b.getAttribute('data-mode')); });
    });

    // Post the time, then redraw the whole board as the signed-in player.
    function postAndRefresh() {
      return submitScore(ctx.date, ctx.result).then(function () {
        renderInto(ctx.el, ctx.date, ctx.result);
      });
    }

    function field(n) {
      var f = form.elements[n];
      return f ? f.value.trim() : '';
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      err.style.display = 'none';

      var name = field('displayName');
      var email = field('email');
      var password = form.elements.password ? form.elements.password.value : '';

      if (mode === 'name' || mode === 'signup') {
        var nameErr = validateName(name);
        if (nameErr) return fail(nameErr);
      }
      if (mode === 'signup' || mode === 'signin' || mode === 'reset') {
        if (!email) return fail('Enter your email.');
      }
      if (mode === 'signup' && password.length < PASSWORD_MIN) {
        return fail('Password must be at least ' + PASSWORD_MIN + ' characters.');
      }
      if (mode === 'signin' && !password) return fail('Enter your password.');

      btn.disabled = true;
      btn.textContent = BUSY_LABEL[mode];

      if (mode === 'post') {
        postAndRefresh().catch(function (e) {
          console.error('[lb] submit failed', e);
          fail('Could not submit right now. Try again.');
        });
      } else if (mode === 'name') {
        nameTaken(name).then(function (taken) {
          if (taken) return fail('That display name is taken. Try another.');
          return createProfile(auth().currentUser, name).then(postAndRefresh);
        }).catch(function (e) { fail(authErrorMessage(e)); });
      } else if (mode === 'signup') {
        nameTaken(name).then(function (taken) {
          if (taken) return fail('That display name is taken. Try another.');
          return auth().createUserWithEmailAndPassword(email, password).then(function (cred) {
            try { localStorage.setItem('lb_has_account', '1'); } catch (e) {}
            return createProfile(cred.user, name).then(postAndRefresh, function (e) {
              // Account exists but the name was claimed in the meantime: ask for another.
              renderPanel(panel, ctx, 'name', authErrorMessage(e));
            });
          });
        }).catch(function (e) { fail(authErrorMessage(e)); });
      } else if (mode === 'signin') {
        auth().signInWithEmailAndPassword(email, password).then(function (cred) {
          try { localStorage.setItem('lb_has_account', '1'); } catch (e) {}
          return loadProfile(cred.user).then(function () {
            if (_profile) return postAndRefresh();
            renderInto(ctx.el, ctx.date, ctx.result);
          });
        }).catch(function (e) { fail(authErrorMessage(e)); });
      } else if (mode === 'reset') {
        auth().sendPasswordResetEmail(email).catch(function (e) {
          // Don't reveal whether an account exists for this email.
          if (e && e.code === 'auth/user-not-found') return;
          throw e;
        }).then(function () {
          btn.textContent = idleLabel;
          var ok = form.querySelector('.tl-lb-ok');
          ok.textContent = 'If there’s an account for that email, a reset link is on its way. Check your spam folder too.';
          ok.style.display = '';
        }).catch(function (e) { fail(authErrorMessage(e)); });
      }
    });
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
