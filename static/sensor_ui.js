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
        thisForm = this.form;

    this.submit = function() {
        thisForm.submit();
        thisForm.reset();
        thisObject.inputs["value"].select();
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

function submitContainingForm(input) {
    for (var i = 0; i < sensorInputs.length; i++) {
        if (sensorInputs[i].form.contains(input)) {
            console.log(sensorInputs[i]);
            sensorInputs[i].submit();
            return;
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
                submitContainingForm(target);
            }
            break;
        default:
            break;
    }
});

// NUMPAD INITIALIZATION
var numpadContainer = document.getElementById("numpad-container"),
    numpadTable = document.createElement("table"),
    numpadKeys = [
        [7, 8, 9],
        [4, 5, 6],
        [1, 2, 3],
        [" ", ".", "enter"]
    ],
    numpadRows = 4, // just to make programming easier
    numpadColumns = 3;

numpadTable.setAttribute("id", "numpad-table");
numpadContainer.appendChild(numpadTable);

function flashButton(button) {
    button.setAttribute("style", "background-color: #6a6a6a;");
    window.setTimeout(function() {
        button.removeAttribute("style");
    }, 100);
}

for (var row = 0; row < numpadRows; row++) {
    var newRow = document.createElement("tr");
    for (var column = 0; column < numpadColumns; column++) {
        var button = document.createElement("td"),
            value = numpadKeys[row][column];
        button.innerHTML = value;

        // this can probably be refactored in an OOP way
        switch (value) {
            case " ":
                break;
            case "enter":
                (function(button) {
                    button.onclick = function() {
                        flashButton(button);
                        if (document.activeElement.tagName == "INPUT") {
                            submitContainingForm(document.activeElement);
                        } else {
                            console.log("no input selected");
                        }
                    }
                })(button);
                break;
            default:
                (function(button, value) {
                    button.onclick = function() {
                        flashButton(button);
                        if (document.activeElement.tagName == "INPUT") {
                            document.activeElement.value = document.activeElement.value + value;
                        } else {
                            console.log("no input selected");
                        }
                    }
                })(button, value);
                break;
        }
            newRow.appendChild(button);
    }
    numpadTable.appendChild(newRow);
}

document.addEventListener("mousedown", function(e) {
    var key = e.key,
        target = e.target;
    if (numpadContainer.contains(e.target)) {
        e.preventDefault();
    }
});
