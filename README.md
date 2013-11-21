aws-logstash-rpm
================

Builds an rpm for logstash to work with AWS Linux.

Based on 
* https://github.com/dephub/logstash-rpm
* https://github.com/lfrancke/logstash-rpm 

To build rpm with rpmbuild run the following:
```
rpmbuild --define "_topdir `pwd`"  -bb SPECS/logstash.spec
```

This rpm will build
* Default conf in /etc/logstash/logstash.conf that puts syslog messages in elastic search
* Adds logstash user and group
* Creates elastic search data directory in /var/logstash/data

