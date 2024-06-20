if ENV['OTEL_EXPORTER_OTLP_ENDPOINT'].present?
  require 'opentelemetry/sdk'
  require 'opentelemetry/exporter/otlp'
  require 'opentelemetry/instrumentation/all'
  OpenTelemetry::SDK.configure do |c|
      c.use_all() # enables all instrumentation!
      c.logger = Rails.logger
  end
end
