const tmplt = document.querySelector("#answerTemplate")
const backLink = document.querySelector("#backLink")
const answersListElem = document.querySelector("#answersList")
const questionId = answersListElem.dataset.questionId

const params = new URLSearchParams()
params.append("question_id", questionId)
fetch(`/api/answers?${params}`, {method: "GET"}).then((response) => response.json()).then((data) => {
    if (data.length !== 0) {
        answersListElem.innerHTML = ""
    }
    loadAnswers(data)
})

function loadAnswers(answersList) {
    let pointsSum = 0
    for (let ind = 0; ind < Math.min(6, answersList.length); ind++) {
        pointsSum += answersList[ind].quantity
    }

    answersList.forEach((answer, ind) => {
        const newElem = tmplt.content.cloneNode(true).childNodes[1]
        const points = Math.round(1.0 * answer.quantity / pointsSum * 100)
        const pointsStats = newElem.querySelector(".points-stats")

        newElem.querySelector("span").innerHTML = `${answer.answer}`
        pointsStats.innerHTML = `ответов: ${answer.quantity}`
        answersListElem.appendChild(newElem)

        if (ind < 6) {
            newElem.classList.add("border-3")
            newElem.classList.add("border-success")
            pointsStats.innerText = `очков: ${points}, ` + pointsStats.innerText
        }

        newElem.querySelector("button").addEventListener("click", () => deleteAnswerRequest(answer.id, newElem))
    })
}

async function deleteAnswerRequest(answerId, toBeDeleted) {
    const response = await fetch(`/api/answers/${answerId}`, {method: "DELETE"})
    if (response.ok) {
        toBeDeleted.remove()
    } else {
        const data = await response.json()
        console.log(response.status)
        console.log(data)
    }
}

backLink.addEventListener("click", () => {
    document.location.href = document.referrer
})

