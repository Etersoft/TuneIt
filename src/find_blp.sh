#!/usr/bin/bash
find . -type f -name "*.blp" | sed "s|^\./$1/||"