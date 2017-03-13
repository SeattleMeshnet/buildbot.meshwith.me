#!/bin/bash
set -ex
mkdir -p repo
cd repo
mkdir -p pool/main
cp -v ../*.deb pool/main
for release in jessie stretch sid; do
  for arch in amd64 i386; do
    mkdir -p dists/$release/main/binary-$arch
    dpkg-scanpackages -m pool > dists/$release/main/binary-$arch/Packages
    gzip -c dists/$release/main/binary-$arch/Packages > dists/$release/main/binary-$arch/Packages.gz
  done
  apt-ftparchive release dists/$release > dists/$release/Release
  gpg --clearsign -o dists/$release/InRelease dists/$release/Release
  gpg -abs -o dists/$release/Release.gpg dists/$release/Release
done
