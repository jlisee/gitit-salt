# Author: Joseph Lisee <jlisee@gmail.com>

# Installs the packages needed for gitit

pandoc:
  cabal:
    - installed
    - user: gitit
    - version: 1.11.1
    - flags:
      - highlighting
    - require:
      - pkg: {{ pillar['cabal-install'] }}
      - user: gitit

gitit-cabal:
  cabal:
    - installed
    - name: gitit
    - version: 0.10.3.1
    - user: gitit
    - require:
      - cabal: pandoc
      - user: gitit

# Make sure we have git installed
git:
  pkg.installed

{# Set some local variable to simplify the states -#}
{% set gitit = pillar['gitit'] -%}
{% set gitit_repo_dir = gitit['root_dir'] + '/' + gitit['repo_name'] -%}

# Create a the gitit user
gitit:
  group.present:
    - gid:  {{ gitit['gid'] }}
  user.present:
    - shell: /bin/bash
    - uid: {{ gitit['uid'] }}
    - gid: {{ gitit['gid'] }}
    - groups:
      - gitit
    - require:
      - group: gitit

# Create the main git directory
gitit_dir:
  file.directory:
    - name: {{ gitit['root_dir'] }}
    - user: gitit
    - group: gitit
    - dir_mode: 755
    - require:
      - user: gitit

# Create repo directory
gitit_repo:
  file.directory:
    - name: {{ gitit_repo_dir }}
    - user: gitit
    - group: gitit
    - dir_mode: 755
    - require:
      - file: gitit_dir
      - user: gitit

# Install the conf file
gitit_conf_file:
  file.managed:
    - name: {{ gitit['root_dir'] }}/{{ gitit['conf_file'] }}
    - source: salt://gitit/wiki.conf
    - makedirs: True
    - user: gitit
    - group: gitit
    - mode: 644
    - template: jinja
    - require:
      - file: gitit_dir
      - user: gitit

# Create git repo if it doesn't exist'
init_repo:
  cmd.run:
    - name: git init
    - unless: ls {{ gitit_repo_dir }}/.git
    - cwd: {{ gitit_repo_dir }}
    - user: gitit
    - group: gitit
    - require:
      - file: gitit_repo
      - pkg: git
      - user: gitit

# Install the upstart job
/etc/init/gitit.conf:
  file.managed:
    - source: salt://upstart/gitit.conf
    - user: root
    - group: root
    - mode: 644
    - template: jinja

# Make sure the job it running
gitit_service:
  service:
    - name: gitit
    - running
    - require:
      - cabal: gitit
      - cmd: init_repo
      - file: /etc/init/gitit.conf
      - file: gitit_conf_file
      - user: gitit
