# Contributing to CascadeRisk-SL

How the four of us work together in this repository. Read this before your first commit.

## Team and components

| Component | Folder | Owner | Reviewer |
|---|---|---|---|
| C1 Ingestion and quality | `c1_ingestion/` | Pabasara | Lokitha |
| C2 Flood risk prediction | `c2_prediction/` | Dhatshikha | Pabasara |
| C3 Exposure mapping | `c3_exposure/` | Inzith | Dhatshikha |
| C4 Access and routing | `c4_routing/` | Lokitha | Inzith |
| API and dashboard | `api/`, `dashboard/` | Inzith and Lokitha | each other |

---

## 1. One-time setup

1. Install **Git for Windows** from https://git-scm.com (keep the default options).
2. Create a GitHub account and send your username to be added as a collaborator.
3. Open **Git Bash** and set your name and email (use your GitHub email):

   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```

4. Clone the project:

   ```bash
   git clone https://github.com/<owner>/CascadeRisk-Project.git
   cd CascadeRisk-Project
   ```

5. Install **VS Code** (recommended) to see Git changes visually.

---

## 2. Key terms

- **Repository (repo):** the project folder with its full history.
- **Commit:** a saved snapshot of your changes, with a message.
- **Branch:** your own separate line of work.
- **Push / pull:** send your commits to GitHub / get everyone else's.
- **Pull request (PR):** a request to merge your branch into `dev`, reviewed first.

---

## 3. Branches

```
main ──●────────────────●──────────────●──>  stable: SRS, prototype, final
        \              /              /
dev ─────●──●──●──●──●──●──●──●──●──●──>  everyone merges here
          \  /  \  /  \  /
           c1/...  c2/...  c3/...  c4/...

data ──●──●──●──●──●──>  hourly gauge CSVs (GitHub Actions only)
```

| Branch | Purpose | Who writes to it |
|---|---|---|
| `main` | Stable, working version. Updated only at milestones. | Merged from `dev` when the team agrees |
| `dev` | Integration branch (default branch) | Pull requests only |
| `c1/...` `c2/...` `c3/...` `c4/...` | One branch per task, e.g. `c1/validation`, `c4/road-graph` | The component owner |
| `api/...` `dashboard/...` | API and web map work | Inzith and Lokitha |
| `data` | Hourly collected gauge CSVs | GitHub Actions bot only |

**Branch names:** `<component>/<short-task>` in lowercase with hyphens, e.g. `c2/lightgbm-model`.

**Milestone tags on `main`:** `v0.1-srs`, `v0.2-prototype`, `v1.0-final`.

---

## 4. Daily workflow

**Start of the day: get the latest code**

```bash
git checkout dev
git pull
```

**Start a new task on its own branch**

```bash
git checkout -b c1/validation
```

**Check what changed**

```bash
git status
```

**Save a snapshot**

```bash
git add c1_ingestion/validate.py
git commit -m "C1: add range check for water levels"
```

**Upload your branch**

```bash
git push -u origin c1/validation
```

**Open a pull request on GitHub**

1. Open a pull request from your branch into `dev`.
2. Your reviewer checks it and approves it.
3. Merge it, then delete the branch.

---

## 5. Team rules

1. **Never work directly on `main` or `dev`.** Always create a branch first.
2. **Pull `dev` before you start work,** every day.
3. **Commit small and often,** one change per commit.
4. **Write clear messages** starting with the component, e.g. `C3: add GN division overlay`. Not `update` or `fixed`.
5. **Use `git add <file>`** instead of `git add .` until you are confident.
6. **Stay in your own folder.** Tell the group before changing shared files: `requirements.txt`, `db/schema.sql`, `api/`, `.github/`.
7. **Never commit secrets or large data:** passwords, `.env`, API keys, raw CSVs, large GIS or raster files.
8. **Every pull request needs one approval** from your reviewer (see the table at the top).
9. **Keep branches short-lived:** merge within a few days.
10. **Make sure your code runs** before you push. Do not break `dev`.
11. **Tell the group** when you merge something others depend on.
12. **Never use `git push --force`** on `dev` or `main`.

---

## 6. Fixing common problems

**"Your local changes would be overwritten"**

```bash
git stash
git pull
git stash pop
```

**Merge conflict**

Git marks the conflicting part of the file:

```
<<<<<<< HEAD
your version
=======
their version
>>>>>>> dev
```

1. Keep the correct lines and delete the marker lines.
2. Then save the result:

   ```bash
   git add <file>
   git commit
   ```

3. If unsure, ask the person who wrote the other version.

**Change the last commit message (not pushed yet)**

```bash
git commit --amend -m "new message"
```

**Discard changes to a file (not committed yet)**

```bash
git restore <file>
```

**Committed on the wrong branch:** stop, and ask the group before trying to fix it.

---

## 7. Quick reference

| I want to… | Command |
|---|---|
| See what changed | `git status` |
| Get the latest code | `git checkout dev`, then `git pull` |
| Start a task | `git checkout -b c3/gn-overlay` |
| Save work | `git add <file>`, then `git commit -m "C3: ..."` |
| Upload work | `git push` |
| See history | `git log --oneline` |
| Switch branch | `git checkout <branch>` |
| List branches | `git branch -a` |

---

## 8. Folder structure

```
CascadeRisk-Project/
├── c1_ingestion/        collectors, validation, reconciliation, loader
├── c2_prediction/       features, models, evaluation
├── c3_exposure/         flood zones, GN overlay
├── c4_routing/          road graph, risk-weighted routing
├── api/                 FastAPI service
├── dashboard/           web map
├── db/schema.sql        database tables
├── .github/workflows/   scheduled jobs
├── requirements.txt
├── .gitignore
├── CONTRIBUTING.md
└── README.md
```