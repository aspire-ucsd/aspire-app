<script>
export default {
    name: 'QuizLoading',
    friendly_name: "Quiz Loading"
}
</script>

<script setup>

</script>

<template>
    <div class="loading-screen">
        <h3>Retrieving Question...</h3>
        <img class="loading-icon" src="/static/assets/icon-loading.png" />
    </div>
</template>

<style>
.loading-screen {
    height: 100%;
    width:100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.loading-icon {
    max-height: 10%;
    animation: spin 4s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(360deg); }
    100% { transform: rotate(0deg); }
}
</style>