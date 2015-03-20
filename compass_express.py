import os, json
from sys import argv, exit
from fabric.api import settings, local

from dutils.conf import DUtilsKey, DUtilsKeyDefaults, build_config, BASE_DIR, append_to_config, save_config, __load_config
from dutils.dutils import build_routine, build_dockerfile

API_PORT = 8889
MESSAGE_PORT = 8890
FRONTEND_PORT = 8888
NLP_PORT = 8887

DEFAULT_PORTS = [22]
DEFAULT_GENSIM_LIB = os.path.join(BASE_DIR, "gensim_lib.tar.gz")

def init_d(with_config):
	port_to_int = lambda p : int(p.strip())
	clean_up_port_map = lambda p : "%s%s" % (p.split(":")[1], p) if p.split(":")[0] == "" else p

	conf_keys = [
		DUtilsKeyDefaults['USER_PWD'],
		DUtilsKeyDefaults['IMAGE_NAME'],
		DUtilsKey("GENSIM_LIB", "Where do you have the gensim_lib tarball?", 
			DEFAULT_GENSIM_LIB, DEFAULT_GENSIM_LIB, None)
		DUtilsKey("API_PORT", "Annex api port", API_PORT, str(API_PORT), port_to_int),
		DUtilsKey("MESSAGE_PORT", "Annex messaging port", API_PORT + 1, str(API_PORT + 1), port_to_int),
		DUtilsKey("FRONTEND_PORT", "Frontend port", FRONTEND_PORT, str(FRONTEND_PORT), port_to_int),
		DUtilsKey("NLP_PORT", "NLP Port", NLP_PORT, str(NLP_PORT), port_to_int)
	]

	for k in ["API_PORT", "MESSAGE_PORT", "FRONTEND_PORT"]:
		k_port = locals[k]
		conf_keys.append(DUtilsKey("%s_PUBLISHED" % k, "What port will we publish %s on? (\"client:host\" or \":host\" if client doesn't need to change)" % k,
			"%d:%d" % (k_port, k_port), "%d:%d" % (k_port, k_port), clean_up_port_map))

	config = build_config(conf_keys, with_config)
	config['USER'] = "compass"

	from dutils.dutils import get_docker_exe, get_docker_ip, validate_private_key

	docker_exe = get_docker_exe()
	if docker_exe is None:
		return False

	save_config(config, with_config=with_config)

	WORKING_DIR = BASE_DIR if with_config is None else os.path.dirname(with_config)
	if not validate_private_key(os.path.join(WORKING_DIR, "%s.privkey" % config['IMAGE_NAME']), with_config):
		return False
	
	res, config = append_to_config({
		'DOCKER_EXE' : docker_exe, 
		'DOCKER_IP' : get_docker_ip()
	}, return_config=True, with_config=with_config)

	print config

	if not res:
		return False

	with settings(warn_only=True):
		if not os.path.exists(os.path.join(BASE_DIR, "src", ".ssh")):
			local("mkdir %s" % os.path.join(BASE_DIR, "src", ".ssh"))
	
		local("cp %s %s" % (config['SSH_PUB_KEY'], os.path.join(BASE_DIR, "src", ".ssh", "authorized_keys")))

	annex_config = {
		'nlp_pkg' : "stanford-corenlp-full-2014-01-04",
		'nlp_port' : NLP_PORT,
		'annex_dir' : "/home/%s/unveillance_remote" % config['USER'],
		'uv_server_host' : config['DOCKER_IP'],
		'uv_uuid' : config['IMAGE_NAME'],
		'uv_log_cron' : 3,
		'ssh_root' : "/home/%s/.ssh" % config['USER']
	}

	frontend_config = {
		'documentcloud_no_ask' : True,
		'api.port' : config['FRONTEND_PORT'],
		'gdrive_auth_no_ask' : True,
		'server_host' : "localhost",
		'server_force_ssh' : False,
		'annex_local' : "/home/%s/unveillance_local" % config['USER'],
		'server_port' : config['API_PORT'],
		'server_message_port' : config['MESSAGE_PORT'],
		'annex_remote' : annex_config['annex_dir'],
		'server_use_ssl' : False,
		'uv_uuid' : annex_config['uv_uuid']
	}

	with open(os.path.join(BASE_DIR, "src", "unveillance.compass.annex.json"), 'wb+') as A:
		A.write(json.dumps(annex_config))

	with open(os.path.join(BASE_DIR, "src", "unveillance.compass.frontend.json"), 'wb+') as F:
		F.write(json.dumps(frontend_config))

	with settings(warn_only=True):
		if not os.path.exists(config['GENSIM_LIB']):
			from fabric.operations import prompt

			download_gensim_lib = prompt("Where should we download gensim_lib.tar.gz from?")
			local("wget -O %s --continue %s" % (config['GENSIM_LIB'], download_gensim_lib))

		local("mv %s %s" % (config['GENSIM_LIB'], os.path.join(BASE_DIR, "src", "CompassAnnex", "lib")))

	print "CONFIG JSONS WRITTEN."

	from dutils.dutils import generate_init_routine
	return build_dockerfile("Dockerfile.init", config) and generate_init_routine(config, with_config=with_config)

def build_d(with_config):
	res, config = append_to_config({'COMMIT_TO' : "compass_express"}, return_config=True, with_config=with_config)
	
	if not res:
		return False

	with settings(warn_only=True):
		local("mv %s %s" % (os.path.join(BASE_DIR, "src", "CompassAnnex", "lib", "gensim_lib.tar.gz"), config['GENSIM_LIB']))

	for p in ["API_PORT", "MESSAGE_PORT", "FRONTEND_PORT", "NLP_PORT"]:
		DEFAULT_PORTS.append(config[p])

	res, config = append_to_config({
		'DEFAULT_PORTS' : " ".join([str(p) for p in DEFAULT_PORTS]),
		'PUBLISH_PORTS' : [
			config['API_PORT_PUBLISHED'], 
			config['FRONTEND_PORT_PUBLISHED'], 
			config['MESSAGE_PORT_PUBLISHED']
		]
	}, return_config=True, with_config=with_config)

	if not res:
		return False

	print config

	from dutils.dutils import generate_build_routine
	return (build_dockerfile("Dockerfile.build", config) and generate_build_routine(config, with_config=with_config))
	
def commit_d(with_config):	
	try:
		config = __load_config(with_config=with_config)
	except Exception as e:
		print e, type(e)

	if config is None:
		return False

	print config

	from dutils.dutils import generate_run_routine, generate_shutdown_routine, finalize_assets
	return (generate_run_routine(config, src_dirs=["CompassAnnex", "CompassFrontend"], with_config=with_config) and generate_shutdown_routine(config, with_config=with_config) and finalize_assets(with_config=with_config))


def update_d(with_config):
	return build_dockerfile("Dockerfile.update", __load_config(with_config=with_config))

if __name__ == "__main__":
	res = False
	with_config = None if len(argv) == 2 else argv[2]

	if argv[1] == "init":
		res = init_d(with_config)
	elif argv[1] == "build":
		res = build_d(with_config)
	elif argv[1] == "commit":
		res = commit_d(with_config)
	elif argv[1] == "finish":
		res = True
	elif argv[1] == "update":
		res = update_d(with_config)
	
	print "RESULT: ", res 
	exit(0 if res else -1)