import {formError} from "./toasts.js";

const gamesList = document.querySelectorAll("#gamesList>li")

let jwtToken
const cookieArr = document.cookie.split("; ")
cookieArr.forEach((elem) => {
    const parsed = elem.split("=")
    if (parsed[0] === "jwtToken") {
        jwtToken = parsed[1]
    }
})

async function deleteGameRequest(gameId, toBeDeletedElem) {
    const response = await fetch(`/api/games/${gameId}`, {
        method: "DELETE", headers: {"Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`}
    })
    const data = await response.json()

    if (!response.ok) {
        formError(`${response.status}: ${data.message}`)
    } else {
        toBeDeletedElem.remove()
    }

}

gamesList.forEach((elem) => {
    const gameId = elem.dataset.id
    const deleteBtn = elem.querySelector(".delete-btn")
    deleteBtn.addEventListener("click", async () => deleteGameRequest(gameId, elem))
})