import {formError, getJwt} from "./tools.js";

const gamesList = document.querySelectorAll("#gamesList>li")

let jwtToken = getJwt()

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