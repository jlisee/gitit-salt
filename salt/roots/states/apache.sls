# Author: Joseph Lisee <jlisee@gmail.com>

# Installs apache and makes sure it's running

{{ pillar['apache'] }}:
  pkg:
    - installed
  service:
    - running
    - require:
      - pkg: {{ pillar['apache'] }}