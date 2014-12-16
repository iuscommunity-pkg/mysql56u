%global basever 5.6

# Regression tests may take a long time (many cores recommended), skip them by 
# passing --nocheck to rpmbuild

# set to 1 to avoid file conflict
%global with_shared_lib_major_hack 0

%global _hardened_build 1

%{?filter_setup:
%filter_from_requires /perl(th.*/d; /perl(lib::mtr.*/d; /perl(lib::v1\/mtr.*/d; /perl(mtr.*/d; /perl(hostnames)/d;
%filter_provides_in %{_datadir}/%{name}/
%filter_setup
}

# By default, patch(1) creates backup files when chunks apply with offsets.
# Turn that off to ensure such files don't get included in RPMs (cf bz#884755).
%global _default_patch_flags --no-backup-if-mismatch

Name:             mysql56u
Version:          5.6.22
Release:          1.ius%{?dist}
Summary:          MySQL client programs and shared libraries
Group:            Applications/Databases
URL:              http://www.mysql.com

# Exceptions allow client libraries to be linked with most open source SW,
# not only GPL code.  See README.mysql-license
License:          GPLv2 with exceptions

Source0: http://dev.mysql.com/get/Downloads/MySQL-5.6/mysql-%{version}.tar.gz

Source1:          generate-tarball.sh
Source2:          mysql.init

Source3:          my.cnf
Source4:          scriptstub.c
Source5:          my_config.h
Source6:          README.mysql-docs
Source7:          README.mysql-license
Source9:          mysql-embedded-check.c
Source10:         mysql.tmpfiles.d
Source11:         mysqld.service
Source12:         mysqld-prepare-db-dir
Source13:         mysqld-wait-ready
Source14:         rh-skipped-tests-base.list
Source15:         rh-skipped-tests-arm.list
# To track rpmlint warnings
Source17:         mysql-5.6.10-rpmlintrc

Source100: my-56-terse.cnf
Source101: my-56-verbose.cnf
Source102: mysql.logrotate

# Comments for these patches are in the patch files
Patch1:           mysql-errno.patch
Patch2:           mysql-strmov.patch
Patch3:           mysql-install-test.patch
Patch4:           mysql-expired-certs.patch
Patch5:           mysql-stack-guard.patch
Patch6:           mysql-chain-certs.patch
Patch10:          mysql-plugin-bool.patch
Patch11:          mysql-s390-tsc.patch
Patch14:          mysql-va-list.patch
Patch15:          mysql-netdevname.patch
Patch16:          mysql-logrotate.patch
Patch18:          mysql-5.6.11-cipherspec.patch
Patch19:          mysql-file-contents.patch
Patch20:          mysql-string-overflow.patch
Patch21:          mysql-dh1024.patch
Patch23:          mysql-5.6.10-libmysql-version.patch
Patch24:          mysql-5.6.11-editline.patch
Patch25:          mysql-5.6.14-mysql-install.patch
Patch26:          mysql-5.6.11-major.patch

Patch28:          community-mysql-5.6.13-truncate-file.patch
Patch29:          community-mysql-tmpdir.patch
Patch30:          community-mysql-cve-2013-1861.patch
Patch31:          community-mysql-innodbwarn.patch
Patch32:          community-mysql-covscan-signexpr.patch
Patch33:          community-mysql-covscan-stroverflow.patch
Patch34:          community-mysql-pluginerrmsg.patch
Patch99:          mysql-5.6.17-libevent.patch



BuildRequires:    cmake
BuildRequires:    dos2unix
BuildRequires:    libaio-devel
BuildRequires:    ncurses-devel
BuildRequires:    libevent-devel
BuildRequires:    openssl-devel
BuildRequires:    perl
BuildRequires:    systemtap-sdt-devel
BuildRequires:    zlib-devel
# Tests requires time and ps and some perl modules
BuildRequires:    procps
BuildRequires:    time
BuildRequires:    perl(Socket)
BuildRequires:    perl(Time::HiRes)
%if 0%{?fedora} > 14
BuildRequires:    systemd-units
%endif

Requires:         bash
Requires:         grep
Requires:         fileutils
Requires:         %{name}-common%{?_isa} = %{version}-%{release}
Provides:         mysql = %{version}-%{release} 
Provides:         mysql%{?_isa} = %{version}-%{release}
Conflicts:        mariadb
# mysql-cluster used to be built from this SRPM, but no more
Obsoletes:        mysql-cluster < 5.1.44

# IUS-isms
Requires: mysqlclient16
Conflicts: mysql < %{basever}
Provides: mysql = %{version}-%{release}

%description
MySQL is a multi-user, multi-threaded SQL database server. MySQL is a
client/server implementation consisting of a server daemon (mysqld)
and many different client programs and libraries. The base package
contains the standard MySQL client programs and generic MySQL files.


%package          libs
Summary:          The shared libraries required for MySQL clients
Group:            Applications/Databases
Requires:         /sbin/ldconfig
Requires:         %{name}-common%{?_isa} = %{version}-%{release}

# IUS-isms
Conflicts: mysql-libs < %{basever}
Provides: mysql-libs = %{version}-%{release}
Provides: config(mysql-libs) = %{version}-%{release}

%description      libs
The mysql-libs package provides the essential shared libraries for any 
MySQL client program or interface. You will need to install this package
to use any other MySQL package or any clients that need to connect to a
MySQL server.

%package          common
Summary:          The shared files required for MySQL server and client
Group:            Applications/Databases
%description      common
The mysql-common package provides the essential shared files for any
MySQL program. You will need to install this package to use any other
MySQL package.

%package          server
Summary:          The MySQL server and related files
Group:            Applications/Databases

# note: no version here = %{version}-%{release}
#Requires:         mysql%{?_isa} 
Requires:         %{name}%{?_isa} 
Requires:         %{name}-libs%{?_isa} = %{version}-%{release}
Requires:         sh-utils
Requires(pre):    /usr/sbin/useradd
Requires(post):   chkconfig
Requires(preun):  chkconfig
%if 0%{?fedora} > 14
# We require this to be present for %%{_prefix}/lib/tmpfiles.d
Requires:         systemd-units
# Make sure it's there when scriptlets run, too
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
# This is actually needed for the %%triggerun script but Requires(triggerun)
# is not valid.  We can use %%post because this particular %%triggerun script
# should fire just after this package is installed.
Requires(post):   systemd-sysv
%endif
# mysqlhotcopy needs DBI/DBD support
Requires:         perl(DBI)
Requires:         perl(DBD::mysql)
#Provides:         mysql-server = %{version}-%{release} 
Provides:         mysql-server%{?_isa} = %{version}-%{release}
Conflicts:        mariadb-server, MySQL-server

# IUS-isms
Conflicts: mysql-server < %{basever}
Provides: mysql-server = %{version}-%{release}
Provides: config(mysql-server) = %{version}-%{release}

%description      server
MySQL is a multi-user, multi-threaded SQL database server. MySQL is a
client/server implementation consisting of a server daemon (mysqld)
and many different client programs and libraries. This package contains
the MySQL server and some accompanying files and directories.


%package          devel
Summary:          Files for development of MySQL applications
Group:            Applications/Databases
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-libs%{?_isa} = %{version}-%{release}
Requires:         openssl-devel%{?_isa}
Conflicts:        mariadb-devel, MySQL-devel

#Provides:         mysql-devel = %{version}-%{release}
Provides:         mysql-devel%{?_isa} = %{version}-%{release}
# IUS-isms
Conflicts: mysql-devel < %{basever}
Provides: mysql-devel = %{version}-%{release}

%description      devel
MySQL is a multi-user, multi-threaded SQL database server. This
package contains the libraries and header files that are needed for
developing MySQL client applications.


%package          embedded
Summary:          MySQL as an embeddable library
Group:            Applications/Databases
#Provides:         mysql-embedded = %{version}-%{release}
Provides:         mysql-embedded%{?_isa} = %{version}-%{release}

# IUS-isms
Conflicts: mysql-embedded < %{basever}
Provides: mysql-embedded = %{version}-%{release}

%description      embedded
MySQL is a multi-user, multi-threaded SQL database server. This
package contains a version of the MySQL server that can be embedded
into a client application instead of running as a separate process.


%package          embedded-devel
Summary:          Development files for MySQL as an embeddable library
Group:            Applications/Databases
Requires:         %{name}-embedded%{?_isa} = %{version}-%{release}
Requires:         %{name}-devel%{?_isa} = %{version}-%{release}
Conflicts:        mariadb-embedded-devel, MySQL-embedded-devel
#Provides:         mysql-embedded-devel = %{version}-%{release}
Provides:         mysql-embedded-devel%{?_isa} = %{version}-%{release}

# IUS-isms
Conflicts: mysql-embedded-devel < %{basever}
Provides: mysql-embedded-devel = %{version}-%{release}

%description      embedded-devel
MySQL is a multi-user, multi-threaded SQL database server. This
package contains files needed for developing and testing with
the embedded version of the MySQL server.


%package          bench
Summary:          MySQL benchmark scripts and data
Group:            Applications/Databases
Requires:         %{name}%{?_isa} = %{version}-%{release}
Conflicts:        mariadb-bench, MySQL-bench
#Provides:         mysql-bench = %{version}-%{release}
Provides:         mysql-bench%{?_isa} = %{version}-%{release}

# IUS-isms
Conflicts: mysql-bench < %{basever}
Provides: mysql-bench = %{version}-%{release}

%description      bench
MySQL is a multi-user, multi-threaded SQL database server. This
package contains benchmark scripts and data for use when benchmarking
MySQL.


%package          test
Summary:          The test suite distributed with MySQL
Group:            Applications/Databases
Requires:         %{name}%{?_isa} = %{version}-%{release}
Requires:         %{name}-libs%{?_isa} = %{version}-%{release}
Requires:         %{name}-server%{?_isa} = %{version}-%{release}
Conflicts:        mariadb-test, MySQL-test
#Provides:         mysql-test = %{version}-%{release}
Provides:         mysql-test%{?_isa} = %{version}-%{release}
# IUS-isms
Conflicts: mysql-test < %{basever}
Provides: mysql-test = %{version}-%{release}

%description test
MySQL is a multi-user, multi-threaded SQL database server. This
package contains the regression test suite distributed with
the MySQL sources.


%prep
%setup -q -n mysql-%{version}

# my-55-verbose.cnf
cp %{SOURCE101} .

#%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
#%patch5 -p1
%patch6 -p1
#%patch10 -p1
%patch11 -p1
#%patch14 -p1
#%patch15 -p1
%patch16 -p1
%patch18 -p1
#%patch19 -p1
#%patch20 -p1
%patch21 -p1
%patch23 -p1
#%patch24 -p1
%patch25 -p1
%if %{with_shared_lib_major_hack}
%patch26 -p1
%endif
#%patch28 -p0
%patch29 -p1
#%patch30 -p1
%patch31 -p1
#%patch32 -p1
#%patch33 -p1
%patch34 -p1
%patch99 -p1

# fix from http://repo.mysql.com/yum/mysql-5.6-community/el/6/SRPMS/mysql-community-5.6.20-4.el6.src.rpm
# Avoid dtrace dep
sed -i -e "1d" mysql-test/std_data/dtrace.d
chmod 0664 mysql-test/std_data/dtrace.d

# Workaround for upstream bug #56342
rm -f mysql-test/t/ssl_8k_key-master.opt

# Generate a list of tests that fail, but are not disabled by upstream
cat %{SOURCE14} > mysql-test/rh-skipped-tests.list
# Disable some tests failing on ARM architectures
%ifarch %{arm}
cat %{SOURCE15} >> mysql-test/rh-skipped-tests.list
%endif
# Upstream bug: http://bugs.mysql.com/68520
dos2unix -k README

%build
# fail quickly and obviously if user tries to build as root
if [ x"$(id -u)" = "x0" ]; then
    echo "mysql's regression tests fail if run as root."
    echo "If you really need to build the RPM as root, use"
    echo "--nocheck to skip the regression tests."
    exit 1
fi

CFLAGS="%{optflags} -D_GNU_SOURCE -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE"
# MySQL 4.1.10 definitely doesn't work under strict aliasing; also,
# gcc 4.1 breaks MySQL 5.0.16 without -fwrapv
CFLAGS="$CFLAGS -fno-strict-aliasing -fwrapv"
# force PIC mode so that we can build libmysqld.so
CFLAGS="$CFLAGS -fPIC"
# gcc seems to have some bugs on sparc as of 4.4.1, back off optimization
# submitted as bz #529298
%ifarch sparc sparcv9 sparc64
CFLAGS=$(echo $CFLAGS| sed -e "s|-O2|-O1|g" )
%endif
CXXFLAGS="$CFLAGS"
export CFLAGS CXXFLAGS
%if %{_hardened_build}
LDFLAGS="$LDFLAGS -pie"
export LDFLAGS
%endif

#  build out of source
mkdir build
pushd build

# The INSTALL_xxx macros have to be specified relative to CMAKE_INSTALL_PREFIX
# so we can't use %%{_datadir} and so forth here.
cmake .. -DBUILD_CONFIG=mysql_release \
         -DFEATURE_SET="community" \
         -DCOMPILATION_COMMENT="Distributed by The IUS Community Project" \
         -DINSTALL_LAYOUT=RPM \
         -DCMAKE_INSTALL_PREFIX="%{_prefix}" \
         -DINSTALL_INCLUDEDIR=include/mysql \
         -DINSTALL_INFODIR=share/info \
         -DINSTALL_LIBDIR="%{_lib}/mysql" \
         -DINSTALL_MANDIR=share/man \
         -DINSTALL_MYSQLSHAREDIR=share/mysql \
         -DINSTALL_MYSQLTESTDIR=share/mysql-test \
         -DINSTALL_PLUGINDIR="%{_lib}/mysql/plugin" \
         -DINSTALL_SBINDIR=libexec \
         -DINSTALL_SCRIPTDIR=bin \
         -DINSTALL_SQLBENCHDIR=share \
         -DINSTALL_SUPPORTFILESDIR=share/mysql \
         -DMYSQL_DATADIR="/var/lib/mysql" \
         -DMYSQL_UNIX_ADDR="/var/lib/mysql/mysql.sock" \
         -DENABLED_LOCAL_INFILE=ON \
         -DENABLE_DTRACE=ON \
         -DWITH_EMBEDDED_SERVER=ON \
         -DWITH_EDITLINE=bundled \
         -DWITH_LIBEVENT=system \
         -DWITH_SSL=system \
         -DWITH_ZLIB=system \
         -DWITH_INNODB_MEMCACHED=on \
%if %{_hardened_build}
         -DWITH_MYSQLD_LDFLAGS="-Wl,-z,relro,-z,now"
%endif

%{__cc} $CFLAGS $LDFLAGS -o scriptstub "-DLIBDIR=\"%{_libdir}/mysql\"" %{SOURCE4}

make %{?_smp_mflags} VERBOSE=1

# Regular build will make libmysqld.a but not libmysqld.so :-(
# Upstream bug: http://bugs.mysql.com/68559
mkdir libmysqld/work
pushd libmysqld/work
ar -x ../libmysqld.a
%{__cc} $CFLAGS $LDFLAGS -shared -Wl,-soname,libmysqld.so.0 -o libmysqld.so.0.0.1 \
   *.o \
  -lpthread -laio -lcrypt -lssl -lcrypto -lz -lrt -lstdc++ -ldl -lm -lc
# This is to check that we built a complete library
cp %{SOURCE9} .
ln -s libmysqld.so.0.0.1 libmysqld.so.0
%{__cc} -I../../../include -I../../include $CFLAGS mysql-embedded-check.c libmysqld.so.0
LD_LIBRARY_PATH=. ldd ./a.out


%install
mkdir -p %{buildroot}/var/log/mysql \
         %{buildroot}/var/lib/mysqllogs \
         %{buildroot}/var/lib/mysqltmp
pushd build
make DESTDIR=%{buildroot} install

# List the installed tree for RPM package maintenance purposes.
find %{buildroot} -print | sed "s|^%{buildroot}||" | sort > ROOTFILES

# Multilib header hacks
# We only apply this to known Red Hat multilib arches, per bug #181335
case $(uname -i) in
  i386 | x86_64 | ppc | ppc64 | s390 | s390x | sparc | sparc64 )
    mv %{buildroot}/usr/include/mysql/my_config.h %{buildroot}/usr/include/mysql/my_config_$(uname -i).h
    install -m 644 %{SOURCE5} %{buildroot}/usr/include/mysql/
    ;;
  *)
    ;;
esac

# cmake generates some completely wacko references to -lprobes_mysql when
# building with dtrace support.  Haven't found where to shut that off,
# so resort to this blunt instrument.  While at it, let's not reference
# libmysqlclient_r anymore either.
sed -e 's/-lprobes_mysql//' -e 's/-lmysqlclient_r/-lmysqlclient/' \
  %{buildroot}%{_bindir}/mysql_config >mysql_config.tmp
cp -f mysql_config.tmp %{buildroot}%{_bindir}/mysql_config
chmod 755 %{buildroot}%{_bindir}/mysql_config

# install INFO_SRC, INFO_BIN into libdir (upstream thinks these are doc files,
# but that's pretty wacko --- see also mysql-file-contents.patch)
install -m 644 Docs/INFO_SRC %{buildroot}%{_libdir}/mysql/
install -m 644 Docs/INFO_BIN %{buildroot}%{_libdir}/mysql/

mkdir -p %{buildroot}/var/log
touch %{buildroot}/var/log/mysqld.log

mkdir -p %{buildroot}/var/run/mysqld
install -m 0755 -d %{buildroot}/var/lib/mysql

mkdir -p %{buildroot}/etc
install -m 0644 %{SOURCE3} %{buildroot}/etc/my.cnf

%if 0%{?fedora} < 15
install -m 0755 -D %{SOURCE2} %{buildroot}/etc/rc.d/init.d/mysqld
%endif

%if 0%{?fedora} > 14
# install systemd unit files and scripts for handling server startup
mkdir -p %{buildroot}%{_unitdir}
install -m 644 %{SOURCE11} %{buildroot}%{_unitdir}/
install -m 755 %{SOURCE12} %{buildroot}%{_libexecdir}/
install -m 755 %{SOURCE13} %{buildroot}%{_libexecdir}/

mkdir -p %{buildroot}%{_prefix}/lib/tmpfiles.d
install -m 0644 %{SOURCE10} %{buildroot}%{_prefix}/lib/tmpfiles.d/mysql.conf
%endif

# Fix scripts for multilib safety
mv %{buildroot}%{_bindir}/mysqlbug %{buildroot}%{_libdir}/mysql/mysqlbug
install -m 0755 scriptstub %{buildroot}%{_bindir}/mysqlbug
mv %{buildroot}%{_bindir}/mysql_config %{buildroot}%{_libdir}/mysql/mysql_config
install -m 0755 scriptstub %{buildroot}%{_bindir}/mysql_config

# Remove libmysqld.a, install libmysqld.so
rm -f %{buildroot}%{_libdir}/mysql/libmysqld.a
install -m 0755 libmysqld/work/libmysqld.so.0.0.1 %{buildroot}%{_libdir}/mysql/libmysqld.so.0.0.1
ln -s libmysqld.so.0.0.1 %{buildroot}%{_libdir}/mysql/libmysqld.so.0
ln -s libmysqld.so.0 %{buildroot}%{_libdir}/mysql/libmysqld.so

# install my-55-terse.cnf
install -m 0644 %{SOURCE100} ${RPM_BUILD_ROOT}%{_sysconfdir}/my.cnf

# logrotate
mkdir -p %{buildroot}/etc/logrotate.d/
install -m 0644 %{SOURCE102} %{buildroot}/etc/logrotate.d/mysqld

# libmysqlclient_r is no more.  Upstream tries to replace it with symlinks
# but that really doesn't work (wrong soname in particular).  We'll keep
# just the devel libmysqlclient_r.so link, so that rebuilding without any
# source change is enough to get rid of dependency on libmysqlclient_r.
rm -f %{buildroot}%{_libdir}/mysql/libmysqlclient_r.so*
ln -s libmysqlclient.so %{buildroot}%{_libdir}/mysql/libmysqlclient_r.so

# mysql-test includes one executable that doesn't belong under /usr/share,
# so move it and provide a symlink
mv %{buildroot}%{_datadir}/mysql-test/lib/My/SafeProcess/my_safe_process %{buildroot}%{_bindir}
ln -s ../../../../../bin/my_safe_process %{buildroot}%{_datadir}/mysql-test/lib/My/SafeProcess/my_safe_process

# not needed in rpm package
rm -f %{buildroot}%{_bindir}/mysqlaccess.conf
rm -f %{buildroot}%{_bindir}/mysql_embedded
rm -f %{buildroot}%{_libdir}/mysql/*.a
rm -f %{buildroot}%{_datadir}/mysql/binary-configure
rm -f %{buildroot}%{_datadir}/mysql/magic
rm -f %{buildroot}%{_datadir}/mysql/mysql.server
rm -f %{buildroot}%{_datadir}/mysql/mysqld_multi.server
rm -rf %{buildroot}%{_datadir}/mysql/solaris
rm -f %{buildroot}%{_mandir}/man1/comp_err.1*
rm -f %{buildroot}%{_mandir}/man1/mysql-stress-test.pl.1*
rm -f %{buildroot}%{_mandir}/man1/mysql-test-run.pl.1*

# put logrotate script where it needs to be
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
mv %{buildroot}%{_datadir}/mysql/mysql-log-rotate %{buildroot}%{_sysconfdir}/logrotate.d/mysqld
chmod 644 %{buildroot}%{_sysconfdir}/logrotate.d/mysqld

mkdir -p %{buildroot}/etc/ld.so.conf.d
echo "%{_libdir}/mysql" > %{buildroot}/etc/ld.so.conf.d/%{name}-%{_arch}.conf

# Back to src dir
popd

# copy additional docs into build tree so %%doc will find them
cp %{SOURCE6} README.mysql-docs
cp %{SOURCE7} README.mysql-license

# Install the list of skipped tests to be available for user runs
install -m 0644 mysql-test/rh-skipped-tests.list %{buildroot}%{_datadir}/mysql-test

# Upstream bugs: http://bugs.mysql.com/68517 http://bugs.mysql.com/68519  http://bugs.mysql.com/68521
chmod 0644 %{buildroot}/usr/share/mysql/innodb_memcached_config.sql
find %{buildroot}/usr/share/mysql-test/{r,suite,t} -type f -print0 | xargs --null chmod 0644
chmod 0644 %{buildroot}/usr/share/mysql-test/include/{start_mysqld,shutdown_mysqld,check_ipv4_mapped}.inc
for f in std_data/checkDBI_DBD-mysql.pl suite/engines/rr_trx/run_stress_tx_rr.pl \
         suite/funcs_1/lib/DataGen_local.pl suite/funcs_1/lib/DataGen_modify.pl \
         suite/funcs_2/lib/gen_charset_utf8.pl  suite/opt_trace/validate_json.py \
         suite/rpl/extension/bhs.pl suite/rpl/extension/checksum.pl ; do
    chmod 0755 %{buildroot}/usr/share/mysql-test/$f
done
for f in bench-count-distinct bench-init.pl compare-results copy-db crash-me \
         innotest1 innotest1a innotest1b innotest2 innotest2a innotest2b \
         run-all-tests server-cfg test-alter-table test-ATIS \
         test-big-tables test-connect test-create test-insert \
         test-select test-transactions test-wisconsin ; do
    chmod 0755 %{buildroot}/usr/share/sql-bench/$f
done
dos2unix -k %{buildroot}/usr/share/sql-bench/innotest*

# These are in fact identical
rm %{buildroot}/usr/share/man/man1/{mysqltest,mysql_client_test}_embedded.1
cp -p %{buildroot}/usr/share/man/man1/mysqltest.1 %{buildroot}/usr/share/man/man1/mysqltest_embedded.1
cp -p %{buildroot}/usr/share/man/man1/mysql_client_test.1 %{buildroot}/usr/share/man/man1/mysql_client_test_embedded.1

mkdir %{buildroot}%{_sysconfdir}/my.cnf.d

%check
pushd build
# Hack to let 32- and 64-bit tests run concurrently on same build machine
case $(uname -m) in
    ppc64 | s390x | x86_64 | sparc64 )
        MTR_BUILD_THREAD=7
        ;;
    *)
        MTR_BUILD_THREAD=11
        ;;
esac

export MTR_BUILD_THREAD

make test VERBOSE=1

# The cmake build scripts don't provide any simple way to control the
# options for mysql-test-run, so ignore the make target and just call it
# manually.  Nonstandard options chosen are:
# --force to continue tests after a failure
# no retries please
# test SSL with 
# skip tests that are listed in rh-skipped-tests.list
# avoid redundant test runs with --binlog-format=mixed
# increase timeouts to prevent unwanted failures during mass rebuilds
# todo: reenable --ssl
pushd mysql-test
cp ../../mysql-test/rh-skipped-tests.list .
./mtr \
    --mem --parallel=auto --force --retry=0 \
    --skip-test-list=rh-skipped-tests.list \
    --mysqld=--binlog-format=mixed \
    --suite-timeout=720 --testcase-timeout=30 --max-test-fail=0 --clean-vardir
rm -rf var/*
popd

%pre server
/usr/sbin/groupadd -g 27 -o -r mysql >/dev/null 2>&1 || :
/usr/sbin/useradd -M -N -g mysql -o -r -d /var/lib/mysql -s /bin/bash \
  -c "MySQL Server" -u 27 mysql >/dev/null 2>&1 || :

%post libs -p /sbin/ldconfig

%post server
%if 0%{?fedora} < 15
if [ $1 = 1 ]; then
    /sbin/chkconfig --add mysqld
fi
%else
%if 0%{?systemd_post:1}
%systemd_post mysqld.service
%else
if [ $1 = 1 ]; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi
%endif
%endif
/bin/touch /var/log/mysqld.log

# Handle upgrading from SysV initscript to native systemd unit.
# We can tell if a SysV version of mysql was previously installed by
# checking to see if the initscript is present.
%triggerun server -- mysql-server
%if 0%{?fedora} > 14
if [ -f /etc/rc.d/init.d/mysqld ]; then
  # Save the current service runlevel info
  # User must manually run systemd-sysv-convert --apply mysqld
  # to migrate them to systemd targets
  /usr/bin/systemd-sysv-convert --save mysqld >/dev/null 2>&1 || :

  # Run these because the SysV package being removed won't do them
  /sbin/chkconfig --del mysqld >/dev/null 2>&1 || :
  /bin/systemctl try-restart mysqld.service >/dev/null 2>&1 || :
fi
%endif

%preun server
%if 0%{?fedora} < 15
if [ $1 = 0 ]; then
    /sbin/service mysqld stop >/dev/null 2>&1
    /sbin/chkconfig --del mysqld
fi
%else
%if 0%{?systemd_preun:1}
%systemd_preun mysqld.service
%else
if [ $1 = 0 ]; then
  # Package removal, not upgrade
  /bin/systemctl --no-reload disable mysqld.service >/dev/null 2>&1 || :
  /bin/systemctl stop mysqld.service >/dev/null 2>&1 || :
fi
%endif
%endif

%postun libs -p /sbin/ldconfig

%postun server
%if 0%{?fedora} < 15
if [ $1 -ge 1 ]; then
    /sbin/service mysqld condrestart >/dev/null 2>&1 || :
fi
%else
%if 0%{?systemd_postun_with_restart:1}
%systemd_postun_with_restart mysqld.service
%else
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ]; then
  # Package upgrade, not uninstall
  /bin/systemctl try-restart mysqld.service >/dev/null 2>&1 || :
fi
%endif
%endif


%files
%doc README COPYING README.mysql-license
%doc README.mysql-docs

%{_bindir}/msql2mysql
%{_bindir}/mysql
%{_bindir}/mysql_config
%{_bindir}/mysql_config_editor
%{_bindir}/mysql_find_rows
%{_bindir}/mysql_waitpid
%{_bindir}/mysqlaccess
%{_bindir}/mysqladmin
%{_bindir}/mysqlbinlog
%{_bindir}/mysqlcheck
%{_bindir}/mysqldump
%{_bindir}/mysqlimport
%{_bindir}/mysqlshow
%{_bindir}/mysqlslap
%{_bindir}/my_print_defaults

%{_mandir}/man1/msql2mysql.1*
%{_mandir}/man1/mysql.1*
%{_mandir}/man1/mysql_config.1*
%{_mandir}/man1/mysql_config_editor.1*
%{_mandir}/man1/mysql_find_rows.1*
%{_mandir}/man1/mysql_waitpid.1*
%{_mandir}/man1/mysqlaccess.1*
%{_mandir}/man1/mysqladmin.1*
%{_mandir}/man1/mysqlbinlog.1*
%{_mandir}/man1/mysqlcheck.1*
%{_mandir}/man1/mysqldump.1*
%{_mandir}/man1/mysqlimport.1*
%{_mandir}/man1/mysqlshow.1*
%{_mandir}/man1/mysqlslap.1*
%{_mandir}/man1/my_print_defaults.1*

%{_libdir}/mysql/mysql_config

%files libs
%doc README COPYING README.mysql-license
# although the default my.cnf contains only server settings, we put it in the
# libs package because it can be used for client settings too.
%config(noreplace) /etc/my.cnf
%dir %{_libdir}/mysql
%{_libdir}/mysql/libmysqlclient.so.*
%config(noreplace) /etc/ld.so.conf.d/*

%files common
%dir %{_sysconfdir}/my.cnf.d
%dir %{_datadir}/mysql
%{_datadir}/mysql/english
%lang(bg) %{_datadir}/mysql/bulgarian
%lang(cs) %{_datadir}/mysql/czech
%lang(da) %{_datadir}/mysql/danish
%lang(nl) %{_datadir}/mysql/dutch
%lang(et) %{_datadir}/mysql/estonian
%lang(fr) %{_datadir}/mysql/french
%lang(de) %{_datadir}/mysql/german
%lang(el) %{_datadir}/mysql/greek
%lang(hu) %{_datadir}/mysql/hungarian
%lang(it) %{_datadir}/mysql/italian
%lang(ja) %{_datadir}/mysql/japanese
%lang(ko) %{_datadir}/mysql/korean
%lang(no) %{_datadir}/mysql/norwegian
%lang(no) %{_datadir}/mysql/norwegian-ny
%lang(pl) %{_datadir}/mysql/polish
%lang(pt) %{_datadir}/mysql/portuguese
%lang(ro) %{_datadir}/mysql/romanian
%lang(ru) %{_datadir}/mysql/russian
%lang(sr) %{_datadir}/mysql/serbian
%lang(sk) %{_datadir}/mysql/slovak
%lang(es) %{_datadir}/mysql/spanish
%lang(sv) %{_datadir}/mysql/swedish
%lang(uk) %{_datadir}/mysql/ukrainian
%{_datadir}/mysql/charsets

%files server
%doc README COPYING README.mysql-license
%{_bindir}/myisamchk    
%{_bindir}/myisam_ftdump
%{_bindir}/myisamlog
%{_bindir}/myisampack
%{_bindir}/mysql_convert_table_format
%{_bindir}/mysql_fix_extensions
%{_bindir}/mysql_install_db
%{_bindir}/mysql_plugin
%{_bindir}/mysql_secure_installation
%{_bindir}/mysql_setpermission
%{_bindir}/mysql_tzinfo_to_sql
%{_bindir}/mysql_upgrade
%{_bindir}/mysql_zap
%{_bindir}/mysqlbug
%{_bindir}/mysqldumpslow
%{_bindir}/mysqld_multi
%{_bindir}/mysqld_safe
%{_bindir}/mysqlhotcopy
%{_bindir}/mysqltest
%{_bindir}/innochecksum
%{_bindir}/perror
%{_bindir}/replace
%{_bindir}/resolve_stack_dump
%{_bindir}/resolveip

/usr/libexec/mysqld

%{_libdir}/mysql/INFO_SRC
%{_libdir}/mysql/INFO_BIN

%{_libdir}/mysql/mysqlbug

%{_libdir}/mysql/plugin

%{_mandir}/man1/myisamchk.1*
%{_mandir}/man1/myisamlog.1*
%{_mandir}/man1/myisampack.1*
%{_mandir}/man1/mysql_convert_table_format.1*
%{_mandir}/man1/myisam_ftdump.1*
%{_mandir}/man1/mysql.server.1*
%{_mandir}/man1/mysql_fix_extensions.1*
%{_mandir}/man1/mysql_install_db.1*
%{_mandir}/man1/mysql_plugin.1*
%{_mandir}/man1/mysql_secure_installation.1*
%{_mandir}/man1/mysql_upgrade.1*
%{_mandir}/man1/mysql_zap.1*
%{_mandir}/man1/mysqlbug.1*
%{_mandir}/man1/mysqldumpslow.1*
%{_mandir}/man1/mysqld_multi.1*
%{_mandir}/man1/mysqld_safe.1*
%{_mandir}/man1/mysqlhotcopy.1*
%{_mandir}/man1/mysqlman.1*
%{_mandir}/man1/mysql_setpermission.1*
%{_mandir}/man1/mysqltest.1*
%{_mandir}/man1/innochecksum.1*
%{_mandir}/man1/perror.1*
%{_mandir}/man1/replace.1*
%{_mandir}/man1/resolve_stack_dump.1*
%{_mandir}/man1/resolveip.1*
%{_mandir}/man1/mysql_tzinfo_to_sql.1*
%{_mandir}/man8/mysqld.8*

%{_datadir}/mysql/dictionary.txt
%{_datadir}/mysql/errmsg-utf8.txt
%{_datadir}/mysql/fill_help_tables.sql
%{_datadir}/mysql/innodb_memcached_config.sql
%{_datadir}/mysql/mysql_security_commands.sql
%{_datadir}/mysql/mysql_system_tables.sql
%{_datadir}/mysql/mysql_system_tables_data.sql
%{_datadir}/mysql/mysql_test_data_timezone.sql
%{_datadir}/mysql/my-*.cnf

%if 0%{?fedora} > 14
%{_unitdir}/mysqld.service
%{_libexecdir}/mysqld-prepare-db-dir
%{_libexecdir}/mysqld-wait-ready

%{_prefix}/lib/tmpfiles.d/mysql.conf

%else
/etc/rc.d/init.d/mysqld
%endif

%attr(0755,mysql,mysql) %dir /var/run/mysqld
%attr(0755,mysql,mysql) %dir /var/lib/mysql
%attr(0755,mysql,mysql) %dir %{_localstatedir}/lib/mysqltmp/
%attr(0640,mysql,mysql) %config(noreplace) %verify(not md5 size mtime) /var/log/mysqld.log
%config(noreplace) %{_sysconfdir}/logrotate.d/mysqld
%attr(0755,mysql,mysql) %dir /var/log/mysql/

%files devel
%doc README COPYING README.mysql-license
%{_includedir}/mysql
/usr/share/aclocal/mysql.m4
%{_libdir}/mysql/libmysqlclient.so
%{_libdir}/mysql/libmysqlclient_r.so

%files embedded
%doc README COPYING README.mysql-license
%{_libdir}/mysql/libmysqld.so.*

%files embedded-devel
%doc README COPYING README.mysql-license
%{_libdir}/mysql/libmysqld.so
%{_bindir}/mysql_client_test_embedded
%{_bindir}/mysqltest_embedded
%{_mandir}/man1/mysql_client_test_embedded.1*
%{_mandir}/man1/mysqltest_embedded.1*

%files bench
%doc README COPYING README.mysql-license
%{_datadir}/sql-bench

%files test
%doc README COPYING README.mysql-license
%{_bindir}/mysql_client_test
%{_bindir}/my_safe_process
%attr(-,mysql,mysql) %{_datadir}/mysql-test
%{_mandir}/man1/mysql_client_test.1*

%changelog
* Mon Dec 01 2014 Ben Harper <ben.harper@rackspace.com> -  5.6.22-1.ius
- Latest upstream

* Wed Nov 12 2014 Ben Harper <ben.harper@rackspace.com> - 5.6.21-3.ius
- change WITH_EDITLINE from system to bundled see LP bug 1392050

* Mon Nov 10 2014 Ben Harper <ben.harper@rackspace.com> - 5.6.21-2.ius
- update mysql.init, see LP bug 1390900

* Wed Sep 24 2014 Carl George <carl.george@rackspace.com> - 5.6.21-1.ius
- Latest upstream

* Mon Aug 04 2014 Ben Harper <ben.harper@rackspace.com> - 5.6.20-2.ius
- remove dtrace dependencies

* Fri Aug 01 2014 Ben Harper <ben.harper@rackspace.com> - 5.6.20-1.ius
- Latest sources from upstream
- updated Patch25 and Patch34

* Tue Jun 03 2014 Ben Harper <ben.harper@rackspace.com> - 5.6.19-1.ius
- Latest sources from upstream

* Thu Apr 24 2014 Ben Harper <ben.harper@rackspace.com> - 5.6.17-3.ius
- added patch99 and updated cmake options to include '-DWITH_INNODB_MEMCACHED=ON' based on LP bug #1117674 and MySQL bug #72353
- added /var/log/mysql/ to %files
- added DCOMPILATION_COMMENT

* Wed Apr 09 2014 Ben Harper <ben.harper@rackspace.com> - 5.6.17-2.ius
- updated my-56-terse.cnf

* Wed Apr 02 2014 Ben Harper <ben.harper@rackspace.com> - 5.6.17-1.ius
- Latest sources from upstream
- disable Patch28, patched upstream
- update Patch25, mostly patched upstream
- updated my-56-terse.cnf

* Tue Mar 04 2014 Ben Harper <ben.harper@rackspace.com> - 5.6.16-1.ius
- Latest sources from upstream
- various updates to insure the use of /usr/share/mysql and not /usr/share/mysql56u
- added my-56-terse.cnf, my-56-verbose.cnf and mysql.logrotate
- updated mysql.init not to overwrite our my.cnf with stock my.cnf
- disable Patch30, Patch31 and Patch32, patched upstream
- update Patch25 from http://repo.mysql.com/yum/mysql-5.6-community/el/6/SRPMS/mysql-community-5.6.16-1.el6.src.rpm
- update Patch29, mostly patched upstream


* Mon Jan 20 2014 Ben Harper <ben.harper@rackspace.com> - 5.6.15-2.ius
- add Patch28-34 from Fedora http://koji.fedoraproject.org/koji/buildinfo?buildID=485187
- and --clean-vardir for test suite to attempt to correct some issues in build system
- updated Patch25 from http://repo.mysql.com/yum/mysql-5.6-community/el/6/SRPMS/mysql-community-5.6.15-1.el6.src.rpm

* Tue Jan 14 2014 Ben Harper <ben.harper@rackspace.com> - 5.6.15-1.ius
- Latest sources from upstream
- changed Source0 to URL to tarball since Oracle has removed non-free documentation and tarball is straightforward to download
- disabled Patch15, Patch19 and Patch20, patched upstream

* Thu Oct 31 2013 Ben Harper <ben.harper@rackspace.com> - 5.6.14-2.ius
- disabled with_shared_lib_major_hack as libmysqlclient.so version is now 18.1.0

* Thu Sep 26 2013 Ben Harper <ben.harper@rackspace.com> - 5.6.14-1.ius
- porting from http://home.online.no/~bjornmu/fedora/mysql-community-5.6.13-1.fc19.src.rpm

* Tue Apr 30 2013 Bjorn Munch <bjorn.munch@oracle.com> 5.6.11-1
- renaming to mysql-community
- hardened_build (bz #955199)

* Tue Apr 23 2013 Bjorn Munch <bjorn.munch@oracle.com> 5.6.11-0.1
- 5.6.11
- Release notes: 
   https://dev.mysql.com/doc/relnotes/mysql/5.6/en/news-5-6-11.html
- zlib patch now upstream
- remove probes.o from linking of shared lib
- rediff cipher patch
- my.cnf.d support

* Fri Apr 12 2013 Bjorn Munch <bjorn.munch@oracle.com> 5.6.10-1
- Update to MySQL 5.6.10
- Release notes:
   https://dev.mysql.com/doc/relnotes/mysql/5.6/en/news-5-6-10.html
- Build outside source
- readline -> libedit
- Move mtr to %%check and drop ssl option for now
- Some initial rpmlint clean up
- Use %%filter_setup
- Change source0 comments
- Adjust req and buildreq
- Update patches
- Add zlib, libmysql-version, libedit and install patches
- Move man pages to correct subpackages
- Rediff patches
- Ship .rpmlintrc file
- Add useful comments in my.cnf
- Allow server to be installed without client side
- Separate -lib and -common sub-packages

* Wed Mar 20 2013 Honza Horak <hhorak@redhat.com> 5.5.30-5
- Renaming package MySQL to community-mysql to handle issues
  introduced by case-insensitive operations of yum and for proper
  prioritizing mariadb over community-mysql

* Tue Feb 12 2013 Honza Horak <hhorak@redhat.com> 5.5.30-1
- Update to MySQL 5.5.30, for various fixes described at
  http://dev.mysql.com/doc/relnotes/mysql/5.5/en/news-5-5-30.html

* Tue Feb 12 2013 Honza Horak <hhorak@redhat.com> 5.5.29-3
- Use real- prefix for cross-package requirements

* Mon Feb 11 2013 Honza Horak <hhorak@redhat.com> 5.5.29-2
- Provide own symbols with real- prefix to distinguish packages from other
  MySQL implementations unambiguously

* Wed Jan  2 2013 Tom Lane <tgl@redhat.com> 5.5.29-1
- Update to MySQL 5.5.29, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-29.html
- Fix inaccurate default for socket location in mysqld-wait-ready
Resolves: #890535

* Thu Dec  6 2012 Honza Horak <hhorak@redhat.com> 5.5.28-3
- Rebase patches to not leave backup files when not applied smoothly
- Use --no-backup-if-mismatch to prevent including backup files

* Wed Dec  5 2012 Tom Lane <tgl@redhat.com> 5.5.28-2
- Add patch for CVE-2012-5611
Resolves: #883642
- Widen DH key length from 512 to 1024 bits to meet minimum requirements
  of FIPS 140-2
Related: #877124

* Sat Sep 29 2012 Tom Lane <tgl@redhat.com> 5.5.28-1
- Update to MySQL 5.5.28, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-28.html
- Clean up partially-created database files when mysql_install_db fails
Related: #835131
- Honor user and group settings from service file in mysqld-prepare-db-dir
Resolves: #840431
- Export THR_KEY_mysys as a workaround for inadequate threading support
Resolves: #846602
- Adopt new systemd macros for server package install/uninstall triggers
Resolves: #850222
- Use --no-defaults when invoking mysqladmin to wait for the server to start
Related: #855704

* Sun Aug  5 2012 Tom Lane <tgl@redhat.com> 5.5.27-1
- Update to MySQL 5.5.27, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-27.html

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.5.25a-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul  6 2012 Tom Lane <tgl@redhat.com> 5.5.25a-1
- Update to MySQL 5.5.25a, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-25a.html
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-25.html
- Don't use systemd's Restart feature; rely on mysqld_safe instead
Resolves: #832029

* Mon Jun 11 2012 Tom Lane <tgl@redhat.com> 5.5.24-1
- Update to MySQL 5.5.24, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-24.html
  including the fix for CVE-2012-2122
Resolves: #830680
- Tweak logrotate script to put the right permissions on mysqld.log
- Minor specfile fixes for recent packaging guidelines changes

* Sat Apr 28 2012 Tom Lane <tgl@redhat.com> 5.5.23-1
- Update to MySQL 5.5.23, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-23.html

* Sat Mar 24 2012 Tom Lane <tgl@redhat.com> 5.5.22-1
- Update to MySQL 5.5.22, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-22.html
- Turn on PrivateTmp in service file
Resolves: #782513
- Comment out the contents of /etc/logrotate.d/mysqld, so that manual
  action is needed to enable log rotation.  Given the multiple ways in
  which the rotation script can fail, it seems imprudent to try to make
  it run by default.
Resolves: #799735

* Tue Mar 20 2012 Honza Horak <hhorak@redhat.com> 5.5.21-3
- Revise mysql_plugin test patch so it moves plugin files to
  a temporary directory (better solution to #789530)

* Tue Mar 13 2012 Honza Horak <hhorak@redhat.com> 5.5.21-2
- Fix ssl-related tests to specify expected cipher explicitly
Related: #789600
- Fix several strcpy calls to check destination size

* Mon Feb 27 2012 Tom Lane <tgl@redhat.com> 5.5.21-1
- Update to MySQL 5.5.21, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-21.html
- Hack openssl regression test to still work with rawhide's openssl
- Fix assorted failures in post-install regression tests (mysql-test RPM)
Resolves: #789530

* Fri Feb 10 2012 Tom Lane <tgl@redhat.com> 5.5.20-2
- Revise our test-disabling method to make it possible to disable tests on a
  platform-specific basis, and also to get rid of mysql-disable-test.patch,
  which broke in just about every upstream update (Honza Horak)
- Disable cycle-counter-dependent regression tests on ARM, since there is
  not currently any support for that in Fedora ARM kernels
Resolves: #773116
- Add some comments to mysqld.service documenting how to customize it
Resolves: #785243

* Fri Jan 27 2012 Tom Lane <tgl@redhat.com> 5.5.20-1
- Update to MySQL 5.5.20, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-20.html
  as well as security fixes described at
  http://www.oracle.com/technetwork/topics/security/cpujan2012-366304.html
Resolves: #783828
- Re-include the mysqld logrotate script, now that it's not so bogus
Resolves: #547007

* Wed Jan  4 2012 Tom Lane <tgl@redhat.com> 5.5.19-1
- Update to MySQL 5.5.19, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-19.html

* Sun Nov 20 2011 Tom Lane <tgl@redhat.com> 5.5.18-1
- Update to MySQL 5.5.18, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-18.html

* Sat Nov 12 2011 Tom Lane <tgl@redhat.com> 5.5.17-1
- Update to MySQL 5.5.17, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-17.html
- Get rid of version-number assumption in sysv-to-systemd conversion trigger

* Wed Nov 02 2011 Honza Horak <hhorak@redhat.com> 5.5.16-4
- Don't assume all ethernet devices are named ethX
Resolves: #682365
- Exclude user definition from my.cnf, user is defined in mysqld.service now
Resolves: #661265

* Sun Oct 16 2011 Tom Lane <tgl@redhat.com> 5.5.16-3
- Fix unportable usage associated with va_list arguments
Resolves: #744707

* Sun Oct 16 2011 Tom Lane <tgl@redhat.com> 5.5.16-2
- Update to MySQL 5.5.16, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-16.html

* Fri Jul 29 2011 Tom Lane <tgl@redhat.com> 5.5.15-2
- Update to MySQL 5.5.15, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-15.html

* Wed Jul 27 2011 Tom Lane <tgl@redhat.com> 5.5.14-3
- Convert to systemd startup support (no socket activation, for now anyway)
Related: #714426

* Tue Jul 12 2011 Tom Lane <tgl@redhat.com> 5.5.14-2
- Remove make_scrambled_password and make_scrambled_password_323 from mysql.h,
  since we're not allowing clients to call those functions anyway
Related: #690346

* Mon Jul 11 2011 Tom Lane <tgl@redhat.com> 5.5.14-1
- Update to MySQL 5.5.14, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-14.html

* Wed Jul  6 2011 Tom Lane <tgl@redhat.com> 5.5.13-2
- Remove erroneously-included Default-Start line from LSB init block
Resolves: #717024

* Thu Jun  2 2011 Tom Lane <tgl@redhat.com> 5.5.13-1
- Update to MySQL 5.5.13, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-13.html

* Tue May 10 2011 Tom Lane <tgl@redhat.com> 5.5.12-1
- Update to MySQL 5.5.12, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-12.html

* Tue May 10 2011 Tom Lane <tgl@redhat.com> 5.5.10-3
- Add LSB init block to initscript, to ensure sane ordering at system boot
Resolves: #703214
- Improve initscript start action to notice when mysqladmin is failing
  because of configuration problems
Related: #703476
- Remove exclusion of "gis" regression test, since upstream bug 59908
  is fixed (for some value of "fixed") as of 5.5.10.

* Wed Mar 23 2011 Tom Lane <tgl@redhat.com> 5.5.10-2
- Add my_make_scrambled_password to the list of symbols exported by
  libmysqlclient.so.  Needed at least by pure-ftpd.

* Mon Mar 21 2011 Tom Lane <tgl@redhat.com> 5.5.10-1
- Update to MySQL 5.5.10, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-10.html
  Note that this includes a rather belated soname version bump for
  libmysqlclient.so, from .16 to .18
- Add tmpfiles.d config file so that /var/run/mysqld is recreated at boot
  (only needed in Fedora 15 and later)
Resolves: #658938

* Wed Feb 16 2011 Tom Lane <tgl@redhat.com> 5.5.9-2
- Disable a regression test that is now showing platform-dependent results
Resolves: #674253

* Sat Feb 12 2011 Tom Lane <tgl@redhat.com> 5.5.9-1
- Update to MySQL 5.5.9, for various fixes described at
  http://dev.mysql.com/doc/refman/5.5/en/news-5-5-9.html
- Add %%{?_isa} to cross-subpackage Requires, per latest packaging guidelines

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.5.8-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Feb  4 2011 Tom Lane <tgl@redhat.com> 5.5.8-9
- Support s390/s390x in performance schema's cycle-counting functions
  (needed to make regression tests pass on these platforms)

* Thu Feb  3 2011 Tom Lane <tgl@redhat.com> 5.5.8-8
- PPC64 floating-point differences are not masked by -ffloat-store after all,
  so let's just disable gis regression test till upstream makes it less picky
Resolves: #674253
- Add __perllib_requires setting to make rpm 4.9 do what we need

* Wed Feb  2 2011 Tom Lane <tgl@redhat.com> 5.5.8-7
- Work around some portability issues on PPC64
Resolves: #674253

* Thu Jan 20 2011 Tom Lane <tgl@redhat.com> 5.5.8-6
- Remove no-longer-needed special switches in CXXFLAGS, per yesterday's
  discussion in fedora-devel about -fexceptions.
- Rebuild needed anyway to check compatibility with latest systemtap.

* Thu Jan 13 2011 Tom Lane <tgl@redhat.com> 5.5.8-5
- Fix failure to honor MYSQL_HOME environment variable
Resolves: #669364

* Thu Jan 13 2011 Tom Lane <tgl@redhat.com> 5.5.8-4
- Fix crash during startup of embedded mysqld library
Resolves: #667365

* Mon Jan  3 2011 Tom Lane <tgl@redhat.com> 5.5.8-3
- my_print_help, load_defaults, free_defaults, and handle_options all turn
  out to be documented/recommended in Paul DuBois' MySQL book, so we'd better
  consider them part of the de-facto API.
Resolves: #666728

* Mon Dec 27 2010 Tom Lane <tgl@redhat.com> 5.5.8-2
- Add mysql_client_errors[] to the set of exported libmysqlclient symbols;
  needed by PHP.

* Thu Dec 23 2010 Tom Lane <tgl@redhat.com> 5.5.8-1
- Update to MySQL 5.5.8 (major version bump).  Note this includes removal
  of libmysqlclient_r.so.
- Add a linker version script to hide libmysqlclient functions that aren't
  part of the documented API.

* Mon Nov  1 2010 Tom Lane <tgl@redhat.com> 5.1.52-1
- Update to MySQL 5.1.52, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-52.html
Resolves: #646569

* Thu Oct  7 2010 Tom Lane <tgl@redhat.com> 5.1.51-2
- Re-disable the outfile_loaddata test, per report from Dan Horak.

* Wed Oct  6 2010 Tom Lane <tgl@redhat.com> 5.1.51-1
- Update to MySQL 5.1.51, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-51.html

* Sat Aug 28 2010 Tom Lane <tgl@redhat.com> 5.1.50-2
- Include my_compiler.h in distribution, per upstream bug #55846.
  Otherwise PHP, for example, won't build.

* Sat Aug 28 2010 Tom Lane <tgl@redhat.com> 5.1.50-1
- Update to MySQL 5.1.50, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-50.html
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-49.html

* Wed Jul 14 2010 Tom Lane <tgl@redhat.com> 5.1.48-3
- Fix FTBFS with gcc 4.5.
Related: #614293

* Tue Jul 13 2010 Tom Lane <tgl@redhat.com> 5.1.48-2
- Duplicate COPYING and EXCEPTIONS-CLIENT in -libs and -embedded subpackages,
  to ensure they are available when any subset of mysql RPMs are installed,
  per revised packaging guidelines
- Allow init script's STARTTIMEOUT/STOPTIMEOUT to be overridden from sysconfig
Related: #609734

* Mon Jun 21 2010 Tom Lane <tgl@redhat.com> 5.1.48-1
- Update to MySQL 5.1.48, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-48.html
  including a fix for CVE-2010-2008
Related: #614214

* Fri Jun  4 2010 Tom Lane <tgl@redhat.com> 5.1.47-2
- Add back "partition" storage engine
Resolves: #597390
- Fix broken "federated" storage engine plugin
Related: #587170
- Read all certificates in SSL certificate files, to support chained certs
Related: #598656

* Mon May 24 2010 Tom Lane <tgl@redhat.com> 5.1.47-1
- Update to MySQL 5.1.47, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-47.html
  including fixes for CVE-2010-1848, CVE-2010-1849, CVE-2010-1850
Resolves: #592862
Resolves: #583717
- Create mysql group explicitly in pre-server script, to ensure correct GID
Related: #594155

* Sat Apr 24 2010 Tom Lane <tgl@redhat.com> 5.1.46-1
- Update to MySQL 5.1.46, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-46.html

* Thu Mar 25 2010 Tom Lane <tgl@redhat.com> 5.1.45-2
- Fix multiple problems described in upstream bug 52019, because regression
  tests fail on PPC if we don't.

* Wed Mar 24 2010 Tom Lane <tgl@redhat.com> 5.1.45-1
- Update to MySQL 5.1.45, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-45.html

* Sun Feb 21 2010 Tom Lane <tgl@redhat.com> 5.1.44-2
- Add "Obsoletes: mysql-cluster" to fix upgrade-in-place from F-12
- Bring init script into some modicum of compliance with Fedora/LSB standards
Related: #557711
Related: #562749

* Sat Feb 20 2010 Tom Lane <tgl@redhat.com> 5.1.44-1
- Update to MySQL 5.1.44, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-44.html
- Remove mysql.info, which is not freely redistributable
Resolves: #560181
- Revert broken upstream fix for their bug 45058
Resolves: #566547

* Sat Feb 13 2010 Tom Lane <tgl@redhat.com> 5.1.43-2
- Remove mysql-cluster, which is no longer supported by upstream in this
  source distribution.  If we want it we'll need a separate SRPM for it.

* Fri Feb 12 2010 Tom Lane <tgl@redhat.com> 5.1.43-1
- Update to MySQL 5.1.43, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-43.html

* Fri Jan 29 2010 Tom Lane <tgl@redhat.com> 5.1.42-7
- Add backported patch for CVE-2008-7247 (upstream bug 39277)
Related: #543619
- Use non-expired certificates for SSL testing (upstream bug 50702)

* Tue Jan 26 2010 Tom Lane <tgl@redhat.com> 5.1.42-6
- Emit explicit error message if user tries to build RPM as root
Related: #558915

* Wed Jan 20 2010 Tom Lane <tgl@redhat.com> 5.1.42-5
- Correct Source0: tag and comment to reflect how to get the tarball

* Fri Jan  8 2010 Tom Lane <tgl@redhat.com> 5.1.42-4
- Disable symbolic links by default in /etc/my.cnf
Resolves: #553652

* Tue Jan  5 2010 Tom Lane <tgl@redhat.com> 5.1.42-3
- Remove static libraries (.a files) from package, per packaging guidelines
- Change %%define to %%global, per packaging guidelines

* Sat Jan  2 2010 Tom Lane <tgl@redhat.com> 5.1.42-2
- Disable building the innodb plugin; it tickles assorted gcc bugs and
  doesn't seem entirely ready for prime time anyway.

* Fri Jan  1 2010 Tom Lane <tgl@redhat.com> 5.1.42-1
- Update to MySQL 5.1.42, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-42.html
- Start mysqld_safe with --basedir=/usr, to avoid unwanted SELinux messages
Resolves: #547485

* Thu Dec 17 2009 Tom Lane <tgl@redhat.com> 5.1.41-2
- Stop waiting during "service mysqld start" if mysqld_safe exits
Resolves: #544095

* Mon Nov 23 2009 Tom Lane <tgl@redhat.com> 5.1.41-1
- Update to MySQL 5.1.41, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-41.html
  including fixes for CVE-2009-4019
Related: #540906
- Don't set old_passwords=1; we aren't being bug-compatible with 3.23 anymore
Resolves: #540735

* Tue Nov 10 2009 Tom Lane <tgl@redhat.com> 5.1.40-1
- Update to MySQL 5.1.40, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-40.html
- Do not force the --log-error setting in mysqld init script
Resolves: #533736

* Sat Oct 17 2009 Tom Lane <tgl@redhat.com> 5.1.39-4
- Replace kluge fix for ndbd sparc crash with a real fix (mysql bug 48132)

* Thu Oct 15 2009 Tom Lane <tgl@redhat.com> 5.1.39-3
- Work around two different compiler bugs on sparc, one by backing off
  optimization from -O2 to -O1, and the other with a klugy patch
Related: #529298, #529299
- Clean up bogosity in multilib stub header support: ia64 should not be
  listed (it's not multilib), sparc and sparc64 should be

* Wed Sep 23 2009 Tom Lane <tgl@redhat.com> 5.1.39-2
- Work around upstream bug 46895 by disabling outfile_loaddata test

* Tue Sep 22 2009 Tom Lane <tgl@redhat.com> 5.1.39-1
- Update to MySQL 5.1.39, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-39.html

* Mon Aug 31 2009 Tom Lane <tgl@redhat.com> 5.1.37-5
- Work around unportable assumptions about stpcpy(); re-enable main.mysql test
- Clean up some obsolete parameters to the configure script

* Sat Aug 29 2009 Tom Lane <tgl@redhat.com> 5.1.37-4
- Remove one misguided patch; turns out I was chasing a glibc bug
- Temporarily disable "main.mysql" test; there's something broken there too,
  but we need to get mysql built in rawhide for dependency reasons

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 5.1.37-3
- rebuilt with new openssl

* Fri Aug 14 2009 Tom Lane <tgl@redhat.com> 5.1.37-2
- Add a couple of patches to improve the probability of the regression tests
  completing in koji builds

* Sun Aug  2 2009 Tom Lane <tgl@redhat.com> 5.1.37-1
- Update to MySQL 5.1.37, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-37.html

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.36-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 10 2009 Tom Lane <tgl@redhat.com> 5.1.36-1
- Update to MySQL 5.1.36, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-36.html

* Sat Jun  6 2009 Tom Lane <tgl@redhat.com> 5.1.35-1
- Update to MySQL 5.1.35, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-35.html
- Ensure that /var/lib/mysql is created with the right SELinux context
Resolves: #502966

* Fri May 15 2009 Tom Lane <tgl@redhat.com> 5.1.34-1
- Update to MySQL 5.1.34, for various fixes described at
  http://dev.mysql.com/doc/refman/5.1/en/news-5-1-34.html
- Increase startup timeout per bug #472222

* Wed Apr 15 2009 Tom Lane <tgl@redhat.com> 5.1.33-2
- Increase stack size of ndbd threads for safety's sake.
Related: #494631

* Tue Apr  7 2009 Tom Lane <tgl@redhat.com> 5.1.33-1
- Update to MySQL 5.1.33.
- Disable use of pthread_setschedparam; doesn't work the way code expects.
Related: #477624

* Wed Mar  4 2009 Tom Lane <tgl@redhat.com> 5.1.32-1
- Update to MySQL 5.1.32.

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.31-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 13 2009 Tom Lane <tgl@redhat.com> 5.1.31-1
- Update to MySQL 5.1.31.

* Thu Jan 22 2009 Tom Lane <tgl@redhat.com> 5.1.30-2
- hm, apparently --with-innodb and --with-ndbcluster are still needed
  even though no longer documented ...

* Thu Jan 22 2009 Tom Lane <tgl@redhat.com> 5.1.30-1
- Update to MySQL 5.1.30.  Note that this includes an ABI break for
  libmysqlclient (it's now got .so major version 16).
- This also updates mysql for new openssl build

* Wed Oct  1 2008 Tom Lane <tgl@redhat.com> 5.0.67-2
- Build the "embedded server" library, and package it in a new sub-RPM
  mysql-embedded, along with mysql-embedded-devel for devel support files.
Resolves: #149829

* Sat Aug 23 2008 Tom Lane <tgl@redhat.com> 5.0.67-1
- Update to mysql version 5.0.67
- Move mysql_config's man page to base package, again (apparently I synced
  that change the wrong way while importing specfile changes for ndbcluster)

* Sun Jul 27 2008 Tom Lane <tgl@redhat.com> 5.0.51a-2
- Enable ndbcluster support
Resolves: #163758
- Suppress odd crash messages during package build, caused by trying to
  build dbug manual (which we don't install anyway) with dbug disabled
Resolves: #437053
- Improve mysql.init to pass configured datadir to mysql_install_db,
  and to force user=mysql for both mysql_install_db and mysqld_safe.
Related: #450178

* Mon Mar  3 2008 Tom Lane <tgl@redhat.com> 5.0.51a-1
- Update to mysql version 5.0.51a

* Mon Mar  3 2008 Tom Lane <tgl@redhat.com> 5.0.45-11
- Fix mysql-stack-guard patch to work correctly on IA64
- Fix mysql.init to wait correctly when socket is not in default place
Related: #435494

* Mon Mar 03 2008 Dennis Gilmore <dennis@ausil.us> 5.0.45-10
- add sparc64 to 64 bit arches for test suite checking
- add sparc, sparcv9 and sparc64 to multilib handling

* Thu Feb 28 2008 Tom Lane <tgl@redhat.com> 5.0.45-9
- Fix the stack overflow problem encountered in January.  It seems the real
issue is that the buildfarm machines were moved to RHEL5, which uses 64K not
4K pages on PPC, and because RHEL5 takes the guard area out of the requested
thread stack size we no longer had enough headroom.
Related: #435337

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 5.0.45-8
- Autorebuild for GCC 4.3

* Tue Jan  8 2008 Tom Lane <tgl@redhat.com> 5.0.45-7
- Unbelievable ... upstream still thinks that it's a good idea to have a
  regression test that is guaranteed to begin failing come January 1.
- ... and it seems we need to raise STACK_MIN_SIZE again too.

* Thu Dec 13 2007 Tom Lane <tgl@redhat.com> 5.0.45-6
- Back-port upstream fixes for CVE-2007-5925, CVE-2007-5969, CVE-2007-6303.
Related: #422211

* Wed Dec  5 2007 Tom Lane <tgl@redhat.com> 5.0.45-5
- Rebuild for new openssl

* Sat Aug 25 2007 Tom Lane <tgl@redhat.com> 5.0.45-4
- Seems we need explicit BuildRequires on gawk and procps now
- Rebuild to fix Fedora toolchain issues

* Sun Aug 12 2007 Tom Lane <tgl@redhat.com> 5.0.45-3
- Recent perl changes in rawhide mean we need a more specific BuildRequires

* Thu Aug  2 2007 Tom Lane <tgl@redhat.com> 5.0.45-2
- Update License tag to match code.
- Work around recent Fedora change that makes "open" a macro name.

* Sun Jul 22 2007 Tom Lane <tgl@redhat.com> 5.0.45-1
- Update to MySQL 5.0.45
Resolves: #246535
- Move mysql_config's man page to base package
Resolves: #245770
- move my_print_defaults to base RPM, for consistency with Stacks packaging
- mysql user is no longer deleted at RPM uninstall
Resolves: #241912

* Thu Mar 29 2007 Tom Lane <tgl@redhat.com> 5.0.37-2
- Use a less hacky method of getting default values in initscript
Related: #233771, #194596
- Improve packaging of mysql-libs per suggestions from Remi Collet
Resolves: #233731
- Update default /etc/my.cnf ([mysql.server] has been bogus for a long time)

* Mon Mar 12 2007 Tom Lane <tgl@redhat.com> 5.0.37-1
- Update to MySQL 5.0.37
Resolves: #231838
- Put client library into a separate mysql-libs RPM to reduce dependencies
Resolves: #205630

* Fri Feb  9 2007 Tom Lane <tgl@redhat.com> 5.0.33-1
- Update to MySQL 5.0.33
- Install band-aid fix for "view" regression test designed to fail after 2006
- Don't chmod -R the entire database directory tree on every startup
Related: #221085
- Fix unsafe use of install-info
Resolves: #223713
- Cope with new automake in F7
Resolves: #224171

* Thu Nov  9 2006 Tom Lane <tgl@redhat.com> 5.0.27-1
- Update to MySQL 5.0.27 (see CVE-2006-4031, CVE-2006-4226, CVE-2006-4227)
Resolves: #202247, #202675, #203427, #203428, #203432, #203434, #208641
- Fix init script to return status 1 on server start timeout
Resolves: #203910
- Move mysqldumpslow from base package to mysql-server
Resolves: #193559
- Adjust link options for BDB module
Resolves: #199368

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 5.0.22-2.1
- rebuild

* Sat Jun 10 2006 Tom Lane <tgl@redhat.com> 5.0.22-2
- Work around brew's tendency not to clean up failed builds completely,
  by adding code in mysql-testing.patch to kill leftover mysql daemons.

* Thu Jun  8 2006 Tom Lane <tgl@redhat.com> 5.0.22-1
- Update to MySQL 5.0.22 (fixes CVE-2006-2753)
- Install temporary workaround for gcc bug on s390x (bz #193912)

* Tue May  2 2006 Tom Lane <tgl@redhat.com> 5.0.21-2
- Fix bogus perl Requires for mysql-test

* Mon May  1 2006 Tom Lane <tgl@redhat.com> 5.0.21-1
- Update to MySQL 5.0.21

* Mon Mar 27 2006 Tom Lane <tgl@redhat.com> 5.0.18-4
- Modify multilib header hack to not break non-RH arches, per bug #181335
- Remove logrotate script, per bug #180639.
- Add a new mysql-test RPM to carry the regression test files;
  hack up test scripts as needed to make them run in /usr/share/mysql-test.

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 5.0.18-2.1
- bump again for double-long bug on ppc(64)

* Thu Feb  9 2006 Tom Lane <tgl@redhat.com> 5.0.18-2
- err-log option has been renamed to log-error, fix my.cnf and initscript

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 5.0.18-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Thu Jan  5 2006 Tom Lane <tgl@redhat.com> 5.0.18-1
- Update to MySQL 5.0.18

* Thu Dec 15 2005 Tom Lane <tgl@redhat.com> 5.0.16-4
- fix my_config.h for ppc platforms

* Thu Dec 15 2005 Tom Lane <tgl@redhat.com> 5.0.16-3
- my_config.h needs to guard against 64-bit platforms that also define the
  32-bit symbol

* Wed Dec 14 2005 Tom Lane <tgl@redhat.com> 5.0.16-2
- oops, looks like we want uname -i not uname -m

* Mon Dec 12 2005 Tom Lane <tgl@redhat.com> 5.0.16-1
- Update to MySQL 5.0.16
- Add EXCEPTIONS-CLIENT license info to the shipped documentation
- Make my_config.h architecture-independent for multilib installs;
  put the original my_config.h into my_config_$ARCH.h
- Add -fwrapv to CFLAGS so that gcc 4.1 doesn't break it

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Mon Nov 14 2005 Tom Lane <tgl@redhat.com> 5.0.15-3
- Make stop script wait for daemon process to disappear (bz#172426)

* Wed Nov  9 2005 Tom Lane <tgl@redhat.com> 5.0.15-2
- Rebuild due to openssl library update.

* Thu Nov  3 2005 Tom Lane <tgl@redhat.com> 5.0.15-1
- Update to MySQL 5.0.15 (scratch build for now)

* Wed Oct  5 2005 Tom Lane <tgl@redhat.com> 4.1.14-1
- Update to MySQL 4.1.14

* Tue Aug 23 2005 Tom Lane <tgl@redhat.com> 4.1.12-3
- Use politically correct patch name.

* Tue Jul 12 2005 Tom Lane <tgl@redhat.com> 4.1.12-2
- Fix buffer overflow newly exposed in isam code; it's the same issue
  previously found in myisam, and not very exciting, but I'm tired of
  seeing build warnings.

* Mon Jul 11 2005 Tom Lane <tgl@redhat.com> 4.1.12-1
- Update to MySQL 4.1.12 (includes a fix for bz#158688, bz#158689)
- Extend mysql-test-ssl.patch to solve rpl_openssl test failure (bz#155850)
- Update mysql-lock-ssl.patch to match the upstream committed version
- Add --with-isam to re-enable the old ISAM table type, per bz#159262
- Add dependency on openssl-devel per bz#159569
- Remove manual.txt, as upstream decided not to ship it anymore;
  it was redundant with the mysql.info file anyway.

* Mon May  9 2005 Tom Lane <tgl@redhat.com> 4.1.11-4
- Include proper locking for OpenSSL in the server, per bz#155850

* Mon Apr 25 2005 Tom Lane <tgl@redhat.com> 4.1.11-3
- Enable openssl tests during build, per bz#155850
- Might as well turn on --disable-dependency-tracking

* Fri Apr  8 2005 Tom Lane <tgl@redhat.com> 4.1.11-2
- Avoid dependency on <asm/atomic.h>, cause it won't build anymore on ia64.
  This is probably a cleaner solution for bz#143537, too.

* Thu Apr  7 2005 Tom Lane <tgl@redhat.com> 4.1.11-1
- Update to MySQL 4.1.11 to fix bz#152911 as well as other issues
- Move perl-DBI, perl-DBD-MySQL dependencies to server package (bz#154123)
- Override configure thread library test to suppress HAVE_LINUXTHREADS check
- Fix BDB failure on s390x (bz#143537)
- At last we can enable "make test" on all arches

* Fri Mar 11 2005 Tom Lane <tgl@redhat.com> 4.1.10a-1
- Update to MySQL 4.1.10a to fix security vulnerabilities (bz#150868,
  for CAN-2005-0711, and bz#150871 for CAN-2005-0709, CAN-2005-0710).

* Sun Mar  6 2005 Tom Lane <tgl@redhat.com> 4.1.10-3
- Fix package Requires: interdependencies.

* Sat Mar  5 2005 Tom Lane <tgl@redhat.com> 4.1.10-2
- Need -fno-strict-aliasing in at least one place, probably more.
- Work around some C spec violations in mysql.

* Fri Feb 18 2005 Tom Lane <tgl@redhat.com> 4.1.10-1
- Update to MySQL 4.1.10.

* Sat Jan 15 2005 Tom Lane <tgl@redhat.com> 4.1.9-1
- Update to MySQL 4.1.9.

* Wed Jan 12 2005 Tom Lane <tgl@redhat.com> 4.1.7-10
- Don't assume /etc/my.cnf will specify pid-file (bz#143724)

* Wed Jan 12 2005 Tim Waugh <twaugh@redhat.com> 4.1.7-9
- Rebuilt for new readline.

* Tue Dec 21 2004 Tom Lane <tgl@redhat.com> 4.1.7-8
- Run make test on all archs except s390x (which seems to have a bdb issue)

* Mon Dec 13 2004 Tom Lane <tgl@redhat.com> 4.1.7-7
- Suppress someone's silly idea that libtool overhead can be skipped

* Sun Dec 12 2004 Tom Lane <tgl@redhat.com> 4.1.7-6
- Fix init script to not need a valid username for startup check (bz#142328)
- Fix init script to honor settings appearing in /etc/my.cnf (bz#76051)
- Enable SSL (bz#142032)

* Thu Dec  2 2004 Tom Lane <tgl@redhat.com> 4.1.7-5
- Add a restorecon to keep the mysql.log file in the right context (bz#143887)

* Tue Nov 23 2004 Tom Lane <tgl@redhat.com> 4.1.7-4
- Turn off old_passwords in default /etc/my.cnf file, for better compatibility
  with mysql 3.x clients (per suggestion from Joe Orton).

* Fri Oct 29 2004 Tom Lane <tgl@redhat.com> 4.1.7-3
- Handle ldconfig more cleanly (put a file in /etc/ld.so.conf.d/).

* Thu Oct 28 2004 Tom Lane <tgl@redhat.com> 4.1.7-2
- rebuild in devel branch

* Wed Oct 27 2004 Tom Lane <tgl@redhat.com> 4.1.7-1
- Update to MySQL 4.1.x.

* Tue Oct 12 2004 Tom Lane <tgl@redhat.com> 3.23.58-13
- fix security issues CAN-2004-0835, CAN-2004-0836, CAN-2004-0837
  (bugs #135372, 135375, 135387)
- fix privilege escalation on GRANT ALL ON `Foo\_Bar` (CAN-2004-0957)

* Wed Oct 06 2004 Tom Lane <tgl@redhat.com> 3.23.58-12
- fix multilib problem with mysqlbug and mysql_config
- adjust chkconfig priority per bug #128852
- remove bogus quoting per bug #129409 (MySQL 4.0 has done likewise)
- add sleep to mysql.init restart(); may or may not fix bug #133993

* Tue Oct 05 2004 Tom Lane <tgl@redhat.com> 3.23.58-11
- fix low-priority security issues CAN-2004-0388, CAN-2004-0381, CAN-2004-0457
  (bugs #119442, 125991, 130347, 130348)
- fix bug with dropping databases under recent kernels (bug #124352)

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com> 3.23.58-10
- rebuilt

* Sat Apr 17 2004 Warren Togami <wtogami@redhat.com> 3.23.58-9
- remove redundant INSTALL-SOURCE, manual.*
- compress manual.txt.bz2
- BR time

* Tue Mar 16 2004 Tom Lane <tgl@redhat.com> 3.23.58-8
- repair logfile attributes in %%files, per bug #102190
- repair quoting problem in mysqlhotcopy, per bug #112693
- repair missing flush in mysql_setpermission, per bug #113960
- repair broken error message printf, per bug #115165
- delete mysql user during uninstall, per bug #117017
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Feb 24 2004 Tom Lane <tgl@redhat.com>
- fix chown syntax in mysql.init
- rebuild

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Nov 18 2003 Kim Ho <kho@redhat.com> 3.23.58-5
- update mysql.init to use anonymous user (UNKNOWN_MYSQL_USER) for
  pinging mysql server (#108779)

* Mon Oct 27 2003 Kim Ho <kho@redhat.com> 3.23.58-4
- update mysql.init to wait (max 10 seconds) for mysql server to 
  start (#58732)

* Mon Oct 27 2003 Patrick Macdonald <patrickm@redhat.com> 3.23.58-3
- re-enable Berkeley DB support (#106832)
- re-enable ia64 testing

* Fri Sep 19 2003 Patrick Macdonald <patrickm@redhat.com> 3.23.58-2
- rebuilt

* Mon Sep 15 2003 Patrick Macdonald <patrickm@redhat.com> 3.23.58-1
- upgrade to 3.23.58 for security fix

* Tue Aug 26 2003 Patrick Macdonald <patrickm@redhat.com> 3.23.57-2
- rebuilt

* Wed Jul 02 2003 Patrick Macdonald <patrickm@redhat.com> 3.23.57-1
- revert to prior version of MySQL due to license incompatibilities 
  with packages that link against the client.  The MySQL folks are
  looking into the issue.

* Wed Jun 18 2003 Patrick Macdonald <patrickm@redhat.com> 4.0.13-4
- restrict test on ia64 (temporary)

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com> 4.0.13-3
- rebuilt

* Thu May 29 2003 Patrick Macdonald <patrickm@redhat.com> 4.0.13-2
- fix filter-requires-mysql.sh with less restrictive for mysql-bench 

* Wed May 28 2003 Patrick Macdonald <patrickm@redhat.com> 4.0.13-1
- update for MySQL 4.0
- back-level shared libraries available in mysqlclient10 package

* Fri May 09 2003 Patrick Macdonald <patrickm@redhat.com> 3.23.56-2
- add sql-bench package (#90110) 

* Wed Mar 19 2003 Patrick Macdonald <patrickm@redhat.com> 3.23.56-1
- upgrade to 3.23.56 for security fixes
- remove patch for double-free (included in 3.23.56) 

* Tue Feb 18 2003 Patrick Macdonald <patrickm@redhat.com> 3.23.54a-11
- enable thread safe client
- add patch for double free fix

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Mon Jan 13 2003 Karsten Hopp <karsten@redhat.de> 3.23.54a-9
- disable checks on s390x

* Sat Jan  4 2003 Jeff Johnson <jbj@redhat.com> 3.23.54a-8
- use internal dep generator.

* Wed Jan  1 2003 Bill Nottingham <notting@redhat.com> 3.23.54a-7
- fix mysql_config on hammer

* Sun Dec 22 2002 Tim Powers <timp@redhat.com> 3.23.54a-6
- don't use rpms internal dep generator

* Tue Dec 17 2002 Elliot Lee <sopwith@redhat.com> 3.23.54a-5
- Push it into the build system

* Mon Dec 16 2002 Joe Orton <jorton@redhat.com> 3.23.54a-4
- upgrade to 3.23.54a for safe_mysqld fix

* Thu Dec 12 2002 Joe Orton <jorton@redhat.com> 3.23.54-3
- upgrade to 3.23.54 for latest security fixes

* Tue Nov 19 2002 Jakub Jelinek <jakub@redhat.com> 3.23.52-5
- Always include <errno.h> for errno
- Remove unpackaged files

* Tue Nov 12 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- do not prereq userdel, not used at all

* Mon Sep  9 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.52-4
- Use %%{_libdir}
- Add patch for x86-64

* Wed Sep  4 2002 Jakub Jelinek <jakub@redhat.com> 3.23.52-3
- rebuilt with gcc-3.2-7

* Thu Aug 29 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.52-2
- Add --enable-local-infile to configure - a new option
  which doesn't default to the old behaviour (#72885)

* Fri Aug 23 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.52-1
- 3.23.52. Fixes a minor security problem, various bugfixes.

* Sat Aug 10 2002 Elliot Lee <sopwith@redhat.com> 3.23.51-5
- rebuilt with gcc-3.2 (we hope)

* Mon Jul 22 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.51-4
- rebuild

* Thu Jul 18 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.51-3
- Fix #63543 and #63542 

* Thu Jul 11 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.51-2
- Turn off bdb on PPC(#68591)
- Turn off the assembly optimizations, for safety. 

* Wed Jun 26 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.51-1
- Work around annoying auto* thinking this is a crosscompile
- 3.23.51

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Mon Jun 10 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.50-2
- Add dependency on perl-DBI and perl-DBD-MySQL (#66349)

* Thu May 30 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.50-1
- 3.23.50

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Mon May 13 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.49-4
- Rebuild
- Don't set CXX to gcc, it doesn't work anymore
- Exclude Alpha

* Mon Apr  8 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.49-3
- Add the various .cnf examples as doc files to mysql-server (#60349)
- Don't include manual.ps, it's just 200 bytes with a URL inside (#60349)
- Don't include random files in /usr/share/mysql (#60349)
- langify (#60349)

* Thu Feb 21 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.49-2
- Rebuild

* Sun Feb 17 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.49-1
- 3.23.49

* Thu Feb 14 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.48-2
- work around perl dependency bug.

* Mon Feb 11 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.48-1
- 3.23.48

* Thu Jan 17 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.47-4
- Use kill, not mysqladmin, to flush logs and shut down. Thus, 
  an admin password can be set with no problems.
- Remove reload from init script

* Wed Jan 16 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.47-3
- remove db3-devel from buildrequires, 
  MySQL has had its own bundled copy since the mid thirties

* Sun Jan  6 2002 Trond Eivind Glomsrd <teg@redhat.com> 3.23.47-1
- 3.23.47
- Don't build for alpha, toolchain immature.

* Mon Dec  3 2001 Trond Eivind Glomsrd <teg@redhat.com> 3.23.46-1
- 3.23.46
- use -fno-rtti and -fno-exceptions, and set CXX to increase stability. 
  Recommended by mysql developers.

* Sun Nov 25 2001 Trond Eivind Glomsrd <teg@redhat.com> 3.23.45-1
- 3.23.45

* Wed Nov 14 2001 Trond Eivind Glomsrd <teg@redhat.com> 3.23.44-2
- centralize definition of datadir in the initscript (#55873)

* Fri Nov  2 2001 Trond Eivind Glomsrd <teg@redhat.com> 3.23.44-1
- 3.23.44

* Thu Oct  4 2001 Trond Eivind Glomsrd <teg@redhat.com> 3.23.43-1
- 3.23.43

* Mon Sep 10 2001 Trond Eivind Glomsrd <teg@redhat.com> 3.23.42-1
- 3.23.42
- reenable innodb

* Tue Aug 14 2001 Trond Eivind Glomsrd <teg@redhat.com> 3.23.41-1
- 3.23.41 bugfix release
- disable innodb, to avoid the broken updates
- Use "mysqladmin flush_logs" instead of kill -HUP in logrotate 
  script (#51711)

* Sat Jul 21 2001 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.40, bugfix release
- Add zlib-devel to buildrequires:

* Fri Jul 20 2001 Trond Eivind Glomsrd <teg@redhat.com>
- BuildRequires-tweaking

* Thu Jun 28 2001 Trond Eivind Glomsrd <teg@redhat.com>
- Reenable test, but don't run them for s390, s390x or ia64
- Make /etc/my.cnf config(noplace). Same for /etc/logrotate.d/mysqld

* Thu Jun 14 2001 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.29
- enable innodb
- enable assembly again
- disable tests for now...

* Tue May 15 2001 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.38
- Don't use BDB on Alpha - no fast mutexes

* Tue Apr 24 2001 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.37
- Add _GNU_SOURCE to the compile flags

* Wed Mar 28 2001 Trond Eivind Glomsrd <teg@redhat.com>
- Make it obsolete our 6.2 PowerTools packages
- 3.23.36 bugfix release - fixes some security issues
  which didn't apply to our standard configuration
- Make "make test" part of the build process, except on IA64
  (it fails there)

* Tue Mar 20 2001 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.35 bugfix release
- Don't delete the mysql user on uninstall

* Tue Mar 13 2001 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.34a bugfix release

* Wed Feb  7 2001 Trond Eivind Glomsrd <teg@redhat.com>
- added readline-devel to BuildRequires:

* Tue Feb  6 2001 Trond Eivind Glomsrd <teg@redhat.com>
- small i18n-fixes to initscript (action needs $)

* Tue Jan 30 2001 Trond Eivind Glomsrd <teg@redhat.com>
- make it shut down and rotate logs without using mysqladmin 
  (from #24909)

* Mon Jan 29 2001 Trond Eivind Glomsrd <teg@redhat.com>
- conflict with "MySQL"

* Tue Jan 23 2001 Trond Eivind Glomsrd <teg@redhat.com>
- improve gettextizing

* Mon Jan 22 2001 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.32
- fix logrotate script (#24589)

* Wed Jan 17 2001 Trond Eivind Glomsrd <teg@redhat.com>
- gettextize
- move the items in Requires(post): to Requires: in preparation
  for an errata for 7.0 when 3.23.31 is released
- 3.23.31

* Tue Jan 16 2001 Trond Eivind Glomsrd <teg@redhat.com>
- add the log file to the rpm database, and make it 0640
  (#24116)
- as above in logrotate script
- changes to the init sequence - put most of the data
  in /etc/my.cnf instead of hardcoding in the init script
- use /var/run/mysqld/mysqld.pid instead of 
  /var/run/mysqld/pid
- use standard safe_mysqld
- shut down cleaner

* Mon Jan 08 2001 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.30
- do an explicit chmod on /var/lib/mysql in post, to avoid 
  any problems with broken permissons. There is a report
  of rm not changing this on its own (#22989)

* Mon Jan 01 2001 Trond Eivind Glomsrd <teg@redhat.com>
- bzipped source
- changed from 85 to 78 in startup, so it starts before
  apache (which can use modules requiring mysql)

* Wed Dec 27 2000 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.29a

* Tue Dec 19 2000 Trond Eivind Glomsrd <teg@redhat.com>
- add requirement for new libstdc++, build for errata

* Mon Dec 18 2000 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.29

* Mon Nov 27 2000 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.28 (gamma)
- remove old patches, as they are now upstreamed

* Tue Nov 14 2000 Trond Eivind Glomsrd <teg@redhat.com>
- Add a requirement for a new glibc (#20735)
- build on IA64

* Wed Nov  1 2000 Trond Eivind Glomsrd <teg@redhat.com>
- disable more assembly

* Wed Nov  1 2000 Jakub Jelinek <jakub@redhat.com>
- fix mysql on SPARC (#20124)

* Tue Oct 31 2000 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.27

* Wed Oct 25 2000 Trond Eivind Glomsrd <teg@redhat.com>
- add patch for fixing bogus aliasing in mysql from Jakub,
  which should fix #18905 and #18620

* Mon Oct 23 2000 Trond Eivind Glomsrd <teg@redhat.com>
- check for negative niceness values, and negate it
  if present (#17899)
- redefine optflags on IA32 FTTB

* Wed Oct 18 2000 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.26, which among other fixes now uses mkstemp()
  instead of tempnam().
- revert changes made yesterday, the problem is now
  isolated
 
* Tue Oct 17 2000 Trond Eivind Glomsrd <teg@redhat.com>
- use the compat C++ compiler FTTB. Argh.
- add requirement of ncurses4 (see above)

* Sun Oct 01 2000 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.25
- fix shutdown problem (#17956)

* Tue Sep 26 2000 Trond Eivind Glomsrd <teg@redhat.com>
- Don't try to include no-longer-existing PUBLIC file
  as doc (#17532)

* Tue Sep 12 2000 Trond Eivind Glomsrd <teg@redhat.com>
- rename config file to /etc/my.cnf, which is what
  mysqld wants... doh. (#17432)
- include a changed safe_mysqld, so the pid file option
  works. 
- make mysql dir world readable to they can access the 
  mysql socket. (#17432)
- 3.23.24

* Wed Sep 06 2000 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.23

* Sun Aug 27 2000 Trond Eivind Glomsrd <teg@redhat.com>
- Add "|| :" to condrestart to avoid non-zero exit code

* Thu Aug 24 2000 Trond Eivind Glomsrd <teg@redhat.com>
- it's mysql.com, not mysql.org and use correct path to 
  source (#16830)

* Wed Aug 16 2000 Trond Eivind Glomsrd <teg@redhat.com>
- source file from /etc/rc.d, not /etc/rd.d. Doh.

* Sun Aug 13 2000 Trond Eivind Glomsrd <teg@redhat.com>
- don't run ldconfig -n, it doesn't update ld.so.cache
  (#16034)
- include some missing binaries
- use safe_mysqld to start the server (request from
  mysql developers)

* Sat Aug 05 2000 Bill Nottingham <notting@redhat.com>
- condrestart fixes

* Tue Aug 01 2000 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.22. Disable the old patches, they're now in.

* Thu Jul 27 2000 Trond Eivind Glomsrd <teg@redhat.com>
- bugfixes in the initscript
- move the .so link to the devel package

* Wed Jul 19 2000 Trond Eivind Glomsrd <teg@redhat.com>
- rebuild due to glibc changes

* Tue Jul 18 2000 Trond Eivind Glomsrd <teg@redhat.com>
- disable compiler patch
- don't include info directory file

* Mon Jul 17 2000 Trond Eivind Glomsrd <teg@redhat.com>
- move back to /etc/rc.d/init.d

* Fri Jul 14 2000 Trond Eivind Glomsrd <teg@redhat.com>
- more cleanups in initscript

* Thu Jul 13 2000 Trond Eivind Glomsrd <teg@redhat.com>
- add a patch to work around compiler bug 
  (from monty@mysql.com) 

* Wed Jul 12 2000 Trond Eivind Glomsrd <teg@redhat.com>
- don't build the SQL daemon statically (glibc problems)
- fix the logrotate script - only flush log if mysql
  is running
- change the reloading procedure 
- remove icon - glint is obsolete a long time ago

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Mon Jul 10 2000 Trond Eivind Glomsrd <teg@redhat.com>
- try the new compiler again
- build the SQL daemon statically
- add compile time support for complex charsets
- enable assembler
- more cleanups in initscript

* Sun Jul 09 2000 Trond Eivind Glomsrd <teg@redhat.com>
- use old C++ compiler
- Exclusivearch x86

* Sat Jul 08 2000 Trond Eivind Glomsrd <teg@redhat.com>
- move .so files to devel package
- more cleanups
- exclude sparc for now

* Wed Jul 05 2000 Trond Eivind Glomsrd <teg@redhat.com>
- 3.23.21
- remove file from /etc/sysconfig
- Fix initscript a bit - initialization of databases doesn't
  work yet
- specify the correct licenses
- include a /etc/my.conf (empty, FTTB)
- add conditional restart to spec file

* Sun Jul  2 2000 Jakub Jelinek <jakub@redhat.com>
- Rebuild with new C++

* Fri Jun 30 2000 Trond Eivind Glomsrd <teg@redhat.com>
- update to 3.23.20
- use %%configure, %%makeinstall, %%{_tmppath}, %%{_mandir},
  %%{_infodir}, /etc/init.d
- remove the bench package
- change some of the descriptions a little bit
- fix the init script
- some compile fixes
- specify mysql user
- use mysql uid 27 (postgresql is 26)
- don't build on ia64

* Sat Feb 26 2000 Jos Vos <jos@xos.nl>
- Version 3.22.32 release XOS.1 for LinuX/OS 1.8.0
- Upgrade from version 3.22.27 to 3.22.32.
- Do "make install" instead of "make install-strip", because "install -s"
  now appears to fail on various scripts.  Afterwards, strip manually.
- Reorganize subpackages, according to common Red Hat packages: the client
  program and shared library become the base package and the server and
  some accompanying files are now in a separate server package.  The
  server package implicitly requires the base package (shared library),
  but we have added a manual require tag anyway (because of the shared
  config file, and more).
- Rename the mysql-benchmark subpackage to mysql-bench.

* Mon Jan 31 2000 Jos Vos <jos@xos.nl>
- Version 3.22.27 release XOS.2 for LinuX/OS 1.7.1
- Add post(un)install scripts for updating ld.so.conf (client subpackage).

* Sun Nov 21 1999 Jos Vos <jos@xos.nl>
- Version 3.22.27 release XOS.1 for LinuX/OS 1.7.0
- Initial version.
- Some ideas borrowed from Red Hat Powertools 6.1, although this spec
  file is a full rewrite from scratch.
