var inspectorElement = null

const records = {}
const debug = false
const current = { id: null }

window.addEventListener('DOMContentLoaded', () => {
    inspectorElement = document.getElementById('inspector')

    document.getElementById('sources-container').addEventListener('mouseleave', unhover)
    if (debug) {
        document.getElementById('sources').addEventListener('load', (ev) => {
            let graphic = ev.target.contentDocument
            let entries = graphic.getElementsByClassName('entry')
            for (let entry of entries) {
                entry.addEventListener('click', select)
            }
        })
        document.getElementById('save-info').addEventListener('click', recordInfo)    
    }
})

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
