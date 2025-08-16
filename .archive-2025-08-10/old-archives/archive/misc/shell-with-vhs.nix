# Nix shell with VHS for creating demo materials
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nix-humanity-demo-shell";
  
  buildInputs = with pkgs; [
    # VHS for creating terminal GIFs
    vhs
    
    # Additional tools for demo creation
    asciinema
    imagemagick  # For converting SVG to PNG
    ffmpeg       # For video processing
    gifsicle     # For GIF optimization
    
    # Python environment
    python311
    python311Packages.rich
    python311Packages.textual
    
    # Terminal tools
    tmux
    ttyrec
  ];
  
  shellHook = ''
    echo "🎬 Demo creation environment loaded!"
    echo ""
    echo "Available tools:"
    echo "  • vhs - Create beautiful terminal GIFs"
    echo "  • asciinema - Record terminal sessions"
    echo "  • ffmpeg - Process videos"
    echo "  • imagemagick - Convert images"
    echo "  • gifsicle - Optimize GIFs"
    echo ""
    echo "Run: vhs demo-tui.tape"
  '';
}