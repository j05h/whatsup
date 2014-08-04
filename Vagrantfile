# encoding: UTF-8

map = {
  'box' => 'hashicorp/precise64',
  'memory' => '2048',
  'address' => '192.168.40.11'
}

Vagrant.configure('2') do |config|
  config.vm.box = map['box']
  config.vm.provision 'ansible' do |ansible|
    ansible.playbook = 'vagrant/site.yml'
    ansible.limit = 'all'
    ansible.sudo = true
    ansible.host_key_checking = false
    # ansible.verbose = "vvv"
    ansible.extra_vars = {
      cassandra_listen_address: map['address'],
      cassandra_rpc_address: map['address']
    }
  end

  config.vm.define 'whatsup-cassandra' do |c|
    c.vm.host_name = 'whatsup-cassandra'
    c.vm.network 'private_network', ip: map['address'] # eth1
  end

  config.vm.provider 'virtualbox' do |v|
    v.customize ['modifyvm', :id, '--memory', map['memory']]
  end
end
