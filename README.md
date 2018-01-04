myf5 - A python utility to manage F5 Local Traffic Managers using the F5 ReST API

The `master` branch supports F5 LTM v12.x
The `v11` tag supports F5 LTM v11.5 - v11.x

To use this package, install git and clone the repo:

```
apt-get install git
git clone https://github.com/busterswt/myf5.git
```

The following OpenStack environment variables must be set:

```
OS_USERNAME
OS_PASSWORD
OS_TENANT_NAME
OS_AUTH_URL
```

The following F5 environment variables must be set:

```
F5_USERNAME       This is the username of the F5 or proxy user
F5_PASSWORD       This is the password of the F5 or proxy user
F5_ENDPOINT       This is the IP address of the F5 self IP or proxy address
F5_PARTITION      This is the partition on the F5 within which objects will created or modified
```

To use this utility, execute the following within the myf5 directory:

```
./myf5.py
```

