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


Scenario: Query items within a shopcart
    When I visit the "Home Page"
    And I set the "ID" to "23"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "23" in the "ID" field
    And I should see "[]" in the "Item_List" field
    When I change "Item_List" to "[{\"product_id\": 1, \"description\": \"Item\", \"price\": 20, \"quantity\": 5}, {\"product_id\": 2, \"description\": \"Item 2\", \"price\": 40, \"quantity\": 3}]"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    And I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "23" in the "ID" field
    And I should see "[{\"product_id\": 1, \"description\": \"Item\", \"price\": 20, \"quantity\": 5}, {\"product_id\": 2, \"description\": \"Item 2\", \"price\": 40, \"quantity\": 3}]" in the "Item_List" field
    When I set the "Threshold" to "30"
    And I press the "Query" button
    Then I should see the message "Success"
    And I should see "[{\"product_id\": 1, \"description\": \"Item\", \"price\": 20, \"quantity\": 5}]" in the results