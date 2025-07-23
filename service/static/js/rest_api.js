$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#customer_id").val(res.customer_id);
        $("#item_list").val(JSON.stringify(res.item_list));
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_id").val("");
        $("#item_list").val("");
        $("#max_price").val("");
        let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">Product ID</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-6">Description</th>'
            table += '</tr></thead><tbody>'
            table += '</tbody></table>';
        $("#search_results").empty();
        $("#search_results").append(table);
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#create-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let item_list = $("#item_list").val();

        try {
            JSON.parse(item_list);
            let data = {
            "customer_id": parseInt(customer_id),
            "item_list": JSON.parse(item_list)
            };

            $("#flash_message").empty();
            
            let ajax = $.ajax({
                type: "POST",
                url: "/api/shopcarts",
                contentType: "application/json",
                data: JSON.stringify(data),
            });

            ajax.done(function(res){
                update_form_data(res)
                flash_message("Success")
            });

            ajax.fail(function(res){
                flash_message(res.responseJSON.message)
            });

        } catch (e) {
            alert('Invalid JSON: ' + e.message);
        }
        
    });


    // ****************************************
    // Update a Shopcart
    // ****************************************

    $("#update-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let item_list = $("#item_list").val();

        try {
            JSON.parse(item_list);
            $("#flash_message").empty();

            let ajax = $.ajax({
                    type: "PUT",
                    url: `/api/shopcarts/${customer_id}`,
                    contentType: "application/json",
                    data: item_list
                })

            ajax.done(function(res){
                update_form_data(res)
                flash_message("Success")
            });

            ajax.fail(function(res){
                flash_message(res.responseJSON.message)
            });

        } catch (e) {
            alert('Invalid JSON: ' + e.message);
        }
    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${customer_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-btn").click(function () {

        let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/shopcarts/${customer_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Prettify JSON input
    // ****************************************

    $("#format-btn").click(function () {
        let ugly = $("#item_list").val();
        try {
            let obj = JSON.parse(ugly);
            let pretty = JSON.stringify(obj, null, 4);
            $("#item_list").val(pretty);
        } catch (e) {
            alert('Invalid JSON: ' + e.message);
        }
    });

    // ****************************************
    // Action on Shopcart (Clear Cart)
    // ****************************************

    $("#action-btn").click(function () {
       let customer_id = $("#customer_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/shopcarts/${customer_id}/clear`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            $("#customer_id").val(customer_id);
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });
  

    // ****************************************
    // Query a Shopcart by Maximum item price
    // ****************************************

    $("#query-btn").click(function () {
        let customer_id = $("#customer_id").val();
        let max_price = $("#max_price").val();

        let queryString = ""

        if (max_price) {
            queryString += 'max-price=' + max_price
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${customer_id}/items?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res) {
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">Product ID</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-6">Description</th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for(let i = 0; i < res.length; i++) {
                let cart = res[i];
                table +=  `<tr id="row_${i}"><td>${cart.product_id}</td><td>${cart.price}</td><td>${cart.quantity}</td><td>${cart.description}</td></tr>`;
                if (i == 0) {
                    firstItem = cart;
                }
            }
            table += '</tbody></table>'
            
            $("#search_results").append(table);
            
            // copy the result to the form
            if (firstItem != "") {
                $("#item_list").val(JSON.stringify(res))
            }
            flash_message("Success");
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // List all Shopcarts
    // ****************************************

    $("#list-btn").click(function () {
        let customer_id = $("#customer_id").val();
        
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${customer_id}/items`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">Product ID</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-6">Description</th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for(let i = 0; i < res.length; i++) {
                let cart = res[i];
                table +=  `<tr id="row_${i}"><td>${cart.product_id}</td><td>${cart.price}</td><td>${cart.quantity}</td><td>${cart.description}</td></tr>`;
                if (i == 0) {
                    firstItem = cart;
                }
            }
            table += '</tbody></table>'
            $("#search_results").append(table);

            // copy the result to the form
            if (firstItem != "") {
                $("#item_list").val(JSON.stringify(res))
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });
});