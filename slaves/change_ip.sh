#/bin/sh
ip_addr=`/sbin/ifconfig vhost0 | grep 'inet ' | cut -d: -f2 | awk '{print $2}'`
echo $ip_addr
ip route add 8.8.8.8 via $ip_addr dev vhost0
sed -i $"s/[0-9]\{1,3\}.[0-9]\{1,3\}.[0-9]\{1,3\}.[0-9]\{1,3\}/$ip_addr/g" /etc/default/mesos
service zookeeper restart
service mesos-master restart
rm -f /var/mesos/meta/slaves/latest
service mesos-slave restart
service marathon restart
