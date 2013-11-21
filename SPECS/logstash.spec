%define debug_package %{nil}
%define base_install_dir %{_javadir}{%name}
%define __jar_repack %{nil}

%global bindir %{_bindir}
%global confdir %{_sysconfdir}/%{name}
%global jarpath %{_javadir}
%global lockfile %{_localstatedir}/lock/subsys/%{name}
%global logdir %{_localstatedir}/log/%{name}
%global piddir %{_localstatedir}/run/%{name}
%global plugindir %{_datadir}/%{name}
%global sysconfigdir %{_sysconfdir}/sysconfig
%global esdatadir %{_localstatedir}/%{name}/data

Name:		logstash
Version:	1.2.2
Release:	1%{?dist}
Summary:	logstash is a tool for managing events and logs.

Group:		System Environment/Daemons
License:	ASL 2.0
URL:		http://logstash.net
Source0:	https://download.elasticsearch.org/logstash/logstash/%{name}-%{version}-flatjar.jar
Source1:	logstash.wrapper
Source2:	logstash.logrotate
Source3:	logstash.init
Source4:	logstash.sysconfig
Source5:	logstash.conf

BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildArch:	noarch
Requires:	java-1.6.0-openjdk
Requires:	jpackage-utils

Requires(post):	chkconfig initscripts
Requires(pre):	chkconfig initscripts
Requires(pre):	shadow-utils

%description
logstash is a tool for managing events and logs. You can use it to collect logs, parse them, and store them for later use (like, for searching). Speaking of searching, logstash comes with a web interface for searching and drilling into all of your logs.

%prep
%build

%install
#rm -rf $RPM_BUILD_ROOT

# JAR file
%{__mkdir} -p %{buildroot}%{_javadir}
%{__install} -p -m 644 %{SOURCE0} %{buildroot}%{jarpath}/%{name}.jar

# Config
%{__mkdir} -p %{buildroot}%{confdir}
%{__install} -m 755 %{SOURCE5} %{buildroot}%{confdir}

# Plugin dir
%{__mkdir} -p %{buildroot}%{plugindir}/inputs
%{__mkdir} -p %{buildroot}%{plugindir}/filters
%{__mkdir} -p %{buildroot}%{plugindir}/outputs

# Wrapper script
%{__mkdir} -p %{buildroot}%{_bindir}
%{__install} -m 755 %{SOURCE1} %{buildroot}%{bindir}/%{name}

%{__sed} -i \
   -e "s|@@@NAME@@@|%{name}|g" \
   -e "s|@@@JARPATH@@@|%{jarpath}|g" \
   %{buildroot}%{bindir}/%{name}

# Logs
%{__mkdir} -p %{buildroot}%{logdir}
%{__install} -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Misc
%{__mkdir} -p %{buildroot}%{piddir}

#This is needed because Logstash will complain if there are no *.rb
# files in its Plugin directory 
/bin/touch %{buildroot}%{plugindir}/inputs/dummy.rb

%{__install} -m 755 %{SOURCE5} %{buildroot}%
# sysconfig and init
%{__mkdir} -p %{buildroot}%{_initddir}
%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 755 %{SOURCE3} %{buildroot}%{_initddir}/%{name}
%{__install} -m 644 %{SOURCE4} %{buildroot}%{sysconfigdir}/%{name}

# elastic search data dir 
%{__mkdir} -p %{buildroot}%{esdatadir}

# Using _datadir for PLUGINDIR because logstash expects a structure like logstash/{inputs,filters,outputs}
%{__sed} -i \
   -e "s|@@@NAME@@@|%{name}|g" \
   -e "s|@@@DAEMON@@@|%{bindir}|g" \
   -e "s|@@@CONFDIR@@@|%{confdir}|g" \
   -e "s|@@@LOCKFILE@@@|%{lockfile}|g" \
   -e "s|@@@LOGDIR@@@|%{logdir}|g" \
   -e "s|@@@PIDDIR@@@|%{piddir}|g" \
   -e "s|@@@PLUGINDIR@@@|%{_datadir}|g" \
   -e "s|@@@DATADIR@@@|%{esdatadir}|g"\
   %{buildroot}%{_initddir}/%{name}

%{__sed} -i \
   -e "s|@@@NAME@@@|%{name}|g" \
   -e "s|@@@CONFDIR@@@|%{confdir}|g" \
   -e "s|@@@LOGDIR@@@|%{logdir}|g" \
   -e "s|@@@PLUGINDIR@@@|%{_datadir}|g" \
   %{buildroot}%{sysconfigdir}/%{name}

%pre
# create logstash group
if ! getent group logstash >/dev/null; then
        groupadd -r logstash
fi

# create logstash user
if ! getent passwd logstash >/dev/null; then
        useradd -r -g logstash -d %{_javadir}/%{name} \
            -s /sbin/nologin -c "You know, for search" logstash
fi

%post
/sbin/chkconfig --add logstash

%preun
if [ $1 -eq 0 ]; then
  /sbin/service logstash stop >/dev/null 2>&1
  /sbin/chkconfig --del logstash
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
# JAR file
%{_javadir}/%{name}.jar

# Config
%config(noreplace) %{confdir}/
%config(noreplace) %{confdir}/

# Plugin dir
%dir %{plugindir}/inputs
%dir %{plugindir}/filters
%dir %{plugindir}/outputs
%{plugindir}/inputs/dummy.rb

# Wrapper script
%{bindir}/*

# Logrotate
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

# Sysconfig and init
%{_initddir}/%{name}
%config(noreplace) %{sysconfigdir}/*

%defattr(-,%{name},%{name},-)
%dir %{logdir}/
%dir %{piddir}/

%dir %{esdatadir}/
 
