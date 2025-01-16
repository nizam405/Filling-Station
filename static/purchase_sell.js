$(document).ready(function() {
    // Select the fields and elements you want to work with
    const productField = $("select[name='product']");
    const quantityField = $("input[name='quantity']");
    const rateField = $("select[id$='_rate']");
    const priceField = $("#price_display");
    // const priceField = $("input[name='price']");
    console.log(productField, quantityField, rateField, priceField)
    
    // Clear quantity
    if(quantityField.val()==0){
        quantityField.val("");
    }

    // Function to calculate and update the display
    function updatePrice() {
        const selectedRate = parseFloat(rateField.find("option:selected").attr('rate')) || 0;
        const quantity = parseFloat(quantityField.val()) || 0;
        const amount = selectedRate * quantity;
        // const amount = parseInt(Math.round(selectedRate * quantity));
        // console.log(selectedRate,quantity,amount)

        // Update displayed values
        priceField.text(amount.toFixed(2));
        // priceField.val(amount);
    }

    // Function to set available rates for selected product
    function setRate() {
        const product = productField.find(":selected");
        const rateDropdown = $("select[id$='_rate']");

        const selected = rateDropdown.find("option:selected").val()
        rateDropdown.empty();

        // Retrieve the available purchase rates from the selected product
        let rates = [];
        if(rateField.attr('name') == 'purchase_rate'){
            rates = JSON.parse(product.attr("purchase_rates") || "[]");
        } else if (rateField.attr('name') == 'selling_rate'){
            rates = JSON.parse(product.attr("selling_rates") || "[]");
        }

        // Populate the rate dropdown with options
        rates.forEach(rate => {
            const isSelected = rate.value==selected;
            const option = new Option(rate.amount, rate.value, isSelected, isSelected);
            option.setAttribute('rate', rate.amount)
            rateDropdown.append(option);
        });

        // Update amount based on the new purchase rate
        updatePrice();
        // Set focus to the quantity field
        quantityField.focus();
    }

    // Initialize amount on page load if there's a pre-filled quantity and rate
    setRate();
    updatePrice();

    // Event listeners for changes in product, rate, or quantity
    productField.on('change', setRate);
    quantityField.on("input", updatePrice);
    rateField.on("change", updatePrice);
});