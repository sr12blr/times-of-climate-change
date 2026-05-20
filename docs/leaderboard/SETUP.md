# Torchlight Leaderboard — Setup

A QR-driven, live-event leaderboard for Torchlight. Players scan a QR, enter their name once, play a puzzle; their time goes to Firestore; the host projects the leaderboard on the big screen. Repeat for each round.

## One-time: Firebase setup

1. Go to https://console.firebase.google.com and click **Add project**.
   - Name it anything (e.g. `torchlight-leaderboard`).
   - You can **disable Google Analytics** — not needed.
2. In the project, sidebar → **Build → Firestore Database** → **Create database**.
   - Pick **Start in test mode** (we'll lock it down in step 5).
   - Pick a region close to you (e.g. `us-central1` or `asia-south1`).
3. Sidebar gear icon → **Project settings** → scroll to **Your apps** → click the **`</>`** (Web) icon.
   - Register the app with any nickname (e.g. `leaderboard`).
   - You do NOT need Firebase Hosting.
   - You'll see a `const firebaseConfig = { apiKey: "...", ... }` snippet. Copy the values inside the braces.
4. Open [`docs/leaderboard/config.js`](./config.js) and paste each value into the matching field. Set `eventId` to something unique (e.g. `event-2026-05-20`). Update `puzzles` to the 3 archive dates (YYMMDD) you want to use.
5. Firestore Database → **Rules** tab → replace with:
   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /events/{eventId}/puzzles/{p}/results/{playerId} {
         allow read: if true;
         allow create: if !exists(/databases/$(database)/documents/events/$(eventId)/puzzles/$(p)/results/$(playerId));
         // no updates, no deletes — first attempt only, enforced server-side
       }
     }
   }
   ```
   Click **Publish**.
6. Commit & push. Once GitHub Pages redeploys, the leaderboard is live.

## Running an event

For each of the 3 rounds:

1. **Host:** open `https://timesofclimatechange.com/leaderboard/` on the projector. Pick the round from the dropdown. The QR is now showing.
2. **Players:** scan QR → enter name (round 1 only — name persists) → play the puzzle.
3. **Host:** when everyone's done, click "View leaderboard →" (or open `/leaderboard/results/?p=<date>` in a separate tab). Project that.
4. Move on to the next round (pick the next puzzle in the dropdown on the QR page).

## Files

- `config.js` — event config + Firebase keys (you edit this).
- `index.html` — host QR generator.
- `r/index.html` — player round entry (name form).
- `done/index.html` — post-solve "wait for next round" screen.
- `results/index.html` — host's live leaderboard view.
- `lb-runtime.js` — injected into puzzle pages when `?lb=1` is present; submits time on solve.

## Notes / caveats

- Client-side timing: a player could in principle edit JS in DevTools to fake their time. Fine for a friendly event.
- Anyone with a QR URL can play; no auth.
- One submission per `(name, puzzle)` — enforced both client-side (precheck) and server-side (Firestore rule). Replaying with the same name is silently rejected.
- The 3 puzzle archive pages must already exist at `docs/torchlight/archive/<YYMMDD>/`.
