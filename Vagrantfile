#-*- mode: ruby -*-
# vi: set ft=ruby :

require 'yaml'
# read config.yaml and set variables
config = YAML.load_file('config.yaml')
num_of_slaves = config['vms']['num_of_slaves']
prefix_ip_addr = config['vms']['prefix_ip_addr']
tag_version = config['vms']['tag_version']
stable_contrail_ansible_sha = config['vms']['stable_contrail_ansible_sha']
box = config['vms']['box']
mesos = config['mesos']['include']

# read any user ports else use the default port
if config['port']['http'] then http = config['port']['http'] else http = 80 end
if config['port']['contrail'] then contrail = config['port']['contrail'] else contrail = 8080 end
if config['port']['controller1'] then controller1 = config['port']['controller1'] else controller1 = 8082 end
if config['port']['controller2'] then controller2 = config['port']['controller2'] else controller2 = 8085 end
if config['port']['contrail_http'] then contrail_http = config['port']['contrail_http'] else contrail_http = 8143 end
if config['port']['marathon'] then  marathon = config['port']['marathon'] else marathon = 8880 end
if config['port']['mesos_master'] then  mesos_master = config['port']['mesos_master'] else mesos_master = 8881 end

Vagrant.configure("2") do |config|
    config.vm.box = box
    config.ssh.insert_key = false

    # Sync fix. deatils(https://seven.centos.org/2017/05/updated-centos-vagrant-images-available-v1704-01/)
    config.vm.synced_folder ".", "/home/vagrant/sync", disabled: true

    #Setup ip's for VMS - builder, controller, slave(s)
    builder_ip = "%s100" % [prefix_ip_addr]
    controller_ip = "%s101" % [prefix_ip_addr]
    
    # slaves_ip = "%s102" % [prefix_ip_addr]
    
    mesos_master_ip = "%s102" % [prefix_ip_addr]
    slaves_ip_string = ""
    
    cntr = 1
    until cntr > (num_of_slaves - 1)  do
        slaves_ip_string.concat("#{prefix_ip_addr}#{101+cntr}\\\n")
        cntr = cntr + 1
    end
    
    slaves_ip_string.concat("#{prefix_ip_addr}#{101+num_of_slaves}")

    # Setup controller
    config.vm.define :controller do |controller|
       # Setup controller VM name and IP
       controller.vm.hostname = "controller"
       controller.vm.network :private_network, ip: controller_ip
       
       # Setup controller VM system requirements
       controller.vm.provider "virtualbox" do |v|
           v.memory = 1024 * 16
           v.cpus = 8
           v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
           v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
       end
        
       # Map controller VM ports to host
       controller.vm.network "forwarded_port", guest: 80, host: http 
       controller.vm.network "forwarded_port", guest: 8080, host: contrail
       controller.vm.network "forwarded_port", guest: 8082, host: controller1
       controller.vm.network "forwarded_port", guest: 8085, host: controller2
       controller.vm.network "forwarded_port", guest: 8143, host: contrail_http
       
       # Provision controller VM with passless access
       controller.vm.provision 'shell', :inline => <<EOF
         mkdir -p /root/.ssh
         cat /vagrant/controller/id_rsa.pub >> /root/.ssh/authorized_keys
         echo "controller setup ends"
EOF
   end

    # Setup slaves
    (1..num_of_slaves).each do |cntr|
	slave_name = "slave-#{101+cntr}"
       	config.vm.define slave_name do |slave|
	    # Setup slave VM name and IP
            slave.vm.hostname = slave_name
            slave_ip = "#{prefix_ip_addr}#{101+cntr}"
            slave.vm.network :private_network, ip: slave_ip
        
            # Setup slave VM system requirements
            slave.vm.provider "virtualbox" do |v|
                v.memory = 1024 * 16
                v.cpus = 8
                v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
                v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
            end
        
        # Map slave VM ports to host

        if cntr == 1
	    slave.vm.network "forwarded_port", guest: 8880, host: marathon
	    slave.vm.network "forwarded_port", guest: 8881, host: mesos_master
	end

        # Provision slave VM with passless access, python, net-tools, 
        # important scipts - get-pip, change_ip.sh, schedule-task.py
        slave.vm.provision 'shell', :inline => <<EOF
            mkdir -p /root/.ssh
            cat /vagrant/slaves/id_rsa.pub >> /root/.ssh/authorized_keys
            yum upgrade -y
            yum install kernel-headers kernel-devel -y
            cp /vagrant/builder/get-pip.py /home/vagrant/get-pip.py	
 
            sudo python /home/vagrant/get-pip.py
            pip install pyroute2==0.4.13
            pip install pyyaml
            yum install net-tools -y
        
	    # Copy change_ip.sh file from host to slave 
            cp /vagrant/slaves/change_ip.sh /home/vagrant/change_ip.sh
            # Copy the schedule-task.py from host to slave
            cp /vagrant/slaves/schedule-task.py /home/vagrant/schedule-task.py
            # copy config.yaml to slave to automate task scheduling
            cp /vagrant/config.yaml /home/vagrant/config.yaml
            echo "slave set up ended for: #{slave_name}"
EOF
        end
    end

    # Setup builder
    config.vm.define :builder do |builder|
        # Setup builder VM and IP
        builder.vm.hostname = "builder"
        builder.vm.network :private_network, ip: builder_ip
        
        # Setup builder VM system requirements
        builder.vm.provider "virtualbox" do |v|
            v.memory = 1024 * 16
            v.cpus = 8
            v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
            v.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
        end

        # Provision builder
        builder.vm.provision 'shell', :inline => <<EOF
              sudo yum install git -y
              echo "git installed"
              # Setup a contrail ansible repo
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
              # git pull
              yum install patch -y
              patch -p2 < patch.diff
              echo "contrail ansible starts executing"
              time ansible-playbook -vvv -i inventory/contrail-inventory.ini site.yml
              echo "contrail ansible ends executing"
EOF

	# If include mesos is true in the conf.yaml, begin provisioning mesos
	if mesos
            # Setup a contrail mesos ansible repo
	    builder.vm.provision "file", source: "~/contrail-mesos-ansible", destination: "contrail-mesos-ansible"
            
	    builder.vm.provision 'shell', :inline => <<EOF
                # Copy contrail-mesos inventory file and run ansible
                cp /vagrant/builder/mesos-inventory.ini /home/vagrant/contrail-mesos-ansible/playbooks/inventory/mesos-inventory.ini
                sed -i $'s/10.10.10.10/#{mesos_master_ip}/g' /home/vagrant/contrail-mesos-ansible/playbooks/inventory/mesos-inventory.ini
                sed -i $'s/20.20.20.20/#{slaves_ip_string}/g' /home/vagrant/contrail-mesos-ansible/playbooks/inventory/mesos-inventory.ini
                cd /home/vagrant/contrail-mesos-ansible/playbooks
                echo "mesos ansible starts executing" 
                time ansible-playbook -vvv -i inventory/mesos-inventory.ini all.yml
                echo "mesos ansible ends executing" 
EOF
        end # END mesos IF
           
        builder.vm.provision 'shell', :inline => <<EOF
            # Configuring link local
            ssh root@#{controller_ip} 'docker exec -i controller /opt/contrail/utils/provision_linklocal.py --api_server_ip #{controller_ip} --linklocal_service_name mesos --linklocal_service_ip 169.254.169.1 --linklocal_service_port 8882 --ipfabric_service_ip 127.0.0.1 --ipfabric_service_port 8882'
EOF

            #Setting route for 8.8.8.8 so that mesos will pick related ip
            
            (1..num_of_slaves).each do |cntr|
                slave_ip = "#{prefix_ip_addr}#{101+cntr}"
                    builder.vm.provision 'shell', :inline => <<EOF
                    echo "before running change ip script on - #{slave_ip}"
 
                    ssh root@#{slave_ip} 'sh /home/vagrant/change_ip.sh'
                 
EOF
            end
            
            slave_ip = "%s102" % [prefix_ip_addr]
             
            builder.vm.provision 'shell', :inline => <<EOF
                echo "run the sample task scheduling script"
                ssh root@#{slave_ip} 'python /home/vagrant/schedule-task.py'
                echo "END SUCCESS"
EOF

    end

end
