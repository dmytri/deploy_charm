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
  Scenario: Verify expected host OS
    Given apk packages must be latest
    Then OS is Alpine Linux 3.21 

  @dev @ci @prod
  Scenario: Verify Soft Serve 0.8.1 Checksums
    When cosign is required
     And Soft Serve checksums file is required
     # And Checksum file must be verified with cosign

  @dev @ci @prod
  Scenario: Require Soft Serve
    # Given I have a Soft Serve Package
    #   And the checksum matches
    When Soft Serve is required
    Then Soft Serve is available
