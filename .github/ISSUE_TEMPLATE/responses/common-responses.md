# Common Response Templates

## Installation Issues

### "Command not found"
```
Thanks for trying Nix for Humanity! It looks like the binary isn't in your PATH. Try:

1. Run directly: `./bin/ask-nix "help"`
2. Or add to PATH: `export PATH=$PATH:$(pwd)/bin`

Let me know if you still have issues!
```

### "Permission denied"
```
This usually means the script needs execute permissions:

```bash
chmod +x bin/ask-nix
./bin/ask-nix "help"
```

Hope this helps!
```

## Feature Requests

### "When will TUI/Voice be available?"
```
Great question! TUI and Voice are already implemented and tested - we just disabled them for v1.0.0 stability. They'll be enabled in v1.1 (targeting 2-4 weeks). 

Want to be notified? Watch this repo for releases!
```

### "Can it do X?"
```
Thanks for the suggestion! Nix for Humanity is designed to learn and grow. Could you:

1. Give an example of what you'd like to say?
2. What should happen when you say it?

This helps us understand your workflow better!
```

## Bug Reports

### Generic Bug Response
```
Thanks for reporting this! To help debug:

1. What command did you run?
2. What did you expect to happen?
3. What actually happened?
4. Can you share any error messages?

Running `ask-nix --diagnose` might also provide helpful info!
```