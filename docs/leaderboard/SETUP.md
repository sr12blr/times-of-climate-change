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
5. Sidebar → **Build → Authentication** → **Get started** → **Sign-in method** → enable **Email/Password** (leave "Email link" off). Under **Settings → User actions**, keep **Email enumeration protection** on. This is used only by the daily leaderboard.
6. Firestore Database → **Rules** tab → replace with:
   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       function signedIn() { return request.auth != null; }

       // QR event rounds: open to anyone, keyed by name, first attempt only.
       match /events/{eventId}/puzzles/{p}/results/{playerId} {
         allow read: if true;
         allow create: if !(eventId in ['daily', 'climate-connections'])
           && !exists(/databases/$(database)/documents/events/$(eventId)/puzzles/$(p)/results/$(playerId));
         // no updates, no deletes — first attempt only, enforced server-side
       }

       // Daily leaderboard: signed-in players only, one result per account per puzzle,
       // posted under the account's own display name.
       match /events/daily/puzzles/{p}/results/{uid} {
         allow read: if true;
         allow create: if signedIn() && request.auth.uid == uid
           && request.resource.data.keys().hasOnly(['name', 'ms', 'mistakes', 'hints', 'adjustedMs', 'won', 'submittedAt'])
           && request.resource.data.name == get(/databases/$(database)/documents/users/$(uid)).data.displayName
           && request.resource.data.ms is int && request.resource.data.ms >= 0
           && request.resource.data.mistakes is int && request.resource.data.mistakes >= 0
           && request.resource.data.hints is int && request.resource.data.hints >= 0
           && request.resource.data.adjustedMs == request.resource.data.ms + request.resource.data.hints * 30000
           && request.resource.data.won is bool
           && request.resource.data.submittedAt == request.time;
       }

       // Climate Connections leaderboard (the 15 grid puzzles opened with ?cc=1):
       // name only, no account. The doc id is the name's key (lowercase letters and
       // digits), so each name posts once per puzzle; no updates or deletes.
       match /events/climate-connections/puzzles/{p}/results/{key} {
         allow read: if true;
         allow create: if request.resource.data.keys().hasOnly(['name', 'ms', 'mistakes', 'hints', 'adjustedMs', 'won', 'submittedAt'])
           && request.resource.data.name is string
           && request.resource.data.name.size() >= 2
           && request.resource.data.name.size() <= 24
           && key == request.resource.data.name.lower().replace('[^a-z0-9]', '')
           && key.size() >= 2
           && request.resource.data.ms is int && request.resource.data.ms >= 0
           && request.resource.data.mistakes is int && request.resource.data.mistakes >= 0
           && request.resource.data.hints is int && request.resource.data.hints >= 0
           && request.resource.data.adjustedMs == request.resource.data.ms + request.resource.data.hints * 30000
           && request.resource.data.won is bool
           && request.resource.data.submittedAt == request.time;
       }

       // Climate Connections play counters, shown on the grid tiles: ccPlays/{date} = { plays }.
       // Anyone can read; writes may only add exactly 1.
       match /ccPlays/{date} {
         allow read: if true;
         allow create: if request.resource.data.keys().hasOnly(['plays'])
           && request.resource.data.plays == 1;
         allow update: if request.resource.data.keys().hasOnly(['plays'])
           && request.resource.data.plays == resource.data.plays + 1;
       }

       // Private profile. Display name is permanent (no updates).
       match /users/{uid} {
         allow read: if signedIn() && request.auth.uid == uid;
         allow create: if signedIn() && request.auth.uid == uid
           && request.resource.data.keys().hasOnly(['displayName', 'nameKey', 'createdAt'])
           && request.resource.data.displayName is string
           && request.resource.data.displayName.size() >= 2
           && request.resource.data.displayName.size() <= 24
           && request.resource.data.nameKey == request.resource.data.displayName.lower().replace('[^a-z0-9]', '')
           && request.resource.data.nameKey.size() >= 2
           && getAfter(/databases/$(database)/documents/displayNames/$(request.resource.data.nameKey)).data.uid == uid;
       }

       // Public name registry: one account per display name.
       match /displayNames/{key} {
         allow read: if true;
         allow create: if signedIn()
           && request.resource.data.keys().hasOnly(['uid'])
           && request.resource.data.uid == request.auth.uid
           && getAfter(/databases/$(database)/documents/users/$(request.auth.uid)).data.nameKey == key;
       }
     }
   }
   ```
   Click **Publish**.
7. Commit & push. Once GitHub Pages redeploys, the leaderboard is live.

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
- `daily.js` — the always-on daily leaderboard on the live puzzle page. Requires an email + password account (Firebase Auth) to post; see the rules above. The same file also runs the Climate Connections leaderboard (`events/climate-connections/puzzles/{date}/results`) on the 15 grid puzzles when they're opened from `/climateconnections/` (URL has `?cc=1`). That board is name-only (no account) with a separate board per puzzle. The grid tiles show live play counts from `ccPlays/{date}`, which goes up by 1 when a player presses Start on a grid puzzle (once per browser).

## Notes / caveats

- Client-side timing: a player could in principle edit JS in DevTools to fake their time. Fine for a friendly event.
- Anyone with a QR URL can play; no auth. (The daily leaderboard does use accounts.)
- Daily leaderboard accounts: display names are unique and can't be changed (there's no update rule). To rename or remove someone, edit `users/{uid}` and `displayNames/{key}` in the Firestore console, and delete the account under Authentication → Users.
- One submission per `(name, puzzle)` — enforced both client-side (precheck) and server-side (Firestore rule). Replaying with the same name is silently rejected.
- The 3 puzzle archive pages must already exist at `docs/torchlight/archive/<YYMMDD>/`.
