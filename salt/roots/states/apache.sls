# Author: Joseph Lisee <jlisee@gmail.com>

{# Read variable to reduce duplication below #}
{% set apache_settings = pillar['apache_settings'] %}

# Installs apache and makes sure it's running
{{ pillar['apache'] }}:
  pkg:
    - installed
  service:
    - running
    - require:
      - pkg: {{ pillar['apache'] }}
    # These watches are needed so that apache is restarted when it's
    # configuration changes
    - watch:
      - file: {{ apache_settings['sites-enabled'] }}/*
      - file: {{ apache_settings['mods-enabled'] }}/*

# Install site
{{ apache_settings['sites-enabled'] }}/gitit:
  file.managed:
    - source: salt://apache/gitit
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - require:
      - pkg: {{ pillar['apache'] }}
    - require_in:
      - service: {{ pillar['apache'] }}

# Make sure the default site is not present
{{ apache_settings['sites-enabled'] }}/000-default:
  file.absent:
    - require:
      - file: {{ apache_settings['sites-enabled'] }}/gitit
      - pkg: {{ pillar['apache'] }}
    - require_in:
      - service: {{ pillar['apache'] }}


# Enabled needed apache modules so the proxy works
{% for file in apache_settings['mod_files'] %}
{{ apache_settings['mods-enabled'] }}/{{ file }}:
  file.symlink:
    - target: {{ apache_settings['mods-available'] }}/{{ file }}
    - require:
      - file: {{ apache_settings['sites-enabled'] }}/gitit
      - pkg: {{ pillar['apache'] }}
    - require_in:
      - service: {{ pillar['apache'] }}
{% endfor -%}
