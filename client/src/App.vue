<template>
  <div id="app">
      <h1>RIM Weight Calculator</h1>
      <p class="filename" v-if="datasetName">{{ datasetName }}</p>
      <component 
        v-bind:is="loadedComponent"
        v-on:dataLoaded="displaySelectionView($event)"
        v-on:resultsIn="displayResultsView($event)"
        v-bind:report="report"
        v-bind:crosstabs="crosstabs"
        v-bind:location="location"
        v-bind:syntax="syntax">
      </component>

  </div>
</template>

<script>
import { eventBus } from './main.js';
import FileSelector from './components/FileSelector.vue';
import SchemeDefinition from './components/SchemeDefinition.vue';
import Results from './components/Results.vue';
export default {
  data(){
    return {
      loadedComponent: 'file-selector',
      crosstabs: null,
      report: null,
      datasetName: '',
      syntax: '',
      location: '',
    }
  },
  components: {
    'file-selector': FileSelector,
    'scheme-definition': SchemeDefinition,
    'results': Results
  },
  methods: {
    displaySelectionView(data){
      this.datasetName = data;
      this.loadedComponent = 'scheme-definition';

    },
    displayResultsView(event){
      this.crosstabs = event.crosstabs;
      this.report = event.report;
      this.syntax = event.syntax;
      this.location = event.location;
      
      // fix spacing in text
      // split the report and crosstabs into arrays by new line
      // split each report and crosstabs line line into arrays by tab (3+ spaces)
      let spaceRegex = /\s{3,}/;
      this.report = this.report.split("\n");  
      this.report = this.report.map(row => row.split(spaceRegex)); 
      this.crosstabs = this.crosstabs.split("\n");  
      this.crosstabs = this.crosstabs.map(row => row.split(spaceRegex));
      
      this.loadedComponent = 'results';
      
    },
    closeResources(){
      // when user closes tab/window, tell server to delete files and session
      navigator.sendBeacon('/close');
    }
  }
}
</script>

<style>
  a {
      margin: 5px 0px;
      display: block;
  }

  #add-factor {
      margin-left: 1vw;
  }

  body {
      padding: 25px;
  }

  #compute {
      margin-top: 5vh;
      margin-right: 2vw;
  }

  #Crosstabs {
      margin-top: 5vh;
      max-width: fit-content;
  }

  #Crosstabs .report-row {
      display: flex;
      justify-content: space-between;
  }

  .xt-labels { /* override #Crosstabs .report-row */
      justify-content: initial !important;
  }

  .xt-labels span {
      width: initial;
  }


  #Crosstabs .text { /* override #Crosstabs .report-row */
      justify-content: initial;
  }

  #download-box {
      margin: 20px 0px;
  }

  #error {
      color: red;
      display: block;
  }

  .factor {
      margin: 20px 0px;
  }

  .factor p:first-child {
      margin-right: 35px;
      font-weight: bold;
  }

  #file-form {
      margin-top: 25px;
  }

  .filename {
      font-weight: bold;
      margin-bottom: 15px;
      font-style: italic;
  }
      
  #grouping-var {
      margin-bottom: 35px;
  }

  h1 {
      margin-bottom: 25px;
  }

  .inline {
      display: inline-block;
  }

  input[type="text"] {
      width: 60px;
      margin-right: 3px;
  }

  .input-group {
      margin-right: 25px;
  }

  .factor * {
      display: inline;
  }

  .factor > input {
      width: 40px;
      margin-right: 3px;
  }

  .factor > label {
      margin-left: 2vw;
      margin-right: 1vw;
  }

  [for="weight-name"] {
      font-size: 12px !important;
      font-weight: 500 !important;
  }

  li {
      margin: 0px 13px;
  }

  .remove-factor {
      text-decoration: underline;
      color: blue;
      float: right;
      margin-left: 35px;
  }

  .remove-factor:hover {
      cursor: pointer;
  }

  .report-row :first-child {
      width: 190px;
      display: inline-block;
      font-weight: bold;
  }


  select {
      margin-bottom: 3vh;
  }

  span + span {
      width: 100px;
      display: inline-block;
  }

  ul {
      list-style: initial;
      font-size: smaller;
      margin-bottom: 3vh;
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
