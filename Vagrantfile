# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # Vagrant box we are building off of
  config.vm.box = "precise64"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"

  # Provision (configure) VM with the Salt Stack
  config.vm.provision :salt do |salt|

    salt.minion_config = "salt/minion"
    salt.run_highstate = true

  end

  # Forward port 80 to 8080 on the host so we can see Apache
  config.vm.network :forwarded_port, guest: 80, host: 8080

  # Mount our salt folder so we have our states to provision with
  config.vm.synced_folder "salt/roots/", "/srv/salt/"
end
