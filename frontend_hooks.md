## Frontend Hooks

Once set up, you can hook in a number of desktop clients on your network.  This is also super useful for development; you can be sure the changes you make locally will be in sync with the master branch.

#### Setup

1.	Start a shell into the engine:

	`./run.sh shell`

1.	Turn the engine on:

	`source ~/.bash_profile && ./startup.sh`

1.	Get the Annex's configuration:

	`cd ~/CompassAnnex/lib/Annex && python unveillance_annex.py -config`

	Copy and past the resulting json into a file on whatever machine you're Frontend will be on.

1.	Modify that config file to include a few new directives:

	{
		"server_force_ssh" : true,
		"api.port" : 8891
	}

	Actually, `api.port` can be anything that is not 8888, 8889, or 8890; those ports are already in use.

1.	Change that config's `annex_remote_port` to whatever it's been mapped to in docker (i.e. 49160)

1.	On the machine hosting the new Frontend, either clone a fresh copy of [CompassFrontend][c_f] or use the one included in src/.
1.	`cd CompassFrontend`
1.	'git submodule update --init --recursive'
1.	`./setup.sh /path/to/config/you/made.json`
1.	Now, push your newly-generated key to the Engine.  The simplest way to do so is to copy-paste its contents into a file on the engine, using `vim` for example.

1.	From the engine, run the following:

	`cd ~/CompassAnnex/lib/Annex`

	`python import_key.py /path/to/that/new/key.pub`

1.	You can now exit out of the shell.  Be sure to save state 