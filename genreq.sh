#!/bin/bash
pip-compile --resolver=backtracking --upgrade --allow-unsafe --no-header  --unsafe-package n/a --output-file requirements.txt
pip-compile --extra test --resolver=backtracking --upgrade --allow-unsafe --no-header  --unsafe-package n/a --output-file requirements-test.txt

