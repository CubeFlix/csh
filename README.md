# csh
A secure python-based file server and client.
-----

The CSH server executables can be built using Py2Exe and executed using `cshs`. They use a special socket protocol and can be accessed using its port, defaulting to 8008.
CSH has user account capabilities and allows the administrator to define permissions for individual users. The user data and settings JSON file will default to `users.json` and `config.json`. 