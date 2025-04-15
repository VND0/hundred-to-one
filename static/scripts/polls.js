import {formError, formMessage, getJwt} from "./tools.js";

const addForm = document.querySelector("#addForm")
const pInput = document.querySelector("#addInput")
const pollsList = document.querySelectorAll("#pollsList>li")

const editInput = document.querySelector("#editInput")
const saveEdit = document.querySelector("#saveEdit")
const dialog = document.querySelector("dialog")

let jwtToken = getJwt()

async function handleApiError(response) {
    if (response.ok) return
    if (response.status === 409) {
        formError("Опросы должны быть уникальными")
    } else if (response.status === 404) {
        formError("Объект не найден")
    } else {
        const body = await response.json()
        formError(body.message)
    }
}

async function addPollRequest(poll) {
    let response;
    try {
        response = await fetch("/api/polls", {
            method: "POST", headers: {
                "Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`
            }, body: JSON.stringify({poll})
        })
    } catch (error) {
        formError("Проблемы с Интернетом")
        return false
    }

    await handleApiError(response)
    return response.ok
}

async function delPollRequest(pollId) {
    let response;
    try {
        response = await fetch(`/api/polls/${pollId}`, {
            method: "DELETE", headers: {"Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`}
        })
    } catch (error) {
        formError("Проблемы с Интернетом")
        return false
    }

    await handleApiError(response)
    return response.ok

}

async function editPollRequest(pollId, newName) {
    let response;
    try {
        response = await fetch(`/api/polls/${pollId}`, {
            method: "PUT", headers: {
                "Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`
            }, body: JSON.stringify({poll: newName})
        })
    } catch (error) {
        formError("Проблемы с Интернетом")
        return false
    }

    await handleApiError(response)
    return response.ok
}

addForm.addEventListener("submit", async function (evt) {
    evt.preventDefault()
    const success = await addPollRequest(pInput.value)
    if (success) {
        window.location.reload()
    }
})

pollsList.forEach((elem) => {
    const id = elem.dataset.id
    const editBtn = elem.querySelector(".edit-btn")
    const deleteBtn = elem.querySelector(".delete-btn")
    const pollValue = elem.querySelector(".poll-name")
    const publicLinkA = elem.querySelector(".public-link")
    const toClipboardBtn = elem.querySelector(".to-clipboard")

    const href = `/public/polls/${id}`
    const publicLink = window.location.host + href;

    toClipboardBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(publicLink)
        formMessage("Скопировано в буфер обмена")
    })

    deleteBtn.addEventListener("click", async () => {
        const success = await delPollRequest(id)
        if (success) {
            elem.remove()
        }
    })

    editBtn.addEventListener("click", () => {
        dialog.showModal()
        editInput.value = pollValue.innerText
        saveEdit.onclick = async (evt) => {
            evt.preventDefault()
            const success = await editPollRequest(id, editInput.value)
            if (success) {
                dialog.close()
                pollValue.innerText = editInput.value
            }
        }
    })
})
