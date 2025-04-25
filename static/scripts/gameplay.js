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

const mistakeClasses = {active: "mistake-active", disabled: "mistake-disabled"}
const mistakeButtons = document.querySelectorAll(".mistake-button")
mistakeButtons.forEach((elem) => elem.addEventListener("click", () => {
    elem.classList.add(mistakeClasses.disabled)
    elem.classList.remove(mistakeClasses.active)
    elem.disabled = true
}))

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

function clearElements() {
    round.innerText = ""
    questionTitle.innerText = ""
    answersList.innerHTML = ""
    questionTitle.innerText = ""
    bank.innerText = "0"
    mistakeButtons.forEach((elem) => {
        elem.classList.remove("mistake-disabled")
        elem.classList.add("mistake-active")
        elem.disabled = false
    })
}

async function revealAnswers() {
    for (const a of answersList.children) {
        if (!a.classList.contains("answerRow")) {
            a.click()
            await new Promise((p) => setTimeout(p, 1000))
        }
    }
    await new Promise((p) => setTimeout(p, 1000))

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
        this.callback = (winner) => revealAnswers().then(() => callback(winner))

        clearElements()
        round.innerText = "Розыгрыш"
        questionTitle.innerText = this.question.question
        fillClosedAnswers()

        this.question.answers.forEach((answer, index) => {
            const answerRow = answersList.childNodes.item(index)
            answerRow.addEventListener("click", () => this.onRowOpened(answer, answerRow))
        })
    }

    onRowOpened(answer, answerRow) {
        const openedAnswer = openedAnswerTemplate.content.cloneNode(true).childNodes[1]
        const points = Math.round(100.0 * answer.quantity / this.votesSum)
        openedAnswer.querySelector(".answerText").innerText = answer.answer
        openedAnswer.querySelector(".answerPoints").innerText = points
        answersList.replaceChild(openedAnswer, answerRow)
        requestAnimationFrame(() => {
            openedAnswer.classList.add("flip-active")
        })
        if (!this.firstScore) {
            this.firstScore = points
        }
        this.addHandlersToTeams(() => this.clickOnTeam(1), () => this.clickOnTeam(2))
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


class Round {
    constructor(index, title, multiplier, scoresDistribution) {
        this.question = gameInfo.questions[index]
        this.title = title

        this.mistakes = {1: 0, 2: 0}
        this.openedQuestions = 0
        this.roundFinished = false

        if (scoresDistribution) {
            this.scoresDistribution = scoresDistribution
        } else {
            let sumPoints = 0
            this.question.answers.forEach((answer) => {
                sumPoints += answer.quantity
            })
            this.scoresDistribution = []
            this.question.answers.forEach((answer) => {
                this.scoresDistribution.push(Math.round(100.0 * multiplier * answer.quantity / sumPoints))
            })
        }

    }

    game(winner, callback) {
        clearElements()
        round.innerText = this.title
        questionTitle.innerText = this.question.question

        if (winner !== null) {
            this.winner = winner
            this.loser = winner === 1 ? 2 : 1
        } else {
            const current1Score = Number.parseInt(team1Score.innerText)
            const current2Score = Number.parseInt(team2Score.innerText)
            if (current1Score < current2Score) {
                this.winner = 1
                this.loser = 2
            } else if (current2Score < current1Score) {
                this.winner = 2
                this.loser = 1
            } else {
                // TODO: добавить обработку жеребьевки при равных очках
                alert("Очки равны")
            }
        }
        this.callback = () => {
            this.roundFinished = true;
            revealAnswers().then(callback)
        }
        this.finalAttempt = false

        fillClosedAnswers()
        this.question.answers.forEach((answer, index) => {
            answersList.childNodes.item(index).addEventListener("click", (evt) => this.onRowOpened(evt, answer, index))
        })

        this.onMistakeMadeBound = this.onMistakeMade.bind(this)
        mistakeButtons.forEach((elem) => elem.addEventListener("click", this.onMistakeMadeBound))
    }

    onRowOpened(evt, answer, index) {
        const openedAnswer = openedAnswerTemplate.content.cloneNode(true).childNodes[1]
        const points = this.scoresDistribution[index]
        openedAnswer.querySelector(".answerText").innerText = answer.answer
        openedAnswer.querySelector(".answerPoints").innerText = points
        answersList.replaceChild(openedAnswer, evt.target)
        requestAnimationFrame(() => openedAnswer.classList.add("flip-active"))
        this.openedQuestions++

        if (this.roundFinished) return

        bank.innerText = Number.parseInt(bank.innerText) + points
        const inBank = Number.parseInt(bank.innerText)

        if (this.finalAttempt) {
            if (this.loser === 1) {
                team1Score.innerText = Number.parseInt(team1Score.innerText) + inBank
            } else {
                team2Score.innerText = Number.parseInt(team2Score.innerText) + inBank
            }

            this.callback()
        } else if (this.openedQuestions === 6) {
            if (this.winner === 1) {
                team1Score.innerText = Number.parseInt(team1Score.innerText) + inBank
            } else {
                team2Score.innerText = Number.parseInt(team2Score.innerText) + inBank
            }

            this.callback()
        }
    }

    onMistakeMade(evt) {
        if (this.roundFinished) return

        if (!this.finalAttempt) {
            const teamNumber = evt.currentTarget.dataset.teamNumber
            evt.currentTarget.removeEventListener("click", this.onMistakeMadeBound)

            this.mistakes[teamNumber]++
            if (this.mistakes[teamNumber] === 3) {
                this.finalAttempt = true
            }
        } else {
            const inBank = Number.parseInt(bank.innerText)
            bank.innerText = "0"
            if (this.winner === 1) {
                team1Score.innerText = Number.parseInt(team1Score.innerText) + inBank
            } else {
                team2Score.innerText = Number.parseInt(team2Score.innerText) + inBank
            }

            this.callback()
        }
    }
}

function showWinnerBanner() {
    const current1Score = Number.parseInt(team1Score.innerText)
    const current2Score = Number.parseInt(team2Score.innerText)
    const overlay = document.querySelector("#overlay")
    const banner = document.querySelector("#winnerBanner")
    const winnerText = document.querySelector("#winnerTeam")

    if (current1Score > current2Score) {
        winnerText.innerText = "1"
    } else if (current2Score > current1Score) {
        winnerText.innerText = "2"
    } else {
        winnerText.innerText = "никто, ничья"
    }
    confetti({
        particleCount: 1500,
        spread: 80,
        origin: {y: 0.7},
    });
    overlay.classList.remove("hidden")
    banner.classList.remove("hidden")

}

const drawB4Simple = new Draw(0)
const simpleGame = new Round(1, "Простая игра", 1)

const drawB4Double = new Draw(2)
const doubleGame = new Round(3, "Двойная игра", 2)

const drawB4Triple = new Draw(4)
const tripleGame = new Round(5, "Тройная игра", 3)

const inverseGame = new Round(6, "Игра наоборот", 1, [15, 30, 60, 120, 180, 240])

drawB4Simple.draw((winner) => simpleGame.game(winner, () => drawB4Double.draw((winner) => doubleGame.game(winner, () =>
    drawB4Triple.draw((winner) => tripleGame.game(winner, () => inverseGame.game(null, () => showWinnerBanner())))))))
