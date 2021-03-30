#!/bin/bash

source debian/vars.sh

autoheader && autoconf -f
# A fragile autoconf test which fails if the code trips
# any other warning; force correct result for OpenLDAP:
export ac_cv_ldap_set_rebind_proc_style=three
./configure --prefix=$prefix_dir \
        --libdir=$prefix_lib \
        --with-apr=$ea_apr_dir \
        --includedir=$prefix_inc/apr-$apuver \
        --with-ldap=ldap_r --without-gdbm \
        --with-sqlite3 --with-pgsql --with-odbc \
        --without-freetds \
        --with-berkeley-db \
        --without-sqlite2 \
        --with-crypto --with-openssl --with-nss \
        --with-mysql
make 
