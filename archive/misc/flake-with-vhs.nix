# Alternative: Add VHS to your flake.nix devShell
# This snippet shows how to add VHS to an existing flake

{
  # In your flake.nix, add vhs to the devShell:
  
  devShells.default = pkgs.mkShell {
    buildInputs = with pkgs; [
      # Existing dependencies...
      python311
      poetry
      
      # Demo creation tools
      vhs              # Terminal GIF recorder
      asciinema        # Terminal session recorder
      imagemagick      # Image conversion
      ffmpeg-full      # Video processing
      gifsicle         # GIF optimization
      
      # Optional: More demo tools
      termtosvg        # Terminal to SVG
      peek             # Simple screen recorder
    ];
    
    shellHook = ''
      echo "🎬 VHS and demo tools available!"
      echo "Create demos with: vhs demo-tui.tape"
    '';
  };
}