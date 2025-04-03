const tmplt = document.querySelector("#answerTemplate")
const answersListElem = document.querySelector("#answersList")
const questionId = answersListElem.dataset.questionId

const params = new URLSearchParams()
params.append("question_id", questionId)
fetch(`/api/answers?${params}`, {method: "GET"}).then((response) => response.json()).then((data) => {
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
        newElem.querySelector("span").innerHTML = `${answer.answer}`
        newElem.querySelector(".points-stats").innerHTML = `ответов: ${answer.quantity}`
        answersListElem.appendChild(newElem)

        if (ind < 6) {
            newElem.classList.add("border-3")
            newElem.classList.add("border-success")
            newElem.querySelector(".points-stats").innerText = `очков: ${points}, ` + newElem.querySelector(".points-stats").innerText
        }
    })
}
