# support-tooling
HWX Private Support tooling repo

## Ambari Config comparison Scripts

### 1. cluster-compare.py

This is a python script to compare configurations of 2 clusters by comparing the latest active configs stored in Ambari Database.

This tool can be run from Windows, Mac or Linux machines installed with python 2.x and one of the python modules : 'pycurl' or 'requests'
The machine should have access to both Ambari Server nodes on each clusters
It generates an HTML output with filename format as '<cluster_name_1>_<cluster_name_2>.html' in the directory from where its run.

#### Usage

```shell
# python  cluster_compare_html/cluster-compare.py  --help
usage: cluster-compare.py [-h] -a AMBARI_HOST_1 AMBARI_HOST_2
                          [-u USERNAME_1 USERNAME_2] [-p PORT_1 PORT_2]
                          [-c CLUSTER_1 CLUSTER_2]
                          [-s SSL_ENABLED_FLAG_1 SSL_ENABLED_FLAG_2]

Version 3.0. Script to compare configs from 2 clusters. NOTE: If the script
takes too long and times out, then try using the IP Addresses of Ambari
Servers instead of hostnames.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME_1 USERNAME_2, --usernames USERNAME_1 USERNAME_2
                        Usernames for first and second Ambari UI. Default:
                        admin
  -p PORT_1 PORT_2, --ports PORT_1 PORT_2
                        Port numbers for first and second Ambari Servers.
                        Default: 8080
  -c CLUSTER_1 CLUSTER_2, --clusternames CLUSTER_1 CLUSTER_2
                        Names of the first and second cluster. Default: First
                        available cluster names from each Ambari
  -s SSL_ENABLED_FLAG_1 SSL_ENABLED_FLAG_2, --ssl_flags SSL_ENABLED_FLAG_1 SSL_ENABLED_FLAG_2
                        Whether SSL is enabled for first and second Ambari
                        URLs (y or n). Default: n

required arguments:
  -a AMBARI_HOST_1 AMBARI_HOST_2, --ambari_hosts AMBARI_HOST_1 AMBARI_HOST_2
                        IPs/Hostnames of first and second Ambari Server
```

### 2. config-history-compare.py

This is a python script to compare configurations history by comparing the  configs stored in Ambari Database.

This tool can be run from Windows, Mac or Linux machines installed with python 2.x and one of the python modules : 'pycurl' or 'requests'
The machine should have access to the Ambari Server node of the cluster
It generates an HTML file output in the directory from where its run.

#### Usage

```shell
# python config_history_compare_html/config-history-compare.sh
Version : 1.0
Usage:
python config_history_compare_html/config-history-compare.sh -h <ambariServer> -o <configDate> [-n <configDate>] [-u <username>] [-c <cluster>] [-p <port>] [-s]
Options:
    -h, --host <ambariServer>
	    Required.
	    IP/Hostname of Ambari Server
    -o, --olderDate <configDate>
	    Required.
	    Provide the older date in "YYYY-MM-DD HH:MI" or YYYY-MM-DD@HH:MI
    -n, --newerDate <configDate>
	    Optional.
	    Provide the newer date in "YYYY-MM-DD HH:MI" or YYYY-MM-DD@HH:MI
	    Default: Current Date & Time. Will use the current active versions/configs
    -u, --username <username>
	    Optional.
	    Username for Ambari.
	    Default: "admin". Will be prompted for the password
    -p, --port <port>
	    Optional.
	    Port number for Ambari Server.
	    Default: "8080"
    -c, --cluster <cluster>
	    Optional.
	    Name of the cluster.
	    Default: First available cluster name configured in Ambari
    -s, --sslEnabled
	    Optional.
	    Flag to indicate whether SSL is enabled for the Ambari URL.
	    Default: Disabled
Note:
	    If the script takes too long and times out, please try
	    using the IP Address of Ambari Server instead of hostname.
```

