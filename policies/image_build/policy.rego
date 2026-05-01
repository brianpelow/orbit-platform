package image_build

import future.keywords.in

default allow = false

approved_base_images := {
  "golden-ubuntu-22.04",
  "golden-ubuntu-20.04",
  "golden-rhel-9",
  "golden-rhel-8",
  "golden-debian-12",
  "golden-alpine-3.19"
}

allow {
  count(deny) == 0
}

deny[msg] {
  not input.service_id
  msg := "Service ID is required — register service before building"
}

deny[msg] {
  base := extract_base_image(input.dockerfile)
  not base in approved_base_images
  msg := sprintf("Base image %q is not in the approved list", [base])
}

deny[msg] {
  "latest" in input.dockerfile
  msg := "Image tag :latest is not allowed — use a pinned version tag"
}

extract_base_image(dockerfile) = image {
  lines := split(dockerfile, "\n")
  from_lines := [l | l := lines[_]; startswith(l, "FROM ")]
  count(from_lines) > 0
  parts := split(from_lines[0], " ")
  image_full := parts[1]
  image := split(image_full, ":")[0]
} else = "unknown"
