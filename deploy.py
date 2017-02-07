
import os
import sys
import time
import shlex

from conf import Conf
from console import Console

class Deploy:

	def __init__(self):
		self.config = Conf()
		self.console = Console()

	def path(self, option):
		path = self.config.get(option)
		return os.path.abspath(path);

	def chown(self, path):
		user = self.config.get('deploy_user')
		self.console.run(['chown', '-R', user, path])

	def linkdir(self, src, dst):
		if os.path.exists(dst) == True:
			self.console.run(['unlink', dst])
		self.console.run(['ln', '-s', src, dst])

	def version(self, deploy_path):
		hash = self.console.run(['git', 'rev-parse', 'HEAD'], cwd=deploy_path);
		return hash[0:8]

	def sync(self, src, dst):
		self.console.run([
			'rsync',
			'--links',
			'--checksum',
			'--whole-file',
			'--recursive',
			src.rstrip('/') + '/',
			dst
		])

	def checkout(self):
		deploy_path = self.path('release_path') + '/' + time.strftime('%Y%m%d%H%M%S')

		if os.path.exists(deploy_path) == False:
			os.makedirs(deploy_path, 0755)

		self.console.success('Fetching files')
		self.console.run([
			'ssh-agent',
			'sh',
			'-c',
			'\'ssh-add',
			self.config.get('deploy_key') + ';',
			'git',
			'clone',
			'--quiet',
			'--recursive',
			'--depth', '1',
			'--branch', 'master',
			self.config.get('repo_url'),
			deploy_path,
			'\''
		])

		return deploy_path

	def composer(self, deploy_path):
		if os.path.exists(deploy_path + '/composer.json') == False:
			return None

		self.console.success('Installing composer dependencies')
		self.console.run([
			'composer',
			'--quiet',
			'--no-interaction',
			'install',
			'--prefer-dist',
			'--no-dev',
			'--optimize-autoloader'
		], cwd=deploy_path);

	def scripts(self, scripts_to_run, deploy_path):
		if self.config.has(scripts_to_run) == False:
			return

		scripts = self.config.get(scripts_to_run)

		for line in scripts:
			command = line.replace('$deploy_path', deploy_path)
			self.console.run(shlex.split(command), cwd=deploy_path)

	def clean(self):
		release_path = self.path('release_path')
		deployments = self.console.run(['ls', '-1tA', release_path])
		deploys_to_keep = int(self.config.get('deploys_to_keep'))

		for folder in deployments.splitlines()[deploys_to_keep:]:
			self.console.run(['rm', '-rf', folder], cwd=release_path);

	def rollback(self, version):
		deploy_path = self.path('release_path') + '/' + version

		if os.path.exists(deploy_path) == False:
			self.console.error('Version does not exist')
			return None

		self.console.success('Rolling back')
		self.linkdir(deploy_path, self.config.get('symlink'))

	def deploy(self):
		# checkout files
		deploy_path = self.checkout()

		# fetch resources
		self.composer(deploy_path)

		# static resources
		if self.config.has('static_path'):
			self.console.success('Copying static resources')
			self.sync(self.path('static_path'), deploy_path)

		self.console.success('Running pre-scripts')
		self.scripts('pre_scripts', deploy_path)

		self.console.success('Updating file owner')
		self.chown(deploy_path)

		self.console.success('Updating symlink')
		self.linkdir(deploy_path, self.config.get('symlink'))

		self.console.success('Running post-scripts')
		self.scripts('post_scripts', deploy_path)

		self.console.success('Cleaning up old releases')
		self.clean()
