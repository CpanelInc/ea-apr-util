#!/bin/bash

source debian/vars.sh

rm -rf $DEB_INSTALL_ROOT
make install DESTDIR=$DEB_INSTALL_ROOT
# Unpackaged files; remove the static libaprutil
rm -f $DEB_INSTALL_ROOT$prefix_lib/aprutil.exp \
      $DEB_INSTALL_ROOT$prefix_lib/libapr*.a
# And remove the reference to the static libaprutil from the .la
# file.
sed -i '/^old_library/s,libapr.*\.a,,' \
      $DEB_INSTALL_ROOT$prefix_lib/libapr*.la
# Remove unnecessary exports from dependency_libs
sed -ri '/^dependency_libs/{s,-l(pq|sqlite[0-9]|rt|dl|uuid) ,,g}' \
      $DEB_INSTALL_ROOT$prefix_lib/libapr*.la
# Trim libtool DSO cruft
rm -f $DEB_INSTALL_ROOT$prefix_lib/apr-util-$apuver/*.*a
# Use our correctly-named package files within pkgconfig
sed -ri '/pkg-config/{s/apr-util-$apuver/$prefix_name-$apuver/}' \
    $DEB_INSTALL_ROOT$prefix_bin/apu-$apuver-config

mkdir -p $DEB_INSTALL_ROOT/docs
cp ./CHANGES $DEB_INSTALL_ROOT/docs/CHANGES
cp ./LICENSE $DEB_INSTALL_ROOT/docs/LICENSE
cp ./NOTICE $DEB_INSTALL_ROOT/docs/NOTICE

mkdir -p $DEB_INSTALL_ROOT/usr/share/pkgconfig/
cp $DEB_INSTALL_ROOT/opt/cpanel/ea-apr16/lib64/pkgconfig/apr-util-1.pc $DEB_INSTALL_ROOT/usr/share/pkgconfig/ea-apr16-util-1.pc
