import os, json
from sys import argv, exit

from dutils.conf import DUtilsKey, DUtilsKeyDefaults, build_config, BASE_DIR, append_to_config, save_config
from dutils.dutils import build_routine, build_dockerfile

API_PORT = 8889
MESSAGE_PORT = 8890
FRONTEND_PORT = 8888
NLP_PORT = 8887

DEFAULT_PORTS = [22, API_PORT, MESSAGE_PORT, FRONTEND_PORT, NLP_PORT]

def init_d(with_config):
	conf_keys = [
		DUtilsKeyDefaults['USER'],
		DUtilsKeyDefaults['USER_PWD'],
		DUtilsKeyDefaults['IMAGE_NAME']
	]

	config = build_config(conf_keys, with_config)

	from dutils.dutils import get_docker_exe, get_docker_ip

	docker_exe = get_docker_exe()
	if docker_exe is None:
		return False

	save_config(config)
	res, config = append_to_config({
		'DOCKER_EXE' : docker_exe, 
		'DOCKER_IP' : get_docker_ip()
	}, return_config=True)

	if not res:
		return False

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
		'api.port' : FRONTEND_PORT,
		'gdrive_auth_no_ask' : True,
		'server_host' : "localhost",
		'server_force_ssh' : False,
		'annex_local' : "/home/%s/unveillance_local" % config['USER'],
		'server_port' : API_PORT,
		'server_message_port' : MESSAGE_PORT,
		'annex_remote' : annex_config['annex_dir'],
		'server_use_ssl' : False,
		'uv_uuid' : annex_config['uv_uuid']
	}

	with open(os.path.join(BASE_DIR, "src", "unveillance.compass.annex.json"), 'wb+') as A:
		A.write(json.dumps(annex_config))

	with open(os.path.join(BASE_DIR, "src", "unveillance.compass.frontend.json"), 'wb+') as F:
		F.write(json.dumps(frontend_config))

	from dutils.dutils import generate_init_routine
	return build_dockerfile("Dockerfile.init", config) and generate_init_routine(config)

def build_d():
	res, config = append_to_config({
		'DEFAULT_PORTS' : " ".join([str(p) for p in DEFAULT_PORTS]),
		'COMMIT_TO' : "compass_express"
	}, return_config=True)
	
	if not res:
		return False

	from dutils.dutils import generate_build_routine
	return (build_dockerfile("Dockerfile.build", config) and generate_build_routine(config))
	
def commit_d():	
	res, config = append_to_config({'PUBLISH_PORTS' : [API_PORT, FRONTEND_PORT, MESSAGE_PORT]},
		return_config=True)

	if not res:
		return False

	from dutils.dutils import generate_run_routine, generate_shutdown_routine
	return (generate_run_routine(config) and generate_shutdown_routine(config))

def update_d():
	from dutils.conf import __load_config
	return build_dockerfile("Dockerfile.update", __load_config(os.path.join(BASE_DIR, "config.json")))

if __name__ == "__main__":
	res = False

	if argv[1] == "init":
		res = init_d(None if len(argv) == 2 else argv[2])
	elif argv[1] == "build":
		res = build_d()
	elif argv[1] == "commit":
		res = commit_d()
	elif argv[1] == "update":
		res = update_d()
	
	exit(0 if res else -1)