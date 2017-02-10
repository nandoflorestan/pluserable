#! /bin/sh

PACKAGE=../pluserable
API=source/api

cd docs && \
rm -r $API

# Generate the API docs automatically
sphinx-apidoc -H "pluserable API" --separate -o $API $PACKAGE && \
make html && \
cd - > /dev/null && \
echo "To read the local docs, type:  xdg-open docs/_build/html/index.html"
