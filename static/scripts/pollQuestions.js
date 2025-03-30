const pollQuestions = document.querySelectorAll("#pollQuestions>li")
const otherQuestions = document.querySelectorAll("#noPollQuestions>li")
const saveButton = document.querySelector("#saveButton")
const requestData = {
    toAdded: [], toOther: [],
}
let changesCounter = 0;

function changesCounterUpdate() {
    saveButton.style.display = changesCounter === 0 ? "none" : "block"
}

function formError(text) {
    const elem = toastTemplate.content.firstElementChild.cloneNode(true)
    elem.classList.add("alert-error")
    elem.querySelector("span").innerText = text
    toastsContainer.append(elem)
    setTimeout(() => elem.remove(), 3000)
}

function highlightCheckedCheckbox(input) {
    const classList = input.classList
    const borderSecondary = "border-secondary"
    const borderAccent = "border-accent"
    if (classList.contains(borderAccent)) {
        classList.remove(borderAccent)
        classList.add(borderSecondary)
    } else {
        classList.remove(borderSecondary)
        classList.add(borderAccent)
    }
}

changesCounterUpdate()
pollQuestions.forEach((elem) => {
    const id = elem.dataset.questionId
    const input = elem.querySelector("input")
    input.addEventListener("change", () => {
        if (input.checked) {
            requestData.toOther.splice(requestData.toOther.indexOf(id))
            changesCounter--
        } else {
            requestData.toOther.push(id)
            changesCounter++
        }
        changesCounterUpdate()
        highlightCheckedCheckbox(input)
    })
})

otherQuestions.forEach((elem) => {
    const id = elem.dataset.questionId
    const input = elem.querySelector("input")
    input.addEventListener("change", () => {
        if (input.checked) {
            requestData.toAdded.push(id)
            changesCounter++
        } else {
            requestData.toAdded.splice(requestData.toAdded.indexOf(id))
            changesCounter--
        }
        changesCounterUpdate()
        highlightCheckedCheckbox(input)
    })
})

saveButton.addEventListener("click", async (evt) => {
    if (changesCounter === 0) { // На всякий
        changesCounterUpdate()
        return
    }

    const pollId = evt.target.dataset.pollId
    const response = await fetch(`/api/poll-questions/${pollId}`, {
        method: "PATCH", headers: {"Content-Type": "application/json"}, body: JSON.stringify(requestData)
    })

    const body = await response.json()
    if (response.ok) {
        window.location.reload()
    } else {
        formError(`${response.status}: ${body.message}`)
    }
})
