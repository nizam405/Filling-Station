$(document).ready(function(){
    $("#get-qnt").click(function(){
        let rate = $("#id_rate").val();
        let amount = $("#id_amount").val();
        if(amount > 0 && rate > 0){
            $("#id_quantity").val(amount/rate);
        }
    });
    $("#get-rate").click(function(){
        let qnt = $("#id_quantity").val();
        let amount = $("#id_amount").val();
        if(qnt > 0 && amount > 0){
            $("#id_rate").val(amount/qnt);
        }
    });
    $("#get-amount").click(function(){
        let qnt = $("#id_quantity").val();
        let rate = $("#id_rate").val();
        if(qnt > 0 && rate > 0){
            $("#id_amount").val(qnt*rate);
        }
    });
});