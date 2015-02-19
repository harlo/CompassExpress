#! /bin/bash

source ~/.bash_profile

function do_update {
	cd $1
	git fetch --all
	git reset --hard origin/master
	git pull origin master
}

C_A=~/CompassAnnex
C_F=~/CompassFrontend

declare -a U_MODS=("$C_A", "$C_A/lib/Annex", "$C_A/lib/Annex/lib/Core", "$C_F", "$C_F/lib/Frontend", "$C_F/lib/Frontend/Core")
for U_MOD in "${U_MODS[@]}"; do
	do_update $U_MOD
done