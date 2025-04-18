import {getJwt} from "./tools.js";

const openedAnswerTemplate = document.querySelector("#answerRowOpened")
const closedAnswerTemplate = document.querySelector("#answerRowClosed")
const answersList = document.querySelector("#answersList")


const jwtToken = getJwt()
const urlParts = document.URL.split("/")
const gameId = urlParts[urlParts.length - 1]

async function getGameInfo() {
    const response = await fetch(`/api/games/${gameId}`, {
        method: "GET",
        headers: {"Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`}
    })
    if (response.ok) {
        return await response.json()
    } else {
        alert(await response.text())
    }
}

const gameInfo = await getGameInfo()

/*{
    questions: [
        question,
        answers: [
            {answer, quantity}
        ]
    ]
}*/

function fillClosedAnswers() {
    for (let i = 1; i <= 6; i++) {
        const elem = closedAnswerTemplate.content.cloneNode(true).childNodes[1]
        elem.innerText = String(i)
        answersList.appendChild(elem)
    }
}

fillClosedAnswers()

document.querySelectorAll("#answersList>li").forEach((elem, index) => {
    elem.addEventListener("click", () => {
            const answer = openedAnswerTemplate.content.cloneNode(true).childNodes[1]
            answersList.replaceChild(answer, elem)
        }
    )
})
