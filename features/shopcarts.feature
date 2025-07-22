Feature: Shopcart Management UI
    As an Administrator
    I need a UI to interact with my shopcart microservice
    So that I can keep track of the shopcart entries in the database

  Background:
    Given the following customers
      | Customer ID | Item List |
      | 23          | []        |
      | 54          | [{"product_id": 12, "price": 220, "quantity": 2, "description": Item 12}] |
      | 81          | []        |
      | 79          | []        |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart REST API Service" in the title
    And I should not see "404 Not Found"

    Scenario: Clear Cart Action upon Shopcart
    When I visit the "Home Page"
    And I set the "Customer ID" to "54"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "54" in the "Customer ID" field
    And I should see "[{\"product_id\": 12, \"price\": 220, \"quantity\": 2, \"description\": \"Item 12\"}]" in the "Item List" field
    When I set the "Customer ID" to "54"
    And I press the "Action" button
    Then I should see the message "Success"
    And I should see "[]" in the "Item List" field
    When I set the "Customer ID" to "54"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "[]" in the "Item List" field
