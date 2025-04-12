import {formError} from "./toasts.js";

let jwtToken
const cookieArr = document.cookie.split("; ")
cookieArr.forEach((elem) => {
    const parsed = elem.split("=")
    if (parsed[0] === "jwtToken") {
        jwtToken = parsed[1]
    }
})

let requestData = {
    toAdded: [], toOther: [],
}
let changesCounter = 0;

const pollQuestions = document.querySelectorAll("#pollQuestions>li")
const otherQuestions = document.querySelectorAll("#noPollQuestions>li")
const saveButton = document.querySelector("#saveButton")


function changesCounterUpdate() {
    saveButton.style.display = changesCounter === 0 ? "none" : "block"
}

function highlightCheckedCheckbox(input, type) {
    const classList = input.classList

    const checkboxPrimary = "checkbox-error"
    const checkboxSecondary = "checkbox-secondary"
    const checkboxAccent = "checkbox-accent"

    if (type === "other") {
        classList.toggle(checkboxSecondary)
    } else {
        classList.toggle(checkboxPrimary)
    }

    classList.toggle(checkboxAccent)
}

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
        highlightCheckedCheckbox(input, "poll")
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
        highlightCheckedCheckbox(input, "other")
    })
})

saveButton.addEventListener("click", async (evt) => {
    if (changesCounter === 0) {
        changesCounterUpdate()
        return
    }

    const pollId = evt.target.dataset.pollId
    const response = await fetch(`/api/poll-questions/${pollId}`, {
        method: "PATCH", headers: {
            "Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`
        }, body: JSON.stringify(requestData)
    })

    const body = await response.json()
    if (response.ok) {
        window.location.reload()
    } else {
        formError(`${response.status}: ${body.message}`)
    }
})

changesCounterUpdate()
