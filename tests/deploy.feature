Feature: Charmebracelet Soft Serv Git Host

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
    Then OS is Alpine Linux 3.21 

  @dev @ci @prod
  Scenario: Require Soft Serve
    When host must run Soft Serve
    Then Soft Serve is available
