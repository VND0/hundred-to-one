import {formError, getJwt} from "./tools.js";

const tmplt = document.querySelector("#answerTemplate")

const addForm = document.querySelector("#addForm")
const answerInput = document.querySelector("#answerInput")
const quantityInput = document.querySelector("#quantityInput")

const noAnswers = document.querySelector("#noAnswers")
const allAnswers = document.querySelector("#allAnswers")
const popularAnswers = document.querySelector("#popularAnswers")
const otherAnswers = document.querySelector("#otherAnswers")

const deleteDialog = document.querySelector("#deleteDialog")
const confirmDeleting = document.querySelector("#confirmDeleting")

const questionId = allAnswers.dataset.questionId
const gamesAmount = allAnswers.dataset.gamesAmount

const params = new URLSearchParams()
params.append("question_id", questionId)

let jwtToken = getJwt()

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

async function refreshContent(state) {
    let response = await getAnswersRequest()
    let data = await response.json()

    if (data.length === 0) {
        noAnswers.classList.remove("hidden")
        allAnswers.classList.add("hidden")

    } else {
        noAnswers.classList.add("hidden")
        allAnswers.classList.remove("hidden")

        if (state === "start") {
            loadAnswers(data)
        }
        else if (state === "update") {
            updateAnswers(data)
        }
    }
}

function fillAnswerElem(answer, elem, ind, points) {
    const answerText = elem.querySelector("span")
    const answerQuantity = elem.querySelector(".answer-quantity")
    const pointsStats = elem.querySelector(".points-stats")

    answerText.innerHTML = `${answer.answer}`
    answerQuantity.innerHTML = `Кол-во: ${answer.quantity}`

    if (ind < 6) {
        elem.classList.add("border")
        elem.classList.add("border-accent")

        pointsStats.innerText = `Очки: ${points}`
        pointsStats.classList.remove("hidden")
    }
}

function recalculatePoints(answersList, answersAmount, pointsSum) {
    if (pointsSum < 100) {
        const newPoints = Math.round(1.0 * answersList[0].quantity / answersAmount * 100) + 100 - pointsSum
        popularAnswers.firstElementChild.querySelector(".points-stats").innerText = `Очки: ${newPoints}`
    }
    else if (pointsSum > 100) {
        let ind = popularAnswers.childNodes.length - 1
        const newPoints = Math.round(1.0 * answersList[ind].quantity / answersAmount * 100) - pointsSum + 100
        popularAnswers.lastElementChild.querySelector(".points-stats").innerText = `Очки: ${newPoints}`
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

        fillAnswerElem(answer, newElem, ind, points)

        if (ind < 6) {
            pointsSum += points
            popularAnswers.appendChild(newElem)
        } else {
            otherAnswers.appendChild(newElem)
        }

        const deleteBtn = newElem.querySelector("button")
        deleteBtn.onclick = () => deleteAnswer(newElem, answer.id, answersList.length, gamesAmount)
    })

    recalculatePoints(answersList, answersAmount, pointsSum)
}

function updateAnswers(answersList) {
    let pointsSum = 0
    let answersAmount = 0

    for (let ind = 0; ind < Math.min(6, answersList.length); ind++) {
        answersAmount += answersList[ind].quantity
    }

    answersList.forEach((answer, ind) => {
        let elem
        const points = Math.round(1.0 * answer.quantity / answersAmount * 100)

        if (ind < 6) {
            elem = popularAnswers.childNodes[ind]
            pointsSum += points
        } else {
            elem = otherAnswers.childNodes[ind - 6]
        }

        if (!elem) {
            elem = tmplt.content.cloneNode(true).childNodes[1]
            if (ind < 6) {
                popularAnswers.appendChild(elem)
            } else {
                otherAnswers.appendChild(elem)
            }
        }

        fillAnswerElem(answer, elem, ind, points)

        const deleteBtn = elem.querySelector("button")
        deleteBtn.onclick = async() => await deleteAnswer(elem, answer.id, answersList.length, gamesAmount)
    })

    if (answersList.length < popularAnswers.childNodes.length + otherAnswers.childNodes.length) {
        otherAnswers.removeChild(otherAnswers.lastChild)
    }

    recalculatePoints(answersList, answersAmount, pointsSum)
}

async function getAnswersRequest() {
    return await fetch(`/api/answers?${params}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${jwtToken}`
        }
    })
}

async function addAnswerRequest(answer, quantity) {
    let response;
    try {
        response = await fetch(`/api/answers?${params}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${jwtToken}`
            },
            body: JSON.stringify({
                answer: answer,
                quantity: quantity
            })
        })
    } catch (error) {
        formError("Проблемы с интернетом")
        return false
    }

    await handleApiError(response)
    return response.ok
}

async function deleteAnswer(elem, answerId, answersAmount, gamesAmount) {
    if (answersAmount === 6 && gamesAmount > 0) {
        deleteDialog.showModal()
        confirmDeleting.onclick = async function (evt) {
            evt.preventDefault()

            const success = await deleteAnswerRequest(answerId)
            if (success) {
                elem.remove()
                deleteDialog.close()
                await refreshContent("update")
            }
        }
    } else {
        const success = await deleteAnswerRequest(answerId)
        if (success) {
            elem.remove()
            await refreshContent("update")
        }
    }
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

    const success = await addAnswerRequest(answerInput.value, quantityInput.value)
    if (success) {
        answerInput.value = ""
        quantityInput.value = 1
        await refreshContent("update")
    }
})

await refreshContent("start")
