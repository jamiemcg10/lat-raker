<template>
    <div id="Crosstabs">
      <h4>Crosstabs</h4>
      <div
        v-for="(row, i) in crosstabsStringArray" 
        v-bind:class="row.class" 
        v-bind:key="i"
        v-html="row.text">
      </div>
    </div>
</template>

<script>
    import { eventBus } from '../main.js';
    export default {
        data(){
            return {
                crosstabsStringArray: []
            }
        },
        created(){
            // append report and crosstabs to body
            for (let i=0; i<eventBus.crosstabs.length; i++){
                let row = eventBus.crosstabs[i];
                let rowString  = '';
                let rowClass = 'report-row'
                let isHeader = false;
                // fix split question values
                if (row[0] === "Question" && row[1] === "Values"){
                    row[0] = "Question Values";
                    row.splice(1,1);
                } else if (row[0].endsWith("All") && eventBus.crosstabs[i-1][0] === "Question Values"){
                    row[0] = row[0].substring(0,row[0].length-3); // remove "All" from end of string
                    row.splice(1,0,"All");
                }
                row.forEach((cell, i)=>{
                    if (cell === 'Question' && i === 0){
                        rowClass += " text";
                    }
                    if (cell === 'Values' && i === 0 && eventBus.groupSelected){
                        rowString += `<span>Values</span><span></span><span>Total</span>`;  
                        eventBus.groupSelected.values.forEach((value)=>{
                        rowString += `<span>${Object.values(value.text)[0]}</span>`; // handle value labels separately
                        }); 
                        isHeader = true;   
                    } else if (cell === 'Question Values' && i === 0){
                        rowString += `<span>Question Values</span><span></span><span><em>%</em></span>`; 
                        if (eventBus.groupSelected){
                            eventBus.groupSelected.values.forEach((value)=>{
                                rowString += `<span><em>%</em></span>`; 
                            });
                        }
                    } else if (row[0] == 'Question' && i==1){
                        rowString += `<span class="question-title">${cell}</span>`;  // insert each cell into a table cell to control spacing
                    } else if (!isHeader & row[0] !== 'Question Values'){
                        rowString += `<span>${cell}</span>`;  // insert each cell into a table cell to control spacing
                    }
                });


                this.crosstabsStringArray.push({class: rowClass, text: rowString});
            }
        }
    }
</script>

<style>
  #Crosstabs {
      margin-top: 5vh;
      max-width: fit-content;
  }

  #Crosstabs .report-row {
      display: flex;
      justify-content: space-between;
  }

  #Crosstabs .text { /* override #Crosstabs .report-row */
    justify-content: initial;
  }

  span + span {
    width: 100px;
    display: inline-block;
  }

  span.question-title {
    width: fit-content;
    font-style: italic;
    font-weight: bold;
  } 
</style>


