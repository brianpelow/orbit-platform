package image_scan

default allow = false

allow {
  count(deny) == 0
}

deny[msg] {
  input.vulnerability_scan.critical_cves > 0
  msg := sprintf("Build blocked: %d critical CVE(s) detected — remediate before deploying", [input.vulnerability_scan.critical_cves])
}

deny[msg] {
  input.vulnerability_scan.high_cves > 5
  msg := sprintf("Build blocked: %d high CVEs detected (maximum allowed: 5)", [input.vulnerability_scan.high_cves])
}

deny[msg] {
  input.secret_scan.secrets_found == true
  msg := "Build blocked: secrets detected in source code — remove secrets before building"
}
