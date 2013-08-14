# Author: Joseph Lisee <jlisee@gmail.com>

# Installs ghc and cabal so we can install other haskell packages
{{ pillar['cabal-install'] }}:
  pkg:
    - installed
