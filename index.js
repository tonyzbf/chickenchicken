var inspectorElement = null
var titleElement = null
var subscriberElement = null

const records = {}
const debug = false
const current = { id: null }
const touchInfo = { id: null }

window.addEventListener('DOMContentLoaded', () => {
    inspectorElement = document.getElementById('inspector')
    titleElement = document.getElementById('inspector-title')
    subscriberElement = document.getElementById('inspector-subscriber')
    document.getElementById('sources').addEventListener('load', (ev) => {
        let graphic = ev.target.contentDocument
        let entries = graphic.getElementsByClassName('entry')
        for (let entry of entries) {
            if (debug) {
                entry.addEventListener('click', select)
            } else {
                entry.addEventListener('mouseenter', hover)
                entry.addEventListener('touchstart', hover2)
            }
        }
    })
    document.getElementById('sources-container').addEventListener('mouseleave', unhover)
    if (debug) {
        document.getElementById('save-info').addEventListener('click', recordInfo)
    }
})

function hover(ev) {
    let tile = ev.currentTarget
    let title = tile.dataset.title
    let subscriber = tile.dataset.subscriber
    unhover(undefined)
    titleElement.innerText = title
    subscriberElement.innerText = subscriber
    inspectorElement.classList.remove('hidden')
}

function hover2(ev) {
    let tile = ev.currentTarget
    if (touchInfo.id != tile.id) {
        ev.preventDefault()
        touchInfo.id = tile.id
    }
    hover(ev)
}

function unhover(ev) {
    inspectorElement.classList.add('hidden')
}

function select(ev) {
    ev.preventDefault()
    let id = ev.currentTarget.id
    current.id = id
    hover(ev)
    let sub = ''
    let time = ''
    if (ev.currentTarget.id in records) {
        sub = records[id].sub
        time = records[id].time
    }
    document.getElementById('subscriber').value = sub
    document.getElementById('timestamp').value = time
}

function recordInfo(ev) {
    if (!current.id) return
    let subscriber = document.getElementById('subscriber').value
    let timestamp = document.getElementById('timestamp').value
    records[current.id] = { sub: subscriber, time: timestamp }
    current.id = null
}
