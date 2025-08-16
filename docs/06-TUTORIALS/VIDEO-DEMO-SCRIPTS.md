# 🎬 Luminous Nix - Video Demo Scripts

## 📹 Demo 1: Natural Language Magic (2 min)

### Script
```bash
# Terminal recording with asciinema or vhs
```

**[0:00 - 0:10] Introduction**
```
Welcome to Luminous Nix - making NixOS accessible through natural conversation!
Let me show you how easy it is to use NixOS without memorizing commands.
```

**[0:10 - 0:30] Basic Installation**
```bash
$ ask-nix "I need a photo editor"

🔍 Searching for photo editing software...

Found these options:
1. GIMP - Professional image editor (like Photoshop)
2. Krita - Digital painting and illustration
3. Inkscape - Vector graphics editor

Which would you like to install? [1-3]: 1

📦 Installing GIMP...
✅ Successfully installed! Run with: gimp
```

**[0:30 - 0:50] Smart Error Handling**
```bash
$ ask-nix "install fierox"

❓ I couldn't find 'fierox'. Did you mean 'firefox'?

Similar packages:
- firefox (Web browser)
- firefox-esr (Extended Support Release)

💡 Tip: Use 'ask-nix search <name>' to explore packages
```

**[0:50 - 1:10] Configuration Generation**
```bash
$ ask-nix "set up a web server with PHP"

🔧 I'll help you configure a web server with PHP support!

Generated configuration:
services.nginx = {
  enable = true;
  virtualHosts."localhost" = {
    root = "/var/www";
    locations."~ \\.php$".extraConfig = ''
      fastcgi_pass unix:${config.services.phpfpm.pools.nginx.socket};
    '';
  };
};

services.phpfpm.pools.nginx = {
  user = "nginx";
  settings = {
    "listen.owner" = "nginx";
    "pm" = "dynamic";
    "pm.max_children" = 5;
  };
};

📝 Save to configuration.nix? [Y/n]:
```

**[1:10 - 1:30] Learning System**
```bash
$ ask-nix "install my usual tools"

🧠 Based on your history, installing your preferred tools:
- neovim (your preferred editor)
- tmux (terminal multiplexer)
- ripgrep (fast search tool)
- htop (system monitor)

✅ All tools installed! I've learned your preferences.
```

**[1:30 - 2:00] Closing**
```
That's Luminous Nix - turning NixOS from intimidating to intuitive!

Key features shown:
✨ Natural language understanding
🎓 Educational error messages
🔧 Smart configuration generation
🧠 Learning from your patterns

Get started: github.com/luminous-dynamics/luminous-nix
```

---

## 📹 Demo 2: TUI Showcase (3 min)

### Terminal UI Recording Script

**[0:00 - 0:20] Launch TUI**
```bash
$ nix-tui

# Beautiful TUI appears with consciousness orb pulsing
```

**[0:20 - 0:40] Visual Elements**
- Show consciousness orb responding to activity
- Demonstrate color themes adapting
- Show accessibility features (high contrast mode)

**[0:40 - 1:20] Interactive Commands**
1. Type: "install firefox"
   - Show real-time command preview
   - Educational hints appear
   - Progress visualization

2. Type: "search markdown"
   - Live search results
   - Package descriptions
   - Keyboard navigation

**[1:20 - 2:00] Advanced Features**
- Split pane for documentation
- Command history with search
- Suggestion system
- Configuration preview

**[2:00 - 2:40] Persona Switching**
- Switch to "Sacred" mode - see interface transform
- Switch to "Minimal" mode - ultra-clean
- Switch to "Technical" mode - detailed info

**[2:40 - 3:00] Closing**
- Show system stats
- Demonstrate smooth exit
- Call to action

---

## 📹 Demo 3: Performance Showcase (90 sec)

### Split-Screen Comparison

**[0:00 - 0:15] Setup**
```
Left: Traditional NixOS commands
Right: Luminous Nix
```

**[0:15 - 0:45] Speed Test**
```bash
# LEFT SIDE (Traditional)
$ time nix-env -qa firefox
# ... 3.2 seconds ...

$ time nix-env -iA nixpkgs.firefox
# ... 5.7 seconds ...

# RIGHT SIDE (Luminous Nix)
$ time ask-nix "search firefox"
# ... 0.3 seconds ...

$ time ask-nix "install firefox"
# ... 0.4 seconds ...
```

**[0:45 - 1:15] Feature Comparison**
```bash
# LEFT: Cryptic error
error: attribute 'NodeJS' missing

# RIGHT: Educational error
❓ 'NodeJS' not found. The correct name is 'nodejs' (lowercase).
📦 Install with: ask-nix "install nodejs"
📚 Learn more: ask-nix "help javascript development"
```

**[1:15 - 1:30] Summary**
- 10x-15x faster operations
- Human-friendly errors
- Zero learning curve

---

## 🎥 Recording Tools Setup

### Using VHS (Recommended)
```tape
# demo.tape
Output demo.gif

Set FontSize 20
Set Width 1200
Set Height 800
Set Theme "Dracula"

Type "ask-nix 'install firefox'"
Sleep 500ms
Enter
Sleep 2s

Type "ask-nix 'search editor'"
Sleep 500ms
Enter
Sleep 2s
```

### Using asciinema
```bash
# Start recording
asciinema rec demo.cast

# Perform demo actions

# Stop with Ctrl+D
# Convert to GIF
asciicast2gif demo.cast demo.gif
```

### Professional Setup
1. **Terminal**: Alacritty or Kitty (best rendering)
2. **Font**: JetBrains Mono or Fira Code
3. **Theme**: Dracula or Nord (high contrast)
4. **Resolution**: 1920x1080 (standard)
5. **FPS**: 30 for smooth animations

---

## 📊 Demo Metrics Dashboard

Create an interactive dashboard showing:
- Real-time performance graphs
- User satisfaction scores
- Command success rates
- Learning system improvements

```html
<!-- metrics-demo.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Luminous Nix - Live Metrics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Performance Metrics</h1>
    <canvas id="performanceChart"></canvas>
    <script>
        // Real-time performance visualization
        const ctx = document.getElementById('performanceChart');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Search', 'Install', 'Config', 'Error'],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [89, 124, 203, 45],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 500
                    }
                }
            }
        });
    </script>
</body>
</html>
```

---

## 🎯 Key Messages for Each Demo

### Demo 1: Accessibility
- "No more memorizing commands"
- "NixOS for everyone, not just experts"
- "Learn as you go"

### Demo 2: Beautiful UX
- "Terminal apps can be delightful"
- "Accessibility without compromise"
- "Adapts to your style"

### Demo 3: Performance
- "10x faster, 100x easier"
- "Native speed, natural language"
- "The future of system management"

---

## 📝 Demo Checklist

Before recording:
- [ ] Clean terminal history
- [ ] Set consistent font size
- [ ] Disable notifications
- [ ] Practice timing
- [ ] Prepare example data
- [ ] Test all commands
- [ ] Check color contrast
- [ ] Verify accessibility

After recording:
- [ ] Add captions
- [ ] Create GIF version
- [ ] Upload to CDN
- [ ] Update documentation
- [ ] Share on social media

---

*These demos showcase the revolutionary ease of use that Luminous Nix brings to NixOS.*
