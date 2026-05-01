package deployment

default allow = false

production_environments := {"production", "prod"}

allow {
  count(deny) == 0
}

deny[msg] {
  input.environment in production_environments
  not input.image_url
  msg := "Production deployments require a registered image URL"
}

deny[msg] {
  input.environment in production_environments
  not input.service_id
  msg := "Production deployments require a registered service ID"
}

deny[msg] {
  input.environment in production_environments
  contains(input.image_url, ":latest")
  msg := "Production deployments cannot use :latest tag — use immutable digest or version tag"
}
