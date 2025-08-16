#!/bin/bash
# Convert demo scripts to animated GIFs

echo "🎬 Converting demos to animated GIFs..."

# Check for dependencies
if ! command -v asciinema &> /dev/null; then
    echo "❌ asciinema not found. Install with: pip install asciinema"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ docker not found. Install Docker to convert to GIF"
    exit 1
fi

# Record each demo
for demo in *.sh; do
    if [[ "$demo" == "convert_to_gifs.sh" ]]; then
        continue
    fi
    
    name="${demo%.sh}"
    echo "Recording $name..."
    
    # Record to asciicast format
    asciinema rec -c "./$demo" "${name}.cast" --overwrite
    
    # Convert to GIF
    echo "Converting to GIF..."
    docker run --rm -v "$PWD:/data" asciinema/asciicast2gif \
        -w 80 -h 24 -t solarized-dark \
        "/data/${name}.cast" "/data/${name}.gif"
    
    echo "✅ Created ${name}.gif"
done

echo "
✨ All demos converted! GIF files created:
"
ls -lh *.gif

echo "
📝 Add to README.md like this:

![Natural Language Demo](demos/1_natural_language.gif)
"
