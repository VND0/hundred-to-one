const tmplt = document.querySelector("#answerTemplate")
const answersListElem = document.querySelector("#answersList")
const questionId = answersListElem.dataset.questionId
let answersList;

const params = new URLSearchParams()
params.append("question_id", questionId)
fetch(`/api/answers?${params}`, {method: "GET"}).then((response) => {
    loadAnswers(response)
})

function loadAnswers(response) {
    answersList = response.json()
    answersList.forEach((answer) => {
        const newElem = tmplt.firstElementChild.cloneNode(true)
        newElem.querySelector("span").innerText = `${answer.answer} (ответов: ${answer.quantity})`
        answersListElem.appendChild(newElem)
    })
}
