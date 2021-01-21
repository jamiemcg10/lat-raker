let weightingDirections = "<li>Choose variables to weight by. These variables must be categorical. Enter the target percentage for each group as a decimal between >0 and 100 (no fractions). Entering a 0 for groups that do not exist in the data is optional.</li><li>Optional: Choose a variable to group by. The weight will be calculated so that the target percentages are the same for each group in this question (e.g., group by ExposedControl and the weighted percentages for target variables will be the same for exposed respondents and control respondents). You cannot group by a variable that targets are set for.</li><li>You will get unexpcted results if you weight an existing group to 0.</li>";
let resultsInfo = "<li>Always check to make sure the weights were computed accurately</li><li>You want the weighting efficiency to be above 70, ideally above 80</li><li>The minimum and maximum weight factor will show the smallest and largest weight used.</li>";

function getFile(){   
    // create FormData object with selected file to send to server

    let formData = new FormData(); 
    let savFile = $('#file')[0].files[0];
    formData.append('file', savFile);
    return formData;
}

function displaySelectionView(metaDataObj, metaDataList){
    // clear file selection screen and display forms for selecting weighting 
    // variables and entering targets

    console.log(metaDataObj);
    clearScreen();
    $('body').append(`<ul>${weightingDirections}</ul>`);
    $('body').append('<p>Choose question to group by:</p>')
    appendQuestionSelectionList('group-select', metaDataList);
    $('body').append('<div id="grouping-var"></div>')
    
    $('body').append('<p>Choose questions to weight by:</p>')
    appendQuestionSelectionList('q-select', metaDataList);
    $('body').append('<button class="button is-ghost" id="add-factor">Add</button>')
    
    $('body').append('<div id="weighting-factors"></div>')
    $('body').append('<button class="button is-solid" id="compute">Compute weights</button><p class="error" id="error"></p>')

}

function appendQuestionSelectionList(id, metaDataList){
    // populate select dropdowns from metadata

    $('body').append(`<div class="input has-arrow inline"><select id="${id}"></select><div>`);
    $(`#${id}`).append(`<option value=''></option>`);
    metaDataList.forEach((question)=>{
        if (question['name'] && question['type'] && (question['type'] === 'single')){ 
            // if the question has a name and type and the type is single, add it as an option 
            // to the select element
            $(`#${id}`).append(`<option value=${question['name']}>${question['name']}: ${Object.entries(question.text)[0][1]}</option>`);
            
        }
    });

}

function displayResultsView(fileLocation, crosstabs, report){
    // remove inputs and dropdowns from screen and show weighting results along with
    // link to download weighted .sav file

    clearScreen();
    $('body').append(`<a href="${fileLocation}" download>Click here to download your weighted file</a>`);
    $('body').append('<h3>Results</h3>');
    $('body').append(`<ul>${resultsInfo}</ul>`);
    
    // fix spacing in text
    // split the report and crosstabs into arrays by new line
    // split each report and crosstabs line line into arrays by tab (3+ spaces)
    let spaceRegex = /\s{3,}/;
    report = report.split("\n");  
    report = report.map(row => row.split(spaceRegex)); 
    crosstabs = crosstabs.split("\n");  
    crosstabs = crosstabs.map(row => row.split(spaceRegex));

    // append report and crosstabs to body
    [{name: "Report", content: report}, {name: "Crosstabs", content: crosstabs}].forEach((section)=>{
        $('body').append(`<div id="${section.name}"></div>`);
        $(`#${section.name}`).append(`<h4>${section.name}</h4>`);
        for (let i=0; i<section.content.length; i++){ 
            let row = section.content[i];
            let rowString  = '';
            let rowClass = 'report-row'
                console.log(row);
                row.forEach((cell)=>{
                    if (cell !== ''){
                        rowString += `<span>${cell}</span>`;  // insert each cell into a span to control spacing
                    }
                });
            if (row[0] === 'Question'){
                rowClass += " text";
            } else if (row[0] === 'Question Values'){
                rowString += "<span><em>%</em></span>";
            } else if (row[0] === 'Values'){
                console.log(rowString);
                rowClass += ' xt-labels';
            }

            $(`#${section.name}`).append(`<div class="${rowClass}">${rowString}</div>`);
        }
    });

}

function clearScreen(){
    // remove everything except the h1 title from the screen

    $('p').remove();
    $('select').remove();
    $('button').remove();
    $('#grouping-var').remove();
    $('#weighting-factors').remove();
    $('#file-select-container').remove();
    $('.input').remove();
    $('ul').remove();
}

function validateInputs(event, numFactors, groupVar, factorList){
    // make sure inputs are valid for weighting

    if (numFactors === 0){
        showError("You need to add at least one factor");
        event.preventDefault();
        return;
    }

    if (factorList.includes(groupVar) || groupVar === null){
        showError("You can't group by a weighting factor");
        event.preventDefault();
        return;
    }
}

function sumsTo100(array){
    // ensure that weighting targets add up to 100%

    let sum = array.reduce((acc, cValue)=>{
        if (acc === undefined){
            acc = 0;
        }
        if (cValue){
            acc += cValue;
        }
        
        return acc;
    });

    if (sum === 100) {
        return true;
    } else{
        return false;
    }
}

function convertArrayToObject(arr){
    // convert an array to an object using array indices as keys and array content as values

    let obj = {};

    for (let i=0; i<arr.length; i++){
        if (arr[i] !== undefined && arr[i] !== null){
            obj[i] = arr[i];
        }
    }

    return obj;
}

function showError(message){
    $('#error').text(message);
}

function clearError(){
    $('#error').text("");
}

