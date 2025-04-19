import {getJwt} from "./tools.js";

const openedAnswerTemplate = document.querySelector("#answerRowOpened")
const closedAnswerTemplate = document.querySelector("#answerRowClosed")

const round = document.querySelector("#round")
const answersList = document.querySelector("#answersList")
const questionTitle = document.querySelector("#questionTitle")
const bank = document.querySelector("#bank")
const team1Block = document.querySelector("#team1Block")
const team2Block = document.querySelector("#team2Block")
const team1Score = document.querySelector("#team1Score")
const team2Score = document.querySelector("#team2Score")
let mistakes = {1: 0, 2: 0}

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

function toggleTeamOutlines() {
    team1Block.classList.toggle("border-2")
    team1Block.classList.toggle("border-4")
    team1Block.classList.toggle("border-accent")
    team2Block.classList.toggle("border-2")
    team2Block.classList.toggle("border-4")
    team2Block.classList.toggle("border-accent")
}

let handlersAdded = false

function addHandlersToTeams(callback1, callback2) {
    if (handlersAdded) {
        return
    } else {
        handlersAdded = true
    }
    toggleTeamOutlines()

    function forTeam1(evt) {
        toggleTeamOutlines()
        callback1()
        evt.target.removeEventListener("click", forTeam1)
    }

    team1Block.addEventListener("click", forTeam1)

    function forTeam2(evt) {
        toggleTeamOutlines()
        callback2()
        evt.target.removeEventListener("click", forTeam2)
    }

    team2Block.addEventListener("click", forTeam2)
}

async function draw(questionIndex, callback) {
    const question = gameInfo.questions[questionIndex]
    let votesSum = 0
    let firstScore = null
    question.answers.forEach((answer) => {
        votesSum += answer.quantity
    })

    round.innerText = "Розыгрыш"
    questionTitle.innerText = question.question
    fillClosedAnswers()

    function clickOnTeam(team) {
        if (team === 1) {
            team1Score.innerText = Number.parseInt(team1Score.innerText) + firstScore
        } else {
            team2Score.innerText = Number.parseInt(team2Score.innerText) + firstScore
        }
        callback(team)
    }

    question.answers.forEach((answer, index) => {
        const answerRow = answersList.childNodes.item(index)
        answerRow.addEventListener("click", () => {
            const openedAnswer = openedAnswerTemplate.content.cloneNode(true).childNodes[1]
            const points = Math.round(100.0 * answer.quantity / votesSum)
            openedAnswer.querySelector(".answerText").innerText = answer.answer
            openedAnswer.querySelector(".answerPoints").innerText = points
            answersList.replaceChild(openedAnswer, answerRow)
            if (!firstScore) {
                firstScore = points
            }
            addHandlersToTeams(() => clickOnTeam(1), () => clickOnTeam(2))
        })
    })
}

draw(0, (result) => {
    alert(result)
    answersList.innerHTML = ""
})
