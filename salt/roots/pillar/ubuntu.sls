# Author: Joseph Lisee <jlisee@gmail.com>

# Define package names for Ubuntu

apache: apache2
cabal-install: cabal-install

# Define the apache specific directory informationx
apache_settings:
  sites-enabled: /etc/apache2/sites-enabled
  mods-available: /etc/apache2/mods-available
  mods-enabled: /etc/apache2/mods-enabled
  mod_files:
    - proxy.conf
    - proxy.load
    - proxy_http.load
    - rewrite.load