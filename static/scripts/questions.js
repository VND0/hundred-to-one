const form = document.querySelector("#addForm")
const qInput = document.querySelector("#addInput")
const questionsList = document.querySelectorAll("#questionsList>li")

const editInput = document.querySelector("#editInput")
const saveEdit = document.querySelector("#saveEdit")
const dialog = document.querySelector("dialog")

const toastTemplate = document.querySelector("#toastTemplate")
const toastsContainer = document.querySelector("#toastsContainer")

const userId = document.querySelector("body").dataset.userId

function formError(text) {
    const elem = toastTemplate.content.firstElementChild.cloneNode(true)
    elem.classList.add("alert-error")
    elem.querySelector("span").innerText = text
    toastsContainer.append(elem)
    setTimeout(() => elem.remove(), 3000)
}

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
    const body = {
        question: value,
        userId
    }
    let response;
    try {
        response = await fetch("/api/questions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body)
        })
    } catch (error) {
        formError("Проблемы с Интернетом")
        return false
    }

    await handleApiError(response)
    return response.ok
}

async function deleteQuestionRequest(questionId) {
    const response = await fetch(`/api/questions/${questionId}`, {method: "DELETE"})
    await handleApiError(response)
    return response.ok
}

async function changeQuestionRequest(questionId, newValue) {
    const response = await fetch(`/api/questions/${questionId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            question: newValue
        })
    })

    await handleApiError(response)
    return response.ok
}


form.addEventListener("submit", async function (evt) {
    evt.preventDefault()
    const success = await addQuestionRequest(qInput.value)
    if (success) {
        window.location.reload()
    }
})

questionsList.forEach((elem) => {
    const id = elem.dataset.id
    const editBtn = elem.querySelector(".edit-btn")
    const deleteBtn = elem.querySelector(".delete-btn")
    const questionValue = elem.querySelector("span")

    editBtn.addEventListener("click", () => {
        dialog.showModal()
        editInput.value = questionValue.innerText
        saveEdit.onclick = async function (evt) {
            evt.preventDefault()
            const value = editInput.value
            const success = await changeQuestionRequest(id, value)
            if (success) {
                questionValue.innerText = value
                dialog.close()
            }
        }
    })

    deleteBtn.addEventListener("click", async function () {
        const success = await deleteQuestionRequest(id)
        if (success) {
            elem.remove()
        }
    })
})
