#!/usr/bin/env bash
# Wrapper script to run Python with PortAudio support

export LD_LIBRARY_PATH="/nix/store/fhg78y7g4jikh01acs0bdb8qw9vvn1vm-portaudio-190700_20210406/lib:$LD_LIBRARY_PATH"
export PORTAUDIO_PATH="/nix/store/fhg78y7g4jikh01acs0bdb8qw9vvn1vm-portaudio-190700_20210406"

echo "🎤 Audio environment configured"
echo "   PortAudio: /nix/store/fhg78y7g4jikh01acs0bdb8qw9vvn1vm-portaudio-190700_20210406"
echo ""

# Run the command passed as arguments
if [ $# -eq 0 ]; then
    echo "Usage: ./run_with_audio.sh <command>"
    echo "Example: ./run_with_audio.sh python test_microphone.py"
    exit 1
fi

exec "$@"
