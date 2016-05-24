# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "ubuntu-monitoring"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 3000, host: 3000
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  config.vm.network "forwarded_port", guest: 8083, host: 8083
  config.vm.network "forwarded_port", guest: 8086, host: 8086

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  config.vm.network "private_network", ip: "192.168.57.199", virtualbox__intnet: "vboxintnet1"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  config.vm.synced_folder "~/Downloads", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    # vb.gui = true
  #
     # Customize the amount of memory on the VM:
     vb.memory = "2048"
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL

    # Install Python
    sudo apt-get update
    sudo apt-get install -y libxml2-dev libxslt1-dev python-dev libz-dev libssl-dev libffi-dev
    curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python2.7
    sudo pip install junos-eznc

    # Install InfluxDB
    wget https://dl.influxdata.com/influxdb/releases/influxdb_0.13.0_amd64.deb
    sudo dpkg -i influxdb_0.13.0_amd64.deb
    # wget -O /tmp/influxdb_latest_amd64.deb https://s3.amazonaws.com/influxdb/influxdb_latest_amd64.deb
    # sudo dpkg -i /tmp/influxdb_latest_amd64.deb
    sudo pip install influxdb

    # Install Grafana
    wget https://grafanarel.s3.amazonaws.com/builds/grafana_3.0.2-1463383025_amd64.deb
    # wget -O /tmp/grafana_2.0.2_amd64.deb https://grafanarel.s3.amazonaws.com/builds/grafana_2.0.2_amd64.deb
    sudo apt-get install -y adduser libfontconfig
    # sudo dpkg -i /tmp/grafana_2.0.2_amd64.deb
    sudo dpkg -i grafana_3.0.2-1463383025_amd64.deb

    # Start our Services
    sudo service influxdb start
    sudo service grafana-server start

    # Configure Graphana to start on boot
    sudo update-rc.d grafana-server defaults 95 10

  SHELL
end