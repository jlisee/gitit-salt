Gitit Salt
===========

Automated install and setup of a Gitit wiki.

Gitit Salt installs the VCS backed [Gitit](http://gitit.net/)
wiki on Ubuntu using the Apache web server as a proxy.
[SaltStack](http://saltstack.org/) and
[Cabal](http://www.haskell.org/cabal/) are used to install and
configure the needed software.

Quick Start
============

If you have an Ubuntu 12.04 server handy these instructions will use
salt to install and configure gitit + apache.

 1. Install Salt:

        wget -O - http://bootstrap.saltstack.org | sudo sh

 2. Grab the code:

        git clone https://github.com/jlisee/gitit-salt

 3. Install our salt minion configuration:

        sudo cp gitit-salt/salt/minion /etc/salt/minion

 4. Install the salt state files:

        sudo mkdir -p /srv
        sudo cp -r gitit-salt/salt/roots /srv/salt

 5. Instruct salt to configuration our server:

        sudo salt-call state.highstate

 6. See you need wiki at: http://youserver.com/


Testing with Vagrant
=====================

If you don't have a server handy, you can use Vagrant to create and
manage a local virtual machine for you.  The Vagrantfile in this
repository creates an Ubuntu 12.04 64 bit VM and uses our salt files to
setup the machine.

 1. Install [Vagrant](http://www.vagrantup.com/)
 2. Install Salty Vagrant (``vagrant plugin install vagrant-salt``)
 3. Run ``vagrant up``
 4. Wait several minutes for everything to compile (more than 10, cabal
 is *really* slow).
 5. See you new wiki [here](http://localhost:8080)


What exactly is this doing?
============================

Best to just lay out what is done step by step:

 1. Install ghc (haskell compiler), apache (web server), cabal-install
 (Haskell's almost package manager) with apt-get.
 2. Use cabal to install gitit.
 3. Setup gitit in ``/srv/gitit`` with the wiki using the git repository
 in ``/srv/gitit/wikidata``.
 4. Create a gitit upstart service (``/etc/init/gitit``) serving on port
 5001.
 4. Configure apache to forward all requests to the local gitit server
 (``/etc/apache2/sites-enabled/gitit``).


How does all this work?
========================

We use the magic of Salt to configure our server. Salt is a
configuration management tool (like
[Ansible](http://www.ansibleworks.com/),
[Puppet](https://puppetlabs.com/) or
[Chef](http://www.opscode.com/chef/)).  It uses all the stuff in this
repository to make sure the right software is installed, the right
configuration files are in place, and the right services are running.

With salt stack you define a set of *states* which define the
configuration you want a system to be in.  Those states are described in
yaml files, optionally parametrized by data stored in *pillars* (also
yaml files).  If those states determine the system needs changes, they
execute those with *modules*.

Modules and states are implemented in python.  In this repository you
fill find custom states and modules for managing Haskell based software
with cabal install.


More information
=================

There are a lot of moving parts here, to learn more about them check out
the documentation sources below:


 * [Gitit README](http://gitit.net/README)
 * [Salt Stack Docs](http://docs.saltstack.com/)
 * [Vagrant Docs](http://docs.vagrantup.com/v2/)
