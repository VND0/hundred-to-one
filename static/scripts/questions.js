import {formError, getJwt} from "./tools.js";

const questionsList = document.querySelectorAll("#questionsList>li")

const addLink = document.querySelector("#addLink")
const addDialog = document.querySelector("#addDialog")
const addInput = document.querySelector("#addInput")
const addConfirm = document.querySelector("#addConfirm")

const editDialog = document.querySelector("#editDialog")
const editInput = document.querySelector("#editInput")
const editConfirm = document.querySelector("#editConfirm")

const deleteDialog = document.querySelector("#deleteDialog")
const deleteConfirm = document.querySelector("#deleteConfirm")

const searchInput = document.querySelector("#searchInput")

let jwtToken = getJwt()

async function handleApiError(response) {
    if (!response.ok) {
        if (response.status === 409) {
            formError("Вопросы должны быть уникальны")
        } else if (response.status === 404) {
            formError("Объект не найден")
        } else {
            const body = await response.json()
            formError(body.message)
        }
    }
}

async function addQuestionRequest(value) {
    let response;
    try {
        response = await fetch("/api/questions", {
            method: "POST", headers: {
                "Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`
            }, body: JSON.stringify({question: value})
        })
    } catch (error) {
        formError("Проблемы с Интернетом")
        return false
    }

    await handleApiError(response)
    return response.ok
}

async function deleteQuestionRequest(questionId) {
    const response = await fetch(`/api/questions/${questionId}`, {
        method: "DELETE", headers: {"Authorization": `Bearer ${jwtToken}`}
    })
    await handleApiError(response)
    return response.ok
}

async function changeQuestionRequest(questionId, newValue) {
    const response = await fetch(`/api/questions/${questionId}`, {
        method: "PUT", headers: {
            "Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`,
        }, body: JSON.stringify({
            question: newValue
        })
    })

    await handleApiError(response)
    return response.ok
}

addLink.addEventListener("click", () => {
    addDialog.showModal()
})

addConfirm.addEventListener("click", async function (evt) {
    evt.preventDefault()
    const success = await addQuestionRequest(addInput.value)
    if (success) {
        window.location.reload()
    }
})

questionsList.forEach((elem) => {
    const id = elem.dataset.id
    const gamesAmount = elem.dataset.gamesAmount

    const editBtn = elem.querySelector(".edit-btn")
    const deleteBtn = elem.querySelector(".delete-btn")
    const questionValue = elem.querySelector("span")

    editBtn.addEventListener("click", () => {
        editDialog.showModal()
        editInput.value = questionValue.innerText
        editConfirm.onclick = async function (evt) {
            evt.preventDefault()
            const value = editInput.value
            const success = await changeQuestionRequest(id, value)
            if (success) {
                questionValue.innerText = value
                editDialog.close()
            }
        }
    })

    deleteBtn.addEventListener("click", async function () {
        if (gamesAmount > 0) {
            deleteDialog.showModal()
            deleteConfirm.onclick = async function () {
                const success = await deleteQuestionRequest(id)
                if (success) {
                    deleteDialog.close()
                    elem.remove()
                }
            }
        } else {
            const success = await deleteQuestionRequest(id)
            if (success) {
                elem.remove()
            }
        }
    })
})

searchInput.addEventListener("input", async () => {
    const searchValue = searchInput.value.trim().toLocaleLowerCase()

    questionsList.forEach((elem) => {
        const questionText = elem.querySelector("span").textContent.toLocaleLowerCase()

        if (questionText.includes(searchValue)) {
            elem.classList.remove("hidden")
        } else {
            elem.classList.add("hidden")
        }
    })
})
