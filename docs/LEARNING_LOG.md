# ProsotaPMO — Plain English Learning Log

This file explains, in simple everyday language, what has been done on this project and in what order. It's written for Maro (or anyone else) to read back later and understand how the app was actually built, step by step — no technical jargon assumed.

`PROJECT_STATE.md` and `ARCHITECTURE.md` are the technical reference docs for Claude. This file is the human story version.

Updated at the end of every working session.

---

## Session 1 — 2026-06-30: Turning the idea into a real project

Before this session, ProsotaPMO only existed as one big demo webpage (a "prototype") that showed what the finished product should look like and do, plus a business case document explaining why it's worth building. Nothing was set up as an actual, real piece of software yet.

Steps taken:

1. **Organised the project into folders.** Created a proper structure: one folder for the backend (the "engine" that stores and manages data), one for the frontend (what users actually see and click on in their browser), one for documentation, and one for infrastructure (cloud setup, later).
2. **Saved the reference materials.** Copied the original demo webpage and the business case/scope documents into the project so they're always available to check against.
3. **Built the "engine" (backend) skeleton.** Set up the technology that will run behind the scenes — a Python-based web service (FastAPI) — and defined the database tables it needs: organisations, projects, time periods, activities (schedule tasks), risks, cost elements, and issues/changes/decisions. Confirmed it actually runs on the computer and can talk to a real database (PostgreSQL).
4. **Chose the database driver.** Had to switch to a different technical library (psycopg3) than originally planned, because the first choice didn't support the Python version installed. Small technical detour, no impact on the product.
5. **Tried Docker, hit a wall.** Docker (a tool for running software in standardised "containers") couldn't download what it needed on this machine, so local development continues without it for now — not a blocker, just a workaround.

End of session 1: the basic skeleton existed and ran, but there were no real features yet — just the foundation.

---

## Session 2 — 2026-06-30 (continued): Building the first real features

1. **Built full CRUD for Activities and Risks.** "CRUD" means Create, Read, Update, Delete — the basic ability to add, view, edit, and remove records. This was the first time the app could actually store and manage real schedule activities and risks, with automated tests proving it works correctly.
2. **Built the "linking" feature.** This is one of the app's special ideas — the ability to connect any record to any other record (e.g. "this risk causes a delay in this activity"). Built and tested that this works in both directions.
3. **Improved Cost Elements.** Added the ability to track costs either as a fixed amount or as a percentage-based calculation.
4. **Built full CRUD for Cost Elements and Issues/Changes/Decisions ("ICD").** Same idea as Activities/Risks — full add/view/edit/delete, fully tested.
5. **Set up automatic checks (CI).** Configured GitHub to automatically run all the tests every time code is pushed, so mistakes get caught early instead of being discovered later.

End of session 2: the backend could fully manage Activities, Risks, Cost Elements, and Issues/Changes/Decisions, with the cross-linking feature working and everything automatically tested.

---

## Session 3 — 2026-07-01: Logging in, and the first screen users see

1. **Added real login (Auth0).** Before this, there was no concept of "users" — anyone could do anything. Now the app requires a real login through Auth0 (a login/security service), so every action is tied to a real, verified person.
2. **Started the frontend (the part users actually see).** Set up the visual side of the app using React — the technology that will render all the buttons, tables, and screens.
3. **Built the Project Selector screen.** This is the very first screen a user sees after logging in — it lists their real projects (pulled from the backend, not fake demo data anymore) and lets them create a new one or pick an existing one to work in.
4. **Built the basic app layout.** Added the sidebar menu listing all 8 planned sections of the app (Dashboard, Scheduling, Risk Register, Cost Plan, ICD Tracker, File Manager, Period Manager, Export Center), even though most of them don't have real screens behind them yet.
5. **Connected frontend and backend.** Made sure the two sides could talk to each other securely (handling a browser security rule called CORS), and made sure that the first time someone logs in, the system automatically creates their organisation and user record behind the scenes.
6. **Added Projects, Periods, and "who am I" backend features**, with tests, to support the above.

End of session 3: a real person can log in, see their real projects, create a new one, and land inside the app shell with a working menu. No individual module screens (like Risk Register) are built yet — that's next.

Checked back in at the start of this session (still 2026-07-01): confirmed all 71 backend automated tests still pass and nothing was left uncommitted. Created this log file so progress stays understandable in plain language going forward.

---

## Session 4 — 2026-07-01 (continued): The first real working screen — Risk Register

1. **Built the Risk Register screen.** This is the first module (out of the 8 planned sections) with a real, working screen instead of a "Coming soon" placeholder. Users can now see a table of risks, add a new one, edit an existing one, or delete one — all of it actually saving to the real backend, not fake demo data.
2. **Demonstrated the "linking" feature on screen for the first time.** Each risk can now be expanded to show and manage connections to other risks (e.g. "this risk causes a delay in that one"). This is only risk-to-risk for now, because the other modules (like Activities or Cost Elements) don't have their own screens yet to pick from — but it proves the underlying linking system works end-to-end, not just in the backend.
3. **Added a small temporary workaround for "periods".** Risks always belong to a specific reporting period (e.g. "Period 1", "Period 2"), but the real Period Manager screen doesn't exist yet. So for now, the app quietly creates a default period automatically if a project doesn't have one yet, just so the Risk Register isn't blocked. This is a stopgap, not the finished feature.
4. **Checked the work carefully before calling it done.** Ran a type-checking tool to catch code mistakes before they'd show up as bugs — confirmed the new code introduced zero new problems (a handful of unrelated pre-existing issues were double-checked and confirmed to already exist before this session's changes, using `git stash` to temporarily "hide" the new work and re-test). Started both the backend and frontend up and confirmed they run without errors.
5. **Hit a real limit: couldn't click through it myself.** The app requires a real login (through Auth0) before you can reach the Risk Register screen, and that login needs real credentials that only the founder has. So while everything technically checks out (no errors, servers running fine), the actual "click Add, type a risk, see it appear" moment still needs to be done by a human in a real browser at least once, to be fully sure it behaves correctly.

End of session 4: Risk Register is built and technically verified, but not yet clicked-through by a human. Nothing has been saved to git yet — that happens after it's confirmed working.

---

## Session 5 — 2026-07-01 (continued): A real bug, found by actually trying it

Maro tried the Risk Register in a real browser as suggested, and hit an error: "Failed to create project." This turned out to be a genuine bug, and a good example of why the "click through it yourself" step matters — all the automated checks in Session 4 had passed, but they couldn't have caught this.

1. **What actually broke.** The backend uses a database driver (something that lets the Python code talk to PostgreSQL) that, on Windows specifically, needs a particular kind of "event loop" (the underlying machinery that lets the program do several things at once) called a `SelectorEventLoop`. Windows normally defaults to a different one. The automated tests already had a workaround for this, but the real running server didn't — and nobody had noticed, because every check so far had only touched a trivial "are you alive?" endpoint that doesn't use the database at all. The moment a real feature tried to write to the database, it broke.
2. **How it was found.** By reading the backend's own error log after the failure — the real cause was clearly written there, several layers down in a technical stack trace, even though the app only showed the user a generic "Failed to create project" message.
3. **How it was fixed.** Added a small new file, `backend/run.py`, whose only job is to tell Windows to use the correct event loop *before* the server starts up. From now on, the backend should be started with `python run.py` instead of the raw `uvicorn` command.
4. **Checked before declaring it fixed.** Ran a direct, isolated database query using the same fix to prove the connection genuinely worked, before asking Maro to try again in the browser rather than just assuming it was fixed.
5. **Confirmed working, then committed.** Maro retried creating a project in the real browser and confirmed it worked. Only then were the Risk Register feature and this bug fix saved to git together.

End of session 5: Risk Register works end-to-end, confirmed by an actual human clicking through it, not just automated checks. This is now the standing rule for every future session too: build it, check what can be checked automatically, but never mark something "done" or commit it until a human has actually confirmed the real thing works.

---

## What's next (in plain terms)

Next up is the Cost Plan screen, following the same approach: build it, verify what can be verified automatically, then have Maro click through it for real before committing.
