const form = document.querySelector("#addForm")
const qInput = document.querySelector("#addInput")
const questionsList = document.querySelectorAll("#questionsList>div")

const editInput = document.querySelector("#editInput")
const saveEdit = document.querySelector("#saveEdit")
const dialog = document.querySelector("dialog")

const host = window.location.host
const userId = document.querySelector("body").dataset.userId

async function addQuestionRequest(value) {
    const response = await fetch(host + "/api/questions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: {
            name: value,
            userId
        }
    })
    return await response.json()
}

async function deleteQuestionRequest(questionId) {
}

async function changeQuestionRequest(questionId, newValue) {
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
        saveEdit.addEventListener("click", async function (evt) {
            evt.preventDefault()
            const value = editInput.value
            if (value.length < 4 || value.length > 250) {

            }

            const success = await changeQuestionRequest(id, value)
            if (success) {
                questionValue.innerText = value
                dialog.close()
            }
        })
    })

    deleteBtn.addEventListener("click", async function () {
        const success = await deleteQuestionRequest(id)
        if (success) {
            elem.remove()
        }
    })
})
