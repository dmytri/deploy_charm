Feature: Charmebracelet Soft Serv Git Host

  @ci
  Scenario: Set deployment target to ci
    Given ci environment

  @dev
  Scenario: Set deployment target to dev
    Given dev environment

  @prod
  Scenario: Set deployment target to prod
    Given prod environment

  @dev @ci @prod
  Scenario: Install Soft Serve
    Given a target host
     And host is available
     When Soft Serve is installed
     Then OS is Alpine Linux 3.21 
