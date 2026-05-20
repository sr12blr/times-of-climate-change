// Torchlight Leaderboard — runtime injected into puzzle pages when ?lb=1 is present.
// Depends on: window.LB_CONFIG (config.js), firebase compat SDK (loaded by the same conditional loader).

(function () {
  if (!window.LB_CONFIG) {
    console.warn('[lb] LB_CONFIG missing — leaderboard disabled');
    return;
  }
  var params = new URLSearchParams(location.search);
  if (!params.has('lb')) return;

  var puzzleDate = params.get('p') || '';
  var name = (localStorage.getItem('lb_name') || '').trim();
  var sessionId = localStorage.getItem('lb_session_id') || '';

  if (!name || !puzzleDate) {
    console.warn('[lb] missing name or puzzle date — leaderboard disabled');
    return;
  }

  // Init Firebase (compat global API)
  function initFirebase() {
    if (window.firebase && !window.firebase.apps.length) {
      window.firebase.initializeApp(window.LB_CONFIG.firebase);
    }
  }

  function nameSlug(s) {
    return s.toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 40);
  }

  function rootPath() {
    // Puzzles live at /torchlight/archive/<date>/, so 3 levels up to site root.
    var p = location.pathname;
    if (p.indexOf('/torchlight/archive/') !== -1) return '../../../';
    return '/';
  }

  // Banner so the player knows leaderboard mode is active
  function injectBanner() {
    var bar = document.createElement('div');
    bar.style.cssText = 'background:#2C5F4A;color:#fff;padding:8px 12px;text-align:center;font-family:"Nunito Sans",sans-serif;font-size:14px;font-weight:600;position:sticky;top:0;z-index:9999';
    bar.textContent = '🏁 Playing for the leaderboard as ' + name;
    document.body.insertBefore(bar, document.body.firstChild);
  }

  function submit(won, ms, mistakes) {
    initFirebase();
    var db = window.firebase.firestore();
    var slug = nameSlug(name);
    var ref = db
      .collection('events').doc(window.LB_CONFIG.eventId)
      .collection('puzzles').doc(puzzleDate)
      .collection('results').doc(slug);

    return ref.get().then(function (snap) {
      if (snap.exists) {
        console.log('[lb] already submitted for this puzzle — first attempt counts');
        return;
      }
      return ref.set({
        name: name,
        ms: ms || 0,
        mistakes: typeof mistakes === 'number' ? mistakes : 0,
        won: !!won,
        sessionId: sessionId,
        submittedAt: window.firebase.firestore.FieldValue.serverTimestamp()
      });
    }).catch(function (e) {
      console.error('[lb] submit failed', e);
    });
  }

  window.LB_RUNTIME = {
    onSolve: function (won, ms, mistakes, date) {
      var p = new Promise(function (resolve) {
        submit(won, ms, mistakes).then(resolve, resolve);
      });
      // Give Firestore a beat, then redirect to the done page
      setTimeout(function () {
        p.then(function () {
          var url = rootPath() + 'leaderboard/done/?p=' + encodeURIComponent(puzzleDate)
            + '&ms=' + (ms || 0) + '&m=' + (mistakes || 0) + '&won=' + (won ? 1 : 0);
          location.href = url;
        });
      }, 1500);
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectBanner);
  } else {
    injectBanner();
  }
})();
