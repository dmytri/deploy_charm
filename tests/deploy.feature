Feature: Charmebracelet Soft Serv Git Host

  @dev
  Scenario: Set deployment target to dev
    Given dev environment

  @ci
  Scenario: Set deployment target to ci
    Given ci environment

  @prod
  Scenario: Set deployment target to prod
    Given prod environment

  @dev @ci @prod
  Scenario: Verify expected host OS
    Given a target host
     Then OS is Alpine Linux 3.21 

  @dev @ci @prod
  Scenario: Require Soft Serve
    Given a target host
    When host should run Soft Serve
    Then Soft Serve should be available
