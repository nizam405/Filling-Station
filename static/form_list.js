$('#add-form').click(function(){
    let container = $('#form-container')
    if (container.hasClass('hidden')){
        container.toggle('fast')
    }
})