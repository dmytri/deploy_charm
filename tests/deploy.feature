Feature: Charmebracelet Soft Serve Git Host

  @dev
  Scenario: dev
     When target dev

  @ci
  Scenario: ci
     When target ci

  @prod
  Scenario: prod
     When target prod

  @dev @ci @prod
  Scenario: Soft Serve deployment needed
    Given Soft Serve v0.8.2
     Then Soft Serve deployed

  @dev @ci @prod
  Scenario: Expected host OS
    Given system packages up to date
     When cosign available
     Then OS Alpine Linux 3.21 

  @dev @ci @prod
  Scenario: Require Soft Serve
     When Soft Serve package downloaded
      And Soft Serve checksums file downloaded 
      And checksums file signature verified
      And package integrity verified
     When Soft Serve installed and configured
     Then Soft Serve running and accessible
