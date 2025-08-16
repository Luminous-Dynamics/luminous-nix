# 📦 GitHub Repository Rename Instructions

## For Repository Owner (Tristan)

### Step 1: Rename on GitHub
1. Go to: https://github.com/Luminous-Dynamics/nix-for-humanity
2. Click **Settings** (gear icon)
3. In the **General** section at the top
4. Find **Repository name** field
5. Change from `nix-for-humanity` to `luminous-nix`
6. Click **Rename**

GitHub will automatically:
- Set up redirects from old URLs
- Update existing clones
- Preserve stars, watches, and forks

### Step 2: Update Local Repository
```bash
cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix

# Update the remote URL
git remote set-url origin https://github.com/Luminous-Dynamics/luminous-nix.git

# Verify the change
git remote -v

# Push the rename changes
git add -A
git commit -m "✨ feat: rename project to Luminous Nix

- Better aligns with consciousness-first philosophy
- Removes negative connotations of 'nix' (to reject)
- Illuminates rather than negates
- Fits within Luminous Dynamics ecosystem"

git push origin main
```

### Step 3: Update GitHub Description
In repository settings, update:
- **Description**: "✨ Natural language interface for NixOS - illuminating system management through consciousness-first design"
- **Website**: Update if applicable
- **Topics**: Add `luminous-nix`, `consciousness-first`, keep existing

### Step 4: Create GitHub Release
```bash
gh release create v1.0.0-luminous \
  --title "v1.0.0: Luminous Nix - A New Dawn" \
  --notes "## 🌟 Introducing Luminous Nix

Formerly 'Nix for Humanity', now reborn with a name that truly reflects our mission:
illuminating the path to NixOS mastery through natural language.

### Why the Rename?
- **Positive Energy**: 'Luminous' means bright, radiant, enlightening
- **Clear Mission**: We illuminate complexity, not negate it
- **No Confusion**: Avoids 'nix' as a verb meaning 'to reject'
- **Ecosystem Alignment**: Part of the Luminous Dynamics family

### For Existing Users
Run the migration script:
\`\`\`bash
./migrate-user-config.sh
\`\`\`

All functionality remains the same - just with a brighter name!"
```

### Step 5: Update Repository Topics
Add these topics in GitHub:
- `luminous-nix`
- `natural-language`
- `nixos`
- `consciousness-first`
- `accessibility`
- `ai-powered`

## For Contributors

### Update Your Fork
```bash
# If you have a fork, update its name too
gh repo rename luminous-nix

# Update your local remote
git remote set-url origin https://github.com/YOUR-USERNAME/luminous-nix.git
git remote set-url upstream https://github.com/Luminous-Dynamics/luminous-nix.git
```

### Update Any Scripts
Search for old references:
```bash
grep -r "nix-for-humanity" ~/
grep -r "NIX_HUMANITY" ~/
```

Update any found references to use:
- `luminous-nix` (repository/directory)
- `LUMINOUS_NIX_*` (environment variables)

## Verification Checklist

- [ ] Repository renamed on GitHub
- [ ] Local remote updated
- [ ] Changes pushed
- [ ] Release created
- [ ] README displays correctly
- [ ] CI/CD pipelines work (if any)
- [ ] Links in documentation updated
- [ ] Community notified

## Redirects

GitHub automatically handles redirects for:
- Repository URL: `github.com/Luminous-Dynamics/nix-for-humanity` → `luminous-nix`
- Git operations: Existing clones will continue to work
- Issues/PRs: All links preserved
- API calls: Redirected automatically

These redirects are permanent unless you create a new repository with the old name.

## Troubleshooting

### If git push fails:
```bash
# Force update the remote
git remote remove origin
git remote add origin https://github.com/Luminous-Dynamics/luminous-nix.git
git branch --set-upstream-to=origin/main main
git push
```

### If submodules exist:
```bash
# Update .gitmodules file
sed -i 's/nix-for-humanity/luminous-nix/g' .gitmodules
git add .gitmodules
git commit -m "chore: update submodule URLs"
```

### If GitHub Actions exist:
Update any workflow files in `.github/workflows/` that reference:
- The old repository name
- Old environment variables
- Old package names

---

*The light of understanding shines brighter with a name that reflects our mission!* ✨