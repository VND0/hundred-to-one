let requestData = []

let questionsCounter = 0;

const listTitle = document.querySelector("#listTitle")
const questionsList = document.querySelectorAll("#questionsList>li")

const addForm = document.querySelector("#addForm")
const gInput = document.querySelector("#addInput")
const addButton = document.querySelector("#addButton")

const userId = document.querySelector("body").dataset.userId

function changesCounterUpdate() {
    listTitle.innerText = `Вопросы для игры (${questionsCounter} / 7)`

    if (questionsCounter === 7) {
        listTitle.classList.add("divider-secondary")
        listTitle.classList.remove("divider-error")

        addButton.classList.remove("btn-disabled")
    } else {
        listTitle.classList.add("divider-error")
        listTitle.classList.remove("divider-secondary")

        addButton.classList.add("btn-disabled")
    }
}

questionsList.forEach((elem) => {
    const id = elem.dataset.questionId
    const input = elem.querySelector("input")

    input.addEventListener("change", () => {
        if (input.checked) {
            requestData.push(id)
            questionsCounter++
        } else {
            requestData.splice(requestData.indexOf(id))
            questionsCounter--
        }

        changesCounterUpdate()
    })
})

changesCounterUpdate()
