# Demo Recording Instructions

## Prerequisites
- asciinema installed: `nix-env -iA nixpkgs.asciinema`
- svg-term for GIF conversion: `npm install -g svg-term`

## Recording Steps

1. **TUI Demo**:
   ```bash
   asciinema rec demos/v1.1/tui_basic.cast
   python3 demos/v1.1/tui_basic_demo.py
   # Ctrl+D to stop
   svg-term --in demos/v1.1/tui_basic.cast --out demos/v1.1/tui_basic.gif
   ```

2. **Voice Demo**:
   ```bash
   # Record audio separately, then create visualization
   python3 demos/v1.1/voice_demo.py
   ```

3. **Performance Demo**:
   ```bash
   asciinema rec demos/v1.1/performance.cast
   python3 demos/v1.1/performance_demo.py
   ```

## Post-Processing
- Optimize GIFs: `gifsicle -O3 input.gif > output.gif`
- Create thumbnails: `convert input.gif[0] thumbnail.png`
