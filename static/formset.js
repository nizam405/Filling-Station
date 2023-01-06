function addForm(e){
    e.preventDefault()
    const forms = $(".forms")
    const container = $("#form-container")
    const totalForms = $("#id_form-TOTAL_FORMS")
    const formNum = forms.length

    const emptyForm = $("#empty-form").clone(true)
    emptyForm.removeClass("d-none")
    emptyForm.addClass("row forms text-center")
    emptyForm.removeAttr("id")
    emptyForm.attr('id',`form-${formNum}`)
    const regex = RegExp('__prefix__','g')
    emptyForm.html(emptyForm.html().replace(regex,formNum))
    container.append(emptyForm)
    
    totalForms.attr('value',formNum+1)

    $(".delete-form").click(deleteForm)
}

function deleteForm(e){
    $(this).closest(".forms").remove()
    $("#id_form-TOTAL_FORMS").attr('value',$(".forms").length)
}