#!/usr/bin/env ruby

sites = ['US-TX', 'US-NC', 'EU-AERO', 'AUS-MEL']
services = ['nova', 'glance', 'neutron', 'cinder', 'swift']
messages = {'nominal' => 1, 'reduced capabilities' => 0, 'failed' => -1}

1.times do
  sites.each do |site|
    services.each do |service|
      message = messages.keys[rand(3)]
      state = messages[message]

      cmd =  %Q{curl -u admin:testing -H "Content-Type: application/json" -X POST -d '{"site":"#{site}","service":"#{service}","message":"#{message}","state":#{state}}' localhost:5000/api/v1.0/status}
      puts cmd
      system cmd
    end
  end
end
