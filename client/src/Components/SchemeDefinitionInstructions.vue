<template>
    <ul>
      <li>Choose variables to weight by. These variables must be categorical. Enter the target percentage for each group as a decimal between &gt;0 and 100 (no fractions). Entering a 0 for groups that do not exist in the data is optional.</li>
      <li>Optional: Choose a variable to group by. The weight will be calculated so that the target percentages are the same for each group in this question (e.g., group by ExposedControl and the weighted percentages for target variables will be the same for exposed respondents and control respondents). You cannot group by a variable that targets are set for.</li>
      <li>You will get unexpcted results if you weight an existing group to 0.</li>
    </ul>
</template>