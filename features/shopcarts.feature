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

Scenario: Delete a shopcart
    When I visit the "Home Page"
    And I set the "Customer ID" to "54"
    And I press the "Delete" button
    Then I should see the message "Success"
    When I set the "Customer ID" to "54"
    And I press the "Retrieve" button
    Then I should see the message "404 Not Found: Shopcart for customer '22' was not found."
