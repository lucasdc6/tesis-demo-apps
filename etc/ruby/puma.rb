#!/usr/bin/env puma

application_path = '/usr/src/redmine'
directory application_path
environment 'production'
pidfile "tmp/pids/puma.pid"
state_path "tmp/pids/puma.state"
bind "tcp://0.0.0.0:3000"
