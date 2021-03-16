<template>
  <div>
    <scheme-definition-instructions></scheme-definition-instructions>
    
    <p>Choose question to group by:</p>
    <div class="input has-arrow inline">
      <select id="group-select" v-model="groupSelected">
        <option value=""></option>
        <option 
          v-for="(q, i) in singleChoiceList" 
          v-bind:value="q['name']"
          v-bind:ref="q['name'] + '_groupBy'"
          v-bind:key="i"
        >
            {{ q['name'] }} : {{ Object.entries(q.text)[0][1] }}
        </option>
      </select>
      <div></div>
    </div>
    <div id="grouping-var"></div>
    <p>Choose questions to weight by:</p>
    <div class="input has-arrow inline">
      <select id="q-select" v-model="qSelected">
        <option value=""></option>
        <option 
          v-for="(q, i) in singleChoiceList" 
          v-bind:value="q['name']"
          v-bind:ref="q['name'] + '_factor'"
          v-bind:key="i"
        >
            {{ q['name'] }} : {{ Object.entries(q.text)[0][1] }}
        </option>
      </select>
      <div></div>
    </div>
    <button 
      class="button is-ghost" 
      id="add-factor"
      v-on:click="addFactor">Add</button>
    <div id="weighting-factors">
      <factor-entry 
        v-for="(q, i) in factorList" 
        v-bind:data="getMetaData(q)"
        v-bind:removeFactor="removeFactor"
        v-bind:key="i"
        v-on:update="updateTargets(q, $event)">
      </factor-entry>
    </div>
    <div class="input input-group inline" style="width: fit-content;">
      <label for="weight-name">Weight name:</label>
      <input 
        id="weight-name" 
        v-model="weightName"
        v-on:keypress="removeInvalidVarChars"
        v-on:keyup="removeStartingNum"
      >
    </div>
    <button 
      class="button is-solid" 
      id="compute"
      v-on:click="computeWeights($event)"
      v-html="computeBtn">
    </button>
    <p class="error" id="error">{{ errorText }}</p>
  </div>
</template>

<script>
import { eventBus } from '../main.js';
import FactorEntry from './FactorEntry.vue';
import SchemeDefinitionInstructions from './SchemeDefinitionInstructions.vue';
export default {
  data(){
    return {
      singleChoiceList: [],
      weightName: 'weight',
      qSelected: '',
      groupSelected: '',
      factorList: [],
      errorText: '',
      targets: {},
      computeBtn: "Compute weights"
    }
  },
  methods: {
    appendQuestionSelectionList(){
    // populate select dropdowns from metadata

      eventBus.metaDataList.forEach((question)=>{
          if (question['name'] && question['type'] && (question['type'] === 'single')){ 
              // if the question has a name and type and the type is single, add it as an option 
              // to the select element
              this.singleChoiceList.push(question);

          }
      });

    },
    removeInvalidVarChars($event){    
        let pattern = /\w/;
        if (!pattern.test($event.key)){
          $event.preventDefault();
        }
    },    
    removeStartingNum($event){  
        if (Number.isInteger(Number.parseInt($event.target.value[0]))){
          this.weightName = $event.target.value.substring(1);
        }
    },
    addFactor(){
      // check that variable isn't already being used and add a row to input targets for it
      if (this.factorList.includes(this.qSelected) || this.qSelected === null || this.qSelected === ''){ // check to make sure variable isn't already added
          return;
      } else {
          this.factorList.push(this.qSelected); // add to list of variables to be used for weighting
          let selectedOption = this.$refs[this.qSelected+'_factor'][0];
          let optionInGroupBy = this.$refs[this.qSelected+'_groupBy'][0];
          selectedOption.disabled = true;
          optionInGroupBy.disabled = true;
      }
            
    },
    removeFactor(factor){        
        // remove variable from factor list
        let ind = this.factorList.indexOf(factor); 
        if (ind >= 0){
            this.factorList.splice(ind, 1);
        }
        
        delete this.targets[factor];
        
        // reenable in select dropdown
        let selectedOption = this.$refs[factor+'_factor'][0];
        let optionInGroupBy = this.$refs[factor+'_groupBy'][0];
        selectedOption.disabled = false;        
        optionInGroupBy.disabled = false;

    },
    updateTargets(q, data){
      this.targets[q] = data;
    },
    computeWeights(event){
      // send targets to server to compute weights
      this.errorText = ''; // remove any previous errors
      let numFactors = this.factorList.length;

      if (!this.validateInputs(numFactors)){
          event.preventDefault();
          return;
      }

      if (!(this.validateTargets())){
        return;
      } else if (!Object.entries(this.targets).length > 0){
        this.errorText = 'You must set targets for at least 1 variable.';
        return;
      } else {
        this.computeBtn = '<div class="loader loader--button"></div>';  // add loader to compute button
        if (this.groupSelected !== '' && this.groupSelected !== null){
            eventBus.groupSelected = eventBus.metaDataObj[this.groupSelected] // replace variable with metadata for that variable
        }

        let data = { // data to send to server
            targetVariables: this.factorList,
            targetMapping: this.targets,
            groupingVariable: eventBus.groupSelected,
            weightName: this.weightName || "weight"
        }

        $.ajax(eventBus.baseUrl+'compute-weights', {
            method: 'POST',
            data: JSON.stringify(data),
            contentType: 'application/json',
            processData: false,
            success: (results)=>{
                console.log(results);
                if(results.success === "true"){
                  eventBus.report = results.report;
                  eventBus.crosstabs = results.crosstabs;
                  this.$emit('resultsIn', {location: results.location, syntax: results.syntax})
                } else {
                    this.errorText = 'Sorry, there was a problem processing your data';
                }
            },
            error: (jqXHR, textStatus, errorThrown)=>{
                console.log(`${errorThrown} - ${textStatus}`);
                this.errorText = 'Sorry, there was a problem processing your data';
            }
        }); 
      }    
    },
    validateTargets(){
      // loop through factors, insert them into an object and validate each sum
      for (let i=0; i<this.factorList.length; i++){
        let q = this.targets[this.factorList[i]];
            if(!this.sumsTo100(Object.values(q))){
                this.errorText = `The target percentages for ${this.factorList[i]} must add up to 100.`;
                return null; // return null so weights aren't computed
            }
        }

      return true;

    },
    validateInputs(numFactors){
      // make sure inputs are valid for weighting
      if (numFactors === 0){
          this.errorText = "You need to add at least one factor";
          return false;
      }

      if (this.factorList.includes(this.groupSelected) || this.groupSelected === null){
          this.errorText = "You can't group by a weighting factor";
          return false;
      }

      return true;
    },
    sumsTo100(array){
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
    },
    getMetaData(q){
      return eventBus.metaDataObj[q];
    }
  },
  components: {
    'factor-entry': FactorEntry,
    SchemeDefinitionInstructions
  },
  created(){
    this.appendQuestionSelectionList();
  }
}
</script>

<style scoped>
  #add-factor {
      margin-left: 1vw;
  }

  #compute {
    margin-top: 5vh;
    margin-right: 2vw;
  }

  [for="weight-name"] {
    font-size: 12px !important;
    font-weight: 500 !important;
  }

  #grouping-var {
    margin-bottom: 35px;
  }

  option:disabled {
    color: lightgray !important;
  }

  .input select {
    padding: 0px 30px 0px 10px;
  }

  #weighting-factors {
    margin-top: 2vh;
    width: max-content;
  }

  #weight-name {
    height: 30px;
    width: 125px;
    display: block;
  }
</style>
