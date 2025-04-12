import {formError, getJwt} from "./tools.js";

const tmplt = document.querySelector("#answerTemplate")
const backLink = document.querySelector("#backLink")

const addForm = document.querySelector("#addForm")
const addInput = document.querySelector("#addInput")

const allAnswers = document.querySelector("#allAnswers")
const popularAnswers = document.querySelector("#popularAnswers")
const otherAnswers = document.querySelector("#otherAnswers")

const questionId = allAnswers.dataset.questionId

let jwtToken = getJwt()

const params = new URLSearchParams()
params.append("question_id", questionId)
fetch(`/api/answers?${params}`, {
    method: "GET", headers: {"Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`}
}).then((response) => response.json()).then((data) => {
    if (data.length === 0) {
        allAnswers.innerHTML = "<h2 class='text-xl font-bold text-center'>Список ответов пустой</h2>"

    } else {
        loadAnswers(data)
    }
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

        const answerQuantity = newElem.querySelector(".answer-quantity")

        newElem.querySelector("span").innerHTML = `${answer.answer}`
        answerQuantity.innerHTML = `Кол-во: ${answer.quantity}`

        if (ind < 6) {
            newElem.classList.add("border-2")
            newElem.classList.add("border-success")

            pointsStats.innerText += `Очки: ${points}`
            pointsStats.classList.remove("hidden")

            popularAnswers.appendChild(newElem)
        } else {
            otherAnswers.appendChild(newElem)
        }

        newElem.querySelector("button").addEventListener("click", () => deleteAnswerRequest(answer.id, newElem))
    })
}

async function addAnswerRequest(value) {
    let response;
    try {
        response = await fetch("/api/answers", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${jwtToken}`
            },
            body: JSON.stringify({
                question_id: questionId,
                answer: value
            })
        })
    } catch (error) {
        formError("Проблемы с интернетом")
        return false
    }

    return response.ok
}

async function deleteAnswerRequest(answerId, toBeDeleted) {
    const response = await fetch(`/api/answers/${answerId}`, {
        method: "DELETE", headers: {"Content-Type": "application/json", "Authorization": `Bearer ${jwtToken}`}
    })
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

addForm.addEventListener("submit", async function (evt) {
    evt.preventDefault()

    const success = await addAnswerRequest(addInput.value)
    if (success) {
        window.location.reload()
    }
})

