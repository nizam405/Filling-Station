function getPurchaseRate(e){
    target = e.target
    let product = $(target).find(":selected")
    let parent = $(target).closest('.forms')
    let rate = product.attr("purchase_rate")
    parent.find("input[id$='-rate']").val(rate)
    console.log("Executed Purchase Rate: ", rate)
}

function getSellingRate(e){
    target = e.target
    let product = $(target).find(":selected")
    let parent = $(target).closest('.forms')
    let rate = product.attr("selling_rate")
    parent.find("input[id$='-rate']").val(rate)
    console.log("Executed Selling Rate: ", rate)
}

function getAmount(e){
    let form = $(e.target).closest('.forms')
    let qnt = form.find("input[id$='-quantity']").val()
    let rate = form.find("input[id$='-rate']").val()
    form.find("input[id$='-amount']").val(Math.round(qnt*rate))
    console.log("Executed Amount: ", qnt*rate)
}

function getRate(e){
    let form = $(e.target).closest('.forms')
    let qnt = form.find("input[id$='-quantity']").val()
    let amount = form.find("input[id$='-amount']").val()
    form.find("input[id$='-rate']").val(amount/qnt)
    console.log("Executed Rate: ", amount/qnt)
}

$("input[id$='-quantity'], input[id$='-rate']").on('keyup', getAmount)
$("#add-form").click(function(){
    addForm()
    $("select[id$='-product']").on('change', getSellingRate)
    $("input[id$='-quantity'], input[id$='-rate']").on('keyup', function(e){
        getAmount(e)
    })
})

$("input[id$='-amount']").on('keyup', getRate)