function setPurchaseRate(e){
    let product = $(e.target).find(":selected")
    let rate = product.attr("purchase_rate")
    let parent = $(e.target).closest('.forms')
    parent.find("input[id$='-rate']").val(rate)
}

function setPurchaseRateDiff(e){
    let parent = $(e.target).closest('.forms')
    let product = parent.find("select[id$='-product'] option:selected")
    let rate = product.attr("purchase_rate")
    let new_rate = parseFloat($(e.target).val())
    let diff = (new_rate-rate).toFixed(2)
    let status = ""
    if(diff > 0){
        status = "<i class='bi bi-caret-up-fill text-warning'></i> " + Math.abs(diff)
    } else if (diff < 0){
        status = "<i class='bi bi-caret-down-fill text-warning'></i> " + Math.abs(diff)
    }
    parent.find(".rate-diff").html(status)
    // console.log(rate,new_rate)
}

function getSellingRate(e){
    target = e.target
    let parent = $(target).closest('.forms')
    let product = parent.find("select[id$='-product'] option:selected")
    console.log("parent:", parent)
    let rate = product.attr("selling_rate")
    parent.find("input[id$='-rate']").val(rate)
    // console.log("Executed Selling Rate: ", rate)
}

function getAmount(e){
    let form = $(e.target).closest('.forms')
    let qnt = form.find("input[id$='-quantity']").val()
    let rate = form.find("input[id$='-rate']").val()
    form.find("input[id$='-amount']").val(Math.round(qnt*rate))
    // console.log("Executed Amount: ", qnt*rate)
}

function getRate(e){
    let form = $(e.target).closest('.forms')
    let qnt = form.find("input[id$='-quantity']").val()
    let amount = form.find("input[id$='-amount']").val()
    form.find("input[id$='-rate']").val(amount/qnt)
    // console.log("Executed Rate: ", amount/qnt)
}

$("input[id$='-quantity'], input[id$='-rate']").on({
    change: getAmount, keyup: getAmount
});
$("input[id$='-rate']").on({
    change: setPurchaseRateDiff, keyup: setPurchaseRateDiff
});
//$("input[id$='-amount']").on('keyup', getRate)
$("input[id$='-amount']").on({keyup: getRate, change: getRate});