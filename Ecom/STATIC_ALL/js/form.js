(() =>{

    let front_end_error = document.querySelector(".front_end_error_validation")

if (! front_end_error.classList.contains("visually-hidden")){
    front_end_error.classList.add('visually-hidden')
}

forms = document.querySelectorAll(".forms")

Array.from(forms).forEach(form =>{

    form.addEventListener('submit' , ()=>{
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
            front_end_error.classList.remove('visually-hidden')
            front_end_error.innerText = "please enter the field"
        }

        

    })
})

})();
