#! /bin/bash

function parse_directive {
	echo $(echo $1 | python -c "import re, sys; r = sys.stdin.read().split(\";\"); rx = re.compile(r[0]); print \"\".join(re.findall(rx, r[1]))")
}

function resolve_git {
	file $1/.git | grep "directory"
	if ([ $? -eq 0 ]); then
		return
	fi

	cd $1 && pwd
	rm .git
	git init

	git remote add origin $2

	cat >> $1/.git/config <<'_EOF'
[branch "master"]
	remote = origin
	merge = refs/head/master
_EOF

	file $1/.gitmodules
	if ([ $? -eq 0 ]); then
		SUBMODULES=$(cat $1/.gitmodules | grep "submodule" -A 2)

		IFS=$'\n'
		PATH_RX='\tpath\s=\s(.*)'
		URL_RX='\turl\s=\s(.*)'
		U_PATH=""
		S_PATH=""

		for SUBMODULE in $SUBMODULES; do
			if [[ -z "$S_PATH" ]]; then
				echo $SUBMODULE | grep -Po $PATH_RX
				if ([ $? -eq 0 ]); then
					S_PATH=$(parse_directive "$PATH_RX;$SUBMODULE")
				fi
			fi

			if [[ -z "$U_PATH" ]]; then
				echo $SUBMODULE | grep -Po $URL_RX
				if ([ $? -eq 0 ]); then
					U_PATH=$(parse_directive "$URL_RX;$SUBMODULE")
				fi
			fi

			if [[ -z "$U_PATH" ]] || [[ -z "$S_PATH" ]]; then
				continue
			else
				echo ""
				echo "HI $U_PATH and $S_PATH"
				echo ""
				
				resolve_git $1/$S_PATH $U_PATH
				U_PATH=""
				S_PATH=""
			fi
		done
	fi
}

git config --global user.name "compass"
git config --global user.email "compass@j3m.info"

declare -a U_MODS=("CompassFrontend" "CompassAnnex")
for U_MOD in "${U_MODS[@]}"; do
	resolve_git ~/$U_MOD "git@github.com:harlo/$U_MOD.git"
done

cd ~/CompassAnnex/lib
tar -xvzf gensim_lib.tar.gz

cd ~/CompassAnnex && ./setup.sh /home/compass/unveillance.compass.annex.json
source ~/.bash_profile
cd ~/CompassFrontend && ./setup.sh /home/compass/unveillance.compass.frontend.json