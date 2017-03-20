#!/bin/bash
set -ex
sed -i 's/Sergey "Shnatsel" Davidoff <shnatsel@gmail.com>/Seattle Meshnet Buildbot <buildbot@seattlemesh.net>/g' debian/control
if [ ! -f ../old-changelog.txt ]; then
  cp debian/changelog ../old-changelog.txt
fi

version=$(git describe --tags | awk -F "-" '{ print substr($2,2) "~" $3 "+" $4 }')
echo -e "cjdns ($version) unstable; urgency=low\n" > debian/changelog
if [ -s ../changelog.txt ]; then
  cat ../changelog.txt >> debian/changelog
else
  echo "  * No changes" >> debian/changelog
fi
echo -e "\n -- Seattle Meshnet Buildbot <buildbot@seattlemesh.net>  $(date '+%a, %d %b %Y %R:%S %z')\n" >> debian/changelog
cat ../old-changelog.txt >> debian/changelog

cp debian/changelog ../old-changelog.txt
