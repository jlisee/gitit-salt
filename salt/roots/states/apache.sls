{{ pillar['apache'] }}:
  pkg:
    - installed
  service:
    - running
    - require:
      - pkg: {{ pillar['apache'] }}