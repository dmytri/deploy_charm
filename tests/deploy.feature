Feature: Charmebracelet Soft Serve Git Host

  @dev
  Scenario: dev
     When target is dev

  @ci
  Scenario: ci
     When target is ci

  @prod
  Scenario: prod
     When target is prod

  @dev @ci @prod
  Scenario: Expected host OS
    Given apk packages must be latest
     When cosign is required
     Then OS is Alpine Linux 3.21 

  @dev @ci @prod
  Scenario: Require Soft Serve
    Given Soft Serve v0.8.1
     When I have a Soft Serve package
      And Soft Serve checksums file is required
      And file must be verified with cosign
      And the checksum matches
     When Soft Serve is required
     Then Soft Serve is available
