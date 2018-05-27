var sensorTable = document.getElementById("sensor-inputs"),
    sensorHeaders = document.getElementById("sensor-input-headers"),
    sensorForms = document.getElementById("sensor-input-forms"),
    responseHeader = document.getElementById("response-header"),
    responseCell = document.getElementById("response-cell");

function setAttributes(element, attributes) {
    for (var attribute in attributes) {
        element.setAttribute(attribute, attributes[attribute]);
    }
}

// SENSOR INPUT INITIALIZATION
function SensorInput(sensorName) {
    this.form = document.createElement("form");
    this.inputs = {
        "sensor": null,
        "value": null,
        "notes": null
    }
    var thisObject = this,
        thisForm = this.form,
        thisValueField = null;

    this.submit = function() {
        thisForm.submit();
        thisForm.reset();
        thisObject.inputs["value"].select();
    }

    this.select = function() {
        thisValueField.select();
    }

    setAttributes(this.form, {
        "id": sensorName.replace(/ /g, "-"),
        "action": "new_observation",
        "target": "response-frame",
        "method": "post",
        "enctype": "multipart/form-data"
    });

    var header = document.createElement("th"),
        cell = document.createElement("td"),
        formTable = document.createElement("table");

    header.innerHTML = "manual sensor input";
    sensorHeaders.insertBefore(header, responseHeader);

    sensorForms.insertBefore(cell, responseCell);
    cell.appendChild(this.form);
    this.form.appendChild(formTable);

    // construct input rows
    for (var inputName in this.inputs) {
        var row = document.createElement("tr"),
            nameCell = document.createElement("td"),
            inputCell = document.createElement("td"),
            input = document.createElement("input");
        this.inputs[inputName] = input;

        nameCell.innerHTML = inputName;
        setAttributes(input, {
            "type": "text",
            "name": inputName,
            "id": inputName
        });
        if (inputName == "sensor") {
            //input.setAttribute("readonly", null);
            input.setAttribute("value", sensorName);
        } else if (inputName == "value") {
            thisValueField = input;
        }

        row.appendChild(nameCell);
        row.appendChild(inputCell);
        inputCell.appendChild(input);
        formTable.appendChild(row);
    }

    // construct fake submit button
    var submitRow = document.createElement("tr"),
        emptyCell = document.createElement("td"),
        submitButton = document.createElement("input");

    setAttributes(submitButton, {
        "type": "button",
        "value": "submit",
        "style": "width: 100%;"
    });
    submitRow.appendChild(emptyCell);
    submitRow.appendChild(submitButton);
    formTable.appendChild(submitRow);
    submitButton.onclick = function() {
        thisObject.submit();
    }
}

var sensorInputs = [
    new SensorInput("3m sd200 slm"),
    new SensorInput("dylos")
];

function getContainingSensorInput(input) {
    for (var i = 0; i < sensorInputs.length; i++) {
        if (sensorInputs[i].form.contains(input)) {
            console.log(sensorInputs[i]);
            return sensorInputs[i];
        }
    }
    console.log("not a sensor form");
}

document.addEventListener("keydown", function(e) {
    var key = e.key,
        target = e.target;
    switch (key) {
        case "Enter":
            if (target.tagName == "INPUT") {
                submitContainingSensorInput(target);
            }
            break;
        default:
            break;
    }
});


// NUMPAD TIMER
var timer = document.getElementById("numpad-timer"),
    time = 0,
    resolutionMs = 100,
    resolutionS = resolutionMs / 1000,
    nDecimals = 2;

function resetTimer() {
    time = 0;
}

function timerLoop() {
    time += resolutionS;
    timer.textContent = time.toFixed(nDecimals);
    window.setTimeout(timerLoop, resolutionMs);
}

timerLoop();

// NUMPAD INITIALIZATION
var numpadContainer = document.getElementById("numpad-container"),
    numpadTable = document.createElement("table"),
    numpadIcons = {
        prevForm: "⇦🗎",
        nextForm: "🗎⇨",
        delLeft: "⌫",
        clear: "⌧",
        submitActive: "⏎",
        resetTimer: "⏱",
    },
    numpadKeys = [
        [7, 8, 9],
        [4, 5, 6],
        [1, 2, 3],
        [" ", 0, numpadIcons.resetTimer],
        [numpadIcons.prevForm, ".", numpadIcons.nextForm],
        [numpadIcons.delLeft, numpadIcons.clear, numpadIcons.submitActive]
    ],
    numpadRows = 6, // just to make programming easier
    numpadColumns = 3;

numpadTable.setAttribute("id", "numpad-table");
numpadContainer.appendChild(numpadTable);

function NumpadButton(buttonText, formFocusedFunction = null, noFormFocusedFunction = null) {
    this.button = document.createElement("td");
    var thisButton = this.button;
    this.button.textContent = buttonText;
    thisButton.onclick = function() {
        thisButton.setAttribute("style", "background-color: #6a6a6a;");
        window.setTimeout(function() {
            thisButton.removeAttribute("style");
        }, 100);

        // default behaviour if a field is selected is to simulate typing button text and reset the timer
        if (document.activeElement.tagName == "INPUT") {
            if (formFocusedFunction == null) {
                document.activeElement.value = document.activeElement.value + buttonText;
            } else {
                formFocusedFunction();
            }

        // default behaviour if a field is selected is nothing
        } else {
            if (noFormFocusedFunction == null) {
                console.log("no input selected");
            } else {
                noFormFocusedFunction();
            }
        }
    }
}

function cycleSensorInputs(direction) {
    var activeSensorInput = getContainingSensorInput(document.activeElement),
        nInputs = sensorInputs.length;
    for (var i = 0; i < sensorInputs.length; i++) {
        if (sensorInputs[i] == activeSensorInput) {
            break;
        }
    }
    sensorInputs[(((i + direction) % nInputs) + nInputs) % nInputs].select();
}

for (var row = 0; row < numpadRows; row++) {
    var newRow = document.createElement("tr");
    for (var column = 0; column < numpadColumns; column++) {
        var value = numpadKeys[row][column],
            formFocusedFunction = null,
            noFormFocusedFunction = null;

        // TODO: possibly refactor by initializing each button with a constructor alone? (no more switch)
        switch (value) {
            case " ":
                formFocusedFunction = function() {
                }
                break;
            case numpadIcons.prevForm:
                formFocusedFunction = function() {
                    cycleSensorInputs(1);
                }
                noFormFocusedFunction = function() {
                    sensorInputs[0].select();
                }
                break;
            case numpadIcons.nextForm:
                formFocusedFunction = function() {
                    cycleSensorInputs(-1);
                }
                noFormFocusedFunction = function() {
                    sensorInputs[sensorInputs.length - 1].select();
                }
                break;
            case numpadIcons.submitActive:
                formFocusedFunction = function() {
                    var sensorInput = getContainingSensorInput(document.activeElement);
                    if (sensorInput !== undefined) {
                        sensorInput.submit();
                    }
                }
                break;
            case numpadIcons.clear:
                formFocusedFunction = function() {
                    document.activeElement.value = "";
                }
                break;
            case numpadIcons.delLeft:
                formFocusedFunction = function() {
                    document.activeElement.value = document.activeElement.value.slice(0, -1);
                }
                break;
            case numpadIcons.resetTimer:
                formFocusedFunction = resetTimer;
                noFormFocusedFunction = resetTimer;
                break;
            default:
                break;
        }
        newRow.appendChild(new NumpadButton(value, formFocusedFunction, noFormFocusedFunction).button);
    }
    numpadTable.appendChild(newRow);
}

document.addEventListener("mousedown", function(e) {
    var key = e.key,
        target = e.target;
    if (e.target.tagName == "TD") {
        e.preventDefault();
    }
});
