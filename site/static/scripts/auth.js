const regForm = document.querySelector("#register");
const loginForm = document.querySelector("#login")

regForm.hidden = true;
document.querySelector("#switcher").addEventListener("click", (evt) => {
    if (regForm.hidden) {
        loginForm.reset();
        loginForm.hidden = true;
        regForm.hidden = false;
    } else {
        regForm.reset();
        regForm.hidden = true;
        loginForm.hidden = false;
    }
});