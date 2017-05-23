# -*- mode: ruby -*-
# vi: set ft=ruby :

num_of_slaves = 1
prefix_ip_addr = "174.10.100."
tag_version = 6
stable_contrail_ansible_sha = "47a025d8bbef129baf4455fe69ad8cc5d8ceb2eb"
mesos_github_username = "username"
mesos_github_password = "password"

Vagrant.configure("2") do |config|
    config.vm.box = "centos/7"

    # Sync fix. deatils(https://seven.centos.org/2017/05/updated-centos-vagrant-images-available-v1704-01/)
    config.vm.synced_folder ".", "/home/vagrant/sync", disabled: true

    #Setup ip's for everyone
    builder_ip = "%s100" % [prefix_ip_addr]
    controller_ip = "%s101" % [prefix_ip_addr]
    slaves_ip = "%s102" % [prefix_ip_addr]
    slaves_ip_string = ""
    cntr = 1
    until cntr > (num_of_slaves - 1)  do
        slaves_ip_string.concat("#{prefix_ip_addr}#{101+cntr}\\\n")
        cntr = cntr + 1
    end
    slaves_ip_string.concat("#{prefix_ip_addr}#{101+num_of_slaves}")

    # Setup controller
    config.vm.define :controller do |controller|
        controller.vm.hostname = "controller"
        controller.vm.network :private_network, ip: controller_ip
        #controller.vm.synced_folder "controller/", "/home/vagrant/sync"
        controller.vm.provider "virtualbox" do |v|
            v.memory = 1024 * 16
            v.cpus = 8
            v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
        end
        controller.vm.network "forwarded_port", guest: 80, host: 80
        controller.vm.network "forwarded_port", guest: 8080, host: 8080
        controller.vm.network "forwarded_port", guest: 8082, host: 8082
        controller.vm.network "forwarded_port", guest: 8085, host: 8085
        controller.vm.network "forwarded_port", guest: 8143, host: 8143
        controller.vm.provision 'shell', :inline => <<EOF
        # Setup passless access
        mkdir -p /root/.ssh
        cat /vagrant/controller/id_rsa.pub >> /root/.ssh/authorized_keys
EOF
    end

    # Setup slaves
    config.vm.define :slave do |slave|
        slave.vm.hostname = "slave"
        slave.vm.network :private_network, ip: slaves_ip
        #slave.vm.synced_folder "slave/", "/home/vagrant/sync"
        slave.vm.provider "virtualbox" do |v|
            v.memory = 1024 * 16
            v.cpus = 8
            v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
        end
        slave.vm.network "forwarded_port", guest: 8880, host: 8880
        slave.vm.network "forwarded_port", guest: 8881, host: 8881
        slave.vm.network "forwarded_port", guest: 8882, host: 8882
        slave.vm.provision 'shell', :inline => <<EOF
 
        # Setup passless access
        mkdir -p /root/.ssh
        cat /vagrant/slaves/id_rsa.pub >> /root/.ssh/authorized_keys
        yum upgrade -y
        yum install kernel-headers kernel-devel -y
EOF
    end

    # Setup builder
    config.vm.define :builder do |builder|
        builder.vm.hostname = "builder"
        builder.vm.network :private_network, ip: builder_ip
        #builder.vm.synced_folder "builder_sync/", "/home/vagrant/sync"
        builder.vm.provider "virtualbox" do |v|
            v.memory = 1024 * 16
            v.cpus = 8
            v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
        end
        # Setup a contrail ansible repo
        builder.vm.provision :shell, inline: "sudo yum install git -y"

        builder.vm.provision 'shell', :inline => <<EOF
            git clone https://github.com/Juniper/contrail-ansible.git
            cd contrail-ansible
            git reset --hard #{stable_contrail_ansible_sha}

            # Copy inventory file
            cp /vagrant/builder/contrail-inventory.ini /home/vagrant/contrail-ansible/playbooks/inventory/contrail-inventory.ini
            sed -i $'s/10.10.10.10/#{controller_ip}/g' /home/vagrant/contrail-ansible/playbooks/inventory/contrail-inventory.ini
            sed -i $'s/20.20.20.20/#{slaves_ip_string}/g' /home/vagrant/contrail-ansible/playbooks/inventory/contrail-inventory.ini
            sed -i $'s/3054/#{tag_version}/g' /home/vagrant/contrail-ansible/playbooks/inventory/contrail-inventory.ini

            # Setup ansible environment
            cp /vagrant/builder/get-pip.py /home/vagrant/get-pip.py
            sudo python /home/vagrant/get-pip.py
            sudo pip install Jinja2==2.8.1
            sudo yum install gcc -y
            sudo yum install openssl-devel -y
            sudo yum install python-devel -y
            sudo pip install ansible==2.2.0

            # Setup passless access
            mkdir -p ~/.ssh
            cp /vagrant/builder/id_rsa /root/.ssh/id_rsa
            cp /vagrant/builder/id_rsa.pub /root/.ssh/id_rsa.pub

            # Run ansible
            echo "Host *" > /root/.ssh/config
            echo "  StrictHostKeyChecking no" >> /root/.ssh/config
            chmod 400 /root/.ssh/config
            cd /home/vagrant/contrail-ansible/playbooks
            cp -r /vagrant/builder/container_images .
            cp /vagrant/builder/patch.diff /home/vagrant/contrail-ansible/playbooks/patch.diff
            #git pull
            yum install patch -y
            patch -p2 < patch.diff
            time ansible-playbook -vvv -i inventory/contrail-inventory.ini site.yml
EOF

        # Setup a contrail mesos ansible repo
        builder.vm.provision 'shell', :inline => <<EOF
            git clone https://#{mesos_github_username}:#{mesos_github_password}@github.com/Juniper/contrail-mesos-ansible.git

            # Copy inventory file
            cp /vagrant/builder/mesos-inventory.ini /home/vagrant/contrail-mesos-ansible/playbooks/inventory/mesos-inventory.ini
            sed -i $'s/20.20.20.20/#{slaves_ip_string}/g' /home/vagrant/contrail-mesos-ansible/playbooks/inventory/mesos-inventory.ini
            cd /home/vagrant/contrail-mesos-ansible/playbooks
            time ansible-playbook -vvv -i inventory/mesos-inventory.ini all.yml
EOF
    end
end
