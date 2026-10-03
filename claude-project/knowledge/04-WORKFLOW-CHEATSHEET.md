# Commands to give the owner

Replace `<plugin>` and `<X.Y.Z>`. Run from the repo root (a clone of https://github.com/Naxasware/Naxasware-Plugins).

## New plugin (from the zip you produced)
```bash
git checkout main && git pull
unzip -o ~/Downloads/<plugin>.zip          # creates plugins/<plugin>/
chmod +x plugins/<plugin>/ci-smoke.sh 2>/dev/null || true
python3 scripts/validate_all_plugins.py .  # expect: No errors.
git add plugins/<plugin>
git commit -m "feat(<plugin>): initial release"
git push
```
(Use a branch + PR instead if `main` is protected: `git checkout -b add-<plugin>`, push, open a PR.)
After the push: CI validates, and the Sync workflow updates `marketplace.json`, the README table and `plugin.json` normalization by itself (also on PRs from branches in this repo).

## Publish
```bash
git pull                                    # picks up the bot's sync commit
git tag <plugin>-v<X.Y.Z>
git push origin <plugin>-v<X.Y.Z>
```
The tag version must equal `version` in `plugins/<plugin>/.claude-plugin/plugin.json`.

## Update an existing plugin
```bash
git checkout main && git pull
rm -rf plugins/<plugin>                     # the new zip is the whole folder
unzip -o ~/Downloads/<plugin>.zip
python3 scripts/validate_all_plugins.py .
git add -A plugins/<plugin>
git commit -m "feat(<plugin>): <what changed>"   # or fix(...)
git push
# then tag as above with the bumped version
```

## Undo a bad tag
```bash
git push --delete origin <plugin>-v<X.Y.Z> && git tag -d <plugin>-v<X.Y.Z>
```

## Commit types
`feat(<plugin>)` new capability · `fix(<plugin>)` correction · `docs` · `chore`.

## Windows
Use Git Bash or WSL for the shell commands. `.gitattributes` forces LF line endings so `ci-smoke.sh` won't break.
