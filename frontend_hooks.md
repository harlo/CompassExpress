## Frontend Hooks

Once set up, you can hook in a number of desktop clients on your network.  This is also super useful for development; you can be sure the changes you make locally will be in sync with the master branch.

#### Setup

1.	Start a shell into the engine:

	`./run.sh shell`

1.	Turn the engine on:

	`source ~/.bash_profile && ./startup.sh`

1.	Get the Annex's configuration:

	`cd ~/CompassAnnex/lib/Annex && python unveillance_annex.py -config`

	Copy and past the resulting json into a file.

1.	Modify that config file to include a few new directives:

	{
		"server_force_ssh" : true,
		"api.port" : 8891
	}

	Actually, `api.port` can be anything that is not 8888, 8889, or 8890; those ports are already in use.

1.	Change that config's `annex_remote_port` to whatever it's been mapped to in docker (i.e. 49160)

1.	Either clone a fresh copy of [CompassFrontend][c_f] or use the one included in src/.
1.	`cd CompassFrontend`
1.	`./setup.sh /path/to/config/you/made.json`