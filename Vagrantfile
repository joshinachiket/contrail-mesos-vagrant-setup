# -*- mode: ruby -*-
num_of_slaves = 2
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
    slaves_ip_string = ""
    num_of_slaves.times do |num|
        slaves_ip_string.concat("#{prefix_ip_addr}#{102+num}\\\n")
    end
    # Setup builder
    vm_name = "builder"
    config.vm.define vm_name do |host|
        host.vm.hostname = vm_name
        host.vm.network :private_network, ip: builder_ip
        # Setup a contrail ansible repo
        host.vm.provision 'shell', :inline => <<EOF
            sudo yum install git -y
            git clone https://github.com/Juniper/contrail-ansible.git
            cd contrail-ansible
            git reset --hard #{stable_contrail_ansible_sha}
EOF

        # Copy inventory file
        host.vm.provision "file", source: "my-inventory.mesos", destination: "/home/vagrant/contrail-ansible/playbooks/inventory/my-inventory.mesos"
        host.vm.provision :shell, inline: "sudo sed -i $'s/10.10.10.10/#{controller_ip}/g' /home/vagrant/contrail-ansible/playbooks/inventory/my-inventory.mesos"
        host.vm.provision :shell, inline: "sudo sed -i $'s/20.20.20.20/#{slaves_ip_string}/g' /home/vagrant/contrail-ansible/playbooks/inventory/my-inventory.mesos"
        host.vm.provision :shell, inline: "sudo sed -i $'s/3054/#{tag_version}/g' /home/vagrant/contrail-ansible/playbooks/inventory/my-inventory.mesos"
    end
end
