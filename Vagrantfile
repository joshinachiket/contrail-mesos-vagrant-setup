# -*- mode: ruby -*-
# vi: set ft=ruby :

num_of_slaves = 1
prefix_ip_addr = "174.24.197."
tag_version = 3055
stable_contrail_ansible_sha = "5587115e2bb551fde745f441c4276494fa0ed57c"

Vagrant.configure("2") do |config|
    config.vm.box = "centos/7"

    # Sync fix. deatils(https://seven.centos.org/2017/05/updated-centos-vagrant-images-available-v1704-01/)
    config.vm.synced_folder ".", "/home/vagrant/sync", disabled: true

    #Setup ip's for everyone
    builder_ip = "%s100" % [prefix_ip_addr]
    controller_ip = "%s101" % [prefix_ip_addr]
    slaves_ip = "%s102" % [prefix_ip_addr]
    slaves_ip_string = ""
    num_of_slaves.times do |num|
        slaves_ip_string.concat("#{prefix_ip_addr}#{102+num}\\\n")
    end

    # Setup controller
    config.vm.define :controller do |controller|
        controller.vm.hostname = "controller"
        controller.vm.network :private_network, ip: controller_ip
        controller.vm.provision 'shell', :inline => <<EOF
            # Setup passless access
            mkdir -p /root/.ssh
            cat /vagrant/id_rsa.pub >> /root/.ssh/authorized_keys
EOF
    end

    # Setup slaves
    config.vm.define :slave do |slave|
        slave.vm.hostname = "slave"
        slave.vm.network :private_network, ip: slaves_ip
        slave.vm.provision 'shell', :inline => <<EOF
            # Setup passless access
            mkdir -p /root/.ssh
            cat /vagrant/id_rsa.pub >> /root/.ssh/authorized_keys
            yum upgrade -y
            yum install kernel-headers kernel-devel -y
EOF
    end

    # Setup builder
    config.vm.define :builder do |builder|
        builder.vm.hostname = "builder"
        builder.vm.network :private_network, ip: builder_ip
        # Setup a contrail ansible repo
        builder.vm.provision :shell, inline: "sudo yum install git -y"

        builder.vm.provision 'shell', :inline => <<EOF
            git clone https://github.com/Juniper/contrail-ansible.git
            cd contrail-ansible
            git reset --hard #{stable_contrail_ansible_sha}

            # Copy inventory file
            cp /vagrant/my-inventory.mesos /home/vagrant/contrail-ansible/playbooks/inventory/my-inventory.mesos
            sed -i $'s/10.10.10.10/#{controller_ip}/g' /home/vagrant/contrail-ansible/playbooks/inventory/my-inventory.mesos
            sed -i $'s/20.20.20.20/#{slaves_ip_string}/g' /home/vagrant/contrail-ansible/playbooks/inventory/my-inventory.mesos
            sed -i $'s/3054/#{tag_version}/g' /home/vagrant/contrail-ansible/playbooks/inventory/my-inventory.mesos

            # Setup ansible environment
            cp /vagrant/get-pip.py /home/vagrant/get-pip.py
            sudo python /home/vagrant/get-pip.py
            sudo pip install Jinja2==2.8.1
            sudo yum install gcc -y
            sudo yum install openssl-devel -y
            sudo yum install python-devel -y
            sudo pip install ansible==2.2.0

            # Setup passless access
            mkdir -p ~/.ssh
            cp /vagrant/id_rsa /root/.ssh/id_rsa
            cp /vagrant/id_rsa.pub /root/.ssh/id_rsa.pub

            # Run ansible
            echo "Host *" > /root/.ssh/config
            echo "  StrictHostKeyChecking no" >> /root/.ssh/config
            chmod 400 /root/.ssh/config
            cd /home/vagrant/contrail-ansible/playbooks
            ansible-playbook -vvv -i inventory/my-inventory.mesos site.yml
EOF
    end
end
