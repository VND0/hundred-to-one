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

const mistakeButtons = document.querySelectorAll(".mistake-button")

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


class Draw {
    constructor(questionIndex) {
        this.question = gameInfo.questions[questionIndex]
        this.handlersAdded = false
        this.votesSum = 0
        this.firstScore = null

        this.question.answers.forEach((answer) => {
            this.votesSum += answer.quantity
        })
    }

    draw(callback) {
        this.callback = callback

        round.innerText = "Розыгрыш"
        questionTitle.innerText = this.question.question
        fillClosedAnswers()

        this.question.answers.forEach((answer, index) => {
            const answerRow = answersList.childNodes.item(index)
            answerRow.addEventListener("click", () => {
                const openedAnswer = openedAnswerTemplate.content.cloneNode(true).childNodes[1]
                const points = Math.round(100.0 * answer.quantity / this.votesSum)
                openedAnswer.querySelector(".answerText").innerText = answer.answer
                openedAnswer.querySelector(".answerPoints").innerText = points
                answersList.replaceChild(openedAnswer, answerRow)
                if (!this.firstScore) {
                    this.firstScore = points
                }
                this.addHandlersToTeams(() => this.clickOnTeam(1), () => this.clickOnTeam(2))
            })
        })
    }

    clickOnTeam(team) {
        if (team === 1) {
            team1Score.innerText = Number.parseInt(team1Score.innerText) + this.firstScore
        } else {
            team2Score.innerText = Number.parseInt(team2Score.innerText) + this.firstScore
        }
        this.callback(team)
    }

    addHandlersToTeams(callback1, callback2) {
        if (this.handlersAdded) {
            return
        } else {
            this.handlersAdded = true
        }
        toggleTeamOutlines()

        function forTeam1() {
            toggleTeamOutlines()
            callback1()
            team1Block.removeEventListener("click", forTeam1)
            team2Block.removeEventListener("click", forTeam2)
        }

        team1Block.addEventListener("click", forTeam1)

        function forTeam2() {
            toggleTeamOutlines()
            callback2()
            team1Block.removeEventListener("click", forTeam1)
            team2Block.removeEventListener("click", forTeam2)
        }

        team2Block.addEventListener("click", forTeam2)
    }
}


class SimpleGame {
    constructor() {
        this.question = gameInfo.questions[1]

        this.mistakes = {1: 0, 2: 0}
        this.sumPoints = 0
        this.openedQuestions = 0

        this.question.answers.forEach((answer) => {
            this.sumPoints += answer.quantity
        })
    }

    game(winner, callback) {
        answersList.innerHTML = ""
        round.innerText = "Простая игра"
        questionTitle.innerText = this.question.question

        this.winner = winner
        this.loser = winner === 1 ? 2 : 1
        this.callback = callback

        fillClosedAnswers()
        this.question.answers.forEach((answer, index) => {
            answersList.childNodes.item(index).addEventListener("click", (evt) => this.onRowOpened(evt, answer))
        })

        this.onMistakeMakeBound = this.onMistakeMade.bind(this)
        mistakeButtons.forEach((elem) => elem.addEventListener("click", this.onMistakeMakeBound))
    }

    onRowOpened(evt, answer) {
        const openedAnswer = openedAnswerTemplate.content.cloneNode(true).childNodes[1]
        const points = Math.round(100.0 * answer.quantity / this.sumPoints)
        openedAnswer.querySelector(".answerText").innerText = answer.answer
        openedAnswer.querySelector(".answerPoints").innerText = points
        answersList.replaceChild(openedAnswer, evt.target)
        this.openedQuestions++
        bank.innerText = Number.parseInt(bank.innerText) + points

        if (this.openedQuestions === 6) {
            const inBank = Number.parseInt(bank.innerText)
            if (this.winner === 1) {
                team1Score.innerText = Number.parseInt(team1Score.innerText) + inBank
            } else {
                team2Score.innerText = Number.parseInt(team2Score.innerText) + inBank
            }
            bank.innerText = "0"
        }
    }

    onMistakeMade(evt) {
        const teamNumber = evt.currentTarget.dataset.teamNumber
        this.mistakes[teamNumber]++
        evt.currentTarget.removeEventListener("click", this.onMistakeMakeBound)
        alert(teamNumber)
    }
}

new Draw(0).draw((winner) => new SimpleGame().game(winner, () => new Draw(2).draw(() => {
})))
