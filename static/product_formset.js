$(document).ready(function() {
    // Select the fields and elements you want to work with
    const $productField = $("select[name='product']");
    const $quantityField = $("input[name='quantity']");
    const $purchaseRateField = $("select[name='purchase_rate']");
    const $amountDisplay = $("#amount");

    // Function to calculate and update the display
    function updateAmount() {
        let selectedRate = parseFloat($purchaseRateField.find("option:selected").attr('rate')) || 0;
        const quantity = parseFloat($quantityField.val()) || 0;
        const amount = selectedRate * quantity;

        // Update displayed values
        $amountDisplay.text(amount.toFixed(2));
    }

    // Function to set available purchase rates for selected product
    function setPurchaseRate() {
        const product = $productField.find(":selected");
        const purchaseRateDropdown = $("select[id$='purchase_rate']");
        const selected = purchaseRateDropdown.find("option:selected").val()
        purchaseRateDropdown.empty();

        // Retrieve the available purchase rates from the selected product
        const purchaseRates = JSON.parse(product.attr("purchase_rates") || "[]");

        // Populate the purchase rate dropdown with options
        purchaseRates.forEach(rate => {
            const isSelected = rate.value==selected;
            const option = new Option(rate.amount, rate.value, isSelected, isSelected);
            option.setAttribute('rate', rate.amount)
            purchaseRateDropdown.append(option);
        });

        // Update amount based on the new purchase rate
        updateAmount();
    }

    // Initialize amount on page load if there's a pre-filled quantity and rate
    setPurchaseRate();
    updateAmount();

    // Event listeners for changes in product, rate, or quantity
    $productField.on('change', setPurchaseRate);
    $quantityField.on("input", updateAmount);
    $purchaseRateField.on("change", updateAmount);
});


// function setPurchaseRateDiff(e){
//     let parent = $(e.target).closest('.forms')
//     let product = parent.find("select[id$='-product'] option:selected")
//     let rate = product.attr("purchase_rate")
//     let new_rate = parseFloat($(e.target).val())
//     let diff = (new_rate-rate).toFixed(2)
//     let status = ""
//     if(diff > 0){
//         status = "<i class='bi bi-caret-up-fill text-warning'></i> " + Math.abs(diff)
//     } else if (diff < 0){
//         status = "<i class='bi bi-caret-down-fill text-warning'></i> " + Math.abs(diff)
//     }
//     parent.find(".rate-diff").html(status)
//     // console.log(rate,new_rate)
// }

function getSellingRate(e){
    target = e.target
    let parent = $(target).closest('.forms')
    let product = parent.find("select[id$='-product'] option:selected")
    console.log("parent:", parent)
    let rate = product.attr("selling_rate")
    parent.find("input[id$='-rate']").val(rate)
}

// function getAmount(e){
//     let form = $(e.target).closest('.forms')
//     let qnt = form.find("input[id$='-quantity']").val()
//     let rate = form.find("input[id$='-rate']").val()
//     form.find("input[id$='-amount']").val(Math.round(qnt*rate))
//     // console.log("Executed Amount: ", qnt*rate)
// }

// function getRate(e){
//     let form = $(e.target).closest('.forms')
//     let qnt = form.find("input[id$='-quantity']").val()
//     let amount = form.find("input[id$='-amount']").val()
//     form.find("input[id$='-rate']").val(amount/qnt)
//     // console.log("Executed Rate: ", amount/qnt)
// }


// $("input[id$='-rate']").on({
//     change: setPurchaseRateDiff, keyup: setPurchaseRateDiff
// });
//$("input[id$='-amount']").on('keyup', getRate)
// $("input[id$='-amount']").on({keyup: getRate, change: getRate});