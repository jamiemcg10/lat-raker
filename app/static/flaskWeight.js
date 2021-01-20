$('document').ready(()=>{
    let metaDataList;
    let metaDataObj;
    let factorList = [];

    $('#file').change(function(){    
            $('#file-select-container').append('<p class="status">Uploading...</p>'); 
            let file = getFile();
            sendFile(file);
    });

    function sendFile(fileToSend){
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
                    $('.status').text("Sorry, there was a problem processing your data.");
                }
            },
            error: (jqXHR, textStatus, errorThrown)=>{
                console.log(`${errorThrown} - ${textStatus}`); 
                $('.status').text("Sorry, there was a problem processing your data.");
            }
        });
    }


    function addFactorEntry(varName){    
        $('#weighting-factors').append(`<div id=${varName} class="factor"><p>${varName}</p><p class="remove-factor" id="clear-${varName}">Remove</p></div>`);
        // what if no value labels
        let values = metaDataObj[varName]['values'];
        values.forEach((value) => {
            let val = value.value;
            $(`#clear-${varName}`).before(`<div class="input-group"><label class="${varName}-val-label" for="${varName}_${val}">${val}</label><label class="${varName}-val-label" for="${varName}_${val}">${Object.entries(value.text)[0][1]}</label><div class=input><input type="text" class="dec ${varName}-factor" id="${varName}_${val}"></div><p>%</p></div>`);
        });
    }

    $(document).on('keypress', '.dec', (event)=>{  // make sure text entered in weight factor box is a number
        if (isNaN(parseInt(event.key)) && event.key !== "."){
            event.preventDefault();
        }
    });

    $(document).on('click', '#add-factor', ()=>{
        let varName = $('#q-select').val();
        if (factorList.includes(varName) || varName === null || varName === ''){ // check to make sure variable isn't already added
            return;
        } else {
            factorList.push(varName); // add to list of variables to be used for weighting
            $(`option[value="${varName}"]`).attr('disabled', true) // disable in select dropdown
            addFactorEntry(varName);
        }
        
    });

    $(document).on('click', '.remove-factor', (event)=>{  // remove factor when x is clicked
        let parentId = event.currentTarget.parentElement.id;
        $(`#${parentId}`).remove() // remove div
        // remove variable from list
        let ind = factorList.indexOf(parentId) 
        if (ind >= 0){
            factorList.splice(ind, 1);
        }
        // un-disable
        $(`option[value="${parentId}"]`).attr('disabled', false) // disable in select dropdown

    }); 

    $(document).on('click', '#compute', (event)=>{
        clearError();
        let numFactors = $('.factor').length;
        let factors = $('.factor');
        let groupVar = $('#group-select').val();

        validateInputs(event, numFactors, groupVar, factorList)

        let targets = populateTargets(factors, numFactors);
        console.log(targets);

        if (targets){
            if (groupVar !== '' && groupVar !== null){
                groupVar = metaDataObj[groupVar]
            }
            let data = {
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
                    console.log(results.crosstabs);
                    console.log(results.report);
                    if(results.success){
                        displayResultsView(results.location, results.crosstabs, results.report);
                    } else {
                        displayFetchErrorView();
                    }
                },
                error: (jqXHR, textStatus, errorThrown)=>{
                    console.log(`${errorThrown} - ${textStatus}`);
                    displayFetchErrorView();
                }
            }); 
        }         

    });


    
    function populateTargets(factors, numFactors){
        // loop through factors and validate each sum
        let targets = {};
        console.log(factors);
        for (let i=0; i<numFactors; i++){
            let factor = factors[i];
            console.log(factor);
            console.log(factor.id);
            let q = factor.id;

            // get target percentages
            let pcts = $(`.${q}-factor`);
            console.log(pcts);
            let numValues = $(`.${q}-factor`).length;
            console.log(numValues);
            if (numValues === 0){ // this really shouldn't happen
                showError("Looks like there's a problem.");
                return null;
            } else {
                // loop through percentages
                for (let j=0; j<numValues; j++){
                    let value = pcts[j].labels[0].textContent;
                    let target = pcts[j].value;

                    if (targets[q] === undefined){ // variable has not been added to targets
                        targets[q] = [];
                    }

                    if (target !== '' & target != 0){ // target box is not empty and not 0
                        // problem if only weighted value is 100
                        targets[q][value] = parseFloat(target);
                    }

                }

                if(!sumsTo100(targets[q])){
                    showError(`The target percentages for ${q} must add up to 100.`);
                    return null;
                }

                // replace list with object
                targets[q] = convertArrayToObject(targets[q]);
            }
        }

        return targets;
    }


});

$(window).on('beforeunload', (event)=>{
    navigator.sendBeacon('/close');
});
