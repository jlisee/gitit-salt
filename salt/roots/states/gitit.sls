# Author: Joseph Lisee <jlisee@gmail.com>

# Installs the packages needed for gitit

pandoc:
  cabal:
    - installed
    - flags:
        - highlighting
    - require:
        - pkg: {{ pillar['cabal-install'] }}

gitit:
  cabal:
    - installed
    - require:
        - cabal: pandoc