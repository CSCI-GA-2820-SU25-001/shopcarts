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

Scenario: Update a shopcart
    When I visit the "Home Page"
    And I set the "Customer ID" to "23"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "23" in the "Customer ID" field
    And I should see "[]" in the "Item List" field
    When I change "Item List" to "[{\"product_id\": 1, \"description\": \"Item\", \"price\": 20, \"quantity\": 5}]"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Customer ID" field
    And I press the "Clear" button
    And I paste the "Customer ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "23" in the "Customer ID" field
    And I should see "[{\"product_id\": 1, \"description\": \"Item\", \"price\": 20, \"quantity\": 5}]" in the "Item List" field
