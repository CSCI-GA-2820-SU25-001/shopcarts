Feature: Shopcart Management UI
    As an Administrator
    I need a UI to interact with my shopcart microservice
    So that I can keep track of the shopcart entries in the database

  Background:
    Given the following customers
      | Customer ID | Item List |
      | 23          | []        |
      | 54          | []        |
      | 81          | []        |
      | 79          | []        |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart Administration" in the title
    And I should not see "404 Not Found"

Scenario: List all shopcarts
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "23" in the results
    And I should see "54" in the results
    And I should see "79" in the results
    And I should see "81" in the results
    And I should not see "124" in the results