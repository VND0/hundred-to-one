import {formError, getJwt} from "./tools.js";

const tmplt = document.querySelector("#answerTemplate")

const addForm = document.querySelector("#addForm")
const addInput = document.querySelector("#addInput")

const allAnswers = document.querySelector("#allAnswers")
const popularAnswers = document.querySelector("#popularAnswers")
const otherAnswers = document.querySelector("#otherAnswers")

const dialog = document.querySelector("#deleteDialog")
const confirmDeleting = document.querySelector("#confirmDeleting")

const questionId = allAnswers.dataset.questionId

const params = new URLSearchParams()
params.append("question_id", questionId)

let jwtToken = getJwt()

fetch(`/api/answers?${params}`, {
    method: "GET",
    headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${jwtToken}`
    }
}).then((response) => response.json()).then((data) => {
    if (data.length === 0) {
        allAnswers.innerHTML = "<h2 class='text-xl font-bold text-center'>Список ответов пустой</h2>"
    } else {
        loadAnswers(data)
    }
})

async function handleApiError(response) {
    if (!response.ok) {
        if (response.status === 404) {
            return formError("Такого вопроса не существует")
        }
        else {
            const body = await response.json()
            return formError(body.message)
        }
    }
}

function loadAnswers(answersList) {
    let pointsSum = 0
    let answersAmount = 0

    for (let ind = 0; ind < Math.min(6, answersList.length); ind++) {
        answersAmount += answersList[ind].quantity
    }

    answersList.forEach((answer, ind) => {
        const newElem = tmplt.content.cloneNode(true).childNodes[1]

        const points = Math.round(1.0 * answer.quantity / answersAmount * 100)
        const pointsStats = newElem.querySelector(".points-stats")

        const answerQuantity = newElem.querySelector(".answer-quantity")

        newElem.querySelector("span").innerHTML = `${answer.answer}`
        answerQuantity.innerHTML = `Кол-во: ${answer.quantity}`

        if (ind < 6) {
            pointsSum += points

            newElem.classList.add("border")
            newElem.classList.add("border-accent")

            pointsStats.innerText = `Очки: ${points}`
            pointsStats.classList.remove("hidden")

            popularAnswers.appendChild(newElem)
        } else {
            otherAnswers.appendChild(newElem)
        }

        if (ind === 5) {
            if (pointsSum < 100) {
                const newPoints = Math.round(1.0 * answersList[0].quantity / answersAmount * 100) + 100 - pointsSum
                popularAnswers.firstElementChild.querySelector(".points-stats").innerText = `Очки: ${newPoints}`
            }
            else if (pointsSum > 100) {
                const newPoints = Math.round(1.0 * answersList[5].quantity / answersAmount * 100) - pointsSum + 100
                popularAnswers.lastElementChild.querySelector(".points-stats").innerText = `Очки: ${newPoints}`
            }
        }

        newElem.querySelector("button").addEventListener("click", async () => {
            if (answersList.length === 6) {
                console.log(confirmDeleting)
                dialog.showModal()
                confirmDeleting.onclick = async function (evt) {
                    evt.preventDefault()

                    const success = await deleteAnswerRequest(answer.id)
                    if (success) {
                        newElem.remove()
                        dialog.close()
                        window.location.reload()
                    }
                }
            } else {
                const success = await deleteAnswerRequest(answer.id)
                if (success) {
                    newElem.remove()
                    window.location.reload()
                }
            }
        })
    })
}

async function addAnswerRequest(value) {
    let response;
    try {
        response = await fetch(`/api/answers?${params}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${jwtToken}`
            },
            body: JSON.stringify({
                answer: value
            })
        })
    } catch (error) {
        formError("Проблемы с интернетом")
        return false
    }

    await handleApiError(response)
    return response.ok
}

async function deleteAnswerRequest(answerId) {
    const response = await fetch(`/api/answers/${answerId}`, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${jwtToken}`
        }
    })

    await handleApiError(response)
    return response.ok
}

addForm.addEventListener("submit", async function (evt) {
    evt.preventDefault()

    const success = await addAnswerRequest(addInput.value)
    if (success) {
        window.location.reload()
    }
})
