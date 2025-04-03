const tmplt = document.querySelector("#answerTemplate")
const answersListElem = document.querySelector("#answersList")
const questionId = answersListElem.dataset.questionId

const params = new URLSearchParams()
params.append("question_id", questionId)
fetch(`/api/answers?${params}`, {method: "GET"}).then((response) => response.json()).then((data) => {
    loadAnswers(data)
})

function loadAnswers(answersList) {
    answersList.forEach((answer, ind) => {
        const newElem = tmplt.content.cloneNode(true).childNodes[1]
        newElem.querySelector("span").innerHTML =
            `${answer.answer} <span class="text-info">(ответов: ${answer.quantity})</span>`
        answersListElem.appendChild(newElem)

        if (ind < 6) {
            newElem.classList.add("border-3")
            newElem.classList.add("border-success")
        }
    })
}
