class Gamebook {
    _textBack = 'Welcome to the adventure where you get to make the decisions.\n\nType "show" to export the current nodes, "edit" to make changes, and "load" to load an existing file\n\n'

    thisnode = 'start'
    adventureNodes = {'start': {'message': 'load error'}}
    dumpout = false
    editmode = 0
    holdnode = ''
    holdprompt = ""
    holdbranches = 0
    thisbranch = 0
    choosenode = 1
    replaceconfirm = 2
    yntrap = 3
    nodetext = 4
    numbranches = 5
    entermessage = 6
    entertarget = 7
    loadmode = false
    listeners = []

    setup() {
    }

    setadventure(data) {
        this.adventureNodes = data
    }
    
    get textBack() {
        return this._textBack
    }
    
    set textBack(value) {
        this._textBack = value
        this.listeners.forEach(fn => fn(value))
    }
    
    subscribe(fn) {
        this.listeners.push(fn)
        fn(this._textBack)
    }

    loadfile() {
        const myport = window.location.port

        const path = '/sillyadventure.txt'

        return fetch(path).then((response) => response.json()).then((data) => {
            this.setadventure(data)
            return data
        })
    }

    constructor() {
        this.loadfile().then(() => {
            this.dumpout = true
            this.stepThrough('')
        })        
    }

    stepThrough(inputval) {
        let retval = ""
        if (!this.dumpout) {
            return ''
        }
        if (inputval === "show") {
            // overall JSON
            retval = "{"
            // no linebreak for the first go round, it breaks the JSON parse
            let lbreak = ""
            // put linebreaks between the nodes
            Object.keys(this.adventureNodes).forEach((node) => {
                retval = `${retval}${lbreak}"${node}": ${JSON.stringify(this.adventureNodes[node])},`
                lbreak = '\n'
            })
            // remove trailing comma and add trailing }
            retval = retval.slice(0, retval.length - 1).concat("}")
            this.textBack = this._textBack.concat('\n\n', retval)
            return this._textBack
        }
        if (inputval === "load") {
            this.loadmode = true
            this.editmode = 0
            this.textBack = 'Please paste in an adventure'
            return 'Please paste in an adventure'
        }
        if (inputval === "edit") {
            this.editmode = this.choosenode
            this.loadmode = false
        }
        if (this.loadmode) {
            let loaded = {}
            try {
                loaded = JSON.parse(inputval)
            } catch (error) {
                this.textBack = `could not parse your adventure, ${error}. Reload the page to abort.`
                return `could not parse your adventure, ${error}. Reload to abort.`
            }
            if ('start' in loaded) {
                this.adventureNodes = loaded
                this.thisnode = 'start'
                this.loadmode = false
                this.textBack = 'successfully parsed the adventure\n\n'
            } else {
                return 'could not find a start node.  Reload to abort.'
            }
        }
        // this needs to go before the choosenode and nodetext so it can drop through
        if (this.editmode === this.yntrap) {
            if (inputval === 'Y' || inputval === 'y') {
                this.editmode = this.nodetext
                this.holdprompt = ""
            } else if (inputval === 'N' || inputval === 'n') {
                retval = 'ok, keeping that node as-is.\n\n'
                this.editmode = this.choosenode
                this._textBack = this._textBack.concat(retval)
                inputval = 'edit'
            } else {
                retval = 'Please enter Y or N\n\n'
                this.textBack = this._textBack.concat(retval)
                return this._textBack
            }
        }
        if (this.editmode === this.numbranches) {
            if (this.thisbranch === 0 && Number(inputval) >= 0 && Number(inputval) <= 9) {
                this.holdbranches = Math.round(Number(inputval))
                this.thisbranch = 1
                this.adventureNodes[this.holdnode]['prompt'] = this.holdprompt
                this.adventureNodes[this.holdnode]['messages'] = []
                this.adventureNodes[this.holdnode]['nodes'] = []
                if (this.holdbranches === 0) {
                    retval = `Thank you for entering node ${this.holdnode}\n\n`
                    this._textBack = this._textBack.concat(retval)
                    // drop through to the node selector
                    inputval = 'edit'
                    this.editmode = this.choosenode
                } else {
                    this.editmode = this.entermessage
                    retval = `Enter the message for choice #${this.thisbranch}\n\n`
                    this.textBack = this._textBack.concat(retval)
                    return this._textBack
                }
            } else {
                retval = 'Please enter the number of branches from 0 to 9\n'
                this.holdprompt = `${this.holdprompt}\n${inputval}`
                this.textBack = this._textBack.concat('\n\n', retval)
                return this._textBack
            }
        }
        if (this.editmode === this.entertarget) {
            // no input validation, can enter nodes that don't exist (yet)
            this.adventureNodes[this.holdnode]["nodes"].push(inputval)
            this.thisbranch = this.thisbranch + 1
            if (this.thisbranch > this.holdbranches) {
                // drop through to the node selector
                retval = `Thank you for entering node ${this.holdnode}\n\n`
                this._textBack = this._textBack.concat(retval)
                inputval = 'edit'
                this.editmode = this.choosenode
            } else {
                this.editmode = this.entermessage
                retval = `Enter the message for choice #${this.thisbranch}\n\n`
                this.textBack = this._textBack.concat(retval)
                return this._textBack
            }
        }
        if (this.editmode === this.choosenode) {
            if (inputval === 'quit!') {
                this.thisnode = 'start'
                this.editmode = 0
            } else if (inputval in this.adventureNodes) {
                this.editmode = this.replaceconfirm
            } else if (inputval !== 'edit') {
                this.holdnode = inputval
                this.holdprompt = ""
                this.editmode = this.nodetext
            } else {
                retval = 'These nodes are already part of the tree:\n\n'
                let sep = ''
                Object.keys(this.adventureNodes).forEach((node) => {
                    retval = `${retval}${sep}${node}`
                    sep = ', '
                })
                retval = `${retval}\n\nPlease name or create a node to edit, starting with 'start' (or type quit! to return to the game)\n\n`
                this.textBack = this._textBack.concat('\n\n', retval)
                return this._textBack
            }
        }
        if (this.editmode === this.replaceconfirm) {
            this.holdnode = inputval
            retval = `Node ${this.holdnode} reads like this right now ${JSON.stringify(this.adventureNodes[this.holdnode])}\nare you sure you want to replace it? (Y/N)\n\n`
            this.textBack = this._textBack.concat(retval)
            this.editmode = this.yntrap
            return this._textBack
        }
        if (this.editmode === this.nodetext) {
            // exit out
            if (inputval === '//') {
                this.editmode = this.numbranches
                this.thisbranch = 0
                retval = 'Thank you for the prompt.  How many branches would you like?  Please enter a number from 0 (making this an end node) to 9.\n\n'
                this.textBack = this._textBack.concat('\n\n', retval)
                return this._textBack
            }
            // first run of being here
            if ((inputval === this.holdnode || inputval === 'Y' || inputval === 'y') && this.holdprompt === "") {
                retval = `Please enter the prompt text for this node.  You may use several lines.  When you are done, enter a new line that's just "//" (without quotes)`
                this.textBack = this._textBack.concat('\n\n', retval)
                return this._textBack
            }
            // continued run
            retval = inputval
            this.holdprompt = `${this.holdprompt}\n${inputval}`
            this.textBack = this._textBack.concat('\n', retval)
            return this._textBack
        }
        if (this.editmode === this.entermessage) {
            // no input validation, just any message the user wants
            this.adventureNodes[this.holdnode]["messages"].push(inputval)
            this.editmode = this.entertarget
            retval = `Enter the target node name for choice #${this.thisbranch}\n\n`
            this.textBack = this._textBack.concat(retval)
            return this._textBack
        }
        // next section is navigate around the adventure
        if (this.adventureNodes[this.thisnode].nodes.length < 1) {
            this.thisnode = 'start'
            this._textBack = this._textBack.concat('\n\n')
        } else if (Number(inputval) > 0 && Number(inputval) <= this.adventureNodes[this.thisnode].nodes.length) {
            this.thisnode = this.adventureNodes[this.thisnode].nodes[Number(inputval) - 1]
            this._textBack = this._textBack.concat('\n\n')
        }
        // check for legality
        if (!(this.thisnode in this.adventureNodes)) {
            this.thisnode = 'start'
        }
        retval = this._textBack.concat(this.adventureNodes[this.thisnode].prompt, '\n\n')
        if (this.adventureNodes[this.thisnode].messages.length < 1) {
            retval = retval.concat('1) Return to the beginning')
        } else if (this.adventureNodes[this.thisnode].messages.length < 2) {
            retval = retval.concat('1) ', this.adventureNodes[this.thisnode].messages[0])
        } else {
            for (let i = 0; i < this.adventureNodes[this.thisnode].messages.length; i++) {
                retval = retval.concat(String(i + 1), ') ', this.adventureNodes[this.thisnode].messages[i], '\n')
            }
        }
        this.textBack = retval
        return retval
    }

}

const output = document.getElementById('output')
const input = document.getElementById('input')
const submit = document.getElementById('submit')

const game = new Gamebook()
game.subscribe(value => {
    output.textContent = value
    output.scrollTop = output.scrollHeight
})

function runInput() {
  const value = input.value
  const response = game.stepThrough(value)
  //output.textContent = response
  input.value = ''
  input.focus()
}

submit.addEventListener('click', runInput)
input.addEventListener('keyup', (event) => {
  if (event.key === 'Enter') {
    runInput()
  }
})

input.focus()
