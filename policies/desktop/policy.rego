package desktop

default allow = false

allow {
  count(deny) == 0
}

deny[msg] {
  required := input.required_patches[_]
  not required in input.applied_patches
  msg := sprintf("Required patch %v missing from desktop image", [required])
}

deny[msg] {
  software := input.software_manifest[_]
  min_ver := input.approved_software[software.name].min_version
  software.version < min_ver
  msg := sprintf("Software %q version %v is below minimum required %v", [software.name, software.version, min_ver])
}

deny[msg] {
  not input.truist_root_ca_injected
  msg := "Corporate root CA certificate must be injected into desktop image"
}

deny[msg] {
  not input.endpoint_security_installed
  msg := "Endpoint security agent must be installed in desktop image"
}
