
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
  Scenario: Soft Serve Deployment is needed
    Given Soft Serve v0.8.2
     Then deploy Soft Serve

  @dev @ci @prod
  Scenario: Expected host OS
    Given the system packages are up to date
    When cosign is available for verification
    Then OS is Alpine Linux 3.21 

  @dev @ci @prod
  Scenario: Require Soft Serve
    When the Soft Serve package is downloaded
    And Soft Serve checksums file is required
    And the checksums file signature is verified
    And the package integrity is verified
    When Soft Serve is installed and configured
    Then Soft Serve is running and accessible
