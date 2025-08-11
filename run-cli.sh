#!/bin/bash
source .venv/bin/activate
export PYTHONPATH="${PWD}/src:$PYTHONPATH"
python -m nix_humanity.interfaces.cli "$@"
