const toastTemplate = document.querySelector("#toastTemplate")
const toastsContainer = document.querySelector("#toastsContainer")

function formToast(text) {
    const elem = toastTemplate.content.firstElementChild.cloneNode(true)
    elem.querySelector("span").innerText = text
    toastsContainer.append(elem)
    setTimeout(() => elem.remove(), 3000)
    return elem
}

export function formError(text) {
    const elem = formToast(text)
    elem.classList.add("alert-error")
}

export function formMessage(text) {
    const elem = formToast(text)
    elem.classList.add("alert-success")
}
