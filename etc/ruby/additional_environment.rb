config.public_file_server.enabled = ENV['RAILS_SERVE_STATIC_FILES'].present?

config.lograge.enabled = true
config.lograge.ignore_custom = lambda do |event|
  event.payload[:controller] == "HealthCheck::HealthCheckController"
end

config.logger = ActiveSupport::Logger.new(STDOUT)

if ENV['FLUENTD_URL']
  uri = URI.parse ENV['FLUENTD_URL']
  config.logger = Fluent::Logger::LevelFluentLogger.new(nil,
                                                        host: uri.host,
                                                        port: uri.port,
                                                        use_nonblock: true,
                                                        wait_writeable: false
                                                      )
  config.logger.formatter = proc do |severity, datetime, progname, message|
    map = { level: severity }
    map[:message]   = message if message
    map[:progname]  = progname if progname
    map[:service]   = uri.path[1..-1] if uri.path[1..-1]
    if ENV['OTEL_EXPORTER_OTLP_ENDPOINT'].present?
      map[:span_id]   = OpenTelemetry::Trace.current_span.context.hex_span_id
      map[:trace_id]  = OpenTelemetry::Trace.current_span.context.hex_trace_id
    end
    map
  end
  stdout_logger = ActiveSupport::Logger.new(STDOUT)
  config.logger.extend(ActiveSupport::Logger.broadcast(stdout_logger))
end
