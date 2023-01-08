function addForm(e){
    // e.preventDefault()
    const forms = $(".forms")
    const container = $("#form-container")
    const totalForms = $("#id_form-TOTAL_FORMS")
    const formNum = forms.length

    const emptyForm = $("#empty-form").clone(true)
    emptyForm.removeClass("d-none")
    emptyForm.addClass("row forms text-center")
    emptyForm.removeAttr("id")
    emptyForm.attr('form-num',formNum)
    const regex = RegExp('__prefix__','g')
    emptyForm.html(emptyForm.html().replace(regex,formNum))
    container.append(emptyForm)
    
    totalForms.attr('value',formNum+1)
    $('input[id$="-DELETE"]').click(markDelete)
}

function markDelete(e){
    let form = $(e.target).closest('.forms')
    if($(e.target).is(':checked')){
        form.find('select, input').addClass('text-danger')
    } else {
        form.find('input, select').removeClass('text-danger')
    }
}

$('input[id$="-DELETE"]').click(markDelete)