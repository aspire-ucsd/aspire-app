#!/bin/bash

#Script for automatically building a vue.js app and transfering the files to FastAPI on app startup (DEV Only)
set -e

export NODE_PATH=/usr/local/lib/node_modules

cd /app/vue_dev

node --version
npm --version

echo "Vue.js: Installing Dependencies"
npm install
echo "Vue.js: Building App"
npm run build

STATIC_DIR=/app/app/static
INDEX_DIR=/app/app/app/templates/index.html
TEMPLATES_DIR=/app/app/app/templates

echo "Vue.js: Clearing Static Files"

rm -rf $STATIC_DIR
mkdir -p $STATIC_DIR

echo "Vue.js: Transfering Static Files"

mv /app/vue_dev/dist/assets $STATIC_DIR
# mv /app/vue_dev/dist/img $STATIC_DIR
mv /app/vue_dev/dist/css $STATIC_DIR
mv /app/vue_dev/dist/js $STATIC_DIR

echo "Vue.js: Transfering Template File"

rm -rf $INDEX_DIR
# mkdir -p $TEMPLATES_DIR
mv /app/vue_dev/dist/index.html $TEMPLATES_DIR

cd ../

exec "$@"