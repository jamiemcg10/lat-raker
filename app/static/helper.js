let weightingDirections = "<li>Choose variables to weight by. These variables must be categorical. Enter the target percentage for each group as a decimal between >0 and 100 (no fractions). Entering a 0 for groups that do not exist in the data is optional.</li><li>Optional: Choose a variable to group by. The weight will be calculated so that the target percentages are the same for each group in this question (e.g., group by ExposedControl and the weighted percentages for target variables will be the same for exposed respondents and control respondents). You cannot group by a variable that targets are set for.</li><li>You will get unexpcted results if you weight an existing group to 0.</li>";

function getFile(){   
    let formData = new FormData(); 
    let savFile = $('#file')[0].files[0];
    formData.append('file', savFile);
    return formData;
}

function displaySelectionView(metaDataObj, metaDataList){
    console.log(metaDataObj);
    clearScreen();
    //$('body').append("<ul><li>Choose variables to weight by. These variables must be categorical. Enter the target percentage for each group as a decimal between >0 and 100 (no fractions). Entering a 0 for groups that do not exist in the data is optional.</li><li>Optional: Choose a variable to group by. The weight will be calculated so that the target percentages are the same for each group in this question (e.g., group by ExposedControl and the weighted percentages for target variables will be the same for exposed respondents and control respondents). You cannot group by a variable that targets are set for.</li><li>You will get unexpcted results if you weight an existing group to 0.</li></ul>");
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
    $('body').append(`<div class="input has-arrow inline"><select id="${id}"></select><div>`);
    $(`#${id}`).append(`<option value=''></option>`);
    metaDataList.forEach((question)=>{
        console.log(question);
        if (question['name']){
            if (question['type'] && (question['type'] === 'single')){
                $(`#${id}`).append(`<option value=${question['name']}>${question['name']}</option>`);
            }
        }
    });

}

function displayResultsView(fileLocation, crosstabs, report){
    clearScreen();
    $('body').append(`<a href="${fileLocation}" download>Click here to download your weighted file</a>`);
    $('body').append('<h3>Results</h3>');
    // fix spacing
    let spaceRegex = /\s{3,}/;
    report = report.split("\n");
    report = report.map(row => row.split(spaceRegex));
    crosstabs = crosstabs.split("\n");
    crosstabs = crosstabs.map(row => row.split(spaceRegex));

    [{name: "Report", content: report}, {name: "Crosstabs", content: crosstabs}].forEach((section)=>{
        $('body').append(`<div id="${section.name}"></div>`);
        $(`#${section.name}`).append(`<h4>${section.name}</h4>`);
        for (let i=0; i<section.content.length; i++){ 
            let row = section.content[i];
            let rowString  = '';
            let rowClass = 'report-row'
                row.forEach((cell)=>{
                    rowString += `<span>${cell}</span>`
                });
            if (row[0] === 'Question'){
                rowClass += " text";
            } else if (row[0] === 'Question Values'){
                rowString += "<span><em>%</em></span>";
            } else if (row[0] === 'Values'){
                continue;
            }

            $(`#${section.name}`).append(`<div class="${rowClass}">${rowString}</div>`);
        }
    });

}

function clearScreen(){
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
    if (numFactors === 0){
        console.log("You need to add at least one factor");
        showError("You need to add at least one factor");
        event.preventDefault();
        return;
    }

    if (factorList.includes(groupVar) || groupVar === null){
        console.log("You can't group by a weighting factor");
        showError("You can't group by a weighting factor");
        event.preventDefault();
        return;
    }
}

function displayFetchErrorView(){
    clearScreen();
}

function sumsTo100(array){
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

