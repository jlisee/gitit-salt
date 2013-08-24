# Author: Joseph Lisee <jlisee@gmail.com>

# Installs apache and makes sure it's running

{{ pillar['apache'] }}:
  pkg:
    - installed
  service:
    - running
    - require:
      - pkg: {{ pillar['apache'] }}

# Read variable to reduce duplication below
{% set apache_settings = pillar['apache_settings'] %}

# Install site
{{ apache_settings['sites-enabled'] }}/gitit:
  file.managed:
    - source: salt://apache/gitit
    - user: root
    - group: root
    - mode: 644
    - template: jinja

# Make sure the default site is not present
{{ apache_settings['sites-enabled'] }}/000-default:
  file.absent:
    - require:
      - file: {{ apache_settings['sites-enabled'] }}/gitit

# Enabled needed apache modules so the proxy works
{% for file in apache_settings['mod_files'] %}
{{ apache_settings['mods-enabled'] }}/{{ file }}:
  file.symlink:
    - target: {{ apache_settings['mods-available'] }}/{{ file }}
    - require:
      - file: {{ apache_settings['sites-enabled'] }}/gitit
{% endfor -%}
