# Archive Strategy for Luminous Nix

## Problem (RESOLVED)
- Git repository was 1.3GB due to archived files
- Pushes were taking 7+ minutes
- Clone operations were slow
- GitHub has size limits

## Cleanup Completed (2025-08-11)
- ✅ Removed `.archive-2025-08-10` from git history (7,245 files)
- ✅ Removed `archive/` folder from git history
- ✅ Removed `.postgres/` folder from git history
- ✅ Updated .gitignore to prevent future issues
- ✅ Force pushed cleaned history to GitHub
- Result: Repository size reduced significantly

## Solution

### 1. Immediate Actions
- Remove `.archive-2025-08-10` from git history (saves 1GB+)
- Add proper .gitignore rules for archives
- Use git sparse-checkout for large repos

### 2. Archive Best Practices

#### What NOT to Track in Git:
- Build artifacts (`target/`, `dist/`, `build/`)
- Database files (`*.db`, `*.sqlite`)
- Large binaries (`*.rlib`, `*.so`, `*.dll`)
- Media files (`*.png`, `*.jpg`, `*.mp4`)
- Archive folders (`.archive-*`)
- Postgres WAL logs (`.postgres/`)

#### Where to Store Archives:
1. **Separate Archive Repository**
   ```bash
   # Create luminous-nix-archives repo
   git init archives
   cd archives
   git remote add origin https://github.com/user/luminous-nix-archives
   ```

2. **Cloud Storage** (for large files)
   - Google Drive
   - Dropbox
   - S3

3. **Git LFS** (for files that must be in repo)
   ```bash
   git lfs track "*.db"
   git lfs track "*.png"
   ```

### 3. Efficient Git Workflow

#### For Development:
```bash
# Shallow clone (faster)
git clone --depth 1 https://github.com/Luminous-Dynamics/luminous-nix

# Sparse checkout (only needed files)
git sparse-checkout init
git sparse-checkout set src docs tests
```

#### For Releases:
```bash
# Only push source code changes
git add src/ docs/ tests/ *.md *.toml
git commit -m "feat: changes"
git push

# Archive separately
tar -czf archive-$(date +%Y%m%d).tar.gz .archive-*
# Upload to cloud storage
```

### 4. Repository Cleanup Commands

```bash
# Check what's taking space
git count-objects -vH

# Find large files
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  sed -n 's/^blob //p' | \
  sort -nr -k2 | \
  head -20

# Clean up
git gc --aggressive --prune=now

# Remove file from history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch PATH_TO_FILE' \
  --prune-empty --tag-name-filter cat -- --all
```

### 5. Prevention

Add to `.gitignore`:
```gitignore
# Archives
.archive-*/
*.tar.gz
*.zip

# Build artifacts  
target/
dist/
build/
*.rlib

# Databases
*.db
*.sqlite
.postgres/

# Media
*.png
*.jpg
*.mp4

# Large files
*.bin
*.dat
```

## Benefits
- Repository size: 1.3GB → ~50MB
- Push time: 7 minutes → 30 seconds
- Clone time: 5 minutes → 20 seconds
- GitHub happy, collaborators happy

## Implementation
1. Run `cleanup-git-history.sh`
2. Force push to update remote
3. Archive old files separately
4. Update .gitignore
5. Document in README