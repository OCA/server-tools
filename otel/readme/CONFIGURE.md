The module aims to accomodate different use-cases, and as such, there are quite a
few configuration options. Generally, only a few basic options are needed for most
deployments.

# Minimum Config

For most basic use-cases, the following config will be sufficient.

*Note*: This assumes a collector is running locally, and accepts `http/protobuf`
requests.

```ini
# odoo-server.conf
[options]
# ...

[otel]
# enable the module
enable = True

# these vars will be tacked onto *all* traces; you should set `service.name` at least
resource_attributes = service.name=odoo,odoo.version=18.0,deployment.environment=dev

# your OTLP endpoint
exporter_otlp_endpoint = http://localhost:4318/v1/traces

# you may also need to set this, if your collector wants gRPC
# exporter_otlp_protocol = grpc
```

Configuration options can be passed either by environment variables, or set in the
Odoo conf file. Environment variables take precedence. Option names are consistent
between these two options. To convert from env-var toconf, simply strip the leading
`OTEL_`, and make lowercase. For example:
 - `OTEL_ENABLE` -> `enable`
 - `OTEL_EXPORTER_OTLP_ENDPOINT` -> `exporter_otlp_endpoint`
 - etc

# Config Reference

## Core Options

 * `OTEL_ENABLE` will enable (or disable) the module. Possible values: `true` or
        `false`
 * `OTEL_RESOURCE_ATTRIBUTES` should be a set of `key1=value,key2=value` pairs. You
        should set `service.name` at least, and consider setting
        `deployment.environment`
 * `OTEL_RESOURCE_ATTRIBUTES_SERVICE_NAME` will override the `service.name`
        attribute in the Resource Attributes
 * `OTEL_RESOURCE_ATTRIBUTES_SERVICE_VERSION` as above, but for the `service.version`
        attribute; useful if you want to set the version dynamically (e.g., to a
        docker build hash, or git revision)
 * `OTEL_RESOURCE_ATTRIBUTES_DEPLOYMENT_ENVIRONMENT` as above, but for the
        `deployment.environment` attribute (again, useful to be configureable
        dynamically)

## Collector Options

 * `OTEL_EXPORTER_OTLP_PROTOCOL` is the protocol the OTel SDK will use to
        communicate with your collector. Possible values: `grpc` or `http` (which
        is an alias for `http/protobuf`)
 * `OTEL_EXPORTER_OTLP_ENDPOINT` is the collector endpoint. Examples are:
    * `http://localhost:4317` (gRPC)
    * `http://localhost:4318` (http/protobuf)
 * `OTEL_EXPORTER_OTLP_HEADERS` accepts a set of `header=value,header2=value`
        pairs, which will be sent along with requests to the collector. This is
        useful for passing auth headers. Examples are:
    * `exporter_otlp_headers = Authorization=Bearer 12345`

## 