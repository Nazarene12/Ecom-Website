(()=>{

    checkBox = document.getElementById("show_password")
    password  = document.querySelectorAll(".password")

    checkBox.addEventListener('change' , ()=>{

        if (checkBox.checked){
            password.forEach(element => {
                element.type = "text"
            });
            return
        }

        password.forEach(element => {
            element.type = "password"
        });
    })

})()