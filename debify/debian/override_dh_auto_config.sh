#!/bin/bash

source debian/vars.sh

autoheader && autoconf -f
# A fragile autoconf test which fails if the code trips
# any other warning; force correct result for OpenLDAP:
export ac_cv_ldap_set_rebind_proc_style=three

export PKG_CONFIG_PATH="$PKG_CONFIG_PATH:`pwd`/config"

# `touch configure` needs done or configure goes down a path that results in:
#     cp: cannot stat '/apr_rules.mk': No such file or directory
# which results in this failure:
#     [  145s] Makefile:50: /usr/src/packages/BUILD/build/rules.mk: No such file or directory
#     [  145s] make[2]: *** No rule to make target '/usr/src/packages/BUILD/build/rules.mk'.  Stop.
touch configure

mkdir -p config
cp $ea_apr_config config/apr-1-config
cp $ea_apr_config config/apr-config
cp /usr/share/pkgconfig/ea-apr16-1.pc config/apr-1.pc

./configure --prefix=$prefix_dir \
        --libdir=$prefix_lib \
        --with-apr=$ea_apr_config \
        --includedir=$prefix_inc/apr-$apuver \
        --with-ldap=ldap_r --without-gdbm \
        --with-sqlite3 --with-pgsql --with-odbc \
        --without-freetds \
        --with-berkeley-db \
        --without-sqlite2 \
        --with-crypto --with-openssl --with-nss \
        --with-mysql

make
