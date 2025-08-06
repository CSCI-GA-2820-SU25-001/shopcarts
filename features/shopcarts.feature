Feature: Shopcart Management UI
    As an Administrator
    I need a UI to interact with my shopcart microservice
    So that I can keep track of the shopcart entries in the database

  Background:
    Given the following shopcarts
      | Customer ID | Item List |
      | 23          | []        |
      | 79          | [{"product_id": 12, "price": 220, "quantity": 2, "description": "Item 12"}] |
      | 54          | []        |
      | 81          | [{"product_id": 1, "description": "Item 1", "price": 200, "quantity": 2}, {"product_id": 2, "description": "Item 2", "price": 240, "quantity": 5}] |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Shopcart REST API Service" in the title
    And I should not see "404 Not Found"

    Scenario: Clear Cart Action upon Shopcart
    When I visit the "Home Page"
    And I set the "Customer ID" to "79"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "79" in the "Customer ID" field
    And I should see "Item 12" in the "Item List" field
    When I set the "Customer ID" to "79"
    And I press the "Action" button
    Then I should see the message "Success"
    When I set the "Customer ID" to "54"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "[]" in the "Item List" field

Scenario: Query items within a shopcart
    When I visit the "Home Page"
    And I set the "Customer ID" to "81"
    And I set the "Max Price" to "220"
    And I press the "Query" button
    Then I should see the message "Success"
    And I should see "81" in the "Customer ID" field
    And I should see "Item 1" in the "Item List" field

Scenario: Read a shopcart
    When I visit the "Home Page"
    And I set the "Customer ID" to "23"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "23" in the "Customer ID" field
    And I should see "[]" in the "Item List" field

Scenario: Create a Shopcart
    When I visit the "Home Page"
    And I set the "Customer ID" to "99"
    And I set the "Item List" to "[]"
    And I press the "Create" button
    Then I should see the message "Success"
    And I should see "99" in the "Customer ID" field
    And I should see "[]" in the "Item List" field

Scenario: Update a shopcart
    When I visit the "Home Page"
    And I set the "Customer ID" to "23"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "23" in the "Customer ID" field
    And I should see "[]" in the "Item List" field
    When I change "Item List" to "[{^product_id^: 1, ^description^: ^Item^, ^price^: 20, ^quantity^: 5}]"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Customer ID" field
    And I press the "Clear" button
    And I paste the "Customer ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "23" in the "Customer ID" field
    And I should see "20" in the "Item List" field

Scenario: List all items
    When I visit the "Home Page"
    And I set the "Customer ID" to "81"
    And I press the "List" button
    Then I should see the message "Success"
    And I should see "Item 1" in the "Item List" field
    And I should see "Item 2" in the "Item List" field
    And I should see "200" in the "Item List" field
    And I should see "240" in the "Item List" field

Scenario: List all shopcarts
    When I visit the "Home Page"
    And I press the "All" button
    Then I should see the message "Success"
    And I should see "23" in the results
    And I should see "79" in the results
    And I should see "54" in the results
    And I should see "81" in the results

Scenario: Delete a shopcart
    When I visit the "Home Page"
    And I set the "Customer ID" to "79"
    And I press the "Delete" button
    Then I should see the message "Success"
    When I set the "Customer ID" to "79"
    And I press the "Retrieve" button
    Then I should see the message "Shopcart for customer '79' was not found. You have requested this URI [/api/shopcarts/79] but did you mean /api/shopcarts//items/ or /api/shopcarts or /api/shopcarts//items ?"
