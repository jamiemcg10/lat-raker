<template>
  <div v-bind:id="data.name" class="factor">
    <p>{{ data.name }}</p>
    <div class="input-group"
        v-for="val in data.values"
        v-bind:key="val">
      <label v-bind:class="data.name+'-val-label'" v-bind:for="data.name+'_'+val.value">{{ val.value }}</label>
      <label v-bind:class="data.name+'-val-label'" v-bind:for="data.name+'_'+val.value">{{ Object.entries(val.text)[0][1] }}</label>
      <div class="input">
        <input 
          type="text" 
          v-bind:class="'dec '+data.name+'-factor'" 
          v-bind:id="data.name+'_' +val.value"
          v-on:keypress="validateInput"
          v-on:keyup="updateFactor(val.value, $event)">
      </div>
      <p>%</p>
    </div>
    <p class="remove-factor" 
      v-bind:id="'clear-'+data.name"
      v-on:click="removeFactor(data.name)">Remove</p></div>
</template>

<script>
export default {
  data(){
    return {
      factor: {}      
    }
  },
  props: ['data', 'removeFactor'],
  methods: {
    validateInput(event){
      if (isNaN(parseInt(event.key)) && event.key !== "."){
          event.preventDefault();
      }
      if (event.key === "." && $event.target.value.indexOf(".") >= 0){  // only one decimal per number
        event.preventDefault();
      }
    },
    updateFactor(val, event){
      if (event.target.value === ""){
        delete this.factor[val];
      } else {
        this.factor[val] = Number.parseFloat(event.target.value);
      }
      this.$emit('update', this.factor);
    }
  }
}
</script>

<style scoped>
  .factor {
      margin: 20px 0px;
  }

  .factor p:first-child {
      margin-right: 35px;
      font-weight: bold;
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
  
  .remove-factor {
    text-decoration: underline;
    color: blue;
    float: right;
    margin-left: 35px;
  }

  .remove-factor:hover {
      cursor: pointer;
  }
</style>
