$('document').ready(()=>{
    let metaDataList;
    let metaDataObj;
    let factorList = [];

    $('#file').change(function(){  
            // get file and send it when one is selected  
            $('#file-select-container').append('<p class="status">Uploading...</p>'); 
            $('#error').text('');
            let file = getFile();
            sendFile(file);
    });

    function sendFile(fileToSend){
        // send file to server using ajax request
        $.ajax('/get-meta', {
            method: 'POST',
            data: fileToSend,
            processData: false,
            contentType: false, 
            success: (results)=>{
                $('.status').remove(); 
                console.log(results);
                if (results.success === "true"){
                    metaDataList = results.meta_data_array;
                    metaDataObj = results.meta_data_obj;
                    displaySelectionView(metaDataObj, metaDataList);
                } else {
                    $('#error').text(results.message);
                }
            },
            error: (jqXHR, textStatus, errorThrown)=>{
                console.log(`${errorThrown} - ${textStatus}`); 
                $('.status').text("Sorry, there was a problem processing your data.");
            }
        });
    }


    function addFactorEntry(varName){    
        // add a row to input target percentages for a variable

        $('#weighting-factors').append(`<div id=${varName} class="factor"><p>${varName}</p><p class="remove-factor" id="clear-${varName}">Remove</p></div>`);
        // what if no value labels?
        let values = metaDataObj[varName]['values'];
        values.forEach((value) => {
            // add an input box and a label for the box for each value
            let val = value.value;
            $(`#clear-${varName}`).before(`<div class="input-group"><label class="${varName}-val-label" for="${varName}_${val}">${val}</label><label class="${varName}-val-label" for="${varName}_${val}">${Object.entries(value.text)[0][1]}</label><div class=input><input type="text" class="dec ${varName}-factor" id="${varName}_${val}"></div><p>%</p></div>`);
        });
    }

    function populateTargets(factors, numFactors){
        // loop through factors, insert them into an object and validate each sum

        let targets = {};
        console.log(factors);
        for (let i=0; i<numFactors; i++){
            let factor = factors[i];
            let q = factor.id;

            // get target percentages
            let pcts = $(`.${q}-factor`);
            let numValues = $(`.${q}-factor`).length;
            if (numValues === 0){ // this really shouldn't happen
                showError("Looks like there's a problem.");
                return null; // return null so weights aren't computed
            } else {                
                for (let j=0; j<numValues; j++){ // loop through percentages
                    let value = pcts[j].labels[0].textContent;
                    let target = pcts[j].value;

                    if (targets[q] === undefined){ // variable has not been added to targets
                        targets[q] = [];
                    }

                    if (target !== '' & target != 0){ // target box is not empty and not 0
                        targets[q][value] = parseFloat(target);
                    }

                }

                if(!sumsTo100(targets[q])){
                    showError(`The target percentages for ${q} must add up to 100.`);
                    return null; // return null so weights aren't computed
                }

                // replace list with object
                targets[q] = convertArrayToObject(targets[q]);
            }
        }

        return targets;
    }

    $(document).on('keypress', '.dec', (event)=>{  // make sure text entered in weight factor box is a number
        if (isNaN(parseInt(event.key)) && event.key !== "."){
            event.preventDefault();
        }
    });

    $(document).on('click', '#add-factor', ()=>{
        // check that variable isn't already being used and add a row to input targets for it
        let varName = $('#q-select').val();
        if (factorList.includes(varName) || varName === null || varName === ''){ // check to make sure variable isn't already added
            return;
        } else {
            factorList.push(varName); // add to list of variables to be used for weighting
            $(`option[value="${varName}"]`).attr('disabled', true) // disable in select dropdown
            addFactorEntry(varName);
        }
        
    });

    $(document).on('click', '.remove-factor', (event)=>{  // remove factor when "Remove" is clicked
        let parentId = event.currentTarget.parentElement.id;
        $(`#${parentId}`).remove() // remove div
        
        // remove variable from factor list
        let ind = factorList.indexOf(parentId) 
        if (ind >= 0){
            factorList.splice(ind, 1);
        }

        // disable in select dropdown
        $(`option[value="${parentId}"]`).attr('disabled', false) 

    }); 

    $(document).on('click', '#compute', (event)=>{ // send targets to server to compute weights
        clearError(); // remove any previous errors
        let numFactors = $('.factor').length;
        let factors = $('.factor');
        let groupVar = $('#group-select').val();

        if (!validateInputs(numFactors, groupVar, factorList)){
            event.preventDefault();
            return;
        }

        let targets = populateTargets(factors, numFactors);
        console.log(targets);
        
        if (Object.entries(targets).length > 0){
            if (groupVar !== '' && groupVar !== null){
                groupVar = metaDataObj[groupVar] // replace variable with metadata for that variable
            }
            let data = { // data to send to server
                targetVariables: factorList,
                targetMapping: targets,
                groupingVariable: groupVar,
            }

            $.ajax('/compute-weights', {
                method: 'POST',
                data: JSON.stringify(data),
                contentType: 'application/json',
                processData: false,
                success: (results)=>{
                    console.log(results);
                    if(results.success === "true"){
                        displayResultsView(results.location, results.syntax, results.crosstabs, results.report);
                    } else {
                        showError('Sorry, there was a problem processing your data');
                    }
                },
                error: (jqXHR, textStatus, errorThrown)=>{
                    console.log(`${errorThrown} - ${textStatus}`);
                    showError('Sorry, there was a problem processing your data');
                }
            }); 
        }  else {
            // error if there are no targets
            showError('Sorry, there was a problem processing your data. Please make sure you have chosen at least one factor.');
        }     

    });





});

$(window).on('beforeunload', (event)=>{
    // when user closes tab/window, tell server to delete files and session
    navigator.sendBeacon('/close');
});
