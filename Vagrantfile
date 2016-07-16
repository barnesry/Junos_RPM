# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
VAGRANTFILE_API_VERSION = "2"
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    config.ssh.insert_key = false

    config.vm.define "ubuntu-monitoring" do |srv|

        # The most common configuration options are documented and commented below.
        # For a complete reference, please see the online documentation at
        # https://docs.vagrantup.com.

        # Every Vagrant development environment requires a box. You can search for
        # boxes at https://atlas.hashicorp.com/search.
        srv.vm.box = "ubuntu/trusty64"
        srv.vm.hostname = "ubuntu-monitoring"

        # Disable automatic box update checking. If you disable this, then
        # boxes will only be checked for updates when the user runs
        # `vagrant box outdated`. This is not recommended.
        # srv.vm.box_check_update = false

        # Create a forwarded port mapping which allows access to a specific port
        # within the machine from a port on the host machine. In the example below,
        # accessing "localhost:8080" will access port 80 on the guest machine.
        srv.vm.network "forwarded_port", guest: 3000, host: 3000
        srv.vm.network "forwarded_port", guest: 8080, host: 8080
        srv.vm.network "forwarded_port", guest: 8083, host: 8083
        srv.vm.network "forwarded_port", guest: 8086, host: 8086

        # Create a private network, which allows host-only access to the machine
        # using a specific IP.
        srv.vm.network "private_network", ip: "192.168.56.199"
	# virtualbox__intnet: "vboxintnet1"

        # Create a public network, which generally matched to bridged network.
        # Bridged networks make the machine appear as another physical device on
        # your network.
        srv.vm.network "public_network"

        # Share an additional folder to the guest VM. The first argument is
        # the path on the host to the actual folder. The second argument is
        # the path on the guest to mount the folder. And the optional third
        # argument is a set of non-required options.
        srv.vm.synced_folder "~/Downloads", "/vagrant_data"

        # Provider-specific configuration so you can fine-tune various
        # backing providers for Vagrant. These expose provider-specific options.
        # Example for VirtualBox:
        #
        srv.vm.provider "virtualbox" do |vb|
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
        srv.vm.provision "shell", inline: <<-SHELL

        # Install Python
        sudo apt-get update
        sudo apt-get install -y libxml2-dev libxslt1-dev python-dev libz-dev libssl-dev libffi-dev
        curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | sudo python2.7
        sudo pip install junos-eznc

        # Install InfluxDB
        wget --progress=dot:giga -O /tmp/influxdb_0.13.0_amd64.deb https://dl.influxdata.com/influxdb/releases/influxdb_0.13.0_amd64.deb
        sudo dpkg -i /tmp/influxdb_0.13.0_amd64.deb
        sudo pip install influxdb

        # Install Grafana
        wget --progress=dot:giga -O /tmp/grafana_3.0.2-1463383025_amd64.deb https://grafanarel.s3.amazonaws.com/builds/grafana_3.0.2-1463383025_amd64.deb
        sudo apt-get install -y adduser libfontconfig
        sudo dpkg -i /tmp/grafana_3.0.2-1463383025_amd64.deb

        # Start our Services
        sudo service influxdb start
        sudo service grafana-server start

        # Configure Graphana to start on boot
        sudo update-rc.d grafana-server defaults 95 10

        SHELL
    end


    vsrx_name = "vsrx".to_sym

    config.vm.define vsrx_name do |vsrx|

        vsrx.vm.hostname = vsrx_name
        # vsrx.vm.box = 'juniper/ffp-12.1X47-D20.7'
        vsrx.vm.box = 'juniper/ffp-12.1X47-D15.4-packetmode'
        vsrx.ssh.username = 'vagrant'

        vsrx.vm.provider "virtualbox" do |v|
            v.name = "vagrant-" + vsrx.vm.hostname.to_s
            v.memory = 1024
            v.cpus = 2
        end

        # DO NOT REMOVE / NO VMtools installed
        vsrx.vm.synced_folder '.', '/vagrant', disabled: true

        # In vSRX 1.0 the first interface in Vagrant is assigned automagically to the NAT interface (ie. ge-0/0/0)

        # Management port (our inside interface ge-0/0/1 which we want to be vboxnet0 our host-only)
        vsrx.vm.network 'private_network', auto_config: false, nic_type: 'virtio', ip: '192.168.56.107'

    end


    ##############################
    ## Box provisioning    #######
    ##############################
    # https://www.vagrantup.com/docs/provisioning/ansible.html
    ##############################
    if !Vagrant::Util::Platform.windows?
        config.vm.provision "ansible" do |ansible|
            ansible.groups = {
                "vsrx" => [ "127.0.0.1" ],
                "all:children" => ["vsrx" ]
            }
            ansible.verbose = 'v'
            ansible.playbook = "provisioning/playbook-deploy-config.yaml"
        end
    end

end
