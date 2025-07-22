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

Scenario: Read a shopcart
    When I visit the "Home Page"
    Then I set the "Customer ID" to "23"
    And I press "Retrieve"
    Then I should see the message "Success"
    And I should see "23" in the "Customer ID" field
    And I should see "[]" in the "Item List" field
