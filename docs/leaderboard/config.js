// Torchlight Leaderboard — event configuration
// Edit this file per event. Re-deploy (or just commit) to push changes.
//
// SETUP: see docs/leaderboard/SETUP.md for Firebase project setup.
// Paste the firebaseConfig values from the Firebase console into the `firebase` block below.

window.LB_CONFIG = {
  // Bump this per event so each event gets a separate set of leaderboards in Firestore.
  eventId: "event-2026-05-21-live",

  // The puzzle archive dates for this event, in YYMMDD form.
  // These must already exist under docs/torchlight/archive/<date>/index.html
  // Round 1: Apr 27 (Nursery rhymes)
  // Round 2: May 20 (Personal care brands)
  // Round 3: May 12 (AI)
  // Round 4: Apr 16 (Quick commerce)
  puzzles: ["260427", "260520", "260512", "260416"],

  // Paste your Firebase project's web-app config here.
  // Get it from: Firebase console -> Project Settings -> Your apps -> </> Web app
  firebase: {
    apiKey: "AIzaSyBOus4XY3mDs73KcONWaS2lrWkwo2TRThI",
    authDomain: "torchlight-leaderboard-may-21.firebaseapp.com",
    projectId: "torchlight-leaderboard-may-21",
    storageBucket: "torchlight-leaderboard-may-21.firebasestorage.app",
    messagingSenderId: "354962167324",
    appId: "1:354962167324:web:1aca4d7967ea2b170231d9"
  }
};
