%global ns_name ea
%global pkg_base apr-util
%global pkg_name %{ns_name}-%{pkg_base}

%define ea_openssl_ver 1.1.1d-1

%if 0%{?fedora} < 18 && 0%{?rhel} < 7
%define dbdep db4-devel
%else
%define dbdep libdb-devel
%endif

%if 0%{?rhel}
%define with_freetds 0
%else
%define with_freetds 1
%endif

%define apuver 1

%define prefix_name %{ea_apr_name}-util
%define prefix_dir /opt/cpanel/%{ea_apr_name}
%define prefix_lib %{prefix_dir}/%{_lib}
%define prefix_bin %{prefix_dir}/bin
%define prefix_inc %{prefix_dir}/include

Summary: Apache Portable Runtime Utility library
Name: %{pkg_name}
Version: 1.6.3
Vendor: cPanel, Inc.
# Doing release_prefix this way for Release allows for OBS-proof versioning, See EA-4542 for more details
%define release_prefix 1
Release: %{release_prefix}%{?dist}.cpanel
License: ASL 2.0
Group: System Environment/Libraries
URL: http://apr.apache.org/
Source0: http://www.apache.org/dist/apr/%{pkg_base}-%{version}.tar.bz2
Source1: macros.%{ns_name}-apu

Patch1: 0001-Update-pkg-config-variables.patch
Patch2: 0002-Force-static-linking-of-DBM-code.patch
Patch3: 0003-Link-against-ea-openssl-explicitly.patch
Patch4: 0004-apr-util-to-make-it-work-with-Mysql.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires: %{ns_name}-apr%{?_isa} >= 1.6.3
BuildRequires: autoconf, %{ns_name}-apr-devel >= 1.6.3
BuildRequires: %{dbdep}, expat-devel, libuuid-devel

%description
The mission of the Apache Portable Runtime (APR) is to provide a
free library of C data structures and routines.  This library
contains additional utility interfaces for APR; including support
for XML, LDAP, database interfaces, URI parsing and more.

%package devel
Group: Development/Libraries
Summary: APR utility library development kit
Requires: %{pkg_name}%{?_isa} = %{version}-%{release}
Requires: %{ns_name}-apr-devel%{?_isa}, pkgconfig
Requires: %{dbdep}%{?_isa}, expat-devel%{?_isa}, openldap-devel%{?_isa}

%description devel
This package provides the support files which can be used to
build applications using the APR utility library.  The mission
of the Apache Portable Runtime (APR) is to provide a free
library of C data structures and routines.

%package pgsql
Group: Development/Libraries
Summary: APR utility library PostgreSQL DBD driver
BuildRequires: postgresql-devel
Requires: %{pkg_name}%{?_isa} = %{version}-%{release}

%description pgsql
This package provides the PostgreSQL driver for the apr-util
DBD (database abstraction) interface.

%package mysql
Group: Development/Libraries
Summary: APR utility library MySQL DBD driver
BuildRequires: mysql-devel
Requires: %{pkg_name}%{?_isa} = %{version}-%{release}

%if 0%{?rhel} == 9
Requires: mysql-libs
%endif

%description mysql
This package provides the MySQL driver for the apr-util DBD
(database abstraction) interface.

%package sqlite
Group: Development/Libraries
Summary: APR utility library SQLite DBD driver
BuildRequires: sqlite-devel >= 3.0.0
Requires: %{pkg_name}%{?_isa} = %{version}-%{release}

%description sqlite
This package provides the SQLite driver for the apr-util DBD
(database abstraction) interface.

%if %{with_freetds}

%package freetds
Group: Development/Libraries
Summary: APR utility library FreeTDS DBD driver
BuildRequires: freetds-devel
Requires: %{pkg_name}%{?_isa} = %{version}-%{release}

%description freetds
This package provides the FreeTDS driver for the apr-util DBD
(database abstraction) interface.

%endif

%package odbc
Group: Development/Libraries
Summary: APR utility library ODBC DBD driver
BuildRequires: unixODBC-devel
Requires: %{pkg_name}%{?_isa} = %{version}-%{release}

%description odbc
This package provides the ODBC driver for the apr-util DBD
(database abstraction) interface.

%package ldap
Group: Development/Libraries
Summary: APR utility library LDAP support
BuildRequires: openldap-devel
Requires: %{pkg_name}%{?_isa} = %{version}-%{release}

%description ldap
This package provides the LDAP support for the apr-util.

%package openssl
Group: Development/Libraries
Summary: APR utility library OpenSSL crytpo support
%if 0%{?rhel} > 7
# In C8 we use system openssl. See DESIGN.md in ea-openssl11 git repo for details
Requires: openssl
BuildRequires: openssl
BuildRequires: openssl-devel
%else
Requires: ea-openssl11 >= %{ea_openssl_ver}
BuildRequires: ea-openssl11 >= %{ea_openssl_ver}
BuildRequires: ea-openssl11-devel >= %{ea_openssl_ver}
%endif
Requires: %{pkg_name}%{?_isa} = %{version}-%{release}

%description openssl
This package provides the OpenSSL crypto support for the apr-util.

%package nss
Group: Development/Libraries
Summary: APR utility library NSS crytpo support
BuildRequires: nss-devel
Requires: %{pkg_name}%{?_isa} = %{version}-%{release}

%description nss
This package provides the NSS crypto support for the apr-util.

%prep
%setup -q -n %{pkg_base}-%{version}
%patch1 -p1 -b .pkgconf
%patch2 -p1 -b .nodbmdso
%if 0%{?rhel} < 8
%patch3 -p1 -b .ssllinks
%endif

%if 0%{?rhel} > 7
%patch4 -p1 -b .mysql8
%endif

%build

autoheader && autoconf -f
# A fragile autoconf test which fails if the code trips
# any other warning; force correct result for OpenLDAP:
export ac_cv_ldap_set_rebind_proc_style=three
%if 0%{?rhel} < 8
export LDADD_dbd_mysql="-L/opt/cpanel/ea-openssl11/%{_lib} -Wl,-rpath=/opt/cpanel/ea-openssl11/%{_lib}"
export LDADD_crypto_openssl="-L/opt/cpanel/ea-openssl11/%{_lib} -Wl,-rpath=/opt/cpanel/ea-openssl11/%{_lib}"
%endif

./configure --prefix=%{prefix_dir} \
        --libdir=%{prefix_lib} \
        --with-apr=%{ea_apr_dir} \
        --includedir=%{prefix_inc}/apr-%{apuver} \
        --with-ldap=ldap_r --without-gdbm \
        --with-sqlite3 --with-pgsql --with-odbc \
%if %{with_freetds}
        --with-freetds \
%else
        --without-freetds \
%endif
        --with-berkeley-db \
        --without-sqlite2 \
%if 0%{?rhel} < 8
        --with-crypto --with-openssl=/opt/cpanel/ea-openssl11 --with-nss \
%else
        --with-crypto --with-openssl --with-nss \
%endif
        --with-mysql

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# Unpackaged files; remove the static libaprutil
rm -f $RPM_BUILD_ROOT%{prefix_lib}/aprutil.exp \
      $RPM_BUILD_ROOT%{prefix_lib}/libapr*.a

# And remove the reference to the static libaprutil from the .la
# file.
sed -i '/^old_library/s,libapr.*\.a,,' \
      $RPM_BUILD_ROOT%{prefix_lib}/libapr*.la

# Remove unnecessary exports from dependency_libs
sed -ri '/^dependency_libs/{s,-l(pq|sqlite[0-9]|rt|dl|uuid) ,,g}' \
      $RPM_BUILD_ROOT%{prefix_lib}/libapr*.la

# Trim libtool DSO cruft
rm -f $RPM_BUILD_ROOT%{prefix_lib}/apr-util-%{apuver}/*.*a

# Use our correctly-named package files within pkgconfig
sed -ri '/pkg-config/{s/apr-util-%{apuver}/%{prefix_name}-%{apuver}/}' \
    $RPM_BUILD_ROOT%{prefix_bin}/apu-%{apuver}-config
%ea_apr_fix_requires $RPM_BUILD_ROOT%{prefix_lib}/pkgconfig/apr-util-%{apuver}.pc

# In order for apr-util and our package to coexist, we have to name
# our pkgconfig files something else
mkdir -p $RPM_BUILD_ROOT%{_libdir}/pkgconfig
mv $RPM_BUILD_ROOT%{prefix_lib}/pkgconfig/apr-util-%{apuver}.pc $RPM_BUILD_ROOT%{_libdir}/pkgconfig/%{prefix_name}-%{apuver}.pc

# Set up the macros file
install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/rpm
sed -e 's/@APU_NAME@/%{prefix_name}/g' \
    -e 's/@APU_VER@/%{apuver}/g' \
    -e 's,@APU_DIR@,%{prefix_dir},g' \
    -e 's/@NAMESPACE@/%{ns_name}_/g' \
    %{SOURCE1} > $RPM_BUILD_ROOT%{_sysconfdir}/rpm/macros.%{pkg_name}

%check
# Run the less verbose test suites
export MALLOC_CHECK_=2 MALLOC_PERTURB_=$(($RANDOM % 255 + 1))
cd test
make %{?_smp_mflags} testall
# testall breaks with DBD DSO; ignore
export LD_LIBRARY_PATH="`echo "../dbm/.libs:../dbd/.libs:../ldap/.libs:../crypto/.libs:$LD_LIBRARY_PATH" | sed -e 's/::*$//'`"
./testall -v -q || true
./testall testrmm
./testall testdbm

%clean
rm -rf $RPM_BUILD_ROOT

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc CHANGES LICENSE NOTICE
%{prefix_lib}/libaprutil-%{apuver}.so.*
%dir %{prefix_lib}/apr-util-%{apuver}

%files pgsql
%defattr(-,root,root,-)
%{prefix_lib}/apr-util-%{apuver}/apr_dbd_pgsql*

%files mysql
%defattr(-,root,root,-)
%{prefix_lib}/apr-util-%{apuver}/apr_dbd_mysql*

%files sqlite
%defattr(-,root,root,-)
%{prefix_lib}/apr-util-%{apuver}/apr_dbd_sqlite*

%if %{with_freetds}

%files freetds
%defattr(-,root,root,-)
%{prefix_lib}/apr-util-%{apuver}/apr_dbd_freetds*

%endif

%files odbc
%defattr(-,root,root,-)
%{prefix_lib}/apr-util-%{apuver}/apr_dbd_odbc*

%files ldap
%defattr(-,root,root,-)
%{prefix_lib}/apr-util-%{apuver}/apr_ldap*

%files openssl
%defattr(-,root,root,-)
%{prefix_lib}/apr-util-%{apuver}/apr_crypto_openssl*

%files nss
%defattr(-,root,root,-)
%{prefix_lib}/apr-util-%{apuver}/apr_crypto_nss*

%files devel
%defattr(-,root,root,-)
%{prefix_bin}/apu-%{apuver}-config
%{prefix_lib}/libaprutil-%{apuver}.*a
%{prefix_lib}/libaprutil-%{apuver}.so
%{prefix_inc}/apr-%{apuver}/*.h
%{_libdir}/pkgconfig/*.pc
%{_sysconfdir}/rpm/macros.%{pkg_name}

%changelog
* Thu Feb 02 2023 Tim Mullin <tim@cpanel.net> - 1.6.3-1
- EA-11199: Update apr-util from v1.6.1 to v1.6.3
- CVE-2022-25147
    Integer Overflow or Wraparound vulnerability in apr_base64 functions
    of Apache Portable Runtime Utility (APR-util) allows an attacker to
    write beyond bounds of a buffer.

* Tue Oct 18 2022 Julian Brown <julian.brown@cpanel.net> - 1.6.1-10
- ZC-10391: Fix ubuntu dependency to mysql-libs

* Fri Oct 14 2022 Julian Brown <julian.brown@cpanel.net> - 1.6.1-9
- ZC-10375: Changes to fix for AlmaLinux 9

* Mon Nov 23 2020 Julian Brown <julian.brown@cpanel.net> - 1.6.1-8
- ZC-8005: Remove ea-openssl11 on C8

* Mon Jun 29 2020 Julian Brown <julian.brown@cpanel.net> - 1.6.1-7
- ZC-6801: Build on CentOS 8

* Thu Jun 18 2020 Tim Mullin <tim@cpanel.net> - 1.6.1-6
- EA-9121: Fix ea-apr-util-mysql to link to ea-openssl11

* Tue Sep 24 2019 Daniel Muey <dan@cpanel.net> - 1.6.1-5
- ZC-4361: Update ea-openssl requirement to v1.1.1 (ZC-5583)

* Mon Apr 16 2018 Rishwanth Yeddula <rish@cpanel.net> - 1.6.1-4
- EA-7382: Update dependency on ea-openssl to require the latest version with versioned symbols.

* Mon Apr 09 2018 Rishwanth Yeddula <rish@cpanel.net> - 1.6.1-3
- EA-7390: Avoid random build failures related to the autoconf cache.

* Thu Mar 22 2018 Rishwanth Yeddula <rish@cpanel.net> - 1.6.1-2
- EA-7360: Link against ea-openssl explicitly

* Thu Mar 22 2018 Rishwanth Yeddula <rish@cpanel.net> - 1.6.1-1
- EA-7243: Update to 1.6.1

* Wed Mar 21 2018 Rishwanth Yeddula <rish@cpanel.net> - 1.5.2-15
- ZC-3552: Adjusted for ea-openssl versioning and fixup

* Thu Mar 08 2018 Daniel Muey <dan@cpanel.net> - 1.5.2-14
- ZC-3460: build apr-util against our ea-openssl

* Tue Dec 20 2016 Cory McIntire <cory@cpanel.net> - 1.5.2-13
- Added Vendor Field to the RPM SPEC file

* Fri Dec 02 2016 S. Kurt Newman <kurt.newman@cpanel.net> - 1.5.2-12
- Now depends on ea-apr (EA-5718)
- Uses ns_name macro (EA-5718)

* Mon Jun 20 2016 Dan Muey <dan@cpanel.net> - 1.5.2-11
- EA-4383: Update Release value to OBS-proof versioning

* Fri Jul 31 2015 Trinity Quirk <trinity.quirk@cpanel.net> 1.5.2-9
- Added macro handling for apr dependency resolution

* Mon Jun 29 2015 Matt Dees <matt@cpanel.net> 1.5.2-8
- Move ea-apr-util to /opt/cpanel/ea-apr15-util

* Thu Mar 26 2015 Trinity Quirk <trinity.quirk@cpanel.net> - 1.5.2-7
- Renamed to ea-<pkg>, set conflicts with RHEL/CentOS upstream packages

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 1.5.2-6
- Mass rebuild 2014-01-24

* Wed Jan 15 2014 Honza Horak <hhorak@redhat.com> - 1.5.2-5
- Rebuild for mariadb-libs
  Related: #1045013

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.5.2-4
- Mass rebuild 2013-12-27

* Thu May 09 2013 Jan Kaluza <jkaluza@redhat.com> - 1.5.2-3
- do not build with freetds when it is not available

* Tue Apr  9 2013 Joe Orton <jorton@redhat.com> - 1.5.2-2
- update for aarch64

* Tue Apr  9 2013 Joe Orton <jorton@redhat.com> - 1.5.2-1
- update to 1.5.2

* Thu Feb 07 2013 Jon Ciesla <limburgher@gmail.com> - 1.4.1-8
- Apply private patch from Merge Review BZ 225254.

* Wed Nov 07 2012 Jan Kaluza <jkaluza@redhat.com> - 1.4.1-7
- ensure we use latest libdb5 (not libdb4)

* Thu Oct 18 2012 Joe Orton <jorton@redhat.com> - 1.4.1-6
- use -lldap_r instead of -lldap

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jun  6 2012 Joe Orton <jorton@redhat.com> - 1.4.1-4
- fix crypt_r failure modes (#819650)

* Tue Apr 24 2012 Joe Orton <jorton@redhat.com> - 1.4.1-3
- apply _isa to deps

* Mon Apr 23 2012 Joe Orton <jorton@redhat.com> - 1.4.1-2
- switch to libdb-devel

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Dec 15 2011 Bojan Smojver <bojan@rexursive.com> - 1.4.1-1
- bump up to 1.4.1

* Fri May 20 2011 Bojan Smojver <bojan@rexursive.com> - 1.3.12-1
- bump up to 1.3.12

* Wed May 11 2011 Bojan Smojver <bojan@rexursive.com> - 1.3.11-2
- fix crash in apr_ldap_rebind_init()

* Mon May  9 2011 Bojan Smojver <bojan@rexursive.com> - 1.3.11-1
- bump up to 1.3.11

* Wed Mar 23 2011 Dan Horák <dan@danny.cz> - 1.3.10-7
- rebuilt for mysql 5.5.10 (soname bump in libmysqlclient)

* Wed Mar 23 2011 Joe Orton <jorton@redhat.com> - 1.3.10-6
- rebuild for MySQL soname bump

* Wed Mar  2 2011 Joe Orton <jorton@redhat.com> - 1.3.10-5
- fix build

* Wed Mar  2 2011 Joe Orton <jorton@redhat.com> - 1.3.10-4
- rebuild

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.10-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Dec 29 2010 Bojan Smojver <bojan@rexursive.com> - 1.3.10-2
- rebuild for MySQL 5.5.x

* Tue Oct  5 2010 Joe Orton <jorton@redhat.com> - 1.3.10-1
- update to 1.3.10

* Wed Nov 25 2009 Joe Orton <jorton@redhat.com> - 1.3.9-3
- rebuild for new BDB

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.3.9-2
- rebuilt with new openssl

* Thu Aug  6 2009 Bojan Smojver <bojan@rexursive.com> - 1.3.9-1
- bump up to 1.3.9
- CVE-2009-2412
- allocator alignment fixes

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.8-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 15 2009 Bojan Smojver <bojan@rexursive.com> 1.3.8-2
- adjust apr-util-1.3.7-nodbmdso.patch

* Wed Jul 15 2009 Bojan Smojver <bojan@rexursive.com> 1.3.8-1
- bump up to 1.3.8

* Wed Jul 15 2009 Bojan Smojver <bojan@rexursive.com> 1.3.7-5
- BR: +libuuid-devel, -e2fsprogs-devel

* Tue Jun  9 2009 Joe Orton <jorton@redhat.com> 1.3.7-4
- disable DBM-drivers-as-DSO support
- backport r783046 from upstream

* Mon Jun  8 2009 Bojan Smojver <bojan@rexursive.com> - 1.3.7-3
- make export of LD_LIBRARY_PATH simpler

* Mon Jun  8 2009 Bojan Smojver <bojan@rexursive.com> - 1.3.7-2
- revert tests

* Mon Jun  8 2009 Bojan Smojver <bojan@rexursive.com> - 1.3.7-1
- bump up to 1.3.7
- CVE-2009-0023
- "billion laughs" fix of apr_xml_* interface

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jan 23 2009 Joe Orton <jorton@redhat.com> 1.3.4-2
- rebuild for new MySQL

* Sat Aug 16 2008 Bojan Smojver <bojan@rexursive.com> - 1.3.4-1
- bump up to 1.3.4
- drop PostgreSQL patch, fixed upstream

* Wed Jul 16 2008 Bojan Smojver <bojan@rexursive.com> - 1.3.2-8
- beat the fuzz, rework apr-util-1.2.7-pkgconf.patch

* Wed Jul 16 2008 Bojan Smojver <bojan@rexursive.com> - 1.3.2-7
- ship find_apu.m4, fix bug #455189

* Thu Jul 10 2008 Tom "spot" Callaway <tcallawa@redhat.com> 1.3.2-6
- rebuild for new db4-4.7

* Tue Jul  8 2008 Joe Orton <jorton@redhat.com> 1.3.2-5
- restore requires for openldap-devel from -devel

* Wed Jul  2 2008 Bojan Smojver <bojan@rexursive.com> - 1.3.2-4
- properly fix PostgreSQL detection

* Wed Jul  2 2008 Bojan Smojver <bojan@rexursive.com> - 1.3.2-3
- revert build dependencies, change from -2 didn't help
- add apr-util-1.3.2-pgsql.patch (remove pgsql_LIBS during detection)

* Wed Jul  2 2008 Bojan Smojver <bojan@rexursive.com> - 1.3.2-2
- try adding postgresql-server to build dependencies to pull some libs in

* Thu Jun 19 2008 Bojan Smojver <bojan@rexursive.com> - 1.3.2-1
- bump up to 1.3.2

* Sun Jun  1 2008 Bojan Smojver <bojan@rexursive.com> - 1.3.0-1
- bump up to 1.3.0

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.2.12-5
- Autorebuild for GCC 4.3

* Tue Dec  4 2007 Joe Orton <jorton@redhat.com> 1.2.12-4
- rebuild for OpenLDAP soname bump

* Mon Dec  3 2007 Bojan Smojver <bojan@rexursive.com> - 1.2.12-3
- remove all instances of MySQL flags being added to APRUTIL_LDFLAGS

* Tue Nov 27 2007 Bojan Smojver <bojan@rexursive.com> - 1.2.12-1
- bump up to 1.2.12
- drop MySQL DBD driver, shipped upstream
- adjust various patches to apply
- rework tests in %%check (1.2.x got tests from trunk)

* Mon Sep 24 2007 Jesse Keating <jkeating@redhat.com> - 1.2.10-2
- Rebuild for upgrade path (add dist since that's now on F-7 branch)

* Sun Sep  9 2007 Bojan Smojver <bojan@rexursive.com> 1.2.10-1
- bump up to 1.2.10
- pick up newly checked in MySQL DBD driver directly from ASF
- remove dbdopen patch (fixed upstream)
- remove xmlns patch (fixed upstream)
- remove autoexpat patch (fixed upstream)

* Sun Sep  2 2007 Joe Orton <jorton@redhat.com> 1.2.8-12
- rebuild for fixed APR 32-bit ABI
- remove sqlite driver from main package (#274521)

* Wed Aug 22 2007 Joe Orton <jorton@redhat.com> 1.2.8-11
- rebuild for expat soname bump

* Tue Aug 21 2007 Joe Orton <jorton@redhat.com> 1.2.8-10
- fix License

* Wed Aug  8 2007 Joe Orton <jorton@redhat.com> 1.2.8-9
- add rewrite of expat autoconf code (upstream r493791)
- fix build for new glibc open()-as-macro
- split out sqlite subpackage

* Tue Jul  3 2007 Joe Orton <jorton@redhat.com> 1.2.8-8
- add fix for attribute namespace handling in apr_xml (PR 41908)

* Thu Apr  5 2007 Joe Orton <jorton@redhat.com> 1.2.8-7
- remove old Conflicts, doxygen BR (#225254)

* Fri Mar 23 2007 Joe Orton <jorton@redhat.com> 1.2.8-6
- add DBD DSO lifetime fix (r521327)

* Thu Mar 22 2007 Joe Orton <jorton@redhat.com> 1.2.8-5
- drop doxygen documentation (which caused multilib conflicts)

* Wed Feb 28 2007 Joe Orton <jorton@redhat.com> 1.2.8-4
- add mysql driver in -mysql subpackage (Bojan Smojver, #222237)

* Tue Feb 27 2007 Joe Orton <jorton@redhat.com> 1.2.8-3
- build DBD drivers as DSOs (w/Bojan Smojver, #192922)
- split out pgsql driver into -pgsql subpackage

* Tue Dec  5 2006 Joe Orton <jorton@redhat.com> 1.2.8-2
- update to 1.2.8, pick up new libpq soname

* Fri Dec  1 2006 Joe Orton <jorton@redhat.com> 1.2.7-5
- really rebuild for db45

* Sat Nov 11 2006 Joe Orton <jorton@redhat.com> 1.2.7-4
- add support for BDB 4.5 from upstream, rebuild

* Wed Jul 19 2006 Joe Orton <jorton@redhat.com> 1.2.7-3
- fix buildconf with autoconf 2.60

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.2.7-2.1
- rebuild

* Tue May  2 2006 Joe Orton <jorton@redhat.com> 1.2.7-2
- update to 1.2.7
- use pkg-config in apu-1-config to make it libdir-agnostic

* Thu Apr  6 2006 Joe Orton <jorton@redhat.com> 1.2.6-2
- update to 1.2.6
- define LDAP_DEPRECATED in apr_ldap.h (r391985, #188073)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.2.2-4.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.2.2-4.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Jan 30 2006 Joe Orton <jorton@redhat.com> 1.2.2-4
- rebuild to drop reference to libexpat.la

* Wed Jan 18 2006 Joe Orton <jorton@redhat.com> 1.2.2-3
- disable sqlite2 support
- BuildRequire e2fsprogs-devel
- enable malloc paranoia in %%check

* Tue Jan  3 2006 Jesse Keating <jkeating@redhat.com> 1.2.2-2.2
- rebuilt again

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Dec  6 2005 Joe Orton <jorton@redhat.com> 1.2.2-2
- trim exports from .la file/--libs output (#174924)

* Fri Nov 25 2005 Joe Orton <jorton@redhat.com> 1.2.2-1
- update to 1.2.2

* Thu Oct 20 2005 Joe Orton <jorton@redhat.com> 0.9.7-3
- fix epoch again

* Thu Oct 20 2005 Joe Orton <jorton@redhat.com> 0.9.7-2
- update to 0.9.7
- drop static libs (#170051)

* Tue Jul 26 2005 Joe Orton <jorton@redhat.com> 0.9.6-3
- add FILE bucket fix for truncated files (#159191)
- add epoch to dependencies

* Fri Mar  4 2005 Joe Orton <jorton@redhat.com> 0.9.6-2
- rebuild

* Wed Feb  9 2005 Joe Orton <jorton@redhat.com> 0.9.6-1
- update to 0.9.6

* Wed Jan 19 2005 Joe Orton <jorton@redhat.com> 0.9.5-3
- restore db-4.3 detection lost in 0.9.5 upgrade

* Wed Jan 19 2005 Joe Orton <jorton@redhat.com> 0.9.5-2
- rebuild

* Mon Nov 22 2004 Joe Orton <jorton@redhat.com> 0.9.5-1
- update to 0.9.5

* Thu Nov 11 2004 Jeff Johnson <jbj@jbj.org> 0.9.4-19
- actually explicitly check for and detect db-4.3.

* Thu Nov 11 2004 Jeff Johnson <jbj@jbj.org> 0.9.4-18
- rebuild against db-4.3.21.

* Fri Sep 17 2004 Joe Orton <jorton@redhat.com> 0.9.4-17
- add security fix for CAN-2004-0786

* Sat Jun 19 2004 Joe Orton <jorton@redhat.com> 0.9.4-16
- have -devel require matching release of apr-util

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Apr  1 2004 Joe Orton <jorton@redhat.com> 0.9.4-14
- fix use of SHA1 passwords (#119651)

* Tue Mar 30 2004 Joe Orton <jorton@redhat.com> 0.9.4-13
- remove fundamentally broken check_sbcs() from xlate code

* Fri Mar 19 2004 Joe Orton <jorton@redhat.com> 0.9.4-12
- tweak xlate fix

* Fri Mar 19 2004 Joe Orton <jorton@redhat.com> 0.9.4-11
- rebuild with xlate fixes and tests enabled

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com> 0.9.4-10.1
- rebuilt

* Tue Mar  2 2004 Joe Orton <jorton@redhat.com> 0.9.4-10
- rename sdbm_* symbols to apu__sdbm_*

* Mon Feb 16 2004 Joe Orton <jorton@redhat.com> 0.9.4-9
- fix sdbm apr_dbm_exists() on s390x/ppc64

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com> 0.9.4-8
- rebuilt

* Thu Feb  5 2004 Joe Orton <jorton@redhat.com> 0.9.4-7
- fix warnings from use of apr_optional*.h with gcc 3.4

* Thu Jan 29 2004 Joe Orton <jorton@redhat.com> 0.9.4-6
- drop gdbm support

* Thu Jan  8 2004 Joe Orton <jorton@redhat.com> 0.9.4-5
- fix DB library detection

* Sat Dec 13 2003 Jeff Johnson <jbj@jbj.org> 0.9.4-4
- rebuild against db-4.2.52.

* Mon Oct 13 2003 Jeff Johnson <jbj@jbj.org> 0.9.4-3
- rebuild against db-4.2.42.

* Mon Oct  6 2003 Joe Orton <jorton@redhat.com> 0.9.4-2
- fix 'apu-config --apu-la-file' output

* Mon Oct  6 2003 Joe Orton <jorton@redhat.com> 0.9.4-1
- update to 0.9.4.

* Tue Jul 22 2003 Nalin Dahyabhai <nalin@redhat.com> 0.9.3-10
- rebuild

* Mon Jul  7 2003 Joe Orton <jorton@redhat.com> 0.9.3-9
- rebuild
- don't run testuuid test because of #98677

* Thu Jul  3 2003 Joe Orton <jorton@redhat.com> 0.9.3-8
- rebuild

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue May 20 2003 Joe Orton <jorton@redhat.com> 0.9.3-6
- fix to detect crypt_r correctly (CAN-2003-0195)

* Thu May 15 2003 Joe Orton <jorton@redhat.com> 0.9.3-5
- fix to try linking against -ldb first (#90917)
- depend on openldap, gdbm, db4, expat appropriately.

* Tue May 13 2003 Joe Orton <jorton@redhat.com> 0.9.3-4
- rebuild

* Wed May  7 2003 Joe Orton <jorton@redhat.com> 0.9.3-3
- make devel package conflict with old subversion-devel
- run the less crufty parts of the test suite

* Tue Apr 29 2003 Joe Orton <jorton@redhat.com> 0.9.3-2
- run ldconfig in post/postun

* Mon Apr 28 2003 Joe Orton <jorton@redhat.com> 0.9.3-1
- initial build
