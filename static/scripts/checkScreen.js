const mainContent = document.querySelector("#mainContent")
const widthError = document.querySelector("#widthError")

function checkScreenWidth () {
    if (window.innerWidth > 700) {
        mainContent.classList.remove("hidden")
        widthError.classList.add("hidden")
    } else {
        mainContent.classList.add("hidden")
        widthError.classList.remove("hidden")
    }
}

window.addEventListener("load", checkScreenWidth)
window.addEventListener("resize", checkScreenWidth)
