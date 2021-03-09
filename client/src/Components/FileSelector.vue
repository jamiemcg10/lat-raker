<template>
  <div id="file-select-container">
    <form id="file-form">
        <div class="input-group is-stacked">
            <label for="file">Select an SPSS data file (.sav). The file must have a uuid variable.</label>
            <input 
              type="file" 
              name="file" 
              id="file" 
              accept=".sav"
              v-on:change="fileSelected($event)"
              v-bind:ref="'fileInput'"    
              v-show="false"            
              required >
              
              <button 
              class="button is-ghost"
              v-on:click="selectFile"
              type="button">Choose File</button>
            <p>{{ statusText }}</p>
            <p class="error" id="error">{{ errorText }}</p>
        </div>
    </form>
  </div>
</template>

<script>
import { eventBus } from '../main.js';
export default {
  data(){
    return {
      statusText: '',
      errorText: '',
      file: null,
      savFile: '',
      formData: null,
      datasetName: ''
    }
  },
  methods: {
    fileSelected($event){
      this.savFile = $event.target.files[0];
      this.statusText = 'Uploading...'
      this.errorText = '';
      
      this.getFile();
      this.sendFile();
      
    },
    getFile(){
      // create FormData object with selected file to send to server
      this.formData = new FormData(); 
      this.datasetName = this.savFile.name;
      this.formData.append('file', this.savFile);
      
    },
    selectFile(){
      this.$refs.fileInput.click();
    },
    sendFile(){
      // send file to server using ajax request
      $.ajax(eventBus.baseUrl+'get-meta', {
          method: 'POST',
          data: this.formData,
          processData: false,
          contentType: false, 
          success: (results)=>{
              console.log(results);
              this.statusText = ''
              if (results.success === "true"){
                  eventBus.metaDataObj = results.meta_data_obj;
                  eventBus.metaDataList = results.meta_data_array;
                  this.$emit('dataLoaded', this.datasetName);
              } else {
                  this.errorText = results.message;
              }
          },
          error: (jqXHR, textStatus, errorThrown)=>{
              console.log(`${errorThrown} - ${textStatus}`); 
              this.errorText = "Sorry, there was a problem processing your data.";
          }
      });
    }
  }
}
</script>

<style scoped>
  #file-form {
    margin-top: 25px;
  }
</style>
